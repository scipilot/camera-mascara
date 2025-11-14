import numpy as np

# Strategy : Numpy save NPZ file 
class NPZImageStore:    # (ImageStore)
    def __init__(self, data_path):
        self.data_path = data_path

    # TODO I'm currently not using title, stats which were added in the other strategy, it could be added to the file I guess
    async def store(self, output, dims, mask, title, stats):
        np.savez(self.data_path, output0=output)

