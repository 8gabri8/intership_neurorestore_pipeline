import pandas as pd
import os
 
"""
This Script will create a csv file with all the info relative to all the brains of the study

The script will work only if a specific filesystem disposition is followed

It takes as inputs : the folder that contains all the brain (in this case "connectome_analysis")

"""

# MANDATORY INPUTS
dir_project = "/run/user/1000/gvfs/smb-share:server=upcourtinenas,share=cervical/CERVICAL_ID/connectome_analysis"
test = True #flag this if you want to run the script in debugging mode, i.e only few brains processed
n_test = 2 #how many brains use for testing

############################################################################

# Create dir to store the results
output_folder = dir_project + "/mutiple_brain_analysis"
os.makedirs(output_folder, exist_ok=True)

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
all_df = pd.DataFrame(columns=["ROI", "Synapses", "Area", "Cell Density", "Brain ID", "Side Injection", "Side Lesion", "TimePoint"])

# For each brain creates a set of images
for i, csv_file in enumerate(csv_files):

    print(f"Processing {i+1}th brain:\n\t" + csv_file)

    # Extarct brain ID
    brain_ID = os.path.basename(os.path.dirname(os.path.dirname(csv_file))) #take the granparent folder (2 layer above the csv file)
    # Ectract TimePoint
    time_point = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(csv_file))))

    # Read csv file
    df_single = pd.read_csv(csv_file)

    # Create temp df
    temp_df = pd.DataFrame({
        "ROI": df_single["ROI"],
        "Synapses": df_single["Synapses"],
        "Area": df_single["Area"],
        "Cell Density": df_single["Cell Density"],
        "Brain ID": brain_ID,
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
path_csv = output_folder + "/all_brains.csv"
print(f"\nSaving final csv as {path_csv}\n")
all_df.to_csv(path_csv, index=False)