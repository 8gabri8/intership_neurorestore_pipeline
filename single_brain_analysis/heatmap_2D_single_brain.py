import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import brainglobe_heatmap as bgh #Please use a VE where brainrender is installed
from brainglobe_atlasapi import BrainGlobeAtlas
from PIL import Image


"""
This script creates 2D heatmaps.

This script should be run 2 times
    - one for creating left heatmaps
    - one for right + one for merginf them

"""

##############################################
### FUNCTIONS ###############################
##############################################

def split_and_merge_png_images(image_path_left, image_path_right, output_path, left_ratio=0.493, right_ratio=0.507):
    """
    Splits and merges two PNG images with the specified ratio for each side.

    :param image_path1: Path to the left image.
    :param image_path2: Path to the right image.
    :param output_path: Path to save the combined image.
    :param left_ratio: Ratio of the width to take from the left image.
    :param right_ratio: Ratio of the width to take from the right image.
    """
    # Load PNG images
    img1 = Image.open(image_path_left)
    img2 = Image.open(image_path_right)

    # Ensure images have the same height
    if img1.size[1] != img2.size[1]:
        raise ValueError("Images must have the same height.")

    # Get image dimensions
    width1, height1 = img1.size
    width2, height2 = img2.size

    # Calculate cropping dimensions based on the provided ratios
    left_crop_width = int(width1 * left_ratio)
    right_crop_width = int(width2 * right_ratio)

    # Crop each image according to the calculated dimensions
    left_half_img1 = img1.crop((0, 0, left_crop_width, height1))
    right_half_img2 = img2.crop((width2 - right_crop_width, 0, width2, height2))

    # Save the intermediate halves --> TEST WHERE TO CUT!!!
    #left_half_img1.save('left_half.png')
    #right_half_img2.save('right_half.png')

    # Create a new image with combined width
    new_width = left_half_img1.width + right_half_img2.width
    new_image = Image.new('RGB', (new_width, height1))

    # Paste halves into the new image
    new_image.paste(left_half_img1, (0, 0))
    new_image.paste(right_half_img2, (left_half_img1.width, 0))

    # Save the combined image
    print(f"Saving merged heatmap {output_path}")
    new_image.save(output_path)

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

##############################################
### MANDATORY INPUTS #########################
##############################################

dir_project = "/run/user/1000/gvfs/smb-share:server=upcourtinenas,share=cervical/CERVICAL_ID/connectome_analysis/final_dataset"
test = True #flag this if you want to run the script in debugging mode, i.e only few brains processed
n_test = 1 #how many brains use for testing
single_brain = None #None OR /run/user/1000/gvfs/smb-share:server=upcourtinenas,share=cervical/CERVICAL_ID/Connectome_analysis/Final_dataset/DR/8 weeks/__100__/_Measurements
    #if you want:
        #run the script for all the brains in the project: single brain = None
        #run the script for a specific brain; single_brain = "path_to_Measuremets_dir"
side = "Merge" # "Left", "Right", "Merge"

#Choose how many and from to cut
start_cut = 10000 #from olfacotry bulb
end_cut = 11000 #to myelenchephalon
step = 500

# Select an atlas
atlas_name = "allen_mouse_25um"
bg_atlas = BrainGlobeAtlas(atlas_name, check_latest=False)

##############################################
### FIND CSV FILES ###########################
##############################################

# Find all "_Measurements" directories
if single_brain == None:
    measurement_directories = find_measurement_dirs(dir_project)
else:
    measurement_directories = single_brain

# Find all "whole_brain.csv" file
csv_files = [csv+"/whole_brain.csv" for csv in measurement_directories]

##############################################
### CREATE IMAGES ############################
##############################################

# For each brain creates a set of images
for i, csv_file in enumerate(csv_files):

    print(f"Processing {i+1}th brain: " + csv_file)

    # Read csv file
    df = pd.read_csv(csv_file)

    ##############################################
    ### CREATE FOLDERS ###########################
    ##############################################

    # Make a dir for images (if doesn't yet exist)
    grandparent_folder = os.path.dirname(os.path.dirname(csv_file)) #take the granparent folder (2 layer above the csv file)
    dir_images_name = grandparent_folder + "/_Images"
    print(dir_images_name)
    os.makedirs(dir_images_name, exist_ok=True)

    #Create a folder where to store them
    heatmaps_dir = dir_images_name + "/2D_heatmaps" 
    heatmaps_dir_left = dir_images_name + "/2D_heatmaps/Left" 
    heatmaps_dir_right = dir_images_name + "/2D_heatmaps/Right" 
    heatmaps_dir_merged = dir_images_name + "/2D_heatmaps/Merged" 
    os.makedirs(heatmaps_dir, exist_ok=True)
    os.makedirs(heatmaps_dir_left, exist_ok=True)
    os.makedirs(heatmaps_dir_right, exist_ok=True)
    os.makedirs(heatmaps_dir_merged, exist_ok=True)

    ##############################################
    ### CREATE HEATMAPS ONLY ONE SIDE ############
    ##############################################

    #Create several 2D Heatmpas of ONLY ONE HEMISPHERE og the brain
    #Show all regions, not a subset of the msot dense

    if side != "Merge":

        df_side = df[df["Side"] == side]  # Take the ROI only from one side

        # Use only the ROI that are present in the atlas
        df_side = df_side[df_side['Region'].isin(bg_atlas.lookup_df["acronym"].to_list())]

        # Create the dictionary --> NB take the name withounf left or right
        # ex: dict{"CA1": 10, "ENT": 40, ...}
        cell_density_data = dict(zip(df_side['Region'], df_side['Cell Density']))

        #print(cell_density_data)

        # Iterate over cuts range
        for cut in range(start_cut, end_cut, step):
            
            # Create Heatmap object
            f = bgh.Heatmap(
                cell_density_data,
                position=cut,
                orientation="frontal",  # Adjust orientation as needed
                title="", #f"Side: {side} - Slice position: {cut}",
                vmin=0,
                vmax=0.01,
                cmap='Reds',
                atlas_name=atlas_name,
                format='2D', 
                hemisphere=side.lower(), #Attention lower case
                label_regions=True,
            )
            
            # Save the figure as PDF
            fig = f.my_plot(show_cbar=False) 
                # ATTENTION: MY PLOT IS A CUSTUM FUNCTION
                    #just go in the file brainrender-env/lib/python3.9/site-packages/brainglobe_heatmap/heatmaps.py
                    #create a new fucntion my_plot that copies the function plot()
                    #and comment out the plt.show() at the end
            fig.savefig(os.path.join(heatmaps_dir + "/" + side, f'{cut}.png'), dpi=100)

    ##############################################
    ### MERGE IMAGES #############################
    ##############################################
    
    else:
        for root, dirs, files in os.walk(heatmaps_dir_left):
            for file in files:
                file_path_left = os.path.join(heatmaps_dir_left, file) #path fo the file
                file_path_right = os.path.join(heatmaps_dir_right, file)
                file_path_merged = os.path.join(heatmaps_dir_merged, file)
                split_and_merge_png_images(image_path_left=file_path_right, #ATTENTION, are inverted
                                           image_path_right=file_path_left,  
                                           output_path=file_path_merged, 
                                           left_ratio=0.493, 
                                           right_ratio=0.507)

    ##############################################
    ### MAKE VIDEO ###############################
    ##############################################