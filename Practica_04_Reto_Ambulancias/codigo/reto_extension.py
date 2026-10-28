import os
import sys
import csv
import random
import collections
import math

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.insert(0, tools)
else:
    sys.exit("Por favor, declara la variable de entorno 'SUMO_HOME'")

import traci

random.seed(42)

# --- CONFIGURACIÓN DE CARPETA Y LOG ---
carpeta_resultados = "resultados_extension"
if not os.path.exists(carpeta_resultados):
    os.makedirs(carpeta_resultados)

# Redirigir la salida estándar (print) a un archivo de log
log_path = os.path.join(carpeta_resultados, "eventos.log")
log_file = open(log_path, "w", encoding="utf-8")
sys.stdout = log_file

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
        self.lon = lon
        self.lat = lat
        self.arista, self.pos, self.carril = traci.simulation.convertRoad(lon, lat, isGeo=True, vClass="emergency")
        
        x_hosp, y_hosp = traci.simulation.convertGeo(lon, lat, fromGeo=True)
        x_arista, y_arista = traci.simulation.convert2D(self.arista, self.pos)
        self.dist = math.hypot(x_hosp - x_arista, y_hosp - y_arista)
        
        self.stock_inicial = random.randint(1, 3) if tipo == "público" else random.randint(0, 1)
        self.cola = collections.deque([f"U_{self.id}_{i}" for i in range(self.stock_inicial)])
        self.psin = 0.25
        
        self.despachos = 0
        self.retornos = 0
        self.rechazos = 0
        self.tiempo_ocupado = 0

def dibujar_circulo(poly_id, x, y, radio, color, tipo):
    shape = []
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        shape.append((x + radio * math.cos(rad), y + radio * math.sin(rad)))
    traci.polygon.add(poly_id, shape, color, fill=True, polygonType=tipo)

def generar_agenda():
    agenda = []
    for hora in range(3):
        for _ in range(5):
            t = hora * 3600 + random.uniform(300, 3480)
            agenda.append(t)
    return sorted(agenda)

def crear_gui_settings():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<viewsettings>
    <scheme name="real world"/>
    <vehicles vehicleScale="37"/>
