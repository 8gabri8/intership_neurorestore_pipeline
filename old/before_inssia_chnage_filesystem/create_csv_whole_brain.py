import pandas as pd
import os
import old.before_inssia_chnage_filesystem.find_leaves_atlas as find_leaves_atlas #a module created by me
 
"""
This Script for each brain creates a csv file that contains the ROI and reltive synapses count. 
This file is created by merging all together all the single tsv files of a siingle brain.

The script will work only if a specific filesystem disposition is followed

It takes as inputs : the folder that contains all the brain (in this case "final_dataset")

The single csv file for each brain is saved in the same folder that constains all the csv

Attention:
    - the non-leaves ROI are removed
    - the metric calculates is: sum(dots all slices) / sum(area all slices)
    - 2 different final csv files will be created (same information conveid, just chnaged the format)

"""

# MANDATORY INPUTS
path_atlas = "/home/gabri/Desktop/test_abba/prova_ABBA_automatic/src/main/resources/Adult Mouse Brain - Allen Brain Atlas V3p1-Ontology.json"
dir_project = "/run/user/1000/gvfs/smb-share:server=upcourtinenas,share=cervical/CERVICAL_ID/connectome_analysis/final_dataset"
test = True #flag this if you want to run the script in debugging mode, i.e only few brains processed
n_test = 15 #how many brains use for testing
    
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

# Now for each brain create the relative csv file
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
        "Area" : [0.0] * len(leaves_ROI_df["Acronym"]) #initialize to 0.0 FLOAT!!!
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

    # Put "Region" column
    df_region = df.copy()
    df_region[['Side', 'Region']] = df['ROI'].str.split(': ', expand=True)

    # Calculate cell density (Synapses per Unit Area)
    df_region['Cell Density'] = df_region['Synapses'] / df_region['Area']
    df_region = df_region.fillna(0) # ATTENTION: Handle missing values, NaN converted to 0 !!!
    #print("\nMissing Values:\n", df.isnull().sum())

    # Save csv
    csv_file = measurement_directory + '/whole_brain.csv'
    print(f"Saving {i+1}-th csv as: " + csv_file + "\n")
    df_region.to_csv(csv_file, index=False)

    ##########################################################################

    # Create the same df, but with a different formatting
    # Step 1: Split 'ROI' column into 'Side' and 'Region'
    df[['Side', 'Region']] = df['ROI'].str.split(': ', expand=True)

    # Step 2: Separate data by 'Side'
    left_df = df[df['Side'] == 'Left'].drop(columns=['Side'])
    right_df = df[df['Side'] == 'Right'].drop(columns=['Side'])

    # Step 3: Rename columns to prepare for merging
    left_df = left_df.rename(columns={'Synapses': 'Synapses_Left', 'Area': 'Area_Left'})
    right_df = right_df.rename(columns={'Synapses': 'Synapses_Right', 'Area': 'Area_Right'})

    # Step 4: Merge the left and right DataFrames on 'Region'
    combined_df = pd.merge(left_df, right_df, on='Region', how='outer')

    # Step 5: Rename the 'Region' column to 'ROI'
    #combined_df = combined_df.rename(columns={'Region': 'ROI'})

    # Step 6: subsample columns
    combined_df = combined_df[["Region", "Synapses_Left", "Area_Left", "Synapses_Right", "Area_Right"]]

    # Save csv
    csv_file = measurement_directory + '/whole_brain_splitted_LR.csv'
    print(f"Saving {i+1}-th csv as: " + csv_file)
    combined_df.to_csv(csv_file, index=False)


