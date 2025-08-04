import numpy as np
from scipy.linalg import hadamard
import matplotlib.pyplot as plt

# Create Hadamard patterns
N = 64
H = hadamard(N)

H_ordered = np.zeros((N, N))
for i in range(N):  # Column-wise
    counter = 0
    temp = H[0, i]
    for j in range(1, N):  # Row-wise
        if temp != H[j, i]:
            counter += 1
            temp = H[j, i]
    for k in range(N):
        H_ordered[k, counter] = H[k, i]

L = np.zeros((N, N, N**2))
p = 0

for i in range(N):
    for j in range(N):
        temp = np.outer(H_ordered[i, :], H_ordered[j, :])
        temp[temp == -1] = 0
        L[:, :, p] = temp
        p += 1

plt.imshow(L[:, :, 65], cmap='gray', vmin=0, vmax=1)
plt.title("Hadamard Pattern 0")
plt.axis('off')  # Hide axes for cleaner view
plt.show()