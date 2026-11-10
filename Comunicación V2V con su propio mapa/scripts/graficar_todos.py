cat << 'EOF' > scripts/graficar_todos.py
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob
import os

# Buscar todos los archivos CSV generados en la nueva carpeta datos/csv y ordenarlos numéricamente
archivos = sorted(glob.glob('datos/csv/datos_veh*_completo.csv'), key=lambda x: int(os.path.basename(x).split('_')[1][3:]))

for archivo in archivos:
    # Obtener solo el nombre del archivo (ej: datos_veh1_completo.csv) para procesar el ID
    nombre_archivo = os.path.basename(archivo)
    veh_nombre = nombre_archivo.split('_')[1] # Extrae 'veh1', 'veh2', etc.
    
    # Ignorar el archivo vacío (que será el del veh3, el interferente)
    if os.path.getsize(archivo) < 100:
        print(f"[!] {nombre_archivo} está vacío o es muy pequeño (Es el veh3, el interferente). Saltando...")
        continue
        
    print(f"Generando gráficas para {veh_nombre}...")
    
    # 1. Cargar datos
    df = pd.read_csv(archivo, header=None, 
                     names=['tiempo', 'vel_cruda', 'heading_crudo', 'lat_cruda', 'lon_cruda'])
    
    if df.empty:
        continue
        
    # 2. Procesar variables
    df['vel_kmh'] = (df['vel_cruda'] / 100.0) * 3.6
    df['heading'] = df['heading_crudo'] / 10.0
    df['lat'] = df['lat_cruda'] / 10000000.0
    df['lon'] = df['lon_cruda'] / 10000000.0
    df['intervalo_ms'] = df['tiempo'].diff() * 1000
    df['aceleracion'] = (df['vel_cruda'].diff() / 100.0) / df['tiempo'].diff()
    
    # 3. Crear panel de 6 gráficas (3 filas, 2 columnas)
    fig, axes = plt.subplots(3, 2, figsize=(16, 14))
    fig.suptitle(f'Análisis Cinemático y de Red - {veh_nombre.upper()}', fontsize=18, fontweight='bold')
    
    # Gráfica 1: Velocidad
    axes[0, 0].plot(df['tiempo'], df['vel_kmh'], color='blue', linewidth=2)
    axes[0, 0].set_title('Velocidad vs Tiempo')
    axes[0, 0].set_ylabel('Velocidad (km/h)')
    axes[0, 0].grid(True, linestyle='--', alpha=0.7)
    
    # Gráfica 2: Aceleración
    axes[0, 1].plot(df['tiempo'], df['aceleracion'], color='red', linewidth=2)
    axes[0, 1].axhline(y=0, color='black', alpha=0.5)
    axes[0, 1].axhline(y=0.5, color='gray', linestyle='--', label='Umbral ETSI (+0.5)')
    axes[0, 1].axhline(y=-0.5, color='gray', linestyle='--')
    axes[0, 1].set_title('Aceleración vs Tiempo')
    axes[0, 1].set_ylabel('Aceleración (m/s²)')
    axes[0, 1].legend()
    axes[0, 1].grid(True, linestyle='--', alpha=0.7)
    
    # Gráfica 3: Cadencia (Intervalo)
    axes[1, 0].plot(df['tiempo'], df['intervalo_ms'], color='purple', linewidth=2)
    axes[1, 0].axhline(y=100, color='red', linestyle='--', label='Min 100ms')
    axes[1, 0].axhline(y=1000, color='green', linestyle='--', label='Max 1000ms')
    axes[1, 0].set_title('Cadencia de CAM (Intervalo)')
    axes[1, 0].set_ylabel('Intervalo (ms)')
    axes[1, 0].legend()
    axes[1, 0].grid(True, linestyle='--', alpha=0.7)
    
    # Gráfica 4: Heading (Rumbo)
    axes[1, 1].plot(df['tiempo'], df['heading'], color='orange', linewidth=2)
    axes[1, 1].set_title('Rumbo (Heading) vs Tiempo')
    axes[1, 1].set_ylabel('Grados (0-360)')
    axes[1, 1].set_yticks(range(0, 361, 45))
    axes[1, 1].grid(True, linestyle='--', alpha=0.7)
    
    # Gráfica 5: Trayectoria Exacta (Lat vs Lon)
    axes[2, 0].plot(df['lon'], df['lat'], color='gray', alpha=0.5, linewidth=2)
    scatter = axes[2, 0].scatter(df['lon'], df['lat'], c=df['tiempo'], cmap='viridis', s=30, zorder=3)
    axes[2, 0].set_title('Trayectoria Geográfica (Color = Tiempo)')
    axes[2, 0].set_xlabel('Longitud')
    axes[2, 0].set_ylabel('Latitud')
    axes[2, 0].grid(True, linestyle='--', alpha=0.7)
    axes[2, 0].set_aspect('equal')
    cbar = plt.colorbar(scatter, ax=axes[2, 0])
    cbar.set_label('Tiempo (s)')
    
    # Gráfica 6: Trayectoria con Flechas (Dirección exacta)
    dlon = df['lon'].diff()
    dlat = df['lat'].diff()
    axes[2, 1].quiver(df['lon'][:-1], df['lat'][:-1], dlon[:-1], dlat[:-1], 
                      df['heading'][:-1], cmap='twilight', angles='xy', scale_units='xy', scale=1, width=0.005)
    axes[2, 1].set_title('Reconstrucción de Ruta (Flechas = Rumbo)')
    axes[2, 1].set_xlabel('Longitud')
    axes[2, 1].set_ylabel('Latitud')
    axes[2, 1].grid(True, linestyle='--', alpha=0.7)
    axes[2, 1].set_aspect('equal')
    
    # Ajustar diseño y guardar en la nueva carpeta de evidencias
    plt.tight_layout()
    output_file = f'evidencias/Graficas/analisis_{veh_nombre}.png'
    plt.savefig(output_file, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Guardado: {output_file}")

print("¡Todos los análisis han sido generados!")
EOF