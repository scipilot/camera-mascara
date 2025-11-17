import numpy as np
import imageio
import os
import math

# Parameters
M = 32  # number of pixels to scan
R = 32  # Overall size of image
S = 2   # size of square that is scanned. NOTE: this should be proportional to the resolution, else it's darker at higher res.
file_dir = "patterns/PixelScan_%dx%d_%dx%d/" % (S,S,M,R) # where to save images

# Ensure the output directory exists
os.makedirs(file_dir, exist_ok=True)

# Determine the starting point for the subregion
start_row = (M - R) // 2
start_col = (M - R) // 2

# Number of images and zero-padding digits
num_images = R * R
num_digits = math.ceil(math.log10(num_images + 1))

# Create a blank MxM image template
blank_image = np.zeros((M, M), dtype=np.uint8)

for idx in range(1, num_images + 1):
    # Create a copy of the blank image
    img = blank_image.copy()
    
    # Calculate row and column indices within the subregion
    sub_row = (idx - 1) // R
    sub_col = (idx - 1) % R

    # Determine absolute row and column positions
    row = start_row + sub_row
    col = start_col + sub_col

    # Adjust the square size if near the image boundary
    row_end = min(row + S, M)
    col_end = min(col + S, M)

    # Turn on the SxS pixel square
    img[row:row_end, col:col_end] = 255  # Use 255 for white pixels

    # Zero-pad the filename
    filename = os.path.join(file_dir, f'pixel_{idx:0{num_digits}d}.png')

    # Save the image
    imageio.imwrite(filename, img)

# Also write out a black image for preparing the sensor
    filename = os.path.join(file_dir, f'black.png')
    imageio.imwrite(filename, blank_image)

