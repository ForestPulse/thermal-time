#!/bin/bash


# parallel call:
#ls /data/ahsoka/eocp/forestpulse/01_data/01_raw_data/DWD_calculate/delete/2025/*.tif | parallel -j 32 ./2_warp_file_to_tiles.sh {} /data/ahsoka/eocp/forestpulse/01_data/01_raw_data/DWD_calculate/delete/FORCE/ /data/ahsoka/eocp/forestpulse/02_scripts/DWD/DC_tilelist.txt

# === Konstanten ===
#Y_63=2654919.608
Y_63=2654919.6079648043960333
#X_52=4016026.363
X_52=4016026.3630416505038738


# === Eingabe-Datei prüfen ===
if [ $# -lt 1 ]; then
  echo "Usage: $0 /path/to/thermal_file.tif"
  exit 1
fi

INPUT="$1"
OUTDIR="$2"
TILELIST="$3"

#OUTDIR="/data/ahsoka/eocp/forestpulse/01_data/01_raw_data/DWD_dc/"
#TILELIST="/data/ahsoka/eocp/forestpulse/02_scripts/DWD/DC_tilelist.txt"

BASENAME=$(basename "$INPUT")

# === Tiles sequenziell abarbeiten ===
while read -r ordner; do
  # Ordnername aufteilen
  x_part=${ordner%%_*}
  x=${x_part#X00}
  y_part=${ordner##*_}
  y=${y_part#Y00}
  # Vorzeichen korrekt, um führende Nullen zu vermeiden
  x=$((10#$x))
  y=$((10#$y))

  # Bounding Box berechnen
  YBOT=$(echo "$Y_63 + (63 - $y) * 30000" | bc -l)
  YTOP=$(echo "$YBOT + 30000" | bc -l)
  XLEFT=$(echo "$X_52 + ($x - 52) * 30000" | bc -l)
  XRIGHT=$(echo "$XLEFT + 30000" | bc -l)

  # Output-Pfade
  TILE_FOLDER="$OUTDIR/$ordner"
  mkdir -p "$TILE_FOLDER"
  TEMP="$TILE_FOLDER/temp_$BASENAME"
  OUTPUT="$TILE_FOLDER/$BASENAME"

  # GDAL Warping
  gdalwarp -q -t_srs EPSG:3035 -tr 10 10 -ot Int16 -r near -overwrite \
    -of GTiff -wo "NUM_THREADS=1" -dstnodata -9999 \
    -co BIGTIFF=YES -co COMPRESS=LZW -co TILED=YES -co BLOCKXSIZE=256 -co BLOCKYSIZE=256 \
    -te "$XLEFT" "$YBOT" "$XRIGHT" "$YTOP" "$INPUT" "$OUTPUT"
  # Need to chage from ZSTD to LZW because of the splienecoefs program, 
  # which cannot makes troubel when mixing LZW(SENTINEL2) and ZSTD compressed files.

done < "$TILELIST"

echo "Processing $BASENAME"
