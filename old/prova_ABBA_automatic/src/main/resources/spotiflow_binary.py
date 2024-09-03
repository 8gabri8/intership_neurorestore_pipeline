import napari
import numpy as np
import pandas as pd
from skimage.io import imread, imsave
from spotiflow.model import Spotiflow
import sys
import tifffile #pip install tifffile

# Function to load an image and return it along with its shape
def load_image(image_path):
    #image = imread(image_path)
    image = tifffile.imread(image_path)
    return image, image.shape

# Function to read CSV file and get coordinates
#def read_coordinates(csv_path):
#    df = pd.read_csv(csv_path)
#    return df['axis-0'].astype(int).values, df['axis-1'].astype(int).values

# Function to put white pixels on image B based on coordinates
def put_white_pixels(image, coords):
    for coord in coords:
        x, y = int(coord[0]), int(coord[1])
        image[x, y] = 255  # Assuming the coordinates are (x, y)
    return image

# Main function
def main():

    image_path = sys.argv[1] #image to find the spots within
    output_path = sys.argv[2] #path where to save the final image

    # Load image A (the one to find the spots within)
    print("Loading Image...")
    image_A, shape = load_image(image_path)

    # Maybe improve the contrast????
    # TODO
    # TODO

    # Load a pretrained model
    model = Spotiflow.from_pretrained("general")

    # Predict
    print("Running Spotiflow...")
    n_tiles = tuple(max(1,s//1024) for s in image_A.shape)
    coords, details = model.predict(image_A, n_tiles=n_tiles)

    # Create black image B with the same dimensions as image A
    print("Creating Binary Image...")
    image_B = np.zeros(shape, dtype=np.uint8)

    # Put white pixels in image B
    image_B = put_white_pixels(image_B, coords)

    # Ensure the image is binary
    image_B = (image_B > 0).astype(np.uint8) * 255

    # Save the modified image B as a TIFF file
    print("Saving Binary Image...")
    #imsave(output_path, image_B)
    tifffile.imsave(output_path, image_B)

    # Save csv with points
    points_df = pd.DataFrame(coords, columns=['y', 'x']) #Attention order should be like this
    points_df.to_csv(output_path + '_points_layer.csv', index=False)

    # Start Napari viewer
    #viewer = napari.Viewer()
    #viewer.add_image(image_A, name='Image A')
    #viewer.add_image(image_B, name='Image B')
    #napari.run()

# Example usage
#image_path = '/home/gabri/Desktop/test_abba/587/midbrain_587_HB_2B_01_reverse.vsi - 10x_03.tif'  # Update this path
#image_path = '/home/gabri/Desktop/test_abba/587/easy_dots.tif'
#csv_path = '/home/gabri/Desktop/test_abba/587/points_spotiflow_midbrain.csv'  # Update this path
#output_path = '/home/gabri/Desktop/test_abba/587/binary_points_midbrian.tif'  # Update this path

if __name__ == "__main__":
    main()
