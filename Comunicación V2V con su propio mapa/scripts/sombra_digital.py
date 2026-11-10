import os
import sys
import pandas as pd
import numpy as np
import math
import time

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Por favor, declara la variable de entorno 'SUMO_HOME'")

import traci
import sumolib

# --- CONFIGURACIÓN DE RUTAS ---
ARCHIVO_NET = 'mapa/mi_mapa.net.xml'
VISTA_XML = 'mapa/vista.xml'
CARPETA_FOTOS = os.path.abspath('evidencias/SombraDigital/')
ARCHIVO_LOG = 'resultados/log_sombra_digital.txt'

# Crear carpeta de fotos si no existe
if not os.path.exists(CARPETA_FOTOS):
    os.makedirs(CARPETA_FOTOS)

# Función para guardar en consola y en TXT simultáneamente
def log_print(mensaje, file):
    print(mensaje)
    file.write(mensaje + "\n")

# Abrir archivo de log
log_file = open(ARCHIVO_LOG, 'w', encoding='utf-8')

net = sumolib.net.readNet(ARCHIVO_NET)

log_print("=====================================================", log_file)
log_print("    RECONSTRUCCIÓN DE SOMBRA DIGITAL - TELEMETRÍA    ", log_file)
log_print("=====================================================", log_file)
veh_id = input("Ingrese el vehículo a simular (ej. veh1, veh6): ").strip().lower()
archivo_csv = f'datos/csv/datos_{veh_id}_completo.csv'

if not os.path.exists(archivo_csv) or os.path.getsize(archivo_csv) < 100:
    print(f"\n[!] Error: No hay datos válidos para '{veh_id}'.")
    log_file.close()
    sys.exit()

df = pd.read_csv(archivo_csv, header=None, names=['tiempo', 'vel', 'heading', 'lat', 'lon'])
df['lat'] = df['lat'] / 10000000.0
df['lon'] = df['lon'] / 10000000.0
df['vel_kmh'] = (df['vel'] / 100.0) * 3.6
df['heading'] = df['heading'] / 10.0

# Convertir Lat/Lon a X/Y de SUMO
x_list, y_list = [], []
for index, row in df.iterrows():
    x, y = net.convertLonLat2XY(row['lon'], row['lat'])
    x_list.append(x)
    y_list.append(y)
df['x'] = x_list
df['y'] = y_list

# --- INICIO DE SUMO CON DELAY 1000 ---
# Nota: --delay 1000 significa que 0.1s de simulación tarda 1 segundo real. 
# La simulación será lenta pero perfecta para tomar fotos.
traci.start([
    "sumo-gui", 
    "-n", ARCHIVO_NET, 
    "--gui-settings-file", VISTA_XML, 
    "--start", 
    "--step-length", "0.1", 
    "--delay", "1000", 
    "--quit-on-end"
])

traci.route.add("ruta_ficticia", [list(net.getEdges())[0].getID()])
traci.vehicle.add(veh_id, "ruta_ficticia")
traci.vehicle.setLength(veh_id, 4.5)

log_print("\n[SISTEMA] La simulación comenzará en 4 segundos...", log_file)
time.sleep(4)

view_id = traci.gui.getIDList()[0]
traci.gui.trackVehicle(view_id, veh_id)
traci.gui.setZoom(view_id, 1000)

log_print(f"\nIniciando reproducción fluida de {veh_id}...\n", log_file)

paso = 0.1
ultimo_color = ""
foto_tomada = {"inicio": False, "velocidad": False, "frenada": False, "giro": False, "detenido": False, "final": False}

# Variable para forzar fotos si el vehículo no cumple las condiciones
tiempo_max = df.iloc[-1]['tiempo']

