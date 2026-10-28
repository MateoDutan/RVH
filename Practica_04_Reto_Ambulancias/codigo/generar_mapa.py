import sumolib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

print("Generando mapa definitivo con accidentes...")
net = sumolib.net.readNet('cuenca_ciudad.net.xml')
fig, ax = plt.subplots(figsize=(14, 10))

# 1. Dibujar calles
for edge in net.getEdges():
    if edge.getID().startswith(":"): continue
    shape = edge.getShape()
    x = [p[0] for p in shape]
    y = [p[1] for p in shape]
    ax.plot(x, y, color='#888888', linewidth=0.6, zorder=1)

# 2. Dibujar hospitales
hospitales_coords = {
    "VCM": (-78.992923, -2.911098), "IESS_JCA": (-78.970118, -2.898698),
    "MILITAR": (-79.003968, -2.903146), "MUNI_PAT": (-78.982263, -2.866103),
    "MUNI_VALLE": (-78.961959, -2.919522), "MONTE_SINAI": (-79.007373, -2.908606),
    "DEL_RIO": (-78.960796, -2.892939)
}
min_x, min_y = net.getBBoxXY()[0]
max_x, max_y = net.getBBoxXY()[1]
lon_min, lon_max = -79.030, -78.950
lat_min, lat_max = -2.930, -2.860

def geo_to_xy(lon, lat):
    x = min_x + (lon - lon_min) / (lon_max - lon_min) * (max_x - min_x)
    y = min_y + (lat - lat_min) / (lat_max - lat_min) * (max_y - min_y)
    return x, y

for h, (lon, lat) in hospitales_coords.items():
    x, y = geo_to_xy(lon, lat)
    color = '#e31a1c' if h in ["VCM", "IESS_JCA", "MILITAR", "MUNI_PAT", "MUNI_VALLE"] else '#1f78b4'
    ax.scatter(x, y, color=color, s=200, zorder=4, edgecolors='black', alpha=0.9)
    ax.text(x, y+150, h, fontsize=9, fontweight='bold', zorder=5, ha='center')

# 3. Dibujar accidentes (CORREGIDO)
try:
    tree = ET.parse('collisions.xml')
    root = tree.getroot()
    accidentes_dibujados = 0
    for col in root.findall('collision'):
        # CORRECCIÓN: Los atributos son colliderType y victimType, y los valores son "bus" y "moto"
        tipo1 = col.get('colliderType')
        tipo2 = col.get('victimType')
        tipos = {tipo1, tipo2}
        
        if "bus" in tipos and "moto" in tipos:
            lane_id = col.get('lane')
            
            if lane_id.startswith(':'):
                # Es un carril interno (cruce). Extraemos el ID del nodo.
                parts = lane_id.split('_')
                node_id = parts[0][1:] 
                try:
                    node = net.getNode(node_id)
                    x, y = node.getCoord()
                    ax.scatter(x, y, color='yellow', marker='X', s=200, zorder=6, edgecolors='black')
                    accidentes_dibujados += 1
                except:
                    pass
            else:
                # Es un carril normal (arista)
                edge_id = lane_id.rsplit('_', 1)[0]
                edge = net.getEdge(edge_id)
                if edge:
                    shape = edge.getShape()
                    mid = len(shape) // 2
                    x, y = shape[mid]
                    ax.scatter(x, y, color='yellow', marker='X', s=200, zorder=6, edgecolors='black')
                    accidentes_dibujados += 1
                    
    print(f"Se dibujaron {accidentes_dibujados} accidentes en el mapa.")
except Exception as e:
    print("No se pudo leer collisions.xml:", e)

# Ajustar límites y limpiar
ax.set_xlim(min_x - 500, max_x + 500)
ax.set_ylim(min_y - 500, max_y + 500)
ax.set_title("Red de Cuenca, Hospitales y Accidentes (X Amarillas)")
ax.set_aspect('equal')
ax.axis('off')

plt.tight_layout()
plt.savefig("resultados/grafico_d_mapa.png", dpi=250, bbox_inches='tight')
print("Mapa definitivo generado en resultados/grafico_d_mapa.png")