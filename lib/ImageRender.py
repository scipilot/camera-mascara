import numpy as np
import matplotlib.pyplot as plt

# Renders the brightrness array into a PNG, file or return
class ImageRender:

    # output is the data array of brightness values
    # dims is the resolution dimension tuple (N,N)
    # file is a File-like (for return), or filename (for direct filesystem saving)
    def render(self, output, dims, file):
        image0 = output.reshape(dims)
        
        # === Rescale brightness levels  (normalise)
        print("max:%f, min:%f" % (np.max(image0), np.min(image0)))
        img_norm = image0 - np.min(image0)            # Subtract min
        if np.max(img_norm) > 0:  img_norm = img_norm / np.max(img_norm)        # Divide by normalised max
        img_uint8 = (img_norm * 255).astype(np.uint8) # Scale and convert to uint8

        # render with PyPlot
        fig, axs = plt.subplots(1, 2, figsize=(10, 5))

        # == Write out the PNG
        plt.imsave(file, img_uint8)

