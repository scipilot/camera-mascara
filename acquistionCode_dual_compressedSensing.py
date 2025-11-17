# Purpose: this is the original camera "scan" code for the phase 1  Ardiono, 
#   which has now been evolved and integrated to "run.py" and "lib/Capture"

import os
import time
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pyfirmata
import numpy as np

# ====== USER SETTINGS ======
folder_path = 'patterns/quick'  # <-- Replace with your path

#folder_path = '//Users/jon/Documents/PROJECTS/11_compressedSensing/patterns/hadamard/128x128/'  # <-- Replace with your path
#folder_path = '//Users/jon/Documents/PROJECTS/11_compressedSensing/patterns/hadamard/64x64inverse/'  # <-- Replace with your path
# folder_path = '/Users/jon/Documents/PROJECTS/11_compressedSensing/patterns/pixels/128pixels_6/'  # <-- Replace with your path
#folder_path = '//Users/jon/Documents/PROJECTS/11_compressedSensing/patterns/fourier/256x256/'
# folder_path = '//Users/jon/Documents/PROJECTS/11_compressedSensing/patterns/fourier/128x128/'

# folder_path = '//Users/jon/Documents/PROJECTS/11_compressedSensing/patterns/fourier/32x32/'

#folder_path = '//Users/jon/Documents/PROJECTS/11_compressedSensing/patterns/hadamard/128x128inverse/'

N = 50                                # Number of analog samples
serial_port = '/dev/cu.usbmodem101'  # <-- Replace with your Arduino port

# ====== Setup PyFirmata ====== 
board = pyfirmata.Arduino(serial_port)
pin0 = board.get_pin('a:0:i')      # Analog input A0
pin1 = board.get_pin('a:1:i')      # Analog input A0

pinStart = board.get_pin('d:3:i') # Digital input pin 3

it = pyfirmata.util.Iterator(board)
it.start()
time.sleep(1)  # Allow time for pin setup

# === Load image files ===
valid_exts = ('.jpg', '.jpeg', '.png', '.bmp')
image_files = [os.path.join(folder_path, f)
               for f in sorted(os.listdir(folder_path))
               if f.lower().endswith(valid_exts)]

fig = plt.figure(facecolor='black')        # Set figure background to black
ax = fig.add_subplot(111)                  # Create axes object
ax.set_facecolor('black')                  # Set axes background to black

manager = plt.get_current_fig_manager()
try:
    manager.full_screen_toggle()
except AttributeError:
    try:
        manager.window.showMaximized()
    except:
        pass


plt.axis('off')
output0 = []
output1 = []
started = False

while not started:
    if pinStart.read() is True:
        print(f"start true")
    else:
        print(f"start not true")

    if pinStart.read() is True: 	# PJ: I added external pullup as PyFirmata doesn't support INPUT_PULLUP, so it goes LOW
        started = True
    time.sleep(0.05)

for img_path in image_files:
    # Display image
    # print(f"Displaying: {img_path}")
    img = mpimg.imread(img_path)
    plt.imshow(img, cmap='gray', vmin=0, vmax=1)
    plt.axis('off')
    plt.draw()
    plt.pause(0.2)


    # Take N analog readings
    sample0 = []
    sample1 = []
    while len(sample0) < N:
        val0 = pin0.read()
        val1 = pin1.read()
        if val0 is not None:
            sample0.append(val0)
            time.sleep(0.001)
        if val1 is not None:
            sample1.append(val1)
            time.sleep(0.001)


    analog_sum0 = sum(sample0)
    analog_sum1 = sum(sample1)
    output0.append(analog_sum0)
    output1.append(analog_sum1)

    # Wait briefly before next image (or wait for a condition)
    time.sleep(0.01)
    plt.clf()

# ====== Cleanup ======
plt.close()
board.exit()

# ====== Output results ======
# np.savez('/Users/pip/Documents/OnePixel/projector/data/pixels.npz', output0=output0, output1=output1)
