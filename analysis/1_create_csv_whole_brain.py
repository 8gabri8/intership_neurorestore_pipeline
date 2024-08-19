import pandas as pd
import os
from brainglobe_atlasapi import BrainGlobeAtlas
 
"""
Brain Atlas CSV Generation Script

Overview:
---------
This script processes brain measurement data to create CSV files containing regions of interest (ROI) and their corresponding synapse counts. It aggregates data from individual TSV files for each brain and merges them into a single CSV file per brain. The resulting files provide synapse counts and area measurements across different brain regions.

The script also generates a secondary CSV file that separates synapse counts and area measurements by brain hemisphere (left and right).

Usage:
------
- The script processes data located in a specified directory containing all brain data (in this case, "final_dataset").
- For each brain, it creates a CSV file saved in the same directory structure as the input data.
- The script can be run in test mode, where only a specified number of brains are processed for debugging purposes.

Input:
------
- `dir_project`: Directory containing all the brain data. This directory must follow a specific structure where each brain's data is stored in its subdirectory.
- `bg_atlas`: The brain atlas to use (e.g., "allen_mouse_50um").
- `test`: Boolean flag to indicate if the script should run in test mode.
- `n_test`: Number of brains to process when in test mode.

Output:
-------
- CSV files for each brain containing:
  - `ROI`: Region of Interest with the side specified (e.g., "Left: root").
  - `Region`: The region's acronym.
  - `Name`: The full name of the region.
  - `Side`: The hemisphere (Left or Right).
  - `IsLeaf`: Boolean indicating if the region is a leaf in the atlas hierarchy.
  - `Synapses`: The total number of synapses in the region.
  - `Area`: The total area of the region.
  - `Cell Density`: Synapse density calculated as sum(synapses) / sum(area).

- A second CSV file per brain that contains:
  - `Region`: The region's acronym.
  - `Synapses_Left`: Synapses in the left hemisphere.
  - `Area_Left`: Area in the left hemisphere.
  - `Synapses_Right`: Synapses in the right hemisphere.
  - `Area_Right`: Area in the right hemisphere.

Special Considerations:
-----------------------
- The script assumes that the input directory structure follows a specific layout.
- Not all ROIs created by Qpath are included in the final CSV files; only those present in the "allen_mouse_50um" atlas are considered.
- The density metric is calculated as: sum(dots across all slices) / sum(area across all slices).
- The script fills any NaN values in the `Cell Density` column with 0 to ensure completeness of the data.
- If a region is present in "allen_mouse_50um" but not in the csv file, a 0 value for are and synapses is given
- Two different final CSV files are created for each brain, containing the same information but in different formats.
"""

##############################################
### MANDATORY INPUTS #########################
##############################################
dir_project = "/run/user/1000/gvfs/smb-share:server=upcourtinenas,share=cervical/CERVICAL_ID/connectome_analysis/final_dataset"
bg_atlas = BrainGlobeAtlas("allen_mouse_50um", check_latest=False) # Atlas to use
test = True #flag this if you want to run the script in debugging mode, i.e only few brains processed
n_test = 15 #how many brains use for testing

##############################################
### USEFUL FUNCTIONS #########################
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

##############################################
### ATLAS ROI TO USE #########################
##############################################

# Find ROI that are leaves
list_leaves = []
for roi in bg_atlas.lookup_df["acronym"]:
    #print(bg_atlas.get_structure_descendants(roi))
    if len(bg_atlas.get_structure_descendants(roi)) == 0:
        list_leaves.append(roi)
#print(list_leaves)

# df wiht the ROI of the atlas

roi_atlas_left = bg_atlas.lookup_df.copy()  # ATTENTION: Create a copy!!!!!
roi_atlas_left["acronym_side"] = "Left: " + roi_atlas_left["acronym"] #create a new col with the name "Left: + roi_name"
roi_atlas_left['IsLeaf'] = roi_atlas_left['acronym'].apply(lambda x: x in list_leaves) #Creates a new col boolean, tells if the ROI is a leaf
roi_atlas_left['Side'] = ["Left"] * roi_atlas_left.shape[0] #number of rows

roi_atlas_right = bg_atlas.lookup_df.copy()  # ATTENTION: Create a copy!!!!!
roi_atlas_right["acronym_side"] = "Right: " + roi_atlas_right["acronym"]
roi_atlas_right['IsLeaf'] = roi_atlas_right['acronym'].apply(lambda x: x in list_leaves)
roi_atlas_right['Side'] = ["Right"] * roi_atlas_right.shape[0]

