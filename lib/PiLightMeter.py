#!/usr/bin/python3

import os
import sys
import math
import time
import numpy as np
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import asyncio
from lib.PiHatSensor import PiHatSensor
from lib.Meters.PocketbaseBrightnessMeter import PocketbaseBrightnessMeter
from lib.Pocketbase.Connector import Connector

# ====== USER SETTINGS ======
folder_path = 'patterns/PixelScan_2x2_64x64'
black_image = 'black.png'

I2CBUS = 1

SAMPLE_INTERVAL = 0.001
SAMPLES_PER_PIXEL = 8
N = 64

t1 = time.time()
def pront(str):
	global t1
	t2 = time.time()
	print(	"%00.4f %s" % (t2 - t1, str))
	t1 = time.time()


class PiLightMeter:
    def __init__(self, meter ):
        self.output0 = []
        self.meter = meter


    # this class can be re-called over a long period so set up the job context outside the constructor
    async def configure(self, device):
        self.device = device
        
    async def run(self):
        print("LIGHT METER...")
        await self.meter.init()
        tStart = time.time()

        #pront("Connecting to the PiHat ...")
        # Create a new board wrapper - note it has some settings which control the ADC chip config (sample speed etc)
        self.board = PiHatSensor(I2CBUS)
        self.board.selfConfigure()
        self.board.printConfig()
        
        # Projector ----
        #pront("Setting up plotter...")
        # set up PyGame
        pygame.init()
        border = 0
        #resolution = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        resolution=(N,N)
        screen = pygame.display.set_mode(resolution, pygame.SCALED | pygame.FULLSCREEN) # | pygame.RESIZABLE)
        pygame.display.set_caption("Camera Mascara")
        # show dark screen 
        #pront("Show dark screen...")
        screen.fill((0, 0, 0))
        pygame.mouse.set_visible(False)
        #surface = pygame.image.load(os.path.join(folder_path,black_image)).convert()
        #screen.blit(surface,(border,border))
        #pygame.display.flip()
        
        # run for 30s (paupers stop-job)
        while(time.time() - tStart < 30):
            #time.sleep(0.25)

            #[voltage, sample]  = board.ADCReadVoltageWithData()						# OPTION: SINGLE SAMPLE
            [voltage, sample]  = self.board.ADCReadNewVoltageWithData()						# OPTION: SINGLE SAMPLE await NEW data
            #sample = board.ADCReadVoltageAverage(SAMPLES_PER_PIXEL, SAMPLE_INTERVAL)		# OPTION: Average
            #output0.append(sample)
            #pront('  vin=%0.4f code=%x %x conf=%x'%(voltage, sample[0],sample[1],sample[2],))
            await self.meter.record(self.device, voltage)


        # === Cleanup
        # get overall stats, mean of all voltage sample stdvs, and the stdev of that mean. Indicates how noisy the signal was.
        #stdevs = board.getStdev()
        # Close the serial connection to the Arduino
        self.board.shutdown()

