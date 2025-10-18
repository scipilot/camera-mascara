#!/usr/bin/python3
print("Testing MatPlotLib on the Pi Zero - why so slow...")

print("importing OS...")
import os
import sys
#import pyfirmata2
import time
#print("importing MPL...")
#import matplotlib as mpl
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg
import pygame
print("... imports")

# ====== USER SETTINGS ======
folder_path = '/home/pip/CameraMascara/camera-mascara/patterns/PixelScan_2x2_64x64'
folder_path_cali = '/home/pip/CameraMascara/camera-mascara/patterns/Calibration'

N = 64
3
# ===

t1 = time.time()
def pront(str):
	global t1
	t2 = time.time()
	print(	"%s %s" % (t2 - t1, str))
	t1 = time.time()


# === MASK Load image files =======================================
pront("Collecting mask files...")
valid_exts = ('.jpg', '.jpeg', '.png', '.bmp')
image_files = [os.path.join(folder_path, f)
               for f in sorted(os.listdir(folder_path))
               if f.lower().endswith(valid_exts)]

pront("Setting up plotter...")
#mpl.rcParams['toolbar'] = 'None'
#fig = plt.figure(facecolor='black')        # Set figure background to black
#ax = fig.add_subplot(111)                  # Create axes object
#ax.set_facecolor('black')                  # Set axes background to black

# try to target the projector on 2nd display (note move mouse there first)
#fig.canvas.manager.window.move(0,0)


#manager = plt.get_current_fig_manager()
#try:
#    manager.full_screen_toggle()
#except AttributeError:
#    try:
#        manager.window.showMaximized()
#    except:
#        pass

#plt.axis('off')


# Script -----------

# TRY MPL - VERY SLOW?
# show dark screen to avoid initial flash
#img = mpimg.imread(os.path.join(folder_path,'pixel_0001.png'))
#plt.imshow(img, cmap='gray', vmin=0, vmax=1)
#plt.axis('off')
#plt.draw()
#plt.pause(1)

#TRY OPENCV - CANNOT INSTALL
#import cv2
#img = cv2.imread(folder_path+'/pixel_0001.png', cv2.IMREAD_ANYCOLOR)
#cv2.imgshow("?", img)

# TRY PIL - JUST SAVES IMAGE!
#from PIL import Image
#img = Image.open(folder_path+'/pixel_0001.png')
#img.show()

# Try PYGAME - WORKS WELL
pygame.init()
border = 0
h,w=480,640
#resolution = (pygame.display.Info().current_w, pygame.display.Info().current_h)
resolution=(64,64)
screen = pygame.display.set_mode(resolution, pygame.SCALED | pygame.FULLSCREEN) # | pygame.RESIZABLE)
pygame.display.set_caption("Camera Mascara")
#screen.fill((255, 255, 255))
surface = pygame.image.load(os.path.join(folder_path,'pixel_0001.png')).convert()
screen.blit(surface,(border,border))
pygame.display.flip()

# Mask display synchronised loop
for img_path in image_files:

    # Display next mask image (pixel)
    pront(f"Displaying: {img_path}")
    #img = mpimg.imread(img_path)
    #plt.clf()
    #plt.imshow(img, cmap='gray', vmin=0, vmax=1)
    #plt.axis('off')
    #plt.draw()
    #plt.pause(.1)
    #time.sleep(1)

    surface = pygame.image.load(img_path).convert()
    screen.blit(surface,(border,border))
    pygame.display.flip()

# === Cleanup
#plt.close()


