import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


##############################################
### MANDATORY INPUTS #########################
##############################################
dir_project = "/run/user/1000/gvfs/smb-share:server=upcourtinenas,share=cervical/CERVICAL_ID/connectome_analysis/final_dataset"
test = True #flag this if you want to run the script in debugging mode, i.e only few brains processed
n_test = 1 #how many brains use for testing
n_roi_displayed = 30 # number of the ROI to display in a plot

##############################################
### FIND CSV FILES ###########################
##############################################
    
def find_measurement_dirs(base_directory):
    """
    Recursively searches for directories named '_Measurements' in the specified base directory,
    excluding directories named 'data' and 'classifiers'.

    Args:
        base_directory (str): The base directory path to start the search from.

    Returns:
        list: A list of paths to directories named '_Measurement'.
    """
    measurement_dirs = []

    # Traverse the directory tree
    for dirpath, dirnames, _ in os.walk(base_directory):

        # Remove 'data' and 'classifiers' from search --> faster research
        dirnames[:] = [d for d in dirnames if d not in ('data', 'classifiers', "FB_1","FB_2", "HB_1", "HB_2")]
        
        # Check for '_measurement' directory
        if '_Measurements' in dirnames:
            full_path = os.path.join(dirpath, '_Measurements')
            measurement_dirs.append(full_path)
            #print(f"Found directory: {full_path}")

        print(f"_Measuremets file found until now: {len(measurement_dirs)}")

        #just for testing
        if test and len(measurement_dirs) == n_test: break

    return measurement_dirs

# Find all "_Measurements" directories
measurement_directories = find_measurement_dirs(dir_project)

# Find all "whole_brain.csv" file
csv_files = [csv+"/whole_brain.csv" for csv in measurement_directories]


##############################################
### CREATE IMAGES ############################
##############################################

# For each brain creates a set of images
for i, csv_file in enumerate(csv_files):

    print(f"Processing {i+1}th brain: " + csv_file)

    # Make a dir for images (if doesn't yet exist)
    grandparent_folder = os.path.dirname(os.path.dirname(csv_file)) #take the granparent folder (2 layer above the csv file)
    dir_images_name = grandparent_folder + "/_Images"
    print(dir_images_name)
    os.makedirs(dir_images_name, exist_ok=True)

    # Read csv file
    df = pd.read_csv(csv_file)

    ###
    # PLOT 1: Scatter plot for Synapses vs Area
    ###
    fig, ax = plt.subplots(figsize=(20, 6))
    sns.scatterplot(x='Area', y='Synapses', data=df, hue='Cell Density', palette='viridis', size='Cell Density', sizes=(50, 200))
    ax.set_title('Synapses vs Area')
    ax.set_xlabel('Area')
    ax.set_ylabel('Synapses')
    ax.grid(True)
    ax.set_xscale('log')
    ax.set_yscale('log')
    #plt.colorbar(label='Cell Density')
    #fig.show()
    fig.savefig(dir_images_name + "/scatterplot_area_synapses_density.png")


    ###
    # PLOT 2: Barplot of first 30 msot dense ROI
    ###
    df_sorted = df.sort_values(by='Cell Density', ascending=False)
    df_sorted = df_sorted.iloc[:n_roi_displayed, :] #take first elements

    fig, ax = plt.subplots(figsize=(20,10))
    sns.barplot(x='ROI', y='Cell Density', data=df_sorted)
    ax.set_title(f'ROIs Ordered by Cell Density (Highest to Lowest) - first {n_roi_displayed} ROI shown')
    ax.set_xlabel('Region of Interest (ROI)')
    ax.set_ylabel('Cell Density')
    plt.xticks(rotation=45)
    ax.grid(axis='y')
    #fig.show()
    fig.savefig(dir_images_name + "/barplots_most_dense_ROI.png")


    ###
    # PLOT 3: Barplot of first 30 msot dense ROI, with relative contralateral side
    ###
    df_sorted = df.sort_values(by='Cell Density', ascending=False)
    df_sorted_max = df_sorted.iloc[:n_roi_displayed, :] #take first elements

    name_max_regions = df_sorted_max["ROI"].to_list()
    values_max_regions = df_sorted_max["Cell Density"].to_list()

    name_contralateral_regions = []
    values_contralateral_regions = []

    for idx, row in df_sorted_max.iterrows():

        #info relative to the max region
        region = row['Region']
        side = row['Side']
        contralateral_side = 'Right' if side == 'Left' else 'Left'
        
        # Retrieve contralateral density from the map
        name_contralateral_regions.append(df[(df["Region"] == region) & (df["Side"] == contralateral_side)]["ROI"].values[0])
        values_contralateral_regions.append(df[(df["Region"] == region) & (df["Side"] == contralateral_side)]["Cell Density"].values[0])
    
    #print(name_max_regions, values_max_regions)
    #print(name_contralateral_regions, values_contralateral_regions)

    width = 0.9
    ind = np.arange(len(values_max_regions))
    fig, ax = plt.subplots(figsize=(20,10))
    ax.bar(x=ind, height=values_max_regions, width=width,align='center', label='Max Regions')
    ax.bar(x=ind, height=values_contralateral_regions, width=width/3,  align='center', label='Contralateral Regions')
    ax.legend()
    plt.xticks(ind, name_max_regions, rotation = 45)
    #plt.tight_layout()
    fig.savefig(dir_images_name + "/barplots_most_dense_ROI_with_contralateral.png")


