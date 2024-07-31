// Script to remove images that are not brains from qupath project

// Get the project object, which contains information about the current project
def project = getProject()

// Iterate through all the images in the project's image list
for (entry in project.getImageList()) {
    
    // Retrieve the name of the current image
    def imageName = entry.getImageName()
  
    // Check if the image name contains the keywords "label" or "overview"
    if (imageName.contains("label") || imageName.contains("overview")) {
        
        // Remove the image from the project if it matches the criteria
        // The second argument 'true' specifies that the image should be deleted permanently
        project.removeImage(entry, true)
    }
}

// Refresh the project to reflect the changes made by removing images
getQuPath().refreshProject()

