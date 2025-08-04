import numpy as np
import matplotlib.pyplot as plt
import imageio
import os

# Settings
folder_save = 'Documents/patterns/test/' # where to save images
save_images = True
N = 64

num_images = N**2
num_digits = len(str(num_images))

x = np.linspace(-N/2, N/2, N)
y = np.linspace(-N/2, N/2, N)

freq_max = 1 / (x[1] - x[0]) / 4
num_freq = N // 2

freq_arr = np.linspace(-freq_max, freq_max, num_freq)
X, Y = np.meshgrid(x, y)

phi_arr = [0, np.pi/2, np.pi, 3*np.pi/2]

# Set black background for plot (optional)
plt.figure(facecolor='black')
P = []
p = 0  # MATLAB starts at 1, Python at 0
c = 1

for v in freq_arr:
    for u in freq_arr:
        phi = phi_arr[p]
        temp = np.cos(2 * np.pi * (u * X + v * Y) + phi)
        temp = (temp + 1) / 2

        if save_images:
            filename = os.path.join(folder_save, f'fourier_{c:0{num_digits}d}.png')
            imageio.imwrite(filename, (temp * 255).astype(np.uint8))
        
        c += 1
