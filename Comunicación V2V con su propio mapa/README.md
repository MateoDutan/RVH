# Reto V2V/CAM - Sombra Digital y Análisis ETSI en Cuenca (SUMO + ns-3)

Solución al taller de la Práctica 05 de la asignatura **Redes Vehiculares y Heterogéneas** de la Universidad de Cuenca.

## Descripción
Reconstrucción de tráfico V2V a partir de capturas de red (`.pcap`). El proyecto simula la pila ETSI ITS-G5 (mensajes CAM), extrae datos cinemáticos usando Wireshark/tshark, y genera una Sombra Digital (Digital Shadow) en SUMO. Para garantizar la fluidez del movimiento, se implementa interpolación lineal en Python a través de la interfaz TraCI, validando empíricamente las reglas de generación dinámica del CAM (1 a 10 Hz).

## Cumplimiento de Entregables (Sección 43 del PDF)
De acuerdo a lo solicitado en el manual del taller, este repositorio contiene:
*   **Scripts principales:** 
    *   `scripts/extraer_todos.sh` (Extracción de datos con tshark).
    *   `scripts/graficar_todos.py` (Análisis cinemático y generación de paneles).
    *   `scripts/sombra_digital.py` (Reconstrucción visual fluida con TraCI).
*   **Red y configuración:** Carpeta `mapa/` con `mi_mapa.net.xml`, `mi_mapa.rou.xml`, `mi_mapa.sumocfg` y `vista.xml`.
*   **Archivos CSV y logs:** En `datos/csv/` (datos de los 12 vehículos) y `resultados/` (`corrida_mi_mapa.txt` y `log_sombra_digital.txt`).
*   **Gráficos (Evidencias):** En `evidencias/Graficas/` (paneles de 6 gráficas por vehículo) y `evidencias/SombraDigital/` (6 capturas del recorrido fluido).
*   **Reto Wireshark:** En `evidencias/Wireshark/` (disección del paquete CAM y medición de cadencia).
*   **Informe:** Documento en formato IEEE (doble columna) generado en Overleaf.

## Estructura del Repositorio
*   **`datos/`**: Archivos `.pcap` originales (en `pcap/`) y datos extraídos en `.csv` (en `csv/`).
*   **`mapa/`**: Red de SUMO (`.net.xml`), rutas (`.rou.xml`) y configuración.
*   **`scripts/`**: Scripts de Python y Bash para automatización.
*   **`resultados/`**: Logs de consola de ns-3 y telemetría de la Sombra Digital.
*   **`evidencias/`**: Gráficas de análisis, capturas de Wireshark y fotos del simulador SUMO.

## Ejecución
*(Todos los comandos deben ejecutarse desde la raíz del proyecto).*

1. Extraer datos de los `.pcap` a `.csv`: `bash scripts/extraer_todos.sh`
2. Generar todas las gráficas cinemáticas: `python3 scripts/graficar_todos.py`
3. Ejecutar la Sombra Digital fluida: `python3 scripts/sombra_digital.py` *(El script pedirá el ID del vehículo, ej. `veh6`)*

## Autor
Mateo Fernando Dután Rivas