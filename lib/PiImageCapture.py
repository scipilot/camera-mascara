#!/usr/bin/python3

import os
import sys
import math
import time
from datetime import datetime
import numpy as np
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from lib.PiHatSensor import PiHatSensor

# ====== USER SETTINGS ======
N = 16 # pixel w/h
S = 2  # size of square that is scanned. NOTE: this should be proportional to the resolution, else it's darker at higher res.

folder_path = f'/home/pip/CameraMascara/camera-mascara/patterns/PixelScan_{S}x{S}_{N}x{N}'
black_image = 'black.png'

#folder_path = '/home/pip/CameraMascara/camera-mascara/patterns/PixelScan_1x1_4x4'
#black_image = 'pixel_01.png'
#folder_path = '/home/pip/CameraMascara/camera-mascara/patterns/PixelScan_2x2_16x16'
#black_image = 'pixel_001.png'
#folder_path = '/home/pip/CameraMascara/camera-mascara/patterns/PixelScan_2x2_64x64'
#black_image = 'pixel_0001.png'
#folder_path = '/home/pip/CameraMascara/camera-mascara/patterns/PixelScan_4x4_128x128'
#black_image = 'pixel_00001.png'
folder_path_cali = '/home/pip/CameraMascara/camera-mascara/patterns/Calibration'
data_path = '/home/pip/CameraMascara/camera-mascara/data/pixels.npz'

I2CBUS = 1


SAMPLE_INTERVAL = 0.005
SAMPLES_PER_PIXEL = 1

border = 0

t1 = time.time()
def pront(str):
	global t1
	t2 = time.time()
	print(	"%00.4f %s" % (t2 - t1, str))
	t1 = time.time()

# DI  interfaxce 
class ImageStore():
    """
    The base class for accessing a user's information.
    The client must extend this class and implement its methods.
    """
    def store(self, title):
        raise NotImplementedError


# ===
class PiImageCapture:
    def __init__(self, store: ImageStore):

        # DI of the image storage stratagey (e.g. npz file store, or pocketbase)
        self.store = store

        # Create a new board wrapper - note it has some settings which control the ADC chip config (sample speed etc)
        pront("Connecting to the PiHat ...")
        self.board = PiHatSensor(I2CBUS)

        # File option
        # === MASK Load image files =======================================
        pront("Collecting mask files...")
        valid_exts = ('.jpg', '.jpeg', '.png', '.bmp')
        self.image_files = [os.path.join(folder_path, f)
                       for f in sorted(os.listdir(folder_path))
                       if f.lower().endswith(valid_exts) and f.lower() != black_image]

        # Projector ----
        pront("Setting up plotter...")

        # set up PyGame
        pygame.init()
        #resolution = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        resolution=(N,N)
        self.screen = pygame.display.set_mode(resolution, pygame.SCALED | pygame.FULLSCREEN) # | pygame.RESIZABLE)
        pygame.display.set_caption("Camera Mascara")
        pygame.mouse.set_visible(False)
        print("Capture ready")

    def dark(self):
        # show dark screen to avoid initial flash
        #pront("Show dark screen...")
        self.screen.fill((0, 0, 0))
        surface = pygame.image.load(os.path.join(folder_path,black_image)).convert()
        self.screen.blit(surface,(border,border))
        pygame.display.flip()
        
    async def run(self):
        print("Image capture starting...")
        #samples = []
        output0 = []    
        
        self.dark()
        time.sleep(1)

        tStart = time.time()

        # Mask display synchronised loop
        for img_path in self.image_files:				# File option
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
            self.screen.blit(surface,(border,border))
            #pront(f"blitted: {idx}")
            pygame.display.flip()				# flip is slow on large screen resolutions! so set the desktop to 640x480
            #pront(f"flipped: {idx}")

            # At 15SPS is 0.066s fastest possible case, so sleep for 60 as the code takes some time anyway (tune via the stats)
            time.sleep(0.060)
            #pront("Done sleep")

            #pront("Sampling... %s"%(img_path))
            #sample = board.ADCReadVoltage()						                    	# OPTION: SINGLE SAMPLE
            #sample = board.ADCReadVoltageAverage(SAMPLES_PER_PIXEL, SAMPLE_INTERVAL)		# OPTION: Average
            sample = self.board.ADCReadNewVoltage()	                                        	# OPTION: Await new data (single sample)
            #pront('  level=%0.4f %s'%(sample, img_path[-10:]))
            output0.append(sample)

        
        self.dark()
        tEnd = time.time()

        # === Cleanup
        # get overall stats, mean of all voltage sample stdvs, and the stdev of that mean. Indicates how noisy the signal was.
        #stdevs = board.getStdev()
        waitss = self.board.getWaits()

        ts = datetime.now().isoformat(sep='_', timespec='seconds') 
        title = f"PointScan_{ts}_{N}x{N}_WR_{SAMPLES_PER_PIXEL}SPP"
                                                  
        stats = ' Res:{N}x{N} SPP:%d wait:WR (mean wait:%0.4f, stdev wait:%0.4f) min:%0.4f max:%0.4f took:%d s'%(SAMPLES_PER_PIXEL, waitss[1], waitss[2], np.min(output0), np.max(output0), tEnd-tStart)
        #stats = '  samples/pixel:%d interval:%.4f s (mean*stdev:%0.4f, stdev*stdev:%0.4f) min:%0.4f max:%0.4f took:%d s'%(SAMPLES_PER_PIXEL, SAMPLE_INTERVAL, stdevs[0], stdevs[1], np.min(output0), np.max(output0), tEnd-tStart))
        #print(output0)
        await self.store.store(np.array(output0), (N,N), title, stats)
        # np.savez(data_path, output0=output0)

        print(stats)
        print("Image capture complete ----------------")

    def stop():
        # Close the serial connection to the Arduino
        self.board.shutdown()
        
