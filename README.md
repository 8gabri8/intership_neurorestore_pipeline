# intership_neurorestore_pipeline

This folder contains a series of scripts that are used for implementiang a regitration and quantification pipeline.

## Virtual Environment
In order to run the jupyter nootebooks and scripts inside this folder, we advise you to create a conda enviroment using the []() file.

   - **Create a Virtual Environment:**
     Use the following command to create a virtual environment from the provided [brainrender-env.yml](assets/yml/brainrender-env.yml) file:
     ```bash
     conda env create -f brainrender-env.yml
     ```

   - **Activate the Environment:**
     Once created, activate the environment using:
     ```bash
     conda activate brainrender-env
     ```

## Partial Automated pipeline in ABBA
After importing the QuPath project into ABBA and have performed the beginning quality control (e.g. slice rotatation, label removal, ...), you can run the Fiji script **[abba_automated_registration.ijm](ABBA_scripts/abba_automated_registration.ijm)**. The main ateps are: slect all slices in ABBA, open  the Fiji macro runner paste the code and run it.
> **Note**:  it is important to note that this script only partially automate the pipeline in ABBA, it is manly meant to execute all together the series of differt registartion methods (linear, splines, ...) in a faster and easier way. 

> **Note**: Please check the paramters of each registration method and chnage them according to your needs.


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
Run the script **[1_create_csv_whole_brain.py](analysis/1_create_csv_whole_brain.py)** for merging all these .tsv files in one single csv file.

>**Note**: the script is meant to run on multiple brains at the same time, pay attention to give as input the root folder of the whole project and to respect the structure of the filesystem expted by the script.

>**Note**: the script will output 2 csv files, they store the same information, but have different formattting.

## All Brains DataFrame
To semplify the future operations all the values of the brains are put together in one single csv file. DO so using the script **[2_create_csv_all_brains.py](analysis/2_create_csv_all_brains.py)**

## Single Brain Analysis
Once we obtained the csv file for each brain, we can perform a simple analysis of the realtive data.
Here are reported a series of scripts for this type of analysis:
- **[3_plot_single_brain.py](analysis/3_plot_single_brain.py)** generates a series of insightful images for individual brain scans. It is designed to process multiple brain images within a single project. By specifying the project directory path as input, the script will handle retrieving individual files and creating necessary folders for output
- **[4_2D_heatmap_single_brain.ipynb](analysis/4_2D_heatmap_single_brain.ipynb)** creates 2D heatmaps of each brain, where differt hemispheres have differt values, along with a video of the relative images.
- **[single_brain_3D_viz.ipynb](analysis/single_brain_3D_viz.ipynb)** allows the user to create and investigate the single brain reuslts using 3D visualization, alogn with HeatMap display.


## Multiple Brain Analysis
Once we have obtained the CSV files for each brain, we can perform comparative analysis across different brain datasets. Below are some scripts that facilitate this type of analysis:

- **[5_plot_single_timepoint.ipynb](analysis/5_plot_single_timepoint.ipynb)**: This script generates a plots and heatmas relative a single timepoint for a specific region fo injection (please see the code for more specific documentation).
- **[6_plot_multiple_timepoints.ipynb](analysis/6_plot_multiple_timepoints.ipynb)**: This script creates plots that summarize the evolution of the density in differt ROIs across differt timepoints. The Region of Injection is keept constant.


## Differential Expression (DE) Analysis
This scripts investigate if there are statistical signficant changes in the espression of Synapses during the TimePoint investigated. More specifically:

- **[check_stat_test.ipynb](analysis/7_DE_analysis/check_stat_test.ipynb)** verify that the variable *Synapses* and *Cell Density* follows a Negative Binomila distribution with overdispersion, in order to verify the assumptions of the followinf statistical model used. **Note**: no necessary for the pipeline, just to analyse the data.
- **[edgeR_LRT_synapses.qmd](analysis/7_DE_analysis/edgeR_LRT_synapses.qmd)** allow the user to investigate the different passages of EdgeR in order to better understand which are the paramters and passage underlying this statistical test. **Note**: no necessary for the pipeline, just to analyse the data.
- **[7_differentail_expression_analysis.qmd](analysis/7_DE_analysis/7_differentail_expression_analysis.qmd)**: This script, given a region of injection, calculates which are the ROI that are statistically differt across times points and classify them in archetypes.


## Unused Scripts
During the course of the internship, many scripts were created. The folder **[old](old/)** contains scripts that are not currently used in the pipeline but may still be useful for other types of analysis (e.g., _detecting spots in images with the Spotiflow ImageJ plugin_). Naturally, the reltive documentation is less cured.








