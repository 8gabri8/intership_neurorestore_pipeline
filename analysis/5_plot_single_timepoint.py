import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


"""
Thos script s creates, for each injection side and each tiempoir a seres fo plots that describe the results, 
namemy:
- 
"""

##############################################
### MANDATORY INPUTS #########################
##############################################

# Dir of the project (if script is run on batch mode, i.e. for all brains of the project)
dir_project = "/run/user/1000/gvfs/smb-share:server=upcourtinenas,share=cervical/CERVICAL_ID/connectome_analysis/final_dataset"

# Csv file with all the brains data
csv_file = "/run/user/1000/gvfs/smb-share:server=upcourtinenas,share=cervical/CERVICAL_ID/Connectome_analysis/Final_dataset/Results/all_brains.csv"

# number of the ROI to display in a plot
n_roi_displayed = 10 

# List of region to injection to invesigate (one for each folder in the porject)
region_injections = ["DR", "STN", "PARN", "IF", "GPi", "GPe", "CU", "BST"]
# List of Timepoints to investigate
timepoints = ["Uninjured", "1 weeks", "8 weeks"]

##############################################
### USEFUL FUNTIONS ##########################
##############################################

def data_summary(data, varname, groupnames):
    """
    Function to calculate the mean and standard deviation for each group.

    Parameters:
    - data: A pandas DataFrame containing the data.
    - varname: The name of the column containing the variable to be summarized (string).
    - groupnames: A list of column names to be used as grouping variables (list of strings).

    Returns:
    - data_sum: A pandas DataFrame with mean and standard deviation for each group.
    """
    
    # Group the data by the specified group names
    grouped = data.groupby(groupnames)
    
    # Apply the summary function to calculate mean and std for the specified variable
    data_sum = grouped[varname].agg(['mean', 'std']).reset_index()
    
    # Rename the mean column to the name of the variable
    data_sum = data_sum.rename(columns={'mean': varname + '_mean', 'std': varname + '_std'})
    
    return data_sum


##############################################
### READ CSV FILE  ###########################
##############################################

df_all = pd.read_csv(csv_file)

##############################################
### CREATE IMAGES ############################
##############################################

# Loop through the folder contents
for dir_inj in os.scandir(dir_project):

    # If the file is not a folder, exit
    if not dir_inj.is_dir():
        continue
    # If the folder is not an injetion folder, exit
    if not os.path.basename(dir_inj.path) in region_injections:
        continue

    # Save injection_side name
    injection_region = os.path.basename(dir_inj.path)

    for dir_timepoint in os.scandir(dir_inj):

        # If the file is not a folder, exit
        if not dir_timepoint.is_dir():
            continue
        # If the folder is not an injetion folder, exit
        if not os.path.basename(dir_timepoint.path) in timepoints:
            continue

        # Create Results folder if not yet present
        dir_results = dir_timepoint.path + "/Results"
        os.makedirs(dir_results, exist_ok=True)

        # Save timepoint
        timepoint = os.path.basename(dir_timepoint.path)

        print(f"Processing {injection_region} {timepoint}")

        ###
        # IMAGE 1: Barplot most dense Regions, Mean and Std
        ###

        # Select only mice with specifi injection region
        df_temp = df_all[df_all["Region Injection"] == injection_region]
        # Select only mice with speicific timepoint
        df_temp = df_temp[df_temp["TimePoint"] == timepoint]

        # In case the df is empty
        if df_temp.shape[0] == 0:
            continue


        # Step 1: Calculate the mean cell density for each ROI
        mean_cell_density = df_temp.groupby('ROI')['Cell Density'].mean().reset_index()
        mean_cell_density.columns = ['ROI', 'Mean Cell Density']

        # Step 2: Sort ROIs by mean cell density and select the top N ROIs
        top_roi = mean_cell_density.sort_values(by='Mean Cell Density', ascending=False).head(n_roi_displayed)
        top_rois = top_roi['ROI'].tolist()

        # Step 3: Filter the data for the top N ROIs
        df_top_rois = df_temp[df_temp['ROI'].isin(top_rois)]

        # Print the filtered DataFrame for debugging
        #print(df_top_rois)

        # Step 4: Create the plot for the top N ROIs
        fig, ax = plt.subplots(figsize=(20,10))

        # Plot mean and standard deviation for each top ROI
        for roi in top_rois:
            # Filter data for the current ROI
            df_roi = df_top_rois[df_top_rois['ROI'] == roi]
            
            # Calculate mean and standard deviation
            mean_value = df_roi['Cell Density'].mean()
            std_value = df_roi['Cell Density'].std()
            
            # Plot the bar for the mean with error bar for std
            ax.bar(roi, mean_value, yerr=std_value, capsize=5, label=f'{roi} (mean ± std)', color = 'lightblue', alpha=0.7)

            # Add the jittered swarm plot
            sns.swarmplot(data=df_roi, x='ROI', y='Cell Density', color='black', alpha=0.6)

        # Add Full name of ROIs
        textstr = df_top_rois[["Region", "Name"]].to_string(index=False)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5) # Properties text
        ax.text(0.7, 1, textstr, transform=ax.transAxes, fontsize=8, verticalalignment='top', multialignment="left", bbox=props)

        # Add labels and title
        ax.set_xlabel('ROI')
        ax.set_ylabel('Value')
        ax.set_title(f'Mean and STD for the Top {n_roi_displayed} ROIs with Highest Mean Cell Density')
        #ax.legend(title='ROIs')
        ax.legend().set_visible(False)
        plt.xticks(rotation=45)
        #ax.tight_layout()

        fig.savefig(dir_results + "/barplots_most_dense_ROI.pdf")


        ###
        # IMAGE 2: Mean HeatMaps
        ###

        ## TODO


        #######

        # Save memory
        plt.close('all')

        #if df_temp.shape[0] != 0:
        #    exit()


