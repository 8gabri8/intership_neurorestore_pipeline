import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import sys


"""
# Outlier Management Script

This script automates the detection of potential outliers in a dataset containing brain region data, and then enables the user to manually validate these outliers before applying changes to the dataset.

## Workflow:
1. **Identify Potential Outliers**:
    - The script calculates z-scores based on the "Cell Density" column for each brain region.
    - Regions with an absolute z-score greater than a user-defined threshold (`thr_z_score`) are flagged as putative outliers.
    - The script creates a CSV file named `all_putative_outliers.csv` with these flagged regions.
    
2. **Manual Verification**:
    - The user manually reviews the `all_putative_outliers.csv` file and marks real outliers by setting the "IsOutlier" column to 1 (leave it as 0 otherwise).
    - Save this reviewed file as `all_putative_outliers_checked.csv`.

3. **Outlier Management**:
    - The script reads the manually checked file (`all_putative_outliers_checked.csv`).
    - Based on the chosen strategy, the script will remove the verified outliers:
      - Removes rows flagged as outliers from the main CSV (`all_brains.csv`).
      - Removes corresponding rows from individual brain files located in `_measurments/whole_brain.csv`.

      
**ATTENTION**: 
If you really want to change the original dataframes, uncommenent the lines in the final part of the script where the df are ovewritten.
"""

##############################################
### MANDATORY INPUTS #########################
##############################################

# path big csv
path_csv = "/Volumes/CERVICAL/CERVICAL_ID/Connectome_analysis/Final_dataset/Results/all_brains.csv"
# path base folder
base_folder = "/Volumes/CERVICAL/CERVICAL_ID/Connectome_analysis/Final_dataset"
#thr_z_score over which a ROI is considered an outlier
thr_z_score = 10

### Choose the stratefy to manage outliers
# Strategy I° : put 0
# Strategy II° : put NaN
# Strategy III° : remove row

strategy = 3

df_original = pd.read_csv(path_csv)
df = df_original.copy()

# ATTENTION: just for now slect only real data
df = df[df["TimePoint"] == "Uninjured"]
# ATTENTION: just for now slect only leaf
df = df[df["IsLeaf"] == True]

##############################################
### USEFUL FUNCTIONS #########################
##############################################

def find_dir(base_dir, name_dir_to_search):
    """
    Searches for a subfolder with a specific name within the given base directory.

    Parameters:
    - base_dir: The path of the base directory to search within (string).
    - name_dir_to_search: The name of the subfolder to search for (string).

    Returns:
    - The full path of the subfolder if found, or None if not found.
    """
    # Ensure the base directory exists
    if not os.path.isdir(base_dir):
        raise ValueError(f"The base directory '{base_dir}' does not exist or is not a directory.")
    
    # Walk through the directory tree
    for root, dirs, files in os.walk(base_dir):
        if name_dir_to_search in dirs:
            # Return the full path to the subfolder
            return os.path.join(root, name_dir_to_search)
    
    # Return None if the subfolder was not found
    return None


##############################################
### SEARCH OUTLIERS ##########################
##############################################

# df with all the putative outliers ROIs of differt brains
df_all_out = pd.DataFrame()

brain_IDs = df["Brain ID"].unique()

for ID in brain_IDs:

    print(f"Analyzing brain {ID}")

    mouse_dir = find_dir(base_folder, str(ID))

    if mouse_dir ==  None: 
        print(f"\tATTENTION: No folder found for sample {ID}")
        continue

    ##########################
    ### DENSITY VALUES PER BRAIN_ID

    ### Select data of isngle mouse
    df_mouse = df[df["Brain ID"] == ID].copy()

    ### Calculate z-score
    mean = np.mean(df_mouse["Cell Density"])
    std = np.std(df_mouse["Cell Density"])
    df_mouse["z-score"] = ( df_mouse["Cell Density"] - mean ) / std
    out = df_mouse[np.abs(df_mouse["z-score"]) > thr_z_score][["ROI", "Brain ID", "z-score"]]
    out = out.sort_values(by="z-score")

    ### Print Outliers based on z-score
    print(f"""Outliers based on |z-score| > {thr_z_score} (tot={len(out)}):\n{out.to_string()}""")

    ### Save out csv
    out.to_csv(os.path.join(mouse_dir, "Results", "putative_outliers_based_on_zscore.csv"), index = False)
    
    ### Scatter Plot Synapses Vs Area --> With Names
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = sns.scatterplot(
        x='Area', y='Synapses', data=df_mouse, hue='Cell Density', palette='viridis', size='Cell Density', sizes=(50, 200)
    )
    ax.set_title('Synapses vs Area')
    ax.set_xlabel('Area')
    ax.set_ylabel('Synapses')
    ax.grid(True)
    ax.set_xscale('log')
    ax.set_yscale('log')

    # Label each point with 'ROI-Brain ID'
    for i, row in df_mouse.iterrows():
        label = f"{row['ROI']}-{row['Brain ID']}"  # Construct the label text
        ax.text(
            row['Area'],  # X coordinate
            row['Synapses'],  # Y coordinate
            label,  # Text label
            fontsize=9,  # Font size of the label
            ha='right',  # Horizontal alignment
            va='bottom',  # Vertical alignment
            color='black'  # Text color
        )

    # Show the plot
    #plt.show()

    # Add single mice to all out
    df_all_out = pd.concat([df_all_out, out], ignore_index=True)

    # Save plot
    fig.savefig(os.path.join(mouse_dir, "Results", "scatterplot_area_synapses_density_with_names.pdf"))

    print("\n")

