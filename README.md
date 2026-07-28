# Calculate Thermal time for Germany using DWD data

This repository contains all scripts we used for the workflow to calculate thermal time for Germany. 

## Steps

1st: ext01_downdload_DWD_data.sh
This bash scripts downloads the original ASCII DWD thermal data for germany for one target year.

2nd: 1_calculate_thermal__time.py
This script does the main part. It is deived in three sub processes:
- projecting the original ASCII file to a 1*1 km .tif raster file
- "Buffering" the extent, to avoid NoData Cells in border regions and islands in Nord- and Ostsee
- calculating the Growing Degree Days and normalize them over the target year

3rd: 2_warp_file_to_tiles.sh
Here the 1*1km resolved thermal data are warped to the FORCE 10*10m Sentinel-2 tiling system

After this, the data are ready to be used for the thermal spline coefficent calculation.




