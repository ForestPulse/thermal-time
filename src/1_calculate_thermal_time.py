import rasterio
from rasterio.transform import from_origin
from rasterio.fill import fillnodata
import rasterio
import numpy as np
import os
from datetime import datetime
import argparse
parser = argparse.ArgumentParser()

parser.add_argument("--o", 
                    help="directory where the output file should be stored", 
                    default= f'/data/ahsoka/eocp/forestpulse/01_data/01_raw_data/DWD_calculate/')
parser.add_argument("--year",
                    help="The year for which the DWD .asc files should be processed",
                    default= '2015')
args = parser.parse_args()

def project_asc_file(output_folder):
    #--------------------------------------
    #- 1) project .asc file to geotiff ----
    #--------------------------------------
    os.makedirs(output_folder, exist_ok=True)

    # Metadaten des Rasters
    ncols = 654
    nrows = 866
    xllcorner = 3280415
    yllcorner = 5237501
    cellsize = 1000
    epsg_code = 31467  # DHDN / 3-degree Gauss-Krüger zone 3
    # Transformation erstellen (oben links als Referenz)
    transform = from_origin(xllcorner, yllcorner + nrows * cellsize, cellsize, cellsize)

    for filename in os.listdir(output_folder):
        if os.path.isfile(os.path.join(output_folder, filename)) & filename.endswith('.asc'):
            tif_filename = filename[:-4]+'.tif'

            if os.path.isfile(os.path.join(output_folder, tif_filename)):
                continue

            with rasterio.open(os.path.join(output_folder, filename)) as src:
                data = src.read(1)
                # Geotiff speichern
                with rasterio.open(
                    os.path.join(output_folder, tif_filename), "w", driver="GTiff",
                    height=nrows, width=ncols, count=1,
                    dtype=data.dtype, crs=f"EPSG:{epsg_code}",
                    transform=transform, nodata = -9999
                ) as dst:
                    dst.write(data, 1)
                    meta = dst.meta.copy()

            os.remove(os.path.join(output_folder, filename))
        
def interpolate_NoData_values(folder):
    print("Interpolate values")
    # Alle TIFF-Dateien sortieren (nach Dateinamen)
    tiff_files = sorted([f for f in os.listdir(folder) if (f.endswith(".tif") & f.startswith("grids"))])
    # Sicherstellen, dass Dateien vorhanden sind
    if not tiff_files:
        raise FileNotFoundError("Keine TIFF-Dateien im angegebenen Ordner gefunden.")
    # Erste Datei öffnen, um Metadaten zu erhalten
    with rasterio.open(os.path.join(folder, tiff_files[0])) as src:
        meta = src.meta.copy()

    # Metadaten anpassen für das Ausgabebild
    meta.update(
        count=1,  # Anzahl der Layer entspricht der Anzahl der TIFFs
        dtype='int16',          # 16-Bit Integer
        compress='lzw'          # LZW-Komprimierung
    )
    for idx, file_name in enumerate(tiff_files, start=1):
        with rasterio.open(os.path.join(folder, file_name)) as src:
            data = src.read(1)
            profile = src.profile
            nodata = src.nodata
        # Maske der gültigen Werte
        mask = data != nodata
        filled = fillnodata(data,mask=mask,max_search_distance=5,smoothing_iterations=0)
        with rasterio.open(os.path.join(folder,file_name[-12:-4]+'_interpolated.tif'), 'w', **meta) as dst:
            dst.write(filled.astype(np.int16), 1)
        os.remove(os.path.join(folder, file_name))

def calculate_thermal_time(folder):
    print("Calculate Thermal Time")
    # Alle TIFF-Dateien sortieren (nach Dateinamen)
    #tiff_files = sorted([f for f in os.listdir(folder) if (f.endswith(".tif") & f.startswith("grids"))])
    tiff_files = sorted([f for f in os.listdir(folder) if (f.endswith("_interpolated.tif"))])
    # Sicherstellen, dass Dateien vorhanden sind
    if not tiff_files:
        raise FileNotFoundError("Keine TIFF-Dateien im angegebenen Ordner gefunden.")

    # Erste Datei öffnen, um Metadaten zu erhalten
    with rasterio.open(os.path.join(folder, tiff_files[0])) as src:
        meta = src.meta.copy()

    # Metadaten anpassen für das Ausgabebild
    meta.update(
        count=1,  # Anzahl der Layer entspricht der Anzahl der TIFFs
        dtype='int16',          # 16-Bit Integer
        compress='lzw'          # LZW-Komprimierung
    )
    # ================
    # = Thermal Time =
    # ================
    # Initialisiere den Summen-Layer
    cumulative_sum = np.zeros((meta['height'], meta['width']), dtype=np.float32)

    for idx, file_name in enumerate(tiff_files, start=1): 
        # Aktuelles Raster einlesen
        with rasterio.open(os.path.join(folder, file_name)) as src:
            data = src.read(1).astype(np.float32)
        no_data_mask = data == -9999
        # Werte auf den Bereich [0, 300] begrenzen
        data = np.clip(data, 0, 300)
        data = data/10
        # Summe aktualisieren
        cumulative_sum += data
        cumulative_sum[no_data_mask] = -9999
        
        # Zwischenspeichern der kumulativen Summe als TIFF
        #with rasterio.open(os.path.join(folder,file_name[-12:-4]+'_temp.tif'), 'w', **meta) as dst:
        with rasterio.open(os.path.join(folder,file_name[0:8]+'_temp.tif'), 'w', **meta) as dst:
            dst.write(cumulative_sum.astype(np.int16), 1)
        os.remove(os.path.join(folder, file_name))

    print('Normalize Thermal Time')
    # ================
    # Normalize Thermal Time
    # ================
    therm_time_files = sorted([f for f in os.listdir(folder) if f.endswith('_temp.tif')])
    for idx, file_name in enumerate(therm_time_files, start=1):
        with rasterio.open(os.path.join(folder, file_name)) as src:
            data = src.read(1).astype(np.float32)
        no_data_mask = data == -9999
        data = (data/cumulative_sum) * 365
        data[no_data_mask] = -9999

        data = np.ndarray.round(data, decimals=0, out=None)

        output_file = os.path.join(folder, file_name[:-8]+'DWD.tif')
        with rasterio.open(output_file, 'w', **meta) as dst:
            dst.write(data.astype(np.int16), 1)
        os.remove(os.path.join(folder, file_name))

if __name__ == '__main__':
    folder = os.path.join(args.o, args.year)
    os.makedirs(folder, exist_ok=True)
    project_asc_file(folder)
    interpolate_NoData_values(folder)
    calculate_thermal_time(folder)