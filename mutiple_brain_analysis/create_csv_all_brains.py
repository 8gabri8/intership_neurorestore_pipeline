import pandas as pd
import os
import sys
 
"""
This Script will create a csv file with all the info relative to all the brains of the study

The script will work only if a specific filesystem disposition is followed

It takes as inputs : the folder that contains all the brain (in this case "connectome_analysis")

"""

# MANDATORY INPUTS
dir_project = "/run/user/1000/gvfs/smb-share:server=upcourtinenas,share=cervical/CERVICAL_ID/connectome_analysis"
path_manual_data = "/run/user/1000/gvfs/smb-share:server=upcourtinenas,share=cervical/CERVICAL_ID/Connectome_analysis/Final_dataset/paper_notes_histology_book.csv" #path to the csv file that contirna the data present in the book in the ystology facility
test = True #flag this if you want to run the script in debugging mode, i.e only few brains processed
n_test = 5 #how many brains use for testing

##############################################
### CREATE ALL_BRAINS.CSV ####################
##############################################

# Create dir to store the results
output_folder = dir_project + "/mutiple_brain_analysis"
os.makedirs(output_folder, exist_ok=True)

# read the paper book metadata
paper_book = pd.read_csv(path_manual_data)

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

# Find all measurements directories
measurement_directories = find_measurement_dirs(dir_project)

# Find all "whole_brain.csv" file
csv_files = [csv+"/whole_brain.csv" for csv in measurement_directories]

# Create an Empty df to fill with all the csv of each brain
all_df = pd.DataFrame(columns=["ROI", "Synapses", "Area", "Cell Density", "Brain ID", "Region Injection", "Side Injection", "Side Lesion", "TimePoint"])

# For each brain creates a set of images
for i, csv_file in enumerate(csv_files):

    print(f"Processing {i+1}th brain:\n\t" + csv_file)

    # Extarct brain ID
    brain_ID = os.path.basename(os.path.dirname(os.path.dirname(csv_file))) #take the granparent folder (2 layer above the csv file)
    # Ectract TimePoint
    time_point = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(csv_file))))
    # Extract Region Injection
    region_injection = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(csv_file)))))
    # Extract side of injection
    try:
        side_injection = paper_book[paper_book["Brain ID"] == int(brain_ID)]["Side Injection"].values[0]
    except:
        side_injection = "Missing"
    # Exctract Side Lesion
    try:
        side_lesion = paper_book[paper_book["Brain ID"] == int(brain_ID)]["Side Lesion"].values[0]
    except:
        side_lesion = "Missing"

    # Read csv file
    df_single = pd.read_csv(csv_file)

    # Create temp df
    temp_df = pd.DataFrame({
        "ROI": df_single["ROI"],
        "Synapses": df_single["Synapses"],
        "Area": df_single["Area"],
        "Cell Density": df_single["Cell Density"],
        "Brain ID": brain_ID,
        "Region Injection": region_injection,
        "Side Injection": side_injection, 
        "Side Lesion": "Missing",
        "TimePoint": time_point
    })

    # Concatenate vertically the df
    all_df = pd.concat([all_df, temp_df], ignore_index=True)

# Little Checks
#print(all_df)
#print(output_folder)

# Saving
path_csv = output_folder + "/all_brains.csv"
print(f"\nSaving final csv as {path_csv}\n")
all_df.to_csv(path_csv, index=False)


##############################################
### CREATE ALL_BRAINS_METADATA.CSV ###########
##############################################

### Make a df with only METADATA info

# Select only meta columns
meta_df = all_df.drop(columns=["ROI", "Synapses", "Area", "Cell Density"])

# Collapse duplicated rows (only one col for brain)
meta_df = meta_df.drop_duplicates()

# Saving
path_csv = output_folder + "/all_brains_meta.csv"
print(f"\nSaving final csv as {path_csv}\n")
meta_df.to_csv(path_csv, index=False)

##############################################
### CREATE ALL_BRAINS_LF.CSV #################
##############################################

# Find all measurements directories
measurement_directories = find_measurement_dirs(dir_project)

# Find all "whole_brain.csv" file
csv_files = [csv+"/whole_brain_splitted_LR.csv" for csv in measurement_directories]

# Create an Empty df to fill with all the csv of each brain
all_df = pd.DataFrame(columns=["Region", "Synapses_Left", "Area_Left", "Synapses_Right", "Area_Right", "Brain ID", "Region Injection", "Side Injection", "Side Lesion", "TimePoint"])

# For each brain creates a set of images
for i, csv_file in enumerate(csv_files):

    print(f"Processing {i+1}th brain:\n\t" + csv_file)

    # Extarct brain ID
    brain_ID = os.path.basename(os.path.dirname(os.path.dirname(csv_file))) #take the granparent folder (2 layer above the csv file)
    # Ectract TimePoint
    time_point = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(csv_file))))
    # Extract Region Injection
    region_injection = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(csv_file)))))

    # Read csv file
    df_single = pd.read_csv(csv_file)

    # Create temp df
    temp_df = pd.DataFrame({
        "Region": df_single["Region"],
        "Synapses_Left": df_single["Synapses_Left"],
        "Area_Left": df_single["Area_Left"],
        "Synapses_Right": df_single["Synapses_Right"],
        "Area_Right": df_single["Area_Right"],
        "Brain ID": brain_ID,
        "Region Injection": region_injection,
        "Side Injection": "Missing", 
        "Side Lesion": "Missing",
        "TimePoint": time_point
    })

    # Concatenate vertically the df
    all_df = pd.concat([all_df, temp_df], ignore_index=True)

# Little Checks
#print(all_df)
#print(output_folder)

# Saving
path_csv = output_folder + "/all_brains_LR.csv"
print(f"\nSaving final csv as {path_csv}\n")
all_df.to_csv(path_csv, index=False)