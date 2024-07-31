def project = getProject() //get the Project Obejct

//Goes though all the images fo the project
for (entry in project.getImageList()) {
    
    def imageName = entry.getImageName()
  
    // Check if the image name contains "label" or "overview"
    if (imageName.contains("label") || imageName.contains("overview")) {
        project.removeImage(entry, true)
    }
}
getQuPath().refreshProject() // to refresh the project