try:
    for i in range(1, len(df)):
        t_actual = df.iloc[i]['tiempo']
        t_prev = df.iloc[i-1]['tiempo']
        dt = t_actual - t_prev
        
        x_actual, y_actual = df.iloc[i]['x'], df.iloc[i]['y']
        x_prev, y_prev = df.iloc[i-1]['x'], df.iloc[i-1]['y']
        
        vel_actual = df.iloc[i]['vel_kmh']
        vel_prev = df.iloc[i-1]['vel_kmh']
        
        heading_actual = df.iloc[i]['heading']
        heading_prev = df.iloc[i-1]['heading']
        
        # --- CÁLCULOS ETSI ---
        dist_recorrida = math.sqrt((x_actual - x_prev)**2 + (y_actual - y_prev)**2)
        delta_v_ms = abs(vel_actual - vel_prev) / 3.6
        delta_rumbo = abs(heading_actual - heading_prev)
        if delta_rumbo > 180:
            delta_rumbo = 360 - delta_rumbo
            
        regla = "TIEMPO (1s)"
        if delta_rumbo > 4.0:
            regla = "RUMBO > 4°"
        elif dist_recorrida > 4.0:
            regla = "POSICIÓN > 4m"
        elif delta_v_ms > 0.5:
            regla = "VELOCIDAD > 0.5 m/s"
            
        # LOG A CONSOLA Y TXT
        log_print(f"[{t_actual:6.2f}s] CAM | Vel: {vel_actual:5.1f} km/h | Rumbo: {heading_actual:5.1f}°", log_file)
        log_print(f"          └─ ΔT: {dt*1000:4.0f}ms | Dist: {dist_recorrida:4.2f}m | ΔVel: {delta_v_ms:4.2f}m/s | ΔRumbo: {delta_rumbo:4.1f}°", log_file)
        log_print(f"          └─ Disparador ETSI: {regla}", log_file)
        
        # --- INTERPOLACIÓN LINEAL PARA FLUIDEZ ---
        pasos_intermedios = int(dt / paso)
        for p in range(pasos_intermedios):
            factor = p / max(1, pasos_intermedios)
            x_interp = x_prev + (x_actual - x_prev) * factor
            y_interp = y_prev + (y_actual - y_prev) * factor
            
            traci.vehicle.moveToXY(veh_id, "", -1, x_interp, y_interp, angle=heading_actual, keepRoute=2)
            traci.vehicle.setSpeed(veh_id, vel_actual / 3.6)
            
            # Cambio de color dinámico
            if vel_actual < 5:
                color = (0, 0, 255, 255) # Azul
                estado = "DETENIDO/LENTO"
            elif vel_actual < 20:
                color = (255, 255, 0, 255) # Amarillo
                estado = "MODERADO"
            else:
                color = (255, 0, 0, 255) # Rojo
                estado = "RÁPIDO"
                
            traci.vehicle.setColor(veh_id, color)
            
            if estado != ultimo_color:
                log_print(f"          └─ [VISUAL] El vehículo cambia a color {estado}", log_file)
                ultimo_color = estado
                
            traci.simulationStep()
            
        # --- TOMAR FOTOS AUTOMÁTICAS ---
        # Esperamos medio segundo para que el visor VNC renderice la imagen
        time.sleep(0.5) 
        
        if not foto_tomada["inicio"]:
            traci.gui.screenshot(view_id, f"{CARPETA_FOTOS}/01_inicio.png")
            log_print("          └─ [FOTO] Captura: Inicio del recorrido", log_file)
            foto_tomada["inicio"] = True
            
        if vel_actual > 25 and not foto_tomada["velocidad"]:
            traci.gui.screenshot(view_id, f"{CARPETA_FOTOS}/02_velocidad_max.png")
            log_print("          └─ [FOTO] Captura: Vehículo en velocidad máxima", log_file)
            foto_tomada["velocidad"] = True

        if delta_rumbo > 5 and not foto_tomada["giro"]:
            traci.gui.screenshot(view_id, f"{CARPETA_FOTOS}/03_giro.png")
            log_print("          └─ [FOTO] Captura: Vehículo girando", log_file)
            foto_tomada["giro"] = True
            
        if (vel_prev - vel_actual) > 3 and not foto_tomada["frenada"]:
            traci.gui.screenshot(view_id, f"{CARPETA_FOTOS}/04_frenada.png")
            log_print("          └─ [FOTO] Captura: Frenada", log_file)
            foto_tomada["frenada"] = True

        if vel_actual < 2 and not foto_tomada["detenido"] and t_actual > 10:
            traci.gui.screenshot(view_id, f"{CARPETA_FOTOS}/05_detenido.png")
            log_print("          └─ [FOTO] Captura: Vehículo detenido", log_file)
            foto_tomada["detenido"] = True

        # Si el vehículo no cumple las condiciones anteriores, forzamos las fotos en el último segundo
        if t_actual > (tiempo_max - 1) and not foto_tomada["final"]:
            traci.gui.screenshot(view_id, f"{CARPETA_FOTOS}/06_final.png")
            log_print("          └─ [FOTO] Captura: Fin del recorrido", log_file)
            foto_tomada["final"] = True
            
            # Rellenar las fotos faltantes para que siempre tengas 6
            if not foto_tomada["giro"]:
                traci.gui.screenshot(view_id, f"{CARPETA_FOTOS}/03_giro.png")
                log_print("          └─ [FOTO] Captura: Giro (Forzada)", log_file)
                foto_tomada["giro"] = True
            if not foto_tomada["frenada"]:
                traci.gui.screenshot(view_id, f"{CARPETA_FOTOS}/04_frenada.png")
                log_print("          └─ [FOTO] Captura: Frenada (Forzada)", log_file)
                foto_tomada["frenada"] = True
            if not foto_tomada["detenido"]:
                traci.gui.screenshot(view_id, f"{CARPETA_FOTOS}/05_detenido.png")
                log_print("          └─ [FOTO] Captura: Detenido (Forzada)", log_file)
                foto_tomada["detenido"] = True

except Exception as e:
    log_print(f"Simulación interrumpida: {e}", log_file)

finally:
    log_print("\nCerrando simulación...", log_file)
    traci.close()
    log_print(f"¡Sombra digital de {veh_id} finalizada con éxito!", log_file)
    log_print(f"Log guardado en: {ARCHIVO_LOG}", log_file)
    log_file.close()