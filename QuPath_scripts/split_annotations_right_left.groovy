import qupath.lib.gui.scripting.QPEx
import qupath.lib.objects.PathObject
import qupath.lib.objects.PathObjects
import qupath.lib.objects.PathAnnotationObject
import qupath.lib.objects.classes.PathClass
import qupath.lib.roi.ROIs

//Script to change, for each annoatation, the "Name" field with the content of the "Classification" field
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

// Update the hierarchy
fireHierarchyUpdate() 

print "Annotation names updated with classification names."
