// Manually insert input
//imagePath = File.openDialog("Select input image: ");
//output = getDirectory("Select output folder: ");

// Get input from command line
input = getArgument();
inputs = split(input, " "); //attention: depending on what is here, you have to chnag the way ion which yuo give inputs
imagePath = inputs[0]; // Input image to process
output = inputs[1]; // Temporary folder where to save

if (!File.exists(output )) {
    File.makeDirectory(output);
}

// Remove all files if the folder already exists
//fileList = getFileList(output);
//for (i = 0; i < fileList.length; i++) {
//    File.delete(dirPath + fileList[i]);
//}

// Set batch mode to true to avoid showing intermediate images
setBatchMode(true);

// Open the selected image
open(imagePath);
name = getTitle();
run("List Elements");
run("To ROI Manager");
setOption("BlackBackground", true);

// Load ROIs into the ROI Manager
run("ROI Manager...");
roiManager("Show All");

// Initialize an array to hold ROI names and particle counts
roiParticleCounts = newArray();

// Loop through each ROI in the ROI Manager
n = roiManager("count");
for (i = 0; i < n; i++) {
    // Select the ROI
    roiManager("Select", i);

    // Run particle analysis
    run("Analyze Particles...", "size=0-Infinity circularity=0.00-1.00 show=Nothing summarize");
}

// Specify the path and file name for the CSV file to be saved
saveAs("Results", output + "/counts.csv");

run("Close", "name=Summary");

// Set Area as a paramter to emasure
run("Set Measurements...", "area mean standard perimeter fit shape feret's integrated redirect=None decimal=3");

for (i = 0; i < n; i++) {
    // Select the ROI
    roiManager("Select", i);

    // Run particle analysis
    run("Measure");
}

saveAs("Results", output + "/areas.csv");

run("Close", "name=Results");

run("ROI Manager...");
roiManager("Show All");

// Initialize an array to hold ROI names and particle counts
roiParticleCounts = newArray();

// Loop through each ROI in the ROI Manager
n = roiManager("count");
for (i = 0; i < n; i++) {
    // Select the ROI
    roiManager("Select", i);

    // Retrieve the particle count directly from the Results table
    z_slice = 0; // Since we're only processing one image, we can set z_slice to 0

    // Get the ROI name
    roiManager("Select", i);
    roiName = Roi.getName();

    // Store the ROI name and particle count in an array
    roiParticleCounts = Array.concat(roiParticleCounts, newArray(roiName, z_slice));

    // Clear the Results table for the next iteration
    run("Clear Results");
}

// Create a new Results window and populate it with the data
for (j = 0; j < roiParticleCounts.length; j += 2) {
    setResult("ROI Name", j / 2, roiParticleCounts[j]);
    setResult("Z-slice", j / 2, roiParticleCounts[j + 1]);
}

updateResults(); // Update the Results table with the new data

saveAs("Results", output + "/names.csv");

// Close all open images
run("Close All");

run("Close All", "name=Summary");
close("ROI Manager");
close("Results");

setBatchMode(false);

