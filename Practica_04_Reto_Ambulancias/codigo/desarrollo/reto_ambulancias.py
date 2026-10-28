import os
import sys

# Configurar la ruta de SUMO para encontrar traci y sumolib
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Por favor, declara la variable de entorno 'SUMO_HOME'")

import traci
import random
import collections
import math

# --- TAREA 2.2: Semilla para reproducibilidad ---
random.seed(42)

# --- DATOS DE LOS HOSPITALES (Tabla 4.5) ---
HOSPITALES = {
    "VCM":        {"lon": -78.992923, "lat": -2.911098, "tipo": "público"},
    "IESS_JCA":   {"lon": -78.970118, "lat": -2.898698, "tipo": "público"},
    "MILITAR":    {"lon": -79.003968, "lat": -2.903146, "tipo": "público"},
    "MUNI_PAT":   {"lon": -78.982263, "lat": -2.866103, "tipo": "público"},
    "MUNI_VALLE": {"lon": -78.961959, "lat": -2.919522, "tipo": "público"},
    "MONTE_SINAI":{"lon": -79.007373, "lat": -2.908606, "tipo": "privado"},
    "DEL_RIO":    {"lon": -78.960796, "lat": -2.892939, "tipo": "privado"}
}

class Hospital:
    def __init__(self, id_hosp, lon, lat, tipo):
        self.id = id_hosp
        self.tipo = tipo
        self.lon = lon   # <-- AGREGAR
        self.lat = lat   # <-- AGREGAR

        # Tarea 2.1: Convertir WGS84 a arista con vClass emergency
        self.arista, self.pos, self.carril = traci.simulation.convertRoad(
            lon, lat, isGeo=True, vClass="emergency"
        )
        self.calle = traci.edge.getStreetName(self.arista)
        
        # Verificar distancia
        x_hosp, y_hosp = traci.simulation.convertGeo(lon, lat, fromGeo=True)
        x_arista, y_arista = traci.simulation.convert2D(self.arista, self.pos)
        self.dist = math.hypot(x_hosp - x_arista, y_hosp - y_arista)
        
        # Tarea 2.2: Cola de disponibilidad y stock aleatorio
        stock_inicial = random.randint(1, 3) if tipo == "público" else random.randint(0, 1)
        self.cola = collections.deque([f"U_{self.id}_{i}" for i in range(stock_inicial)])
        self.stock_inicial = stock_inicial
        self.psin = 0.25

def main():
    # Iniciar SUMO con interfaz gráfica para ver los POIs
    traci.start(["sumo-gui", "-c", "reto.sumocfg", "--start"])
    
    # 1. Inicializar hospitales
    lista_hospitales = []
    print("\n--- TABLA DE HOSPITALES ---")
    print(f"{'Hospital':<12} | {'Tipo':<8} | {'Arista':<15} | {'Calle':<25} | {'Dist':<5} | {'Stock'}")
    print("-" * 85)
    
    for hid, info in HOSPITALES.items():
        h = Hospital(hid, info["lon"], info["lat"], info["tipo"])
        lista_hospitales.append(h)
        
        # Tarea 2.1: Dibujar POI (Rojo para públicos, Azul para privados)
        color = (255, 0, 0, 255) if h.tipo == "público" else (0, 0, 255, 255)
        # Usamos las coordenadas del mapa (x,y) para el POI
        x, y = traci.simulation.convertGeo(h.lon, h.lat)
        traci.poi.add(f"POI_{h.id}", x, y, color, poiType="hospital")
        
        print(f"{h.id:<12} | {h.tipo:<8} | {h.arista:<15} | {h.calle[:25]:<25} | {h.dist:>4.0f}m | {h.stock_inicial}")
    
    print("-" * 85)
    print("¡Revisa SUMO-GUI para ver los 7 POIs sobre las avenidas!\n")
    
    # --- TAREA 2.3: Ambulancia de prueba VCM -> IESS_JCA ---
    print("--- PRUEBA DE AMBULANCIA (t=120s) ---")
    t = 0
    while t < 120:
        traci.simulationStep()
        t += 1
        
    h_origen = next(h for h in lista_hospitales if h.id == "VCM")
    h_destino = next(h for h in lista_hospitales if h.id == "IESS_JCA")
    
    # Calcular ruta con findRoute
    ruta = traci.simulation.findRoute(h_origen.arista, h_destino.arista, vType="ambulance")
    
    if ruta.edges:
        print(f"Ruta encontrada: {len(ruta.edges)} aristas, {ruta.length:.0f} m, ETA: {ruta.travelTime:.0f} s")
        
        # Insertar ambulancia
        id_amb = "ambulancia_prueba"
        traci.route.add(id_amb, ruta.edges)
        traci.vehicle.add(
            id_amb, id_amb, typeID="ambulance", 
            depart="now", departPos=h_origen.pos, departSpeed=0
        )
        
        # Avanzar hasta que llegue
        llegada = False
        while not llegada:
            traci.simulationStep()
            t += 1
            if id_amb in traci.simulation.getArrivedIDList():
                llegada = True
                print(f"¡Ambulancia llegó a IESS_JCA en el paso {t} (t={t}s)!")
                print(f"Tiempo real medido: {t - 120} s")
            elif id_amb not in traci.vehicle.getIDList():
                print(f"Error: La ambulancia desapareció (posible teleport).")
                break
    else:
        print("Error: No se encontró ruta entre VCM e IESS_JCA.")
    
    traci.close()
    print("\nSimulación finalizada.")

if __name__ == "__main__":
    main()
