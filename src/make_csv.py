import csv
import argparse
import os
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--DWD_dc_folder", 
                    help="path to the folder, where the DWD .tif files are stored", 
                    default= f'/data/ahsoka/eocp/forestpulse/01_data/01_raw_data/DWD_dc')
parser.add_argument("--year", 
                    help="The yeare for which the DWD .tif files should be processed", 
                    default= '2021')
parser.add_argument("--tile", 
                    help="The tile to be normalize", 
                    default= 'X0055_Y0053')
parser.add_argument("--dc_folder", 
                    help="path to the folder, where the FORCE and DWD .vrt files should be stored", 
                    default= f'/data/ahsoka/dc/deu/ard')
parser.add_argument("--output_csv_folder",
                    help="path to the folder, where the output csv files should be stored",
                    default= f'/data/ahsoka/eocp/forestpulse/02_scripts/dwd-git/src/Tile_csv')
args = parser.parse_args()

def make_csv():
    dateien_BOA = list(Path(os.path.join(args.dc_folder, args.tile)).glob(f"{int(args.year)-2}*SEN2*BOA.tif"))
    dateien_BOA = dateien_BOA + list(Path(os.path.join(args.dc_folder, args.tile)).glob(f"{int(args.year)-1}*SEN2*BOA.tif"))
    dateien_BOA = dateien_BOA + list(Path(os.path.join(args.dc_folder, args.tile)).glob(f"{int(args.year)}*SEN2*BOA.tif"))

    dateien_QAI = list(Path(os.path.join(args.dc_folder, args.tile)).glob(f"{int(args.year)-2}*SEN2*QAI.tif"))
    dateien_QAI = dateien_QAI +list(Path(os.path.join(args.dc_folder, args.tile)).glob(f"{int(args.year)-1}*SEN2*QAI.tif"))
    dateien_QAI = dateien_QAI + list(Path(os.path.join(args.dc_folder, args.tile)).glob(f"{int(args.year)}*SEN2*QAI.tif"))

    dateien_DWD = list(Path(os.path.join(args.DWD_dc_folder, args.tile)).glob(f"{int(args.year)-2}*DWD*.tif"))
    dateien_DWD = dateien_DWD + list(Path(os.path.join(args.DWD_dc_folder, args.tile)).glob(f"{int(args.year)-1}*DWD*.tif"))
    dateien_DWD = dateien_DWD + list(Path(os.path.join(args.DWD_dc_folder, args.tile)).glob(f"{int(args.year)}*DWD*.tif"))

    list_BOA = {os.path.basename(path)[0:8]: path for path in dateien_BOA}
    list_QAI = {os.path.basename(path)[0:8]: path for path in dateien_QAI}
    list_DWD = {os.path.basename(path)[0:8]: path for path in dateien_DWD}

    output_csv = os.path.join(args.output_csv_folder, f"{args.tile}_{args.year}.csv")

    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for date in sorted(list_BOA):
            path_BOA = list_BOA[date]
            path_QAI = list_QAI.get(date, "")
            path_DWD = list_DWD.get(date, "")
            if path_QAI == "" or path_DWD == "":
                print(f"Warning: Missing file(s) for date {date}")
                continue
            else:
                writer.writerow([path_BOA, path_QAI, path_DWD])

if __name__ == "__main__":
    make_csv()
