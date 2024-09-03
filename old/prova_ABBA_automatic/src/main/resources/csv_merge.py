import pandas as pd
import sys
import os
import shutil

def main():

    #Script to merge the 3 csv created by the cell_macro.ijm
    
    dir = sys.argv[1] #dir thar contains the files to process
    path_to_save = sys.argv[2] #path of file to save final csv

    names_df = pd.read_csv(dir + "/names.csv")
    counts_df = pd.read_csv(dir + "/counts.csv")
    areas_df = pd.read_csv(dir + "/areas.csv")

    names = names_df["ROI Name"]
    counts = counts_df["Count"]
    areas = areas_df["Area"]

    merged_df = pd.concat([names, counts, areas], axis=1)

    #print(merged_df)

    merged_df.to_csv(path_to_save, index=False)

    #Delete temp folder
    try:
        shutil.rmtree(dir)
        print(f"Folder '{dir}' deleted successfully.")
    except OSError as e:
        print(f"Error: {dir} : {e.strerror}")

if __name__ == "__main__":
    main()