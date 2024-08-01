# intership_neurorestore_pipeline

This folder contains a series of scripts that are used for implementiang a regitration and quantification pipeline.


## Export Registratiosn from ABBA to QuPath
In ABBA:
- Select all the slices (`Ctrl+A`)
- In the top menu bar `Export > ABBA - Export Registrations To QuPath project`

    ![...](assets/images/abba_export.png)

## QuPath Quantification and Export
In QuPath:
- Open the pre-existing project that contains your image data
- Access the script editor within QuPath to input custom scripts
- Insert the **[measurements_slices_xls.groovy](QuPath_scripts/measurements_slices_xls.groovy)** script, which automates the analysis workflow
- Select `Run → Run for Project` to apply the script to all images within the project

    ![...](assets/images/qupath_quantification_script.png)

> **Note:** For specific steps performed in `measurements_slices_xls.groovy`, please check the script documentation.

## Merging all .tsv files in one .csv for one Brain
The previous step creates one .tsv file for each slice/brain image of the project. 
Run the script **[create_csv_whole_brain.py](create_csv_whole_brain.py)** for merging all these .tsv files in one single csv file.

>**Note**: the script is meant to run on multiple brains at the same time, pay attention to give as input the root folder of the whole project and to respect the structure of the filesystem expted by the script.

>**Note**: the script will output 2 csv files, they store the same information, but have different formattting.

## Single Brain Analysis
Once we obtained the csv file for each brain, we can perform a simple analysis of the realtive data.
Here are reported a series of scripts for this type of analysis:
- **[plots_single_brain.py](single_brain_analysis/plots_single_brain.py)** generates a series of insightful images for individual brain scans. It is designed to process multiple brain images within a single project. By specifying the project directory path as input, the script will handle retrieving individual files and creating necessary folders for output
- **[single_brain_viz.ipynb](single_brain_analysis/single_brain_viz.ipynb)** allows the user to create and investigate the single brain reuslts using 2D and 3D visualization, alogn with HeatMap display. **Note**: in order to achive split between left and right ROIs in the same image a deep modification of brainglob_heatmap packages is necessary (see script for more details).

## Multiple Brain Analysis
Once we have obtained the CSV files for each brain, we can perform comparative analysis across different brain datasets. Below are some scripts that facilitate this type of analysis:

- **[create_csv_all_brains.py](mutiple_brain_analysis/create_csv_all_brains.py)**: This script generates a single CSV file that consolidates information from all individual brain datasets into one comprehensive file.







