# Reto Accidentes Bus-Moto y Ambulancias en Cuenca (SUMO + TraCI)

Solución al Reto de la Práctica 04 de la asignatura **Redes Vehiculares y Heterogéneas** de la Universidad de Cuenca.

## Descripción
Gemelo digital de emergencias sobre la red vial de Cuenca. Simula 3 horas de tráfico, 16 accidentes bus-moto, despacho de ambulancias con disponibilidad aleatoria y retorno dinámico. Incluye una extensión con prioridad semafórica.

## Cumplimiento de Entregables (Sección 4.11 del PDF)
De acuerdo a lo solicitado en el manual de prácticas, este repositorio contiene:
*   **Script principal (`reto_ambulancias.py`):** Implementado en `codigo/reto_final.py` (corrida base) y `codigo/reto_extension.py` (extensión con prioridad).
*   **Script de análisis:** `codigo/analisis.py` y `codigo/generar_mapa.py`.
*   **Red y configuración:** Carpeta `datos/` con `cuenca_ciudad.net.xml`, `vtypes.add.xml`, los 3 `.rou.xml` y `reto.sumocfg`.
*   **Archivos CSV y logs:** En `resultados_base/` y `resultados_extension/` (accidentes.csv, hospitales.csv, stock.csv, eventos.log).
*   **Gráficos (RA_fig_*):** En `resultados/` (base_grafico_a_respuesta.png, base_grafico_b_hospitales.png, base_grafico_c_stock.png, grafico_d_mapa.png y sus equivalentes de extensión).
*   **Evidencias:** En `evidencias/` (capturas de red, accidente, ambulancia y consola).
*   **Informe:** En `informe/` (PDF y LaTeX).

## Estructura del Repositorio
*   **`codigo/`**: Scripts de Python.
*   **`datos/`**: Red de SUMO y archivos de configuración.
*   **`resultados/`**: Gráficos y carpeta `sumo_output/` con XMLs de SUMO.
*   **`resultados_base/`** y **`resultados_extension/`**: CSVs y logs de cada corrida.
*   **`evidencias/`**: Capturas de pantalla.
*   **`informe/`**: PDF final y código LaTeX.

## Ejecución
1. Simulación base: `python3 codigo/reto_final.py`
2. Simulación con extensión: `python3 codigo/reto_extension.py`
3. Análisis y gráficos: `python3 codigo/analisis.py`

## Autor
Mateo Fernando Dután Rivas
