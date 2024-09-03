package ch.epfl.bio410;

import net.imagej.ImageJ;
import org.apache.commons.io.FileUtils;
import org.scijava.command.Command;
import org.scijava.plugin.Plugin;
import ij.IJ;
import ij.ImagePlus;
import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URL;
import java.nio.file.Paths;


@Plugin(type = Command.class, menuPath = "Plugins>BII>SSPD")
public class CorrectFocusAndNormalization implements Command {

	public static File copyFileFromResources(String pathFromResourcesFolder){
		//function get the file that in the "resources" folder

		// get the URL of the file inside the jar
		URL url = CorrectFocusAndNormalization.class.getClassLoader().getResource(pathFromResourcesFolder);

		if(url != null) {
			// get the temporary location where to copy the file
			String outputPath = System.getProperty("user.home") + File.separator + "Downloads";

			// create the new file in the temporary location
			File outputFile = new File(outputPath + File.separator + pathFromResourcesFolder);

			// copy the file
			try {
				FileUtils.copyURLToFile(url, outputFile);
			}catch (IOException e){
				IJ.log("ERROR -- Cannot copy the file '"+url.getPath()+"' to '" +outputFile.getAbsolutePath()+"'");
				return null;
			}

			return outputFile;
		}
		return null;
	}

	@Override
	public void run(){

		//////////////////////////////////////////////////////////////////////////
		// PARAMETERS: CHANGE FREQUENTLY
		String path_original_image ="/run/user/1000/gvfs/smb-share:server=upcourtinenas,share=cervical/CERVICAL_ID/Gabriele/589_comparaison/tiffs/589_FB_1B_01.vsi-10x_03.tif"; // "/home/gabri/Desktop/test_abba/587_automated/easy_dots.tif"; //Image to analyz
		// /run/user/1000/gvfs/smb-share:server=upcourtinenas,share=cervical/CERVICAL_ID/Gabriele/594_cell_detection/tiffs/594_HB_1B_01_reverse.vsi-10x_01_res_2.0.tif

		// PARAMETERS: CHANGE ONCE
		String python_exe_path = "/home/gabri/mambaforge/envs/napari-env/bin/python3.1"; //Path to the .exe python, inside the VE
		String spotiflow_script_path = copyFileFromResources("spotiflow_binary.py").toString();
		String macroFilePath = copyFileFromResources("cell_macro.ijm").toString(); // Path to macro file
		String csv_script_path = copyFileFromResources("csv_merge.py").toString();
		//String pythonEnvDir = "/home/gabri/mambaforge/envs/napari-env";

		// PARAMETERS: CHANGE OUTOMATICALLY

		// extract the name of the original image
		File file = new File(path_original_image);
		String name_original = file.getName();
		if (name_original.endsWith(".tif")) {
			name_original = name_original.substring(0, name_original.length() - 4);
		}

		//exctract the name of the folfer that contaisn the original file
		String dir_original = file.getParent();
			//String dir_original = new File(parentPath).getName(); #this gives only the name of the parent folder

		//path where to save the result of spotiflow
		String path_spotiflow_processed_image = dir_original + "/" + name_original + "_processed.tif";

		//path folder where to save temp files of cell_crunch.ijm
		String folder_temp_macro = dir_original + "/temp_macro";

		//Path final csv file
		String path_final_csv = dir_original + "/" + name_original + ".csv";

		//////////////////////////////////////////////////////////////////////////
		// MAKE SURE THAT THERE ARE NO FILE WITH SPACES INSIDE --> otherwise remove them
		// Get list of files in the folder
		File folder = new File(dir_original);
		File[] files = folder.listFiles();

		// Loop through each file in the folder
		if (files != null) {
			for (File f : files) {
				if (f.isFile()) {
					String fileName = f.getName();

					// Check if file name contains spaces
					if (fileName.contains(" ")) {
						// Replace spaces with underscores
						String newFileName = fileName.replaceAll(" ", "");

						// Construct new file path
						String newFilePath = dir_original + File.separator + newFileName;

						// Rename the file
						if (f.renameTo(new File(newFilePath))) {
							//IJ.log("Renamed: " + fileName + " -> " + newFileName);
						} else {
							//IJ.log("Failed to rename: " + fileName);
						}
					} else {
						//IJ.log("Skipped (no spaces): " + fileName);
					}
				}
			}
			//IJ.log("Batch renaming completed.");
		}

		//////////////////////////////////////////////////////////////////////////
		// OPEN IMAGE
		ImagePlus original_image = IJ.openImage(path_original_image); //Open Original Image
		original_image.setTitle("original_image");
		original_image.show(); //Show Original Image

		//////////////////////////////////////////////////////////////////////////
		// RUN PYTHON SCRIPT: "spotiflow_binary.py"
			//From Brain image --> Detect Spots with Spotiflow --> Create Binary Image

		//depending on the OS the location of the .exe python has to be adapted
		//String os = System.getProperty("os.name");
		//if(os.charAt(0) == 'W'){python_exe_path = Paths.get(pythonEnvDir, "python").toString();}
		//else{python_exe_path = Paths.get(pythonEnvDir, "bin/python3.9").toString();}

		// String that contains the command to run
		String command = python_exe_path + " " + spotiflow_script_path + " " + path_original_image + " " + path_spotiflow_processed_image;

		try {
			Process p = Runtime.getRuntime().exec(command); //run the command

			//Read output directly using InputStreamReader
			InputStreamReader reader = new InputStreamReader(p.getInputStream());
			BufferedReader buffer = new BufferedReader(reader);
			String line;
			while ((line = buffer.readLine()) != null) {
				System.out.println(line);
				//IJ.log(line);
			}
			buffer.close();
			reader.close();

			// Capture error output
			BufferedReader stdError = new BufferedReader(new InputStreamReader(p.getErrorStream()));
			String error;
			while ((error = stdError.readLine()) != null) {
				System.out.println("Python Error: " + error);
			}
			// Wait for process to complete
			int exitCode = p.waitFor();
			if (exitCode == 0) {
				System.out.println("Python script executed successfully.");
			} else {
				System.out.println("Error executing Python script. Exit code: " + exitCode);
			}

		} catch (IOException | InterruptedException e) {
			e.printStackTrace();
		}

		//////////////////////////////////////////////////////////////////////////
		// 	PREPARE BINARY IMAGE OF DOTS TO NEXT STEP
			//Open it --> Overlay the ROI from original image

		System.out.println("Putting ROIs on binary image and saving....");

		ImagePlus spotiflow_binary_image = IJ.openImage(path_spotiflow_processed_image);
		if(spotiflow_binary_image == null){
			System.out.println("Spotiflow Image was not created!!!");
		}
		spotiflow_binary_image.setTitle("spotiflow_binary_image");
		spotiflow_binary_image.show(); //Show Original Image

		//Send to roi manager the ROIs/Overlay of the original image
		IJ.run(original_image, "To ROI Manager", "");

		//Add ROIs to the processed image by Spotiflow
		IJ.run(spotiflow_binary_image,"From ROI Manager", "");

		// Save Image with overlay
		IJ.saveAs(spotiflow_binary_image, "Tiff", path_spotiflow_processed_image); //ATTENTION: I am overwriting the image

		original_image.close(); //No more necessary
		spotiflow_binary_image.close(); //No more necessary

		//////////////////////////////////////////////////////////////////////////
		// RUN MACRO SCRIPT: "cell_macro.ijm"
			// Open binary image with overlay --> For each ROI counts how many dots inside --> save csv files in temp folder

		System.out.println("Counting how many dots per ROI...");

		// Create the argument string
		String arguments = path_spotiflow_processed_image + " " + folder_temp_macro; // " " between imputs bacuse specified by cell_macro

		// Run the macro file with arguments
		IJ.runMacroFile(macroFilePath, arguments);

		//////////////////////////////////////////////////////////////////////////
		// RUN PYTHON FILE: "csv_merge.py"
			// Join all the csv file created in the past macro comman in one sigle and useful csv --> delete also temp folder
			//NB impossible to create direclty only one csv file

		//python .exe already specified before

		System.out.println("Creating final csv...");

		// String that contains the command to run
		command = python_exe_path + " " + csv_script_path + " " + folder_temp_macro + " " + path_final_csv ;

		try {
			Process p = Runtime.getRuntime().exec(command); //run the command

			//Read output directly using InputStreamReader
			InputStreamReader reader = new InputStreamReader(p.getInputStream());
			BufferedReader buffer = new BufferedReader(reader);
			String line;
			while ((line = buffer.readLine()) != null) {
				System.out.println(line);
				//IJ.log(line);
			}
			buffer.close();
			reader.close();

			// Capture error output
			BufferedReader stdError = new BufferedReader(new InputStreamReader(p.getErrorStream()));
			String error;
			while ((error = stdError.readLine()) != null) {
				System.out.println("Python Error: " + error);
			}
			// Wait for process to complete
			int exitCode = p.waitFor();
			if (exitCode == 0) {
				System.out.println("Python script executed successfully.");
			} else {
				System.out.println("Error executing Python script. Exit code: " + exitCode);
			}

		} catch (IOException | InterruptedException e) {
			e.printStackTrace();
		}

		/////////////////////////////////////////////////////////////
		// CLEAR FIJI
		IJ.run("Clear Results");

		System.out.println("\nImage " + name_original + " has been processed.\n");
	}

	/**
	 * This main function serves for development purposes.
	 * It allows you to run the plugin immediately out of
	 * your integrated development environment (IDE).
	 *
	 * @param args whatever, it's ignored
	 * @throws Exception
	 */
	public static void main(final String... args) throws Exception {
		final ImageJ ij = new ImageJ();
		//ij.ui().showUI();
		// Running the plugin manually for testing purposes
		ij.command().run(CorrectFocusAndNormalization.class, true);
	}

}