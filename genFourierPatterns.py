import numpy as np
import matplotlib.pyplot as plt
import imageio
import os

# Settings
N = 128
file_dir = f'patterns/fourier_p4_{N}/' # where to save images
save_images = True

# Ensure the output directory exists
os.makedirs(file_dir, exist_ok=True)

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
        for p in range(4):
            phi = phi_arr[p]
            temp = np.cos(2 * np.pi * (u * X + v * Y) + phi)
            temp = (temp + 1) / 2

            if save_images:
                filename = os.path.join(file_dir, f'fourier_{c:0{num_digits}d}.png')
                imageio.imwrite(filename, (temp * 255).astype(np.uint8))
            
            c += 1