# Add column
df_all_out["IsOutlier"] = [1] * len(df_all_out) # put a column to say if a region is really an otulier
# save df all out
df_all_out.to_csv(os.path.join(base_folder, "Results", "all_putative_outliers.csv"), index=False)


##############################################
### WAIT FOR THE USER TO MANUALLY CHECK ######

user_input = input("""\n\nPlease check the file all_putative_outliers.csv and create a copy of it. In the column \"isOutlier\" put 1 if it is a real ourlier after manually checking it. \nWhen you have done, please press a key: """)

##############################################

##############################################
### MANAGE OUTLIERS ##########################
##############################################

# read manully check
try:
    df = pd.read_csv(os.path.join(base_folder, "Results", "all_putative_outliers_checked.csv"))
except FileNotFoundError:
    print("Manually revised CSV not yet created")
    sys.exit(0)

if strategy == 1:
    print("Not completely Implemented.")
    # for i, row in df.iterrows():
    #     if row["IsOutlier"] == 0: #if it not a real outlier after manually checkin do not do notheinf
    #         continue
    #     roi = row["ROI"]
    #     id = row["Brain ID"]
    #     df_original.loc[(df_original["Brain ID"] == id) & (df_original["ROI"] == roi), ["Synapses"]] = 0
    #     df_original.loc[(df_original["Brain ID"] == id) & (df_original["ROI"] == roi), ["Cell Density"]] = 0
    
elif strategy == 2:
    print("Not completely Implemented.")
    # for i, row in df.iterrows():
    #     if row["IsOutlier"] == 0: #if it not a real outlier after manually checkin do not do notheinf
    #         continue
    #     roi = row["ROI"]
    #     id = row["Brain ID"]
    #     df_original.loc[(df_original["Brain ID"] == id) & (df_original["ROI"] == roi), ["Synapses"]] = None
    #     df_original.loc[(df_original["Brain ID"] == id) & (df_original["ROI"] == roi), ["Cell Density"]] = None

elif strategy == 3:

    ##### REMOVE FROM ALL_BRAINS.CSV
    for i, row in df.iterrows():
        if row["IsOutlier"] == 0: #if it not a real outlier after manually checkin do not do notheinf
            continue
        roi = row["ROI"]
        id = row["Brain ID"]
        df_original = df_original.drop(df_original[(df_original["Brain ID"] == id) & (df_original["ROI"] == roi)].index)
    
    # Save results--> UNCOMMENT TO REALLY CHNAGE DF
    #pd.write_csv(df_original, path_csv)


    ###### REMOVE FROM SINGLE WHOLE_BRAIN.CSV
    for i, row in df.iterrows():
        if row["IsOutlier"] == 0: #if it not a real outlier after manually checkin do not do notheinf
            continue

        # Ectartc brain ID of relative to this outlier
        id = row["Brain ID"]
        roi = row["ROI"]

        #Find the Brain folder
        mouse_dir = find_dir(base_folder, str(ID))
        if mouse_dir ==  None: 
            print(f"\tATTENTION: No folder found for sample {ID}, ROI {roi}")
            continue#Find the Brain folder

        #load csv
        mouse_csv = pd.read_csv(os.path.join(mouse_dir, "_Measurements", "whole_brain.csv"))

        # Remove row
        mouse_csv = mouse_csv.drop(mouse_csv[mouse_csv["ROI"] == roi].index)

        ### Save out csv --> UNCOMMENT TO REALLY CHNAGE DF
        #mouse_csv.to_csv(os.path.join(mouse_dir, "_Measurements", "whole_brain.csv"))



