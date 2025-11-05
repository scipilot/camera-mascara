import numpy as np

# Strategy : Numpy save NPZ file 
class NPZImageStore:    # (ImageStore)
    def __init__(self, data_path):
        self.data_path = data_path

    def store(self, output):
        np.savez(self.data_path, output0=output)

