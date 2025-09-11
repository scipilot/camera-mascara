#!/usr/bin/python3

import os
import sys
import pyfirmata2
import time
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# ====== USER SETTINGS ======
folder_path = '/Users/pip/Documents/OnePixel/projector/patterns/PixelScan_4x4_128x128'
folder_path_cali = '/Users/pip/Documents/OnePixel/projector/patterns/Calibration'

# PORT = '/dev/cu.usbmodem101'
PORT = pyfirmata2.Arduino.AUTODETECT

N = 128

# ===

brightness = 0.0
samples = []
output0 = []
# background0 = []


# Callback function which is called whenever there is a change at the digital port.
def pinCallback(value):
    if value:
        print("Button up")
    else:
        print("Button down")
    
def myPrintCallback(data):
    global brightness	
    #print(data)
    brightness = data
    samples.append(data)
    # print("brightness now:%f" % (brightness	))
    # I found I had to keep re-enabling the DAC else it only gives one number
    board.analog[0].enable_reporting()



# Creates a new board
try:
    board = pyfirmata2.Arduino(PORT)
except:
    sys.exit("Failed to connect to Arduino on port %s - Is the Arduino plugged in?" % (PORT))    

print("Connecting to the Arduino ...")

# default sampling interval is 19ms
board.samplingOn()

# Setup the digital pin with pull-up resistor: "u"
digital_0 = board.get_pin('d:3:u')
digital_0.register_callback(pinCallback)
digital_0.enable_reporting()


## Analogue setup -------

board.analog[0].register_callback(myPrintCallback)
board.analog[0].enable_reporting()
# board.analog[0].enable_reporting()



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

# === MASK Load image files =======================================
valid_exts = ('.jpg', '.jpeg', '.png', '.bmp')
image_files = [os.path.join(folder_path, f)
               for f in sorted(os.listdir(folder_path))
               if f.lower().endswith(valid_exts)]

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

plt.axis('off')


# Script -----------


# print("To stop the program press return.")
# Wait for a key
#input()

# simple loop
#for x in range(N):
#    for y in range(N):
#        time.sleep(0.001)
#        print("brightness stored: %d,%d=%f" % (x, y, brightness))
#        output0.append(brightness)
#    # board.analog[0].enable_reporting()

# show dark screen to avoid initial flash
img = mpimg.imread(os.path.join(folder_path,'pixel_00001.png'))
plt.imshow(img, cmap='gray', vmin=0, vmax=1)
plt.axis('off')
plt.draw()
plt.pause(3)
# time.sleep(5)
samples = []
totalSamplesPerLoop = []
totalWaits = 0

# Mask display synchronised loop
for img_path in image_files:
    # print ("loop>>")
    # LDR is super slow in low light can take 5seconds to settle from higher value!

    # Display next mask image (pixel)
    # print(f"Displaying: {img_path}")
    img = mpimg.imread(img_path)
    plt.imshow(img, cmap='gray', vmin=0, vmax=1)
    plt.axis('off')
    plt.draw()
    # Wait briefly before next image (or wait for a condition)
    plt.pause(0.01)
    # time.sleep(0.01)
    plt.clf()

    # Make sure we have a sample to prevent div/0 ; happens every 20-30 loops?
    if len(samples) == 0:
        # print ("awaiting samples...")
        time.sleep(0.01)
        totalWaits = totalWaits+1
    # print ("got %d" % (len(samples)))
    totalSamplesPerLoop.append(len(samples))

    # avg all the samples taken so far (number can vary)
    avg = sum(samples) / len(samples)
    output0.append(avg)
    #print("avg brightness stored: %s=%f" % (img_path, avg))
    samples = []

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
digital_0.enable_reporting()
board.analog[0].disable_reporting()

plt.close()

# Close the serial connection to the Arduino
board.exit()

print(output0)
np.savez('/Users/pip/Documents/OnePixel/projector/data/pixels.npz', output0=output0)

print('Samples/pixel avg:%0.2f min:%d ma:x%d waits:%d'%(np.average(totalSamplesPerLoop), np.min(totalSamplesPerLoop), np.max(totalSamplesPerLoop), totalWaits))

# print(background0)
# print('BG samples len:%d avg:%0.2f, min:%d max:%d'%(len(background0), np.average(background0), np.min(background0), np.max(background0)))

os.system( "say ooh" )
