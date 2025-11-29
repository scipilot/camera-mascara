import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import ifft2, ifftshift
from PIL import Image

# Renders the captured brightness array into a PNG, file or return
class ImageRender:

    # output is the data array of brightness values
    # dims is the resolution dimension tuple (N,N)
    # file is a File-like (for return), or filename (for direct filesystem saving)
    def render(self, output, dims, mask, file):
        if mask == "point":
           self.render_point(output, dims, file)
        elif mask == "fourier":
           self.render_fourier(output, dims, file)
        else: raise(f"ImageRender.render: Unknown mask type'{mask}' - expecting point or fourier", mask)

    def render_point(self, output, dims, file):
        image0 = output.reshape(dims)
        
        # === Rescale brightness levels  (normalise)
        print("min:%f, max:%f" % (np.min(image0), np.max(image0)), flush=True)
        img_norm = image0 - np.min(image0)            # Subtract min
        if np.max(img_norm) > 0:  img_norm = img_norm / np.max(img_norm)        # Divide by normalised max
        img_uint8 = (img_norm * 255).astype(np.uint8) # Scale and convert to uint8

        # render with PyPlot
        fig, axs = plt.subplots(1, 2, figsize=(10, 5))

        # == Write out the PNG
        plt.imsave(file, img_uint8, cmap="grey")

    def render_fourier(self, output, dims, file):
        N = dims[0]

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
            temp = output[whichImages]
            F[uArr[p], vArr[p]] = (temp[2] - temp[0]) - 1j * (temp[3] - temp[1])
            whichImages += 4

        # Inverse FFT
        R = np.abs(ifftshift(ifft2(F)))
        R = np.rot90(np.fliplr(R), k=3)

        # Display amplitude and phase
        amplitude = np.log(1 + np.abs(F))
        phase = np.angle(F)

        print("min:%f, max:%f" % (np.min(R), np.max(R)))
        # Normalize and save image
        Ri = R - np.min(R)
        Ri = (Ri / np.max(Ri) * 255).astype(np.uint8)

        # Save the image
        plt.imsave(file, Image.fromarray(Ri), cmap="grey")

