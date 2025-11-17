# Purpose: this a manually run camera script to "take a photo" via the Pi Hat
# it's an alternative entrpoint from the pocketbase subscriber, and runs the same code underneath.
# you need to configure the options below manually

import asyncio
from lib.PiImageCapture import PiImageCapture
from lib.ImageStore.NPZImageStore import NPZImageStore
from lib.ImageStore.PocketbaseImageStore import PocketbaseImageStore
from lib.Pocketbase.Connector import Connector 

connector = Connector()

# Storage Strategy 1 - save data in NPZ file
data_path = 'data/pixels.npz'
store = NPZImageStore(data_path)

# Storage Strategy 2 - save output into Pocketbase for GUI and API
#store = PocketbaseImageStore(connector) 

pic = PiImageCapture(store)

SIZE = 128
PIXEL = 2
TYPE = 'fourier'

async def do() -> None:
    await pic.configure(SIZE, PIXEL, TYPE)
    await pic.run()

asyncio.run(do())
