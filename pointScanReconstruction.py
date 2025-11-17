# Purpose: this is the original script to render a photo from the saved NPZ data file
#   it was run after "capture" script.
# It has now been migrated to the lib/ImageRender class which can be called at the end of the scan


import os
import numpy as np
import matplotlib.pyplot as plt

project_path = ''  # <-- Replace with your path

# === Load the data ===
data = np.load(os.path.join(project_path, 'data/pixels.npz')) 
print(data.files)

N = 64

a = data['output0']
#b = data['output1']

# === Reshape to 64x64 ===
image0 = a.reshape((N,N))
#image1 = b.reshape((N,N))
#print(image0)

# === Rescale
print("max:%f, min:%f" % (np.max(image0), np.min(image0)))
img_norm = image0 - np.min(image0)            # Subtract min
img_norm = img_norm / np.max(img_norm)        # Divide by max
img_uint8 = (img_norm * 255).astype(np.uint8) # Scale and convert to uint8


fig, axs = plt.subplots(1, 2, figsize=(10, 5))

# == Write out the PNG

plt.imsave(os.path.join(project_path, 'out/PointScan.png'), img_uint8)


# === Display the image ===
axs[0].imshow(img_uint8, cmap='gray')  # Use 'gray' or remove cmap for default
axs[0].axis('off')

#axs[1].imshow(image1, cmap='gray')  # Use 'gray' or remove cmap for default
#axs[1].axis('off')

plt.tight_layout()
plt.show()

