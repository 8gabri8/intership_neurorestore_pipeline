import pandas as pd
import os

import find_leaves_atlas

"""
This Script takes as inputs 
    - all the csv that contain the number of dots for each ROI --> 1csv for each slice
and returns a single csv 

Attention:
    - the non-leaves ROI are removed
    - the metric calculates is: sum(dots all slices) / sum(area all slices)

"""

# INPUTS
path_atlas = "/home/gabri/Desktop/test_abba/prova_ABBA_automatic/src/main/resources/Adult Mouse Brain - Allen Brain Atlas V3p1-Ontology.json"
dir_xls = "/run/user/1000/gvfs/smb-share:server=upcourtinenas,share=cervical/CERVICAL_ID/Analysis/Connectome Analysis/IF/651/_Measurements"

# Run the script find_leaves_atlas.csv to create a file with only leaves ROIs
path_leaves_ROI = find_leaves_atlas.f(path_atlas)

# Read the leaves ROIs df
leaves_ROI_df = pd.read_csv(path_leaves_ROI)

# Create df that will contain the results
#NB only leave ROIs are inside
df = pd.DataFrame({
    "ROI" : leaves_ROI_df["Acronym"],
    "Synapses" : [0] * len(leaves_ROI_df["Acronym"]),
    "Area" : [0] * len(leaves_ROI_df["Acronym"])
}
)
list_roi_leaves = df['ROI'].astype(str).tolist()

# Loop through all files in the directory
for filename in os.listdir(dir_xls):

    # Take only .xsl file
    if not filename.endswith('.xls'):
        print(f"Skipping {filename} as it is not an .xls file")
        continue

    file_path = os.path.join(dir_xls, filename)
    df_slice = pd.read_csv(file_path, sep="\t") #Attention separator

    for index, row in df_slice.iterrows():

        roi = row["Classification"]
        num_synapses = row["Num CY3"]
        area = row["Area µm^2"]

        if roi in list_roi_leaves: #if ROI is a leaf-ROI
            df.loc[df["ROI"] == roi, "Synapses"] += num_synapses
            df.loc[df["ROI"] == roi, "Area"] += area

csv_file = dir_xls + '/whole_brain.csv'
print("Saving csv as: " + csv_file)
df.to_csv(csv_file, index=False)
