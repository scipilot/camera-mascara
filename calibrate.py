#!/usr/bin/python3

# Purpose: this script can be used to record the output level of the sensor across a range of brightness levels.
# It shows a sequence of (256) images from black to white and records the voltage output.
# This can be plotted to view a response graph to check for linearity, clipping, range etc.
# while you vary other parameters like bias, feeback, amplification, offsets etc.
#
# It targetted the "phase 1" Arduino and has not yet been evovled to the Pi version!

import os
import sys
import pyfirmata2
import time
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from tkinter import Tk 

# ====== USER SETTINGS ======
folder_path = 'patterns/Calibration'

# PORT = '/dev/cu.usbmodem101'
PORT = pyfirmata2.Arduino.AUTODETECT

N = 64

# === vars
brightness = 0.0
samples = []
output0 = []
started = False


# Callback function which is called whenever there is a change at the digital port.
def pinCallback(value):
    global started
    
    if value:
        print("Button up")
    else:
        print("Button down")
        started = True
    
def myPrintCallback(data):
    global brightness	
    #print(data)
    brightness = data
    samples.append(data)
    #print("brightness now:%f" % (brightness	))
    # I found I had to keep re-enabling the DAC else it only gives one number
    board.analog[0].enable_reporting()


print("Setting up Arduino support ...")

# Creates a new board
try:
    board = pyfirmata2.Arduino(PORT)
except:
    sys.exit("Failed to connect to Arduino on port %s - Is the Arduino plugged in?" % (PORT))    

print("Connecting to the Arduino ...")

# default sampling interval is 19ms
board.samplingOn()

print("Setting up Arduino pins ...")

# Setup the digital pin with pull-up resistor: "u"
digital_0 = board.get_pin('d:3:u')
digital_0.register_callback(pinCallback)
digital_0.enable_reporting()


## Analogue setup -------

board.analog[0].register_callback(myPrintCallback)
board.analog[0].enable_reporting()



class AnalogPrinter:

    def __init__(self, board):
        self.samplingRate = 1
        self.timestamp = 0
        self.board = board 		# pyfirmata2.Arduino(PORT)

    def start(self):
        print("Starting ADC...")
        self.board.analog[0].register_callback(self.myPrintCallback)
        self.board.samplingOn(1000 / self.samplingRate)
        self.board.analog[0].enable_reporting()

    def myPrintCallback(self, data):
        print("%f,%f" % (self.timestamp, data))
        self.timestamp += (1 / self.samplingRate)

    def stop(self):
        print("Stopping ADC")
        self.board.analog[0].disable_reporting()
        # done globally: self.board.exit()


# analogPrinter = AnalogPrinter(board)
# analogPrinter.start()

print("Setting up image files ...")

# === MASK Load image files =======================================
valid_exts = ('.jpg', '.jpeg', '.png', '.bmp')
image_files = [os.path.join(folder_path, f)
               for f in sorted(os.listdir(folder_path))
               if f.lower().endswith(valid_exts)]

print("Setting up display ...")

mpl.rcParams['toolbar'] = 'None'
fig = plt.figure(facecolor='black')        # Set figure background to black
ax = fig.add_subplot(111)                  # Create axes object
ax.set_facecolor('black')                  # Set axes background to black

# try to target the projector on 2nd display (note move mouse there first)
#fig.canvas.manager.window.move(0,0)

manager = plt.get_current_fig_manager()
try:
    manager.full_screen_toggle()
except AttributeError:
    try:
        manager.window.showMaximized()
    except:
        pass

# Show dark screen first, to avoid flash on first images (note it needed the pause and clf too)
print(f"Pre-Darkening Displaying: {image_files[0]}")
img = mpimg.imread(image_files[0])
plt.imshow(img, cmap='gray', vmin=0, vmax=1)
plt.axis('off')
plt.draw()
plt.pause(1)
# time.sleep(0.01)
# plt.clf()
samples = []

print("Ready, press the START button (on the board) to start ...")
# print('\a') does a termainal beep but it flashes the dock icon :(
# print('\a')
# mac specific
os.system( "say go" )

# wait for pin callback
# Note: Matplotlib cannot be started in the callback thread - must be in the main script, I want this all in functions... :(
while not started:
    time.sleep(0.05)


# main routine
print(f"Calibrating...")

# Mask display synchronised loop
for img_path in image_files:
    time.sleep(.002)
    # Display next mask image (pixel)
    # print(f"Displaying: {img_path}")
    img = mpimg.imread(img_path)
    plt.imshow(img, cmap='gray', vmin=0, vmax=1)
    plt.axis('off')
    plt.draw()
    plt.pause(0.001)

    # avg all the samples taken so far (number can vary)
    avg = sum(samples) / len(samples)
    samples = []
    output0.append(avg)
    print("%s:%f" % (img_path, avg))

    # Wait briefly before next image (or wait for a condition)
    # time.sleep(0.5)
    plt.clf()


# === Cleanup
#analogPrinter.stop()
digital_0.enable_reporting()
board.analog[0].disable_reporting()

plt.close()

# Close the serial connection to the Arduino
board.exit()

# print(output0)
np.savez('data/calibration.npz', output0=output0)

# copy to clipboard
def toclip(str):
    r = Tk()
    # r.withdraw()
    # r.clipboard_clear()
    # r.clipboard_append(str)
    # r.update() # now it stays on the clipboard after the window is closed
    # r.destroy()

i = 0
clippy = ''
for pair in output0:
    print("%f,%f"%(i,pair))
    clippy += "%f,%f"%(i,pair)
    i = i+1

# toclip(clippy)

os.system( "say ok" )
