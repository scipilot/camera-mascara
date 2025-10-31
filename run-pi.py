#!/usr/bin/python3
print("CAMERA MASCARA ESTA EMPESANDO...")

print("importing OS...")
import os
import sys
import math
import time
print("importing Numpy...")
import numpy as np
print("importing PyGame...")
import pygame
print("importing PiHatSensor...")
from lib.PiHatSensor import PiHatSensor
print("... imports")

# ====== USER SETTINGS ======
#folder_path = '/home/pip/CameraMascara/camera-mascara/patterns/PixelScan_1x1_4x4'
folder_path = '/home/pip/CameraMascara/camera-mascara/patterns/PixelScan_2x2_64x64'
#folder_path = '/home/pip/CameraMascara/camera-mascara/patterns/PixelScan_4x4_128x128'
#black_image = 'pixel_01.png'
black_image = 'pixel_0001.png'
#black_image = 'pixel_00001.png'
folder_path_cali = '/home/pip/CameraMascara/camera-mascara/patterns/Calibration'
data_path = '/home/pip/CameraMascara/camera-mascara/data/pixels.npz'

I2CBUS = 1

N = 64 # pixel w/h
S = 21  # size of square that is scanned. NOTE: this should be proportional to the resolution, else it's darker at higher res.

SAMPLE_INTERVAL = 0.005
SAMPLES_PER_PIXEL = 1

# ===

samples = []
output0 = []

t1 = time.time()
def pront(str):
	global t1
	t2 = time.time()
	print(	"%00.4f %s" % (t2 - t1, str))
	t1 = time.time()

# Callback function which is called whenever there is a change at the digital port.
#def pinCallback(value):
#    if value:
#        print("Button up")
#    else:
#        print("Button down")


pront("Connecting to the PiHat ...")

# Create a new board wrapper - note it has some settings which control the ADC chip config (sample speed etc)
board = PiHatSensor(I2CBUS)

# Generate option
# MASK generate images live =============================================

# Parameters
M = N # number of pixels to scan
R = N # Overall size of image
#S = 2 # size of square that is scanned. NOTE: this should be proportional to the resolution, else it's darker at higher res.

# Determine the starting point for the subregion
start_row = (M - R) // 2
start_col = (M - R) // 2

# Number of images and zero-padding digits
num_images = R * R
num_digits = math.ceil(math.log10(num_images + 1))

# Create a blank MxM image template
blank_image = np.zeros((M, M), dtype=np.uint8)


def genImage(idx):
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

    # Save the image
    #imageio.imwrite(filename, img)

    return img

# File option
# === MASK Load image files =======================================
pront("Collecting mask files...")
valid_exts = ('.jpg', '.jpeg', '.png', '.bmp')
image_files = [os.path.join(folder_path, f)
               for f in sorted(os.listdir(folder_path))
               if f.lower().endswith(valid_exts)]

# Projector ----
pront("Setting up plotter...")

# set up PyGame
pygame.init()
border = 0
#resolution = (pygame.display.Info().current_w, pygame.display.Info().current_h)
resolution=(N,N)
screen = pygame.display.set_mode(resolution, pygame.SCALED | pygame.FULLSCREEN) # | pygame.RESIZABLE)
pygame.display.set_caption("Camera Mascara")

# show dark screen to avoid initial flash
pront("Show dark screen...")
screen.fill((0, 0, 0))
pygame.mouse.set_visible(False)
surface = pygame.image.load(os.path.join(folder_path,black_image)).convert()
screen.blit(surface,(border,border))
pygame.display.flip()


# Script -----------

time.sleep(1)

#samples = []
#totalSamplesPerLoop = []
#totalWaits = 0
tStart = time.time()

# Mask display synchronised loop
for img_path in image_files:				# File option
#for idx in range(1, num_images + 1):			# Generator option

    # Display next mask image (pixel)
    #pront(f"Displaying: {img_path}")
    #pront(f"Show: {idx}")

    # PyGame
    #buffer = genImage(idx)				# Generator option
    #pront(f"Gend: {idx}")
    #surface = pygame.surfarray.make_surface(buffer)
    #surface = pygame.image.frombuffer(buffer, resolution, 'P') #doesn't work
    surface = pygame.image.load(img_path).convert() 	# File option
    #pront(f"made: {idx}")
    screen.blit(surface,(border,border))
    #pront(f"blitted: {idx}")
    pygame.display.flip()				# flip is slow on large screen resolutions!
    #pront(f"flipped: {idx}")

    time.sleep(0.060)
    #pront("Done sleep")

    #pront("Sampling... %s"%(img_path))
    #sample = board.ADCReadVoltage()						                    	# OPTION: SINGLE SAMPLE
    #sample = board.ADCReadVoltageAverage(SAMPLES_PER_PIXEL, SAMPLE_INTERVAL)		# OPTION: Average
    sample = board.ADCReadNewVoltage()	                                        	# OPTION: Await new data (single sample)
    #pront('  level=%0.4f %s'%(sample, img_path[-10:]))
    #myPrintCallback(sample)
    output0.append(sample)

tEnd = time.time()

# === Cleanup
# get overall stats, mean of all voltage sample stdvs, and the stdev of that mean. Indicates how noisy the signal was.
#stdevs = board.getStdev()
waitss = board.getWaits()
# Close the serial connection to the Arduino
board.shutdown()

#print(output0)
np.savez(data_path, output0=output0)

print('Samples/pixel:%d  (mean wait:%0.4f, stdev wait:%0.4f) min:%0.4f max:%0.4f took:%d s'%(SAMPLES_PER_PIXEL, waitss[1], waitss[2], np.min(output0), np.max(output0), tEnd-tStart))
#print('Samples/pixel:%d interval:%.4f s (mean*stdev:%0.4f, stdev*stdev:%0.4f) min:%0.4f max:%0.4f took:%d s'%(SAMPLES_PER_PIXEL, SAMPLE_INTERVAL, stdevs[0], stdevs[1], np.min(output0), np.max(output0), tEnd-tStart))
