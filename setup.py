# used to set up the system one off

from lib.ImageStore.PocketbaseImageStore import PocketbaseImageStore
import asyncio

# Storage Strategy 2 - save output into Pocketbase for GUI and API
store = PocketbaseImageStore() 
asyncio.run(store.setup())
