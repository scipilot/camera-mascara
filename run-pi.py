#!/usr/bin/python3
print("CAMERA MASCARA ESTA EMPESANDO...")

print("importing OS...")
import os
import sys
#import pyfirmata2
import time
print("importing Numpy...")
import numpy as np
print("importing PyGame...")
import pygame
#import matplotlib as mpl
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg
print("importing PiHatSensor...")
from lib.PiHatSensor import PiHatSensor
print("... imports")

# ====== USER SETTINGS ======
#folder_path = '/home/pip/CameraMascara/camera-mascara/patterns/PixelScan_1x1_4x4'
folder_path = '/home/pip/CameraMascara/camera-mascara/patterns/PixelScan_2x2_64x64'
#black_image = 'pixel_01.png'
black_image = 'pixel_0001.png'
folder_path_cali = '/home/pip/CameraMascara/camera-mascara/patterns/Calibration'
data_path = '/home/pip/CameraMascara/camera-mascara/data/pixels.npz'

# PORT = '/dev/cu.usbmodem101'
# PORT = pyfirmata2.Arduino.AUTODETECT
I2CBUS = 1

N = 64

# ===

brightness = 0.0
samples = []
output0 = []
# background0 = []

t1 = time.time()
def pront(str):
	global t1
	t2 = time.time()
	print(	"%s %s" % (t2 - t1, str))
	t1 = time.time()

# Callback function which is called whenever there is a change at the digital port.
def pinCallback(value):
    if value:
        print("Button up")
    else:
        print("Button down")

def myPrintCallback(data):
    global brightness
    brightness = data
    samples.append(data)
    print("brightness now:%f" % (brightness	))


pront("Connecting to the PiHat ...")

# Create a new board wrapper
board = PiHatSensor(I2CBUS)


# TODO convert these firmata settings to the PiHat class - sample speed, data callback
# default sampling interval is 19ms
#board.samplingOn(RATE)
#digital_0.register_callback(pinCallback)
#board.analog[0].register_callback(myPrintCallback)


# === MASK Load image files =======================================
pront("Collecting mask files...")
valid_exts = ('.jpg', '.jpeg', '.png', '.bmp')
image_files = [os.path.join(folder_path, f)
               for f in sorted(os.listdir(folder_path))
               if f.lower().endswith(valid_exts)]

pront("Setting up plotter...")

# set up PyGame
pygame.init()
border = 0
#h,w=480,640
#resolution = (pygame.display.Info().current_w, pygame.display.Info().current_h)
resolution=(N,N)
screen = pygame.display.set_mode(resolution, pygame.SCALED | pygame.FULLSCREEN) # | pygame.RESIZABLE)
pygame.display.set_caption("Camera Mascara")
#screen.fill((255, 255, 255))
surface = pygame.image.load(os.path.join(folder_path,black_image)).convert()
screen.blit(surface,(border,border))
pygame.display.flip()


# RETIRED Matplotlib 
#mpl.rcParams['toolbar'] = 'None'
#fig = plt.figure(facecolor='black')        # Set figure background to black
#ax = fig.add_subplot(111)                  # Create axes object
#ax.set_facecolor('black')                  # Set axes background to black
#
# try to target the projector on 2nd display (note move mouse there first)
#fig.canvas.manager.window.move(0,0)
#
#
#manager = plt.get_current_fig_manager()
#try:
#    manager.full_screen_toggle()
#except AttributeError:
#    try:
#        manager.window.showMaximized()
#    except:
#        pass
#
#plt.axis('off')


# Script -----------

pront("Show dark screen...")

# show dark screen to avoid initial flash
#img = mpimg.imread(os.path.join(folder_path,'pixel_0001.png'))
#plt.imshow(img, cmap='gray', vmin=0, vmax=1)
#plt.axis('off')
#plt.draw()
#plt.pause(3)
# time.sleep(5)

samples = []
totalSamplesPerLoop = []
totalWaits = 0

# Mask display synchronised loop
for img_path in image_files:
    # print ("loop>>")
    # LDR is super slow in low light can take 5seconds to settle from higher value!
    pront("Sampling... %s"%(img_path))

    sample = board.ADCReadVoltage()
    pront('tmp sample=%s'%(sample))
    myPrintCallback(sample)

    # Display next mask image (pixel)
    pront(f"Displaying: {img_path}")

    # MPL
    #img = mpimg.imread(img_path)
    #plt.imshow(img, cmap='gray', vmin=0, vmax=1)
    #plt.axis('off')
    #plt.draw()
    # Wait briefly before next image (or wait for a condition)
    #plt.pause(0.01)

    # PyGame
    surface = pygame.image.load(img_path).convert()
    screen.blit(surface,(border,border))
    pygame.display.flip()

    time.sleep(0.001)
    #plt.clf()
    pront("Done sleep")

    # Make sure we have a sample to prevent div/0 ; happens every 20-30 loops?
    if len(samples) == 0:
        pront ("awaiting samples...")
        time.sleep(0.01)
        totalWaits = totalWaits+1
    pront ("got %d samples after %d waits" % (len(samples), totalWaits))
    totalSamplesPerLoop.append(len(samples))

    if len(samples) > 0:
	    # avg all the samples taken so far (number can vary)
	    avg = sum(samples) / len(samples)
	    output0.append(avg)
	    #print("avg brightness stored: %s=%f" % (img_path, avg))
	    samples = []
    else:
        print("NO SAMPLES!")
        continue

    # Option: record the background level (inc projector brightness bleed)
    # img = mpimg.imread(os.path.join(folder_path_cali,'level_000.png'))
    # plt.imshow(img, cmap='gray', vmin=0, vmax=1)
    # plt.axis('off')
    # plt.draw()
    # plt.pause(.01)
    # plt.clf()
    # #
    # avg = sum(samples) / len(samples)
    # background0.append(avg)
    # samples = []

    # print ("loop<<")


# === Cleanup
#analogPrinter.stop()
#digital_0.enable_reporting()
#board.analog[0].disable_reporting()

#plt.close()

# Close the serial connection to the Arduino
board.shutdown()

print(output0)
np.savez(data_path, output0=output0)

print('Samples/pixel avg:%0.2f min:%d ma:x%d waits:%d'%(np.average(totalSamplesPerLoop), np.min(totalSamplesPerLoop), np.max(totalSamplesPerLoop), totalWaits))

# print(background0)
# print('BG samples len:%d avg:%0.2f, min:%d max:%d'%(len(background0), np.average(background0), np.min(background0), np.max(background0)))

#os.system( "say ooh" )
