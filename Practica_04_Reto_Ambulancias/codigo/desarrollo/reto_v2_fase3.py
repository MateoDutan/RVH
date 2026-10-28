import os
import sys

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Por favor, declara la variable de entorno 'SUMO_HOME'")

import traci
import random

random.seed(42)

def generar_agenda():
    agenda = []
    for hora in range(3):
        for _ in range(5):
            t = hora * 3600 + random.uniform(300, 3480) 
            agenda.append(t)
    return sorted(agenda)

def main():
    print("Iniciando SUMO-GUI (Fase 3)...")
    # Usamos sumo-gui y un delay para que puedas ver la simulación
    traci.start(["sumo-gui", "-c", "reto.sumocfg", "--delay", "50", "--start"])
    
    agenda = generar_agenda()
    print(f"AGENDA: {len(agenda)} accidentes programados.")
    
    accidentes = []
    colisiones_vistas = set()
    t = 0
    
    while t < 12600:
        traci.simulationStep()
        t += 1
        
        # --- GENERAR ACCIDENTES ---
        if agenda and t >= agenda[0]:
            # FILTRO: Bus en marcha, fuera de cruce, >60m recorridos y velocidad >4
            buses = [v for v in traci.vehicle.getIDList() 
                     if traci.vehicle.getTypeID(v) == "bus" 
                     and not traci.vehicle.getRoadID(v).startswith(":")
                     and traci.vehicle.getLanePosition(v) > 60
                     and traci.vehicle.getSpeed(v) > 4]
            
            if buses:
                bus = random.choice(buses)
                try:
                    id_moto = f"moto_imprudente_{t}"
                    
                    # Calcular posición exacta 45m detrás
                    pos_bus = traci.vehicle.getLanePosition(bus)
                    pos_moto = max(0, pos_bus - 45)
                    
                    ruta_bus = traci.vehicle.getRoute(bus)
                    idx_bus = traci.vehicle.getRouteIndex(bus)
                    ruta_moto = ruta_bus[idx_bus:]
                    
                    traci.route.add(id_moto, ruta_moto)
                    traci.vehicle.add(
                        id_moto, id_moto, typeID="moto", 
                        depart="now", 
                        departPos=str(pos_moto), 
                        departSpeed=22,
                        departLane=traci.vehicle.getLaneIndex(bus)
                    )
                    
                    # Sacar del modelo
                    traci.vehicle.setSpeedMode(id_moto, 0)
                    traci.vehicle.setLaneChangeMode(id_moto, 0)
                    traci.vehicle.setSpeed(id_moto, 22)
                    traci.vehicle.setColor(id_moto, (255, 165, 0, 255)) # Naranja
                    
                    print(f"[{t}s] IMPRUDENTE moto {id_moto} insertada a {pos_moto:.0f}m (bus en {pos_bus:.0f}m)")
                except Exception as e:
                    pass
            agenda.pop(0)

        # --- DETECTAR COLISIONES ---
        for col in traci.simulation.getCollisions():
            tipos = {col.colliderType, col.victimType}
            if "bus" in tipos and "motorcycle" in tipos:
                pareja = tuple(sorted([col.collider, col.victim]))
                if pareja not in colisiones_vistas:
                    colisiones_vistas.add(pareja)
                    
                    bus = col.collider if col.colliderType == "bus" else col.victim
                    moto = col.victim if col.colliderType == "bus" else col.collider
                    arista = col.lane if not col.lane.startswith(":") else traci.vehicle.getRoadID(bus)
                    
                    # Crear POI Amarillo en el lugar del accidente
                    x_bus, y_bus = traci.vehicle.getPosition(bus)
                    traci.poi.add(f"acc_{t}", x_bus, y_bus, (255, 255, 0, 255), poiType="accidente")
                    
                    acc = {"id": f"ACC{len(accidentes)+1:02d}", "t": t, "bus": bus, "moto": moto, "arista": arista}
                    accidentes.append(acc)
                    print(f"[{t}s] ACCIDENTE {acc['id']} {bus} x {moto} en {arista}")
                    
                    # Inmovilizar
                    for v in [bus, moto]:
                        traci.vehicle.setSpeedMode(v, 0)
                        traci.vehicle.setSpeed(v, 0)
                        traci.vehicle.setColor(v, (255, 0, 0, 255)) # Rojo
                    for v in [bus, moto]:
                        traci.vehicle.setSpeedMode(v, 31)
                        traci.vehicle.setSpeed(v, 0)

        if t % 1800 == 0:
            print(f"--- Minuto {t//60} completado. Accidentes: {len(accidentes)} ---")

    # Cerramos con True para que la ventana de SUMO-GUI no se cierre hasta que tú la cierres
    traci.close(True) 
    print("Simulación finalizada con éxito.")

if __name__ == "__main__":
    main()