/**
 * Template macro file with useful command to succeed in doing the homework
 * 
 * It implements very basic commands. It loops over all the frames/slices of the 4D image
 * and always set the focus plane as the last image of the z-stack.
 * Finally, it prints a message to inform the user which slice is in focus for which timepoint
 * 
 * Your task
 * 		- Identify the best-focused image at each time point
 * 		- Extract the best-focused image at each time point
 * 		- Normalize each best-focused image to have a mean of 0 and standard deviation of 1
 * 		- Group all normalized best-focused images into one single 32-bit TIF stack
 * 		- Make a 4x4 montage of the in-focus stack before and after normalization
 * 		
 * IMPORTANT : an image must be open before you run this macro.
 * 
 */


// get the title of the current selected image
title = getTitle();

// get the dimensions of the current selected nD image
getDimensions(width, height, channels, slices, frames);

// create an array with initial length
focusPositions = newArray(frames);

// loop of frames and slices. Note : indices begin at 1
for(t=1; t <= frames; t++) {
	for (z=1; z<=slices; z++) {
		// force select an image given its title
		selectImage(title);
		
		// select one plane among the nD image (the order is : 'channel', 'slice', 'frame')
		// and the initial position/increment is '1'
		Stack.setPosition(1, z, t);
		
		// get the statistics of the current selected image
        getStatistics(area, mean, min, max, std, histogram);
        
        /*
         * TODO: Select the correct in-focus plane
         */
        
        // add values in the array
		focusPositions[t] = z;  
	}
	// print a message in the Log window
	print("For frame "+t+", the slice "+focusPositions[t]+" is in focus");
	
	/*
	 * TODO: add the commands to duplicate the in-focus slice
	 */
}

/*
 * TODO: add the commands create the stack from individual images and adjust the brightness/contrast
 * => hint: use the macro recorder
 */

/*
 * TODO: add the command to create the montage and adjust the brightness/contrast
 * => hint: use the search bar and the macro recorder
 */

/*
 * TODO: add the commands to duplicate the in-focus slices, apply the normalization and
 * finally merge the slices into a stack and do the last montage
 */