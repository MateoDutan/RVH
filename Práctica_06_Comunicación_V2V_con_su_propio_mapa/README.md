# Práctica 06 - V2V/CAM - Sombra Digital y Análisis ETSI en Cuenca (SUMO + ns-3)

Solución al taller de la Práctica 06 de la asignatura **Redes Vehiculares y Heterogéneas** de la Universidad de Cuenca.

## Descripción
Reconstrucción de tráfico V2V a partir de capturas de red (`.pcap`). El proyecto simula la pila ETSI ITS-G5 (mensajes CAM), extrae datos cinemáticos usando Wireshark/tshark, y genera una Sombra Digital (Digital Shadow) en SUMO. Para garantizar la fluidez del movimiento, se implementa interpolación lineal en Python a través de la interfaz TraCI, validando empíricamente las reglas de generación dinámica del CAM (1 a 10 Hz).

## Cumplimiento de Entregables (Sección 43 del PDF)
De acuerdo a lo solicitado en la diapositiva 43 del manual del taller, los entregables se encuentran organizados de la siguiente manera:

**1. Su mapa (Red y configuración + Captura del visor)**
*   Archivos de SUMO: En la carpeta **`mapa/`** (`mi_mapa.net.xml`, `mi_mapa.rou.xml` y `mi_mapa.sumocfg`).
*   Captura del visor: En **`evidencias/SombraDigital/`** (se incluyen 6 capturas del vehículo en el mapa, desde `01_inicio.png` hasta `06_final.png`).

**2. La corrida (Estadísticas y comparación)**
*   Log de estadísticas: En **`resultados/corrida_mi_mapa.txt`** (contiene el bloque de PRR, latencias y contadores TX/RX).
*   Comparación: El análisis comparativo frente al mapa por defecto (PRR del 29% en nuestro mapa vs. ~90% en el anillo por defecto) se detalla en el informe IEEE adjunto.

**3. El reto (Wireshark)**
*   Captura con un CAM expandido (HF visible): En **`evidencias/Wireshark/`** (archivos `Contenido_CAM.png` y `Diseccion_Capas.png`).
*   Intervalos mínimo y máximo medidos: En **`evidencias/Wireshark/`** (archivos `Tiempo_Cadencia_0.3.png` y `Tiempo_Cadencia_1.png`) y demostrado numéricamente en la telemetría **`resultados/log_sombra_digital.txt`** (mostrando los picos de 100 ms y 1000 ms).

## Estructura del Repositorio
*   **`datos/`**: Archivos `.pcap` originales (en `pcap/`) y datos extraídos en `.csv` (en `csv/`).
*   **`mapa/`**: Red de SUMO (`.net.xml`), rutas (`.rou.xml`) y configuración.
*   **`scripts/`**: Scripts de Python y Bash para automatización.
*   **`resultados/`**: Logs de consola de ns-3 y telemetría de la Sombra Digital.
*   **`evidencias/`**: Gráficas de análisis (`Graficas/`), capturas de Wireshark (`Wireshark/`) y fotos del simulador SUMO (`SombraDigital/`).

## Ejecución
*(Todos los comandos deben ejecutarse desde la raíz del proyecto).*

1. Extraer datos de los `.pcap` a `.csv`: `bash scripts/extraer_todos.sh`
2. Generar todas las gráficas cinemáticas: `python3 scripts/graficar_todos.py`
3. Ejecutar la Sombra Digital fluida: `python3 scripts/sombra_digital.py` *(El script pedirá el ID del vehículo, ej. `veh6`)*

## Autor
Mateo Fernando Dután Rivas
