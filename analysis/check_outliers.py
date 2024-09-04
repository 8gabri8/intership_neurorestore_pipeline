import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import sys


"""
This script is used to manage the outliers in the final csv file.

Strategy:
1) Check if any otliers is present
2) Create a csv file with all the putative outliers 
3) Manually check if whcih region are outliers
    - open Qupath and checck visually
    - put True in the col "IsOutliers" of the csv file if it is really an otulers
    - save the csv file as all_putative_outliers_checked.csv
4) Change its value with a specific valu
"""

##############################################
### MANDATORY INPUTS #########################
##############################################

# path big csv
path_csv = "/home/gabri/Downloads/all_brains.csv"
# path base folder
base_folder = "/run/user/1000/gvfs/smb-share:server=upcourtinenas,share=cervical/CERVICAL_ID/Connectome_analysis/Final_dataset"
#thr_z_score over which a ROI is considered an outlier
thr_z_score = 10

df_original = pd.read_csv(path_csv)
df = df_original.copy()

# ATTENTION: just for now slect only real data
df = df[df["TimePoint"] == "Uninjured"]
# ATTENTION: just for now slect only leaf
df = df[df["IsLeaf"] == True]

##############################################
### USEFUL FUNCTIONS #########################
##############################################
def find_dir(base_directory, name_dir):
    for root, dirs, files in os.walk(base_directory):
        if name_dir in dirs:
            return os.path.join(root, name_dir)
    return None  # Return None if the directory is not found


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

### Choose the stratefy to manage outliers
# Strategy I° : put 0
# Strategy II° : put NaN
# Strategy III° : remove row

strategy = 4

if strategy == 1:
    for i, row in df.iterrows():
        if row["IsOutlier"] == 0: #if it not a real outlier after manually checkin do not do notheinf
            continue
        roi = row["ROI"]
        id = row["Brain ID"]
        df_original.loc[(df_original["Brain ID"] == id) & (df_original["ROI"] == roi), ["Synapses"]] = 0
        df_original.loc[(df_original["Brain ID"] == id) & (df_original["ROI"] == roi), ["Cell Density"]] = 0
elif strategy == 2:
    for i, row in df.iterrows():
        if row["IsOutlier"] == 0: #if it not a real outlier after manually checkin do not do notheinf
            continue
        roi = row["ROI"]
        id = row["Brain ID"]
        df_original.loc[(df_original["Brain ID"] == id) & (df_original["ROI"] == roi), ["Synapses"]] = None
        df_original.loc[(df_original["Brain ID"] == id) & (df_original["ROI"] == roi), ["Cell Density"]] = None
elif strategy == 3:
    for i, row in df.iterrows():
        if row["IsOutlier"] == 0: #if it not a real outlier after manually checkin do not do notheinf
            continue
        roi = row["ROI"]
        id = row["Brain ID"]
        df_original = df_original.drop(df_original[(df_original["Brain ID"] == id) & (df_original["ROI"] == roi)].index)


# Save results
#pd.write_csv(df_original, path_csv)
