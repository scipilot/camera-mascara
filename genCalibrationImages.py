# Purpose: Creates photosensor calibration images  - see calibrate.py

import numpy as np
import imageio
import os
import math


# Parameters
M = 64 # number of pixels to scan
R = 64 # Overall size of image
file_dir = "patterns/Calibration/" # where to save images

# Ensure the output directory exists
os.makedirs(file_dir, exist_ok=True)

# Number of images 
num_images = 256

# Create a blank MxM image template
blank_image = np.zeros((M, M), dtype=np.uint8)

for idx in range(0, num_images):
    # Create a copy of the blank image
    img = blank_image.copy()
    
    # Set the whole screen to the calibration value
    img[0:R, 0:M] = idx  

    filename = os.path.join(file_dir, f'level_{idx:0{3}d}.png')

    # Save the image
    imageio.imwrite(filename, img)
