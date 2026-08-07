#!/bin/bash

# =============
# 1) Download data
# =============

# Input parameters
#year="2025"
#basefolder="/data/ahsoka/eocp/forestpulse/01_data/01_raw_data/DWD_calculate/"
#base_url="https://opendata.dwd.de/climate_environment/CDC/grids_germany/daily/soil_temperature_5cm/"
# call
# ./ext01_download_DWD_data.sh 2025 /data/ahsoka/eocp/forestpulse/01_data/01_raw_data/DWD_calculate/delete/ https://opendata.dwd.de/climate_environment/CDC/grids_germany/daily/soil_temperature_5cm/
year=$1
basefolder=$2
base_url=$3

# "static" variables
storefolder="$basefolder/$year"

# =============
# 1) Download data
# =============
mkdir -p "$storefolder"
echo "Lese Dateiliste..."
file_links=$(curl -s "$base_url" \
 	| grep -oP 'href="\K[^"]+\.tgz' \
 	| grep "$year")

count=$(echo "$file_links" | wc -l)
echo "Gefundene Dateien: $count"
echo "Lade herunter"
for file in $file_links; do
	wget -q -P "$storefolder" "$base_url$file"
done

echo "Download abgeschlossen"

# =============
# 2) Unzip data
# =============
echo "UnZIP data"
for file in "$storefolder"/*.tgz; do
	[ -e "$file" ] || continue
	tar -xzf "$file" -C "$storefolder"
	rm "$file"
done

echo "I'm done here, bye!"
sleep 1
