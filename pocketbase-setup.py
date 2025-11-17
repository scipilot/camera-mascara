# Purpose - used once-off  to set up the Pocketbase system during initial setup
# TODO: NOT FINISHED! I think only the ImageStore class has it's own "migration" function...
#       So the Job, Camera tables don't have constructors like this, but it was a nice idea.
# You can instead use the exported JSON schema in ./etc/pocketbase

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

