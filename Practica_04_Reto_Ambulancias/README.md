# Reto Accidentes Bus-Moto y Ambulancias en Cuenca (SUMO + TraCI)

Solución al Reto de la Práctica 04 de la asignatura **Redes Vehiculares y Heterogéneas** de la Universidad de Cuenca.

## Descripción
Gemelo digital de emergencias sobre la red vial de Cuenca. Simula 3 horas de tráfico, 16 accidentes bus-moto, despacho de ambulancias con disponibilidad aleatoria y retorno dinámico. Incluye extensión con prioridad semafórica.

## Estructura del Repositorio
*   **`codigo/`**: Scripts principales (`reto_final.py`, `reto_extension.py`, `analisis.py`, `generar_mapa.py`, `leer_stats.py`). Versiones antiguas en `desarrollo/`.
*   **`datos/`**: Red (`cuenca_ciudad.net.xml`), tipos de vehículos (`vtypes.add.xml`), rutas, configuración (`reto.sumocfg`).
*   **`resultados/`**: Gráficos comparativos (base y extensión). Contiene `resultados_base/` y `resultados_extension/` con los archivos CSV y los logs de eventos. También incluye `sumo_output/` con los XML generados por SUMO.
*   **`evidencias/`**: Capturas de pantalla de la simulación en SUMO-GUI.
*   **`informe/`**: Documento final en PDF y código fuente LaTeX.

## Ejecución
1. Simulación base: `python3 codigo/reto_final.py`
2. Simulación con extensión: `python3 codigo/reto_extension.py`
3. Análisis y gráficos: `python3 codigo/analisis.py`

## Autor
Mateo Fernando Dután Rivas
