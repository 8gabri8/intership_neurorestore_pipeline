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
- Insert the [measurements_slices_xls.groovy](QuPath_scripts/measurements_slices_xls.groovy) script, which automates the analysis workflow
- Select `Run → Run for Project` to apply the script to all images within the project

    ![...](assets/images/qupath_quantification_script.png)

Script Functions:

Import Atlas: Import the atlas warped from ABBA (Allen Brain Atlas) to provide anatomical reference points.
Detect Synapses: Utilize the "cell detector" tool to find all synapses in the images.
Refine Classification: Apply a classifier to improve the accuracy of synapse identification.
Export Results: Export the synapse count for each region to an Excel (.xls) file for further analysis.
Execute Script:





