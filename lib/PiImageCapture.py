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

# ====== DEFAULT SETTINGS ======
#N = 16 # pixel w/h
#S = 2  # size of square that is scanned. NOTE: this should be proportional to the resolution, else it's darker at higher res.

base_path = '.'
folder_path_cali = f'{base_path}/patterns/Calibration'
data_path = f'{base_path}/data/pixels.npz'

I2CBUS = 1


SAMPLE_INTERVAL = 0.005
SAMPLES_PER_PIXEL = 1 # TODO Not yet re-implemented in the new sampler...

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
    The base class for storing the image.
    The strategy should  extend this class and implement its methods.
    """
    def store(self, output, dims, mask, title, stats, clipped):
        raise NotImplementedError


# ===
class PiImageCapture:
    def __init__(self, store: ImageStore):

        # DI of the image storage stratagey (e.g. npz file store, or pocketbase)
        self.store = store

        # Create a new board wrapper - note it has some settings which control the ADC chip config (sample speed etc)
        #pront("Connecting to the PiHat ...")
        self.board = PiHatSensor(I2CBUS)
        self.board.selfConfigure()
        #self.board.printConfig()

        # set up PyGame
        pygame.init()
 
        print("Capture ready")

    def dark(self):
        # show dark screen to avoid initial flash
        #pront("Show dark screen...")
        self.screen.fill((0, 0, 0))
        surface = pygame.image.load(os.path.join(self.folder_path,self.black_image)).convert()
        self.screen.blit(surface,(border,border))
        pygame.display.flip()
        
    async def configure(self, image_size, mask_pixel_size, mask_type="point"):
        # update the board config cache in case it the device has been reconfigured
        self.board.selfConfigure()

        print(f"Image capture configure... {image_size}, {mask_pixel_size}, {mask_type}")
        self.N = image_size
        self.S = mask_pixel_size
        self.mask_type = mask_type
        if mask_type == "point":
            self.folder_path = f'{base_path}/patterns/PixelScan_{self.S}x{self.S}_{self.N}x{self.N}'
        elif mask_type == "fourier":
            self.folder_path = f'{base_path}/patterns/fourier_p4_{self.N}'
        else:
            raise(f"PiImageCapture Error: unknown mask type {mask_type} should be 'point' or 'fourier'")
        self.black_image = 'black.png'
        
        # === MASK Load image files =======================================
        pront("Collecting mask files...")
        valid_exts = ('.jpg', '.jpeg', '.png', '.bmp')
        self.image_files = [os.path.join(self.folder_path, f)
                       for f in sorted(os.listdir(self.folder_path))
                       if f.lower().endswith(valid_exts) and f.lower() != self.black_image]
        
        # set up PyGame
        #resolution = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        resolution=(self.N, self.N) 
        self.screen = pygame.display.set_mode(resolution, pygame.SCALED | pygame.FULLSCREEN) # | pygame.RESIZABLE)
        pygame.display.set_caption("Camera Mascara")
        pygame.mouse.set_visible(False)

    async def run(self):
        print("Image capture starting...")
        #samples = []
        output0 = [] 
        clipped = 0 # 2 bit field
        self.board.resetStats()
       
        # swing low
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
            # No sleep is technically needed when using "ReadNewVoltage" as the ADC driver awaits data-ready flag.
            # but i measured it and a 0.060 sleep here reduces the data-ready await cycles (so less I2C commands), which felt better?
            #time.sleep(0.060)
            #pront("Done sleep")

            #pront("Sampling... %s"%(img_path))
            #sample = board.ADCReadVoltage()						                    	# OPTION: SINGLE SAMPLE
            #sample = board.ADCReadVoltageAverage(SAMPLES_PER_PIXEL, SAMPLE_INTERVAL)		# OPTION: Average
            [volts,clip] = self.board.ADCReadNewVoltage()	                                        	# OPTION: Await new data (single sample).Dont really need to sleep with this option
            #pront('  level=%0.4f %s'%(sample, img_path[-10:]))
            output0.append(volts)
            # Report clipping if it happensr, flag the image as clipped
            if clip == +1 and not(clipped & 2): clipped = clipped | 2
            if clip == -1 and not(clipped & 1): clipped = clipped | 1
 

        tEnd = time.time()
        self.dark()

        # === Cleanup
        # get overall stats, mean of all voltage sample stdvs, and the stdev of that mean. Indicates how noisy the signal was.
        #stdevs = board.getStdev()
        waitss = self.board.getWaits()
        cs = self.board.getConfigStruct()

        ts = datetime.now().isoformat(sep='_', timespec='seconds') 
        if self.mask_type == "point":
            title = f"PointScan_{ts}_{self.N}x{self.N}_{self.S}x{self.S}_WR_{SAMPLES_PER_PIXEL}SPP_{cs.PGA_value}PGA_{cs.SPS_value}SPS"
        elif self.mask_type == "fourier":
            title = f"Fourier_{ts}_{self.N}x{self.N}__WR_{SAMPLES_PER_PIXEL}SPP_{cs.PGA_value}PGA_{cs.SPS_value}SPS"
                                                  
        stats = 'Resol:%dx%d Pixel:%dx%d SPP:%d Wait:WR (mean wait:%0.4f s, stdev wait:%0.4f s) LVL-min:%0.4f max:%0.4f Took:%d s'%(self.N,self.N, self.S,self.S, SAMPLES_PER_PIXEL, waitss[1], waitss[2], np.min(output0), np.max(output0), tEnd-tStart)
        #stats = '  samples/pixel:%d interval:%.4f s (mean*stdev:%0.4f, stdev*stdev:%0.4f) min:%0.4f max:%0.4f took:%d s'%(SAMPLES_PER_PIXEL, SAMPLE_INTERVAL, stdevs[0], stdevs[1], np.min(output0), np.max(output0), tEnd-tStart))

        #print(output0)
        await self.store.store(np.array(output0), (self.N,self.N), self.mask_type, title, stats, clipped)
        # np.savez(data_path, output0=output0)

        print(stats)
        print("Image capture complete ----------------")

    def stop():
        # Close the serial connection to the Arduino
        self.board.shutdown()
        