roi_atlas = pd.concat([roi_atlas_left, roi_atlas_right], axis=0, ignore_index=True) #merge the 2 df left and right

#print(roi_atlas)

##############################################
### FIND SINGLE BRAIN FOLDER #################
##############################################

# Find all measurements directories
measurement_directories = find_measurement_dirs(dir_project)

# Print names folder found
if test:
    print("\nAll '_Measurement' directories:")
    for directory in measurement_directories:
        print(directory)
    print("\n")


##############################################
### CREATE CSV FILES #########################
##############################################

# Now for each brain create the relative csv file
for i, measurement_directory in enumerate(measurement_directories):

    # Create df that will contain the results
    #NB only leave ROIs are inside
    df = pd.DataFrame(
    {
        "ROI" : roi_atlas["acronym_side"], # Name with Left and Right
        "Region": roi_atlas["acronym"], # Only name
        "Name": roi_atlas["name"], # Long name
        "Side": roi_atlas["Side"], 
        "IsLeaf": roi_atlas["IsLeaf"],
        "Synapses" : [0] * len(roi_atlas["acronym"]), #initialize to 0
        "Area" : [0.0] * len(roi_atlas["acronym"]) #initialize to 0.0 FLOAT!!!
        # Add Density columns later
    }
    )

    #print(df.to_string())

    # Loop through all files in the directory
    for filename in os.listdir(measurement_directory):

        # Take only .xsl file
        if not filename.endswith('.xls'):
            #print(f"Skipping {filename} as it is not an .xls file")
            continue

        # Create file path
        file_path = os.path.join(measurement_directory, filename)
        # Open tsv file
        df_slice = pd.read_csv(file_path, sep="\t") #Attention separator

        for index, row in df_slice.iterrows():

            roi = row["Classification"] #Roi name with left/right
            num_synapses = row["Num CY3"]
            area = row["Area µm^2"]

            #if ROI is a ROI in the atals choosen
            if roi in df["ROI"].values: #ATTENTION: "in" works only for losts not df columns
                df.loc[df["ROI"] == roi, "Synapses"] += num_synapses
                df.loc[df["ROI"] == roi, "Area"] += area
            else:
                pass
                #print(f"\"{roi}\" not present in allen Atlas choosen.")
        

    #print(df)

    # Calculate cell density (Synapses per Unit Area)
    df['Cell Density'] = df['Synapses'] / df['Area']
    df = df.fillna(0) # ATTENTION: Handle missing values, NaN converted to 0 !!!
    #print("\nMissing Values:\n", df.isnull().sum())

    # Save csv
    csv_file = measurement_directory + '/whole_brain.csv' # Name file to save
    print(f"Saving {i+1}-th csv as: " + csv_file)
    df.to_csv(csv_file, index=False) # Save csv

    # Create results Dir if not yet present
    save_dir = os.path.dirname(measurement_directory) # Folder where to save, i.e parent folder
    save_dir = os.path.join(save_dir, "Results")
    os.makedirs(save_dir, exist_ok=True) #Make fir if it does not exist

    ##########################################################################

    ### Create the same df, but with a different formatting

    # Step 1: Split in 2 df based on side
    left_df = df[df["Side"] == "Left"].copy()
    right_df= df[df["Side"] == "Right"].copy()

    # Step 2: select only specific columns
    cols = ["Region", "Synapses", "Area", "Cell Density"]
    left_df = left_df[cols].copy()
    right_df = right_df[cols].copy()

    # Step 3: Rename columns to prepare for merging
    left_df = left_df.rename(columns={'Synapses': 'Synapses Left', 'Area': 'Area Left', "Cell Density": "Cell Density Left"})
    right_df = right_df.rename(columns={'Synapses': 'Synapses Right', 'Area': 'Area Right', "Cell Density": "Cell Density Right"})

    # Step 4: Merge the left and right DataFrames on 'Region'
    combined_df = pd.merge(left_df, right_df, on='Region', how='outer')

    # Step 5: subsample columns
    #combined_df = combined_df[["Region", "Synapses_Left", "Area_Left", "Synapses_Right", "Area_Right"]]

    # Save csv
    csv_file = measurement_directory + '/whole_brain_splitted_LR.csv'
    print(f"Saving {i+1}-th csv as: " + csv_file)
    combined_df.to_csv(csv_file, index=False)


