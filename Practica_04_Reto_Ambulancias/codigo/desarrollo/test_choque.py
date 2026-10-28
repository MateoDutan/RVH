import os, sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Falta SUMO_HOME")

import traci, random

traci.start(["sumo-gui", "-c", "reto.sumocfg", "--delay", "100", "--start"])

# Avanzar hasta que haya buses
for _ in range(200):
    traci.simulationStep()

# Buscar un bus
buses = [v for v in traci.vehicle.getIDList() if traci.vehicle.getTypeID(v) == "bus"]
if not buses:
    print("No hay buses. Saliendo.")
    traci.close()
    sys.exit()

bus = random.choice(buses)
print(f"Bus elegido: {bus} en carril {traci.vehicle.getLaneID(bus)}")
print(f"Posición bus: {traci.vehicle.getLanePosition(bus)} m")
print(f"Velocidad bus: {traci.vehicle.getSpeed(bus)} m/s")

# Insertar moto 20m detrás
pos_moto = max(0, traci.vehicle.getLanePosition(bus) - 20)
ruta = traci.vehicle.getRoute(bus)[traci.vehicle.getRouteIndex(bus):]
id_moto = "moto_test"

traci.route.add(id_moto, ruta)
traci.vehicle.add(
    id_moto, id_moto, typeID="moto",
    depart="now", departPos=str(pos_moto), departSpeed=0,
    departLane=str(traci.vehicle.getLaneIndex(bus))
)

# PASO 1: La moto aparece
traci.simulationStep()
print(f"\n--- Paso 1 ---")
if id_moto in traci.vehicle.getIDList():
    print(f"Moto existe. Velocidad actual: {traci.vehicle.getSpeed(id_moto):.2f}")
    print(f"Moto carril: {traci.vehicle.getLaneID(id_moto)}")
else:
    print("La moto NO existe.")

# PASO 2: Aplicar speedMode 0 y setSpeed
traci.vehicle.setSpeedMode(id_moto, 0)
traci.vehicle.setLaneChangeMode(id_moto, 0)
traci.vehicle.setSpeed(id_moto, 30)
print(f"\n--- Paso 2 (después de setSpeed) ---")
print(f"Velocidad moto: {traci.vehicle.getSpeed(id_moto):.2f}")

# PASO 3: Avanzar y ver si se mueve
traci.simulationStep()
print(f"\n--- Paso 3 (después de avanzar) ---")
print(f"Velocidad moto: {traci.vehicle.getSpeed(id_moto):.2f}")
print(f"Posición moto: {traci.vehicle.getLanePosition(id_moto):.2f}")
print(f"Posición bus: {traci.vehicle.getLanePosition(bus):.2f}")

# Avanzar 5 segundos más
for i in range(5):
    traci.simulationStep()
    print(f"Paso {i+4}: Moto vel={traci.vehicle.getSpeed(id_moto):.1f}, pos={traci.vehicle.getLanePosition(id_moto):.1f}")

traci.close(True)
