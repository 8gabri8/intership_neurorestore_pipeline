// Scripts that for each slice creates a tsv file with the number of synapses for each ROI
// Scripts works on a single slice/image, so it is supposed to be run with "project" option to do all the images

// Script Operations:

// - Select only the images that have received a registration from ABBA.
//   This ensures that the quantification is performed exclusively on images
//   that have been correctly aligned with the ABBA (Allen Brain Atlas).

// - Import the atlas warped from ABBA to provide anatomical reference points.
//   This step integrates the atlas into the analysis, enabling accurate localization
//   of anatomical regions within each image.

// - Utilize the "Cell Detector" tool to identify potential synapses in the images.
//   This tool scans the images to find detections that are likely to represent synapses,
//   allowing for targeted analysis of these structures.

// - Apply a classifier to improve the accuracy of synapse identification.
//   By refining the initial detections, the classifier enhances the precision of synapse
//   identification, reducing false positives and improving overall data quality.

// - Export the synapse count for each region to an Excel (.xls) file for further analysis.
//   This step compiles the quantified data into an Excel spreadsheet, facilitating
//   subsequent analysis and visualization of the synapse distributions across regions.


//MANDATORY INPUTS:
path_classifier = "/run/user/1000/gvfs/smb-share:server=upcourtinenas,share=cervical/CERVICAL_ID/Hortense/synapse_classifier.json" //path to the pretrained classifier

// setting up the image and necessary QuPath classes
import qupath.lib.objects.PathAnnotationObject
import qupath.lib.objects.PathObjects
import qupath.lib.objects.hierarchy.PathObjectHierarchy
import qupath.lib.gui.tools.MeasurementExporter
import qupath.lib.objects.PathCellObject

//create folder xls files (if it doesnt alredy exist)
def dir_name = buildFilePath(PROJECT_BASE_DIR, '_Measurements') //PROJECT_BASE_DIR  is the folder opf the QuPath Project
if (!fileExists(dir_name)) {
    mkdirs(dir_name)
}
    
//Image processsed now
print getCurrentImageName() 

//Check to process only images with a registration from ABBA --> otherwise do not process
qupath.ext.biop.abba.AtlasTools.loadWarpedAtlasAnnotations(getCurrentImageData(), "acronym", true)
int afterAnnotationCount = getAnnotationObjects().size()
if (afterAnnotationCount == 0 ) {
    println "Error: No atlas registration found for image: ${getCurrentImageName()}. Skipping to the next image."
    return // Continue to the next image
}

//Necessary if forgotten during the importation of the images in the QuPath project
setImageType('FLUORESCENCE')

//Remove all ROIs from ROI manager
clearAllObjects()

// Select the whole image
createFullImageAnnotation(true)

// Cell detector (find detection that are putative to be synapses)
runPlugin('qupath.imagej.detect.cells.WatershedCellDetection', '{"detectionImage":"CY3","requestedPixelSizeMicrons":0.6465,"backgroundRadiusMicrons":8.0,"backgroundByReconstruction":false,"medianRadiusMicrons":0.0,"sigmaMicrons":0.3,"minAreaMicrons":0.5,"maxAreaMicrons":25.0,"threshold":110.0,"watershedPostProcess":true,"cellExpansionMicrons":1.0,"includeNuclei":false,"smoothBoundaries":true,"makeMeasurements":true}')
    //NB. flagged: "split right/left" and "Acronym"
    
// Classifier (use already trained classifier to refine detections that are really synapses)
runObjectClassifier(path_classifier)
	//with these command now we have 2 columns
		//Num Detections
		//Num CY3 --> the real synapses after the object classfication

// Import ABBA annotations (ROIs)
qupath.ext.biop.abba.AtlasTools.loadWarpedAtlasAnnotations(getCurrentImageData(), "acronym", true)
fireHierarchyUpdate() //Update Hierarchy

// Get name of image, for give the same name to the xls file
def name_image = getProjectEntry().getImageName()
name_image = name_image.replaceAll("\\s","") //remove spaces from name
name_image = name_image.replaceAll(".vsi","") // remode .vsi at the end
def measurementFilePath = buildFilePath(dir_name, name_image + '.xls') //name of the xls file of this slice

// Save xls file with #synapense per ROI
saveAnnotationMeasurements(measurementFilePath)
println("Measurements have been written to: $measurementFilePath")


