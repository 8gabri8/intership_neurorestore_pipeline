// This scripts automate the various registration steps to perform in ABBA. 
// Initial and Final manual registration are not covered by the script.


// Manual: Open ABBA

// Manual: Load Project in ABBA

// Manual: Adjust the orientation "non si scappa..."

// Manual: Select all Slices with Crtl+A

// Change display color of channel 3 and 0
run("ABBA - Set Slices Min Max Display Range", 
    "mp=ch.epfl.biop.atlas.aligner.MultiSlicePositioner@3999e91 "+
    "channels_csv=3 "+
    "display_min=0.0 " + 
    "display_max=1200.0");
run("ABBA - Set Slices Min Max Display Range",
    "mp=ch.epfl.biop.atlas.aligner.MultiSlicePositioner@3999e91 "+
    "channels_csv=0 "+
    "display_min=0.0 " + 
    "display_max=1000.0");

// Run DeepSlice
run("DeepSlice setup...", "deepsliceenvdirectory=/home/gabri/mambaforge/envs/deepslice version=1.1.5.1");
run("ABBA - DeepSlice Registration (Local)", 
    "mp=ch.epfl.biop.atlas.aligner.MultiSlicePositioner@3999e91 " + 
    "channels=3 "+ //0-dapi,3-nissl
    "model=mouse "+
    "allow_slicing_angle_change=true "+
    "ensemble=true post_processing=[Keep order + ensure regular spacing] "+
    "slices_spacing_micrometer=0.0");

// Run Elastik Affine(Linear) Registration
run("ABBA - Elastix Registration (Affine)", 
    "mp=ch.epfl.biop.atlas.aligner.MultiSlicePositioner@3999e91 " + 
    "channels_atlas_csv=0 "+ //0-nissl, 0-nissl
    "channels_slice_csv=3 "+ //0-dapi,3-nissl
    "pixel_size_micrometer=20.0 "+ //6um
    "show_imageplus_registration_result=false "+
    "background_offset_value_moving=0.0");

// Run Elastik Spline(Non-Linear) Registration --> run twice
run("ABBA - Elastix Registration (Spline)", 
    "mp=ch.epfl.biop.atlas.aligner.MultiSlicePositioner@3999e91 " + 
    "channels_atlas_csv=0 " + //0-nissl, 0-nissl
    "channels_slice_csv=3 " + //0-dapi,3-nissl
    "pixel_size_micrometer=20 " + //6um
    "show_imageplus_registration_result=false " + 
    "background_offset_value_moving=0.0 " + 
    "nb_control_points_x=20");
run("ABBA - Elastix Registration (Spline)", 
    "mp=ch.epfl.biop.atlas.aligner.MultiSlicePositioner@3999e91 " + 
    "channels_atlas_csv=0 " + //0-nissl, 0-nissl
    "channels_slice_csv=3 " + //0-dapi,3-nissl
    "pixel_size_micrometer=20 " + //6um
    "show_imageplus_registration_result=false " + 
    "background_offset_value_moving=0.0 " + 
    "nb_control_points_x=20");
    
// ATTENTION: after Deepslice, some slices will not me mathced with an atlas
	//this will lead all the following registration to give error.
	//Do not despair: just wait that everything is finished, clik ok on the messages of error
	//and remove manually the non-registered slices

// Manual: Manual correction "non si scappa..."

// Manual: Export Registartions to Qupath project

// ----- move to Quapth

