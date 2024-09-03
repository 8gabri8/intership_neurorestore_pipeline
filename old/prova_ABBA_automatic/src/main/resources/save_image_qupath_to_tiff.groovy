import ij.IJ
import qupath.imagej.gui.IJExtension
import ij.IJ
import ij.CompositeImage
import ij.ImagePlus
import ij.process.ImageProcessor
import ij.plugin.frame.RoiManager
import qupath.imagej.tools.IJTools
import qupath.lib.gui.images.servers.RenderedImageServer
import qupath.lib.gui.viewer.overlays.HierarchyOverlay
import qupath.lib.regions.RegionRequest
import qupath.lib.gui.scripting.QPEx
import static qupath.lib.gui.scripting.QPEx.*
import java.awt.image.BufferedImage
import javax.imageio.ImageIO
import java.io.File

//ATTENTION: BE SURE THAT BEFORE RUNNIN THE SCRIPT THE "ANNOATION OBEJECT" AND "ANNOTATION NAME" ARE VISIBLE (otherwise they will not be exported)
//bottons are on the top center of the QuPath GUI

double downsample = 1 // Increase if you want to export to work at a lower resolution

//// CHANGE ROI NAMES ////

//chnage, for each annoation, the Name field with the content of the Classificatioj field
//In this way the spatial info (left/right) is preserved

// Get the current image data
def imageData = QPEx.getCurrentImageData()

// Get the hierarchy
def hierarchy = imageData.getHierarchy()

// Get all annotations
def annotations = hierarchy.getAnnotationObjects()

// Iterate over each annotation
annotations.each { annotation ->
    // Get the classification
    def classification = annotation.getPathClass()

    // Check if classification is not null
    if (classification != null) {
        // Get the name of the classification
        def className = classification.toString()

        // Set the name of the annotation to the classification name
        annotation.setName(className)

        print classification.toString()

    }
}

fireHierarchyUpdate() // Update the hierarchy

print "Annotation names updated with classification name"

//// REMOVE USELESS CHANNELS ////

// very useful: https://gist.github.com/Svidro/259c8baa9037579828d17e7d65703346
//"Export full image with overlays to ImageJ.groovy"

def server = getCurrentServer()

def request = RegionRequest.createInstance(server, downsample)

boolean setROI = false //if true, the ROI of the pathObject will be set on the image as the 'main' ROI (i.e. not an overlay)

def imp = IJExtension.extractROIWithOverlay(
        getCurrentServer(),
        null,
        getCurrentHierarchy(),
        request,
        setROI,
        getCurrentViewer().getOverlayOptions()
).getImage()
//returns an Image of the class ij.CompositeImage

imp.show() //necessary beacuse the command in Fiji want the image opened

IJ.setSlice(1);
IJ.run("Delete Slice", "delete=channel");
IJ.setSlice(1); //once the first slice is delete, the second becomes the first
IJ.run("Delete Slice", "delete=channel");
IJ.setSlice(2);
IJ.run("Delete Slice", "delete=channel");

//Increase contrast --> MESSING WITH THE REAL PIXEL VALUES !!!!
//IJ.run("Enhance Contrast", "saturated=0.35");
//IJ.run("Apply LUT");

print "Useless channels removed"

//// SAVE IMAGE ////

def title = imp.getTitle()
title = title.replaceAll("\\s","") //remove spaces from name
if (downsample != 1) {
    title = title + "_res_" + downsample
}
def dir_name = buildFilePath(PROJECT_BASE_DIR, "tiffs")
if (!fileExists(dir_name)) {
    mkdirs(dir_name)
}
def path = buildFilePath(dir_name, title + '.tif')
print path
IJ.saveAs("Tiff", path);

imp.close()

//def objClass = imp.getClass()
//println("obj is of type: ${objClass.name}")