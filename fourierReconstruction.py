import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import ifft2, ifftshift
from PIL import Image

# Load .npz data
npz_data = np.load('data/fourier-128.npz')
#data = npz_data['output1']
data = npz_data['output0'] # If you want to use M0 as well

N = 128 

# Frequency arrays
x = np.linspace(-N/2, N/2, N)
y = np.linspace(-N/2, N/2, N)
freqMax = 1 / (x[1] - x[0]) / 2
numFreq = N // 2
freqArr = np.linspace(-freqMax, freqMax, numFreq)

# Generate uArr and vArr
uArr = []
vArr = []
for n in range(len(freqArr)):
    for m in range(len(freqArr)):
        vArr.append(n)
        uArr.append(m)

# Calculate the FFT
F = np.zeros((N//2, N//2), dtype=complex)
whichImages = np.arange(4)
for p in range(N**2 // 4):
    temp = data[whichImages]
    F[uArr[p], vArr[p]] = (temp[2] - temp[0]) - 1j * (temp[3] - temp[1])
    whichImages += 4

# Inverse FFT
R = np.abs(ifftshift(ifft2(F)))
R = np.rot90(np.fliplr(R), k=3)

# Display amplitude and phase
amplitude = np.log(1 + np.abs(F))
phase = np.angle(F)

plt.figure(facecolor='white')
plt.subplot(1, 2, 1)
plt.imshow(amplitude, cmap='gray')
plt.axis('image')
plt.xticks([]); plt.yticks([])
plt.gca().tick_params(color='white', labelcolor='white')

plt.subplot(1, 2, 2)
plt.imshow(phase, cmap='gray')
plt.axis('image')
plt.xticks([]); plt.yticks([])
plt.gca().tick_params(color='white', labelcolor='white')
plt.show()

# Display reconstructed image
plt.figure(facecolor='black')
plt.imshow(R, cmap='gray')
plt.axis('image')
plt.xticks([]); plt.yticks([])
plt.gca().tick_params(color='white', labelcolor='white')
plt.show()

# Normalize and save image
Ri = R - np.min(R)
Ri = (Ri / np.max(Ri) * 255).astype(np.uint8)

# Save the image
Image.fromarray(Ri).save('out/fourier.png')
