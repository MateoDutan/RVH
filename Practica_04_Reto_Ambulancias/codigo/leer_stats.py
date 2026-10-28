import xml.etree.ElementTree as ET

tree = ET.parse('stats.xml')
root = tree.getroot()

vehicles = root.find('vehicles')
if vehicles is not None:
    print(f"Insertados: {vehicles.get('loaded')}")
    print(f"Running al final: {vehicles.get('running')}")

# Buscar teleports
teleports = root.find('.//teleports')
if teleports is not None:
    print(f"Teleports: {teleports.get('total')}")

# Tiempo de pared
print(f"Tiempo de pared (s): {root.get('duration')}")
