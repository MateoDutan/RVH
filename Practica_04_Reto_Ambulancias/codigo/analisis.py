import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

def analizar_carpeta(carpeta_datos, prefijo_salida, nombre_corrida):
    print(f"\n{'='*50}")
    print(f"ANALIZANDO: {nombre_corrida} (Carpeta: {carpeta_datos})")
    print(f"{'='*50}")

    # Verificar que existan los archivos
    archivo_acc = os.path.join(carpeta_datos, "accidentes.csv")
    archivo_hosp = os.path.join(carpeta_datos, "hospitales.csv")
    archivo_stock = os.path.join(carpeta_datos, "stock.csv")

    if not os.path.exists(archivo_acc):
        print(f"Error: No se encontró {archivo_acc}. Ejecuta primero la simulación correspondiente.")
        return

    df_acc = pd.read_csv(archivo_acc)
    df_hosp = pd.read_csv(archivo_hosp)
    df_stock = pd.read_csv(archivo_stock)

    # --- 1. CALCULAR INDICADORES ---
    print("\n--- INDICADORES DE RESPUESTA ---")
    df_acc_val = df_acc.dropna(subset=['tiempo_respuesta', 'tiempo_total'])

    accidentes_hora = len(df_acc) / 3
    print(f"Accidentes totales: {len(df_acc)} ({accidentes_hora:.1f}/hora)")

    for col in ['tiempo_respuesta', 'tiempo_total']:
        if col in df_acc_val.columns and not df_acc_val[col].empty:
            print(f"\n{col.capitalize()}:")
            print(f"  Mediana: {df_acc_val[col].median():.0f} s")
            print(f"  Media:   {df_acc_val[col].mean():.0f} s")
            print(f"  P90:     {df_acc_val[col].quantile(0.9):.0f} s")
            print(f"  Mínimo:  {df_acc_val[col].min():.0f} s")
            print(f"  Máximo:  {df_acc_val[col].max():.0f} s")

    esperas = df_acc_val[df_acc_val['espera'] > 0]
    print(f"\nAccidentes con espera (falta de ambulancia): {len(esperas)}")
    if not esperas.empty:
        print(f"Espera máxima: {esperas['espera'].max():.0f} s")

    retornos_distintos = df_acc_val[df_acc_val['hospital_origen'] != df_acc_val['hospital_retorno']]
    porcentaje_ret = (len(retornos_distintos) / len(df_acc_val)) * 100 if len(df_acc_val) > 0 else 0
    print(f"\nRetornos a un hospital distinto: {porcentaje_ret:.1f}%")

    # --- 2. GRÁFICOS ---
    print("\nGenerando gráficos...")

    # Asegurar que exista la carpeta de salida
    if not os.path.exists("resultados"):
        os.makedirs("resultados")

    # Gráfico A: Tiempo de respuesta por accidente
    plt.figure(figsize=(10, 5))
    x = range(len(df_acc_val))
    plt.bar(x, df_acc_val['tiempo_respuesta'], color='#1f77b4')
    plt.axhline(df_acc_val['tiempo_respuesta'].median(), color='red', linestyle='--', label='Mediana')
    plt.axhline(df_acc_val['tiempo_respuesta'].quantile(0.9), color='orange', linestyle=':', label='P90')
    plt.xticks(x, df_acc_val['id'], rotation=45)
    plt.ylabel('Tiempo (s)')
    plt.title(f'Tiempo de Respuesta por Accidente ({nombre_corrida})')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"resultados/{prefijo_salida}grafico_a_respuesta.png", dpi=150)
    plt.close()

    # Gráfico B: Uso por hospital
    plt.figure(figsize=(10, 6))
    x = range(len(df_hosp))
    width = 0.25
    plt.bar([i - width for i in x], df_hosp['stock_inicial'], width=width, label='Stock Inicial', color='lightgray')
    plt.bar(x, df_hosp['despachos'], width=width, label='Despachos', color='navy')
    plt.bar([i + width for i in x], df_hosp['retornos'], width=width, label='Retornos', color='cornflowerblue')
    plt.xticks(x, df_hosp['hospital'], rotation=45)
    plt.ylabel('Cantidad')
    plt.title(f'Uso de Ambulancias por Hospital ({nombre_corrida})')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"resultados/{prefijo_salida}grafico_b_hospitales.png", dpi=150)
    plt.close()

    # Gráfico C: Stock disponible en el tiempo
    plt.figure(figsize=(12, 6))
    for hospital in df_stock['hospital'].unique():
        df_h = df_stock[df_stock['hospital'] == hospital]
        plt.plot(df_h['tiempo'] / 60, df_h['stock'], label=hospital)
    plt.xlabel('Tiempo (minutos)')
    plt.ylabel('Stock Disponible')
    plt.title(f'Evolución del Stock de Ambulancias ({nombre_corrida})')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(f"resultados/{prefijo_salida}grafico_c_stock.png", dpi=150)
    plt.close()

    print(f"Gráficos guardados en 'resultados/' con prefijo '{prefijo_salida}'")

# --- EJECUTAR PARA AMBAS CORRIDAS ---
if __name__ == "__main__":
    analizar_carpeta("resultados_base", "base_", "CORRIDA BASE")
    analizar_carpeta("resultados_extension", "ext_", "EXTENSIÓN (Prioridad)")
    print("\n¡Análisis completo para ambas corridas! Revisa la carpeta 'resultados/'.")