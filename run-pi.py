import asyncio
from lib.PiImageCapture import PiImageCapture
from lib.ImageStore.NPZImageStore import NPZImageStore
from lib.ImageStore.PocketbaseImageStore import PocketbaseImageStore
from lib.Pocketbase.PocketbaseConnector import PocketbaseConnector 

connector = PocketbaseConnector()

# Storage Strategy 1 - save data in NPZ file
#data_path = '/home/pip/CameraMascara/camera-mascara/data/pixels.npz'
#store = NPZImageStore(data_path)

# Storage Strategy 2 - save output into Pocketbase for GUI and API
store = PocketbaseImageStore(connector) 

pic = PiImageCapture(store)
asyncio.run(pic.run())

