import pandas as pd
import os
import find_leaves_atlas # module created by me
 
"""
This Script for each brain creates a csv file that contains the ROI and reltive synapses count. 
This file is created by merging all together all the single tsv files of a siingle brain.

The script will work only if a specific filesystem disposition is followed

It takes as inputs : the folder that contains all the brain (in this case "final_dataset")

The single csv file for each brain is saved in the "all_xsl_synapses

Attention:
    - the non-leaves ROI are removed
    - the metric calculates is: sum(dots all slices) / sum(area all slices)

"""

# MANDATORY INPUTS
path_atlas = "/home/gabri/Desktop/intership_neurorestore_pipeline/assets/Adult Mouse Brain - Allen Brain Atlas V3p1-Ontology.json"
dir_project = "/run/user/1000/gvfs/smb-share:server=upcourtinenas,share=cervical/CERVICAL_ID/connectome_analysis/final_dataset"
test = True #flag this if you want to run the script in debugging mode, i.e only few brains processed
n_test = 4 #how many brains use for testing
    
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

if test:
    print("\nAll '_Measurement' directories:")
    for directory in measurement_directories:
        print(directory)
    print("\n")

for i, measurement_directory in enumerate(measurement_directories):

    # Run the script find_leaves_atlas.csv to create a file with only leaves ROIs
    path_leaves_ROI = find_leaves_atlas.process_atlas_json(path_atlas)

    # Read the leaves ROIs df
    leaves_ROI_df = pd.read_csv(path_leaves_ROI)

    # Create df that will contain the results
    #NB only leave ROIs are inside
    df = pd.DataFrame(
    {
        "ROI" : leaves_ROI_df["Acronym"],
        "Synapses" : [0] * len(leaves_ROI_df["Acronym"]), #initialize to 0
        "Area" : [0] * len(leaves_ROI_df["Acronym"]) #initialize to 0
    }
    )
    list_roi_leaves = df['ROI'].astype(str).tolist()

    # Loop through all files in the directory
    for filename in os.listdir(measurement_directory):

        # Take only .xsl file
        if not filename.endswith('.xls'):
            #print(f"Skipping {filename} as it is not an .xls file")
            continue

        file_path = os.path.join(measurement_directory, filename)
        df_slice = pd.read_csv(file_path, sep="\t") #Attention separator

        for index, row in df_slice.iterrows():

            roi = row["Classification"]
            num_synapses = row["Num CY3"]
            area = row["Area µm^2"]

            if roi in list_roi_leaves: #if ROI is a leaf-ROI
                df.loc[df["ROI"] == roi, "Synapses"] += num_synapses
                df.loc[df["ROI"] == roi, "Area"] += area

    csv_file = measurement_directory + '/whole_brain.csv'
    print(f"Saving {i+1}-th csv as: " + csv_file)
    df.to_csv(csv_file, index=False)