</viewsettings>
"""
    with open("gui-settings.xml", "w") as f:
        f.write(xml_content)

def guardar_csv(accidentes, hospitales, historial_stock):
    # 1. accidentes.csv
    with open(os.path.join(carpeta_resultados, "accidentes.csv"), "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "t_accidente", "t_despacho", "t_llegada", "t_fin", "hospital_origen", "hospital_retorno", "tiempo_respuesta", "tiempo_total", "espera"])
        for a in accidentes:
            t_desp = a.get("t_despacho", "")
            t_lleg = a.get("t_llegada", "")
            t_fin = a.get("t_fin", "")
            h_orig = a["hospital"].id if a.get("hospital") else "Ninguno"
            h_ret = a["hospital_retorno"].id if a.get("hospital_retorno") else "Ninguno"
            
            resp = (t_lleg - t_desp) if t_lleg and t_desp else ""
            total = (t_lleg - a["t"]) if t_lleg else ""
            espera = (t_desp - a["t"]) if t_desp else ""
            
            writer.writerow([a["id"], a["t"], t_desp, t_lleg, t_fin, h_orig, h_ret, resp, total, espera])

    # 2. hospitales.csv
    with open(os.path.join(carpeta_resultados, "hospitales.csv"), "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["hospital", "tipo", "stock_inicial", "stock_final", "despachos", "retornos", "rechazos", "tiempo_ocupado", "utilizacion"])
        for h in hospitales:
            util = (h.tiempo_ocupado / (10800 * h.stock_inicial)) if h.stock_inicial > 0 else 0
            writer.writerow([h.id, h.tipo, h.stock_inicial, len(h.cola), h.despachos, h.retornos, h.rechazos, h.tiempo_ocupado, f"{util:.2%}"])

    # 3. stock.csv
    with open(os.path.join(carpeta_resultados, "stock.csv"), "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["tiempo", "hospital", "stock"])
        for row in historial_stock:
            writer.writerow(row)

def main():
    print("Iniciando SUMO-GUI (EXTENSIÓN)...")
    crear_gui_settings()
    traci.start(["sumo-gui", "-c", "datos/reto.sumocfg", "-g", "gui-settings.xml", "--delay", "50", "--start"])
    
    hospitales = [Hospital(hid, info["lon"], info["lat"], info["tipo"]) for hid, info in HOSPITALES.items()]
    
    for h in hospitales:
        color = (255, 0, 0, 200) if h.tipo == "público" else (0, 0, 255, 200)
        x, y = traci.simulation.convertGeo(h.lon, h.lat, fromGeo=True)
        dibujar_circulo(f"POLY_{h.id}", x, y, 70, color, "hospital")
    
    agenda = generar_agenda()
    print(f"AGENDA: {len(agenda)} accidentes programados.")
    
    accidentes = []
    colisiones_vistas = set()
    motos_pendientes = []
    motos_activas = []
    historial_stock = []
    t = 0
    
    while t < 12600:
        traci.simulationStep()
        t += 1
        
        for m in list(motos_pendientes):
            if m["id"] in traci.vehicle.getIDList():
                try:
                    traci.vehicle.setSpeedMode(m["id"], 0)
                    traci.vehicle.setLaneChangeMode(m["id"], 0)
                    traci.vehicle.setSpeed(m["id"], 30)
                    traci.vehicle.setColor(m["id"], (255, 0, 255, 255))
                    motos_activas.append(m)
                except Exception:
                    pass
                motos_pendientes.remove(m)
            elif t - m["t_insert"] > 5:
                motos_pendientes.remove(m)

        if agenda and t >= agenda[0]:
            buses = []
            for v in traci.vehicle.getIDList():
                if traci.vehicle.getTypeID(v) != "bus": continue
                road = traci.vehicle.getRoadID(v)
                if road.startswith(":"): continue
                if traci.vehicle.getLanePosition(v) <= 60: continue
                if traci.vehicle.getSpeed(v) <= 4: continue
                lane_id = traci.vehicle.getLaneID(v)
                allowed = traci.lane.getAllowed(lane_id)
                if allowed and "motorcycle" not in allowed and "all" not in allowed: continue
                lane_length = traci.lane.getLength(lane_id)
                if traci.vehicle.getLanePosition(v) > lane_length - 50: continue
                buses.append(v)
            
            if buses:
                bus = random.choice(buses)
                try:
                    id_moto = f"moto_imprudente_{t}"
                    pos_bus = traci.vehicle.getLanePosition(bus)
                    largo_bus = traci.vehicle.getLength(bus)
                    pos_moto = max(0, pos_bus - largo_bus - 20)
                    
                    ruta_bus = traci.vehicle.getRoute(bus)
                    idx_bus = traci.vehicle.getRouteIndex(bus)
                    ruta_moto = ruta_bus[idx_bus:]
                    
                    traci.route.add(id_moto, ruta_moto)
                    traci.vehicle.add(
                        id_moto, id_moto, typeID="moto", 
                        depart="now", departPos=str(pos_moto), departSpeed=0,
                        departLane=str(traci.vehicle.getLaneIndex(bus))
                    )
                    
                    motos_pendientes.append({"id": id_moto, "bus": bus, "t_insert": t})
                except Exception:
                    agenda.append(t + 20)
                    agenda.sort()
            else:
                agenda.append(t + 20)
                agenda.sort()
            
            agenda.pop(0)

        for m in list(motos_activas):
            if m["id"] in traci.vehicle.getIDList():
                try:
                    traci.vehicle.setSpeed(m["id"], 30)
                except:
                    pass
            else:
                motos_activas.remove(m)

        for col in traci.simulation.getCollisions():
            tipos = {col.colliderType, col.victimType}
            if "bus" in tipos and "moto" in tipos:
                pareja = tuple(sorted([col.collider, col.victim]))
                if pareja not in colisiones_vistas:
                    colisiones_vistas.add(pareja)
                    
                    bus = col.collider if col.colliderType == "bus" else col.victim
                    moto = col.victim if col.colliderType == "bus" else col.collider
                    
                    ruta_bus = traci.vehicle.getRoute(bus)
                    idx_bus = traci.vehicle.getRouteIndex(bus)
                    arista_acc = ruta_bus[idx_bus]
                    if arista_acc.startswith(":") and idx_bus + 1 < len(ruta_bus):
                        arista_acc = ruta_bus[idx_bus + 1]
                    
                    pos_acc = traci.vehicle.getLanePosition(bus)
                    lane_id = traci.vehicle.getLaneID(bus)
                    lane_length = traci.lane.getLength(lane_id)
                    pos_acc = max(0, min(pos_acc, lane_length))
                    
                    x_acc, y_acc = traci.vehicle.getPosition(bus)
                    dibujar_circulo(f"acc_{t}", x_acc, y_acc, 150, (255, 255, 0, 255), "accidente")
                    
                    acc = {"id": f"ACC{len(accidentes)+1:02d}", "t": t, "bus": bus, "moto": moto, 
                           "arista": arista_acc, "pos": pos_acc, "x": x_acc, "y": y_acc,
                           "estado": "espera", "hospital": None}
                    accidentes.append(acc)
                    print(f"\n[{t}s] 💥 ACCIDENTE {acc['id']} {bus} x {moto} en {arista_acc}\n")
                    
                    for v in [bus, moto]:
                        traci.vehicle.setSpeedMode(v, 0)
                        traci.vehicle.setSpeed(v, 0)
                        traci.vehicle.setColor(v, (255, 0, 0, 255))
                    for v in [bus, moto]:
                        traci.vehicle.setSpeedMode(v, 31)
                        traci.vehicle.setSpeed(v, 0)
                    
                    motos_activas = [m for m in motos_activas if m["id"] != moto]

        for m in list(motos_activas):
            if t - m["t_insert"] >= 60:
                if m["id"] in traci.vehicle.getIDList():
                    traci.vehicle.remove(m["id"])
                motos_activas.remove(m)
                agenda.append(t + 60)
                agenda.sort()

        for acc in accidentes:
            if acc["estado"] == "espera":
                mejor_hosp = None
                mejor_tiempo = float('inf')
                
                for h in hospitales:
                    if len(h.cola) > 0:
                        if random.random() <= h.psin:
                            h.rechazos += 1
                            continue
                        
                        ruta = traci.simulation.findRoute(h.arista, acc["arista"], vType="ambulance", depart=-1, routingMode=1)
                        if ruta.edges and ruta.travelTime < mejor_tiempo:
                            mejor_tiempo = ruta.travelTime
                            mejor_hosp = h
                            mejor_ruta = ruta
                            
                if mejor_hosp:
                    mejor_hosp.despachos += 1
                    unidad = mejor_hosp.cola.popleft()
                    id_amb = f"amb_{unidad}_{acc['id']}"
                    traci.route.add(id_amb, mejor_ruta.edges)
                    traci.vehicle.add(id_amb, id_amb, typeID="ambulance", depart="now", departPos=mejor_hosp.pos, departSpeed=0)
                    
                    # --- EXTENSIÓN: Prioridad semafórica ---
                    traci.vehicle.setSpeedMode(id_amb, 7) 
                    
                    acc["estado"] = "en_camino"
                    acc["hospital"] = mejor_hosp
                    acc["ambulancia"] = id_amb
                    acc["t_despacho"] = t
                    print(f"[{t}s] DESPACHO {acc['id']} ← {mejor_hosp.id} {unidad} | ETA {mejor_tiempo:.0f}s")

            elif acc["estado"] == "en_camino":
                if acc["ambulancia"] in traci.vehicle.getIDList():
                    dist = -1
                    try:
                        dist = traci.simulation.getDistanceRoad(
                            acc["arista"], acc["pos"], traci.vehicle.getRoadID(acc["ambulancia"]),
                            traci.vehicle.getLanePosition(acc["ambulancia"]), isDriving=True
                        )
                    except:
                        x_amb, y_amb = traci.vehicle.getPosition(acc["ambulancia"])
                        dist = math.hypot(acc["x"] - x_amb, acc["y"] - y_amb)
                    
                    if (dist != -1073741824 and dist <= 50) or (0 < dist <= 300 and traci.vehicle.getSpeed(acc["ambulancia"]) < 0.1):
                        acc["estado"] = "atendiendo"
                        acc["t_llegada"] = t
                        traci.vehicle.setSpeedMode(acc["ambulancia"], 0)
                        traci.vehicle.setSpeed(acc["ambulancia"], 0)
                        print(f"[{t}s] 🚑 LLEGADA {acc['id']} | respuesta {t - acc['t_despacho']}s")
                        
            elif acc["estado"] == "atendiendo":
                if t - acc["t_llegada"] >= 120:
                    for v in [acc["bus"], acc["moto"]]:
                        if v in traci.vehicle.getIDList():
                            traci.vehicle.remove(v, traci.constants.REMOVE_VAPORIZED)
                    try:
                        traci.polygon.remove(f"acc_{acc['t']}")
                    except: pass
                    
                    mejor_hosp_ret = None
                    mejor_tiempo_ret = float('inf')
                    for h in hospitales:
                        ruta = traci.simulation.findRoute(acc["arista"], h.arista, vType="ambulance", depart=-1, routingMode=1)
                        if ruta.edges and ruta.travelTime < mejor_tiempo_ret:
                            mejor_tiempo_ret = ruta.travelTime
                            mejor_hosp_ret = h
                    
                    if mejor_hosp_ret:
                        amb = acc["ambulancia"]
                        traci.vehicle.setSpeedMode(amb, 31)
                        traci.vehicle.setLaneChangeMode(amb, 1621)
                        traci.vehicle.setSpeed(amb, -1)
                        traci.vehicle.changeTarget(amb, mejor_hosp_ret.arista)
                        
                        acc["estado"] = "retorno"
                        acc["hospital_retorno"] = mejor_hosp_ret
                        print(f"[{t}s] RETORNO {acc['id']} → {mejor_hosp_ret.id}")

            elif acc["estado"] == "retorno":
                amb = acc["ambulancia"]
                if amb in traci.simulation.getArrivedIDList():
                    h_ret = acc["hospital_retorno"]
                    h_ret.retornos += 1
                    acc["hospital"].tiempo_ocupado += (t - acc["t_despacho"])
                    
                    id_unidad = f"U_{h_ret.id}_{t}" 
                    h_ret.cola.append(id_unidad)
                    acc["estado"] = "cerrado"
                    acc["t_fin"] = t
                    print(f"[{t}s] ✅ DISPONIBLE {id_unidad} en {h_ret.id} | misión {t - acc['t_despacho']}s")

        if t % 60 == 0:
            for h in hospitales:
                historial_stock.append([t, h.id, len(h.cola)])

    traci.close(False) 
    print("\nSimulación finalizada. Guardando resultados en CSV...")
    guardar_csv(accidentes, hospitales, historial_stock)
    print("Archivos guardados en la carpeta 'resultados_extension'")
    
    # Cerrar el archivo de log y restaurar stdout
    sys.stdout = sys.__stdout__
    log_file.close()

if __name__ == "__main__":
    main()