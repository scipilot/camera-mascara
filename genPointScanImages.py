# Purpose - this generates the mask images for the single-pixel or point-scan method.
# you need to set the options below, and it will save to to an naming convention folder
# which the scanner script will also calculate when this resolution combo is requested.
# So you need to run this script before trying to scan at that resolution combo.
# Note higher resolution makes the single pixel relatively smaller, so you might want a bigger one.
# TODO: Integrate this with the API and/or do on-demand generation when a combo is not found.

import numpy as np
import imageio
import os
import math

# Parameters
M = 64 # number of pixels to scan
R = 64 # Overall size of image
S = 31  # size of square that is scanned. NOTE: this should be proportional to the resolution, else it's darker at higher res. An odd number is better for gaussian.
shape = 'gaussian' # 'square' | 'gaussian'
file_dir = "patterns/PointScan_%dx%d_%dx%d_%s/" % (S,S,M,R,shape) # where to save images

# Ensure the output directory exists
os.makedirs(file_dir, exist_ok=True)

# Determine the starting point for the subregion
start_row = ( R - M) // 2
start_col = ( R - M) // 2

# Number of images and zero-padding digits
num_images = R * R
num_digits = math.ceil(math.log10(num_images + 1))

# Create a blank MxM image template
blank_image = np.zeros((M, M), dtype=np.uint8)

# Creates a gaussian 2D array
def gkernel(l=3, sig=2):
    """\
    Gaussian Kernel Creator via given length and sigma
    """
    ax = np.linspace(-(l - 1) / 2., (l - 1) / 2., l)
    xx, yy = np.meshgrid(ax, ax)

    kernel = np.exp(-0.5 * (np.square(xx) + np.square(yy)) / np.square(sig))

    return kernel / np.sum(kernel)

if shape == 'gaussian':
    # it seems the "sig" parameter needs to be increased slightly with the general size of the image/point.
    # Good settings:- S=9: 1, S=100: 3,
    gaussian_2d = gkernel(S, 2)
    gaussian_2d = gaussian_2d * 255 / np.max(gaussian_2d)
    #print(gaussian_2d)
    mofl = -int(np.floor(S/2))
    mofr = -mofl # needs adjusting + 1 for even mask?

for idx in range(1, num_images + 1):
    # Create a copy of the blank image
    img = blank_image.copy()
    
    # Calculate row and column indices within the subregion
    sub_row = (idx - 1) // R
    sub_col = (idx - 1) % R

    # Determine absolute row and column positions
    x = start_row + sub_row
    y = start_col + sub_col

    # Turn on the SxS pixel square
    if shape == 'square':
        # Adjust the square size if near the image boundary
        row_end = min(x + S, M)
        col_end = min(y + S, M)
        
        # Use 255 for white pixels
        img[row:row_end, col:col_end] = 255
        
    elif shape == 'gaussian':
        # shift gaussian up/left by half of size, and "broadcast" the edge-clipped mask into the offset image location
        ix1 = max(x + mofl, 0)
        ix2 = min(x + mofr, R)
        mx1 = ix1 - (x + mofl)
        mx2 = S + ix2 - (x + mofr) - 1
        iy1 = max(y + mofl, 0)
        iy2 = min(y + mofr, R)
        my1 = iy1 - (y + mofl)
        my2 = S + iy2 - (y + mofr) - 1
        #print(f"{x=} {y=} {ix1=} {ix2=} {mx1=} {mx2=}  {iy1=} {iy2=} {my1=} {my2=}")
        img[ix1:ix2, iy1:iy2] = gaussian_2d[mx1:mx2, my1:my2]

    # Zero-pad the filename
    filename = os.path.join(file_dir, f'pixel_{idx:0{num_digits}d}.png')

    # Save the image
    imageio.imwrite(filename, img)

# Also write out a black image for preparing the sensor
    filename = os.path.join(file_dir, f'black.png')
    imageio.imwrite(filename, blank_image)

