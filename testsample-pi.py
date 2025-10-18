#!/usr/bin/python3
print("CAMERA MASCARA PRUEBA ESTA EMPESANDO...")

print("importing OS...")
import os
import sys
#import pyfirmata2
import time
print("importing Numpy...")
import numpy as np
print("importing PiHatSensor...")
from lib.PiHatSensor import PiHatSensor
print("... imports")

# ====== USER SETTINGS ======
I2CBUS = 1
N = 64

# === vars ===

brightness = 0.0
samples = []
output0 = []

t1 = time.time()
def pront(str):
	global t1
	t2 = time.time()
	print(	"%.5f %s" % (t2 - t1, str))
	t1 = time.time()

pront("Connecting to the PiHat ...")

# Create a new board wrapper
board = PiHatSensor(I2CBUS)


# TODO convert these firmata settings to the PiHat class - sample speed, data callback
# default sampling interval is 19ms
#board.samplingOn(RATE)
#digital_0.register_callback(pinCallback)
#board.analog[0].register_callback(myPrintCallback)

def sampleCallback(data):
    global brightness
    brightness = data
    samples.append(data)
    #print("brightness now:%f" % (brightness     ))


# Script -----------

samples = []
totalSamplesPerLoop = []
totalWaits = 0

# Mask display synchronised loop
for n in range(1000000):
    #pront("Sampling... %d"%(n))

    sample = board.ADCReadVoltage()
    print('sample=%s'%(sample))
    sampleCallback(sample)

    # Wait briefly before next image (or wait for a condition)
    time.sleep(0.001)
    #pront("Done sleep")

    # Make sure we have a sample to prevent div/0 ; happens every 20-30 loops?
    if len(samples) == 0:
        pront ("awaiting samples...")
        time.sleep(0.01)
        totalWaits = totalWaits+1
    #pront ("got %d samples after %d waits" % (len(samples), totalWaits))
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

# === Cleanup
# Close the serial connection to the Arduino
board.shutdown()

print(output0)
#np.savez('/Users/pip/Documents/OnePixel/projector/data/pixels.npz', output0=output0)

print('Samples/pixel avg:%0.2f min:%d ma:x%d waits:%d'%(np.average(totalSamplesPerLoop), np.min(totalSamplesPerLoop), np.max(totalSamplesPerLoop), totalWaits))

