#!/bin/bash
echo "Iniciando extracción de todos los vehículos..."
for i in {0..11}; do
  veh_id=$((i + 1))
  file="v2v-80211p-student-application-${i}-0.pcap"
  
  if [ -f "$file" ]; then
    echo "Procesando $file -> veh${veh_id}..."
    tshark -r "$file" -Y "its" -T fields \
      -e frame.time_relative -e its.speedValue -e its.headingValue \
      -e its.latitude -e its.longitude -E separator=, > "datos_veh${veh_id}_completo.csv"
  fi
done
echo "¡Extracción completada!"
