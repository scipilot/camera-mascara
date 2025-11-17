#!/usr/bin/python3
import matplotlib as mpl
import time

# Purpose: this script was used to check the subject and light levels before running "capture"
# it displays the same frame and black background level so you can adjust the positioning
# of the subject and any voltages on the sensor (bias, amplification, feedback etc),
# before taking a shot.
#  Also see the light-meter which also shows a black screen.


# sleep to let me close the laptop to switch to projector
time.sleep(2)

# get screen dimensions using TKAgg backend as MacOSX doesn't have "manager.window"
mpl.use('TkAgg')
import matplotlib.pyplot as pltTKAGG
manager1 = pltTKAGG.get_current_fig_manager()
window = manager1.window
screen_y = window.winfo_screenheight()
screen_x = window.winfo_screenwidth()
print( screen_x, screen_y)
# the £20 projector reports: 1920 x 1080
# the MBP3 reports 1728 x 1117

# switch back to MacOSX backend
mpl.use('MacOSX')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set up output same as run.py
# With a frame to align the subject

mpl.rcParams['toolbar'] = 'None'
fig = plt.figure(facecolor='grey')        # Set figure background to black
ax = fig.add_subplot(111)                  # Create axes object
ax.set_facecolor('black')                  # Set axes background to black

manager = plt.get_current_fig_manager()

# draw bounding frame
# turns out the size is 1x1 !
# but the projector fades out at the edges!
screen_x = .8 # screen_x /1728
screen_y = .8 # screen_y /1117
# print( screen_x, screen_y)
rect = patches.Rectangle((0.1, 0.1), screen_x, screen_y, linewidth=5, edgecolor='white', facecolor='none')
ax.add_patch(rect)

# try to target the projector on 2nd display (note move mouse there first)
#fig.canvas.manager.window.move(0,0)

try:
    manager.full_screen_toggle()
except AttributeError:
    try:
        manager.window.showMaximized()
    except:
        pass

plt.axis('off')

print("To stop the program press the any key.")
# Wait for a key
input()
