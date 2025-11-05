# used to set up the system one off

from lib.ImageStore.PocketbaseImageStore import PocketbaseImageStore
import asyncio

# TODO I couldn't get the auto-delete to work (see class)
confirm = input("Setup pocketbase - you must delete the existing images collection first. Press 'y' to continue.")
if confirm != 'y': 
    print('Aborted')
    quit()

# Storage Strategy 2 - save output into Pocketbase for GUI and API
store = PocketbaseImageStore() 
asyncio.run(store.setup())

print('Setup pocketbase - complete')

