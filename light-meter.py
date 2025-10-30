#!/usr/bin/python3
print("LIGHT METER...")

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
folder_path = '/home/pip/CameraMascara/camera-mascara/patterns/PixelScan_2x2_64x64'
black_image = 'pixel_0001.png'
data_path = '/home/pip/CameraMascara/camera-mascara/data/pixels.npz'

I2CBUS = 1

N = 64 # pixel w/h

SAMPLE_INTERVAL = 0.001
SAMPLES_PER_PIXEL = 8

# ===

output0 = []

t1 = time.time()
def pront(str):
	global t1
	t2 = time.time()
	print(	"%00.4f %s" % (t2 - t1, str))
	t1 = time.time()

pront("Connecting to the PiHat ...")

# Create a new board wrapper - note it has some settings which control the ADC chip config (sample speed etc)
board = PiHatSensor(I2CBUS)
board.printConfig()

# Projector ----
pront("Setting up plotter...")

# set up PyGame
pygame.init()
border = 0
#resolution = (pygame.display.Info().current_w, pygame.display.Info().current_h)
resolution=(N,N)
screen = pygame.display.set_mode(resolution, pygame.SCALED | pygame.FULLSCREEN) # | pygame.RESIZABLE)
pygame.display.set_caption("Camera Mascara")

# show dark screen 
pront("Show dark screen...")
screen.fill((0, 0, 0))
pygame.mouse.set_visible(False)
#surface = pygame.image.load(os.path.join(folder_path,black_image)).convert()
#screen.blit(surface,(border,border))
#pygame.display.flip()


# Script -----------

while(True):
    time.sleep(0.5)

    [voltage, sample]  = board.ADCReadVoltageWithData()						# OPTION: SINGLE SAMPLE
    #sample = board.ADCReadVoltageAverage(SAMPLES_PER_PIXEL, SAMPLE_INTERVAL)		# OPTION: Average
    #output0.append(sample)
    pront('  vin=%0.4f code=%x %x conf=%x'%(voltage, sample[0],sample[1],sample[2],))


# === Cleanup
# get overall stats, mean of all voltage sample stdvs, and the stdev of that mean. Indicates how noisy the signal was.
stdevs = board.getStdev()
# Close the serial connection to the Arduino
board.shutdown()

#print(output0)
#np.savez(data_path, output0=output0)

print('Samples/pixel:%d interval:%f s (mean*stdev:%0.4f, stdev*stdev:%0.4f) min:%0.4f max:%0.4f'%(SAMPLES_PER_PIXEL, SAMPLE_INTERVAL, stdevs[0], stdevs[1], np.min(output0), np.max(output0)))
