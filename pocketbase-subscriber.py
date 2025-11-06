import asyncio
import os
from datetime import datetime

from pocketbase import PocketBase
from pocketbase.models.dtos import RealtimeEvent
from dotenv import load_dotenv

from lib.PiImageCapture import PiImageCapture
from lib.ImageStore import NPZImageStore
from lib.ImageStore.PocketbaseImageStore import PocketbaseImageStore
from lib.Pocketbase.PocketbaseConnector import PocketbaseConnector 

connector = PocketbaseConnector()

# Storage Strategy 1 - save data in NPZ file
#data_path = '/home/pip/CameraMascara/camera-mascara/data/pixels.npz'
#store = NPZImageStore(data_path)

# Storage Strategy 2 - save output into Pocketbase for GUI and API
store = PocketbaseImageStore(connector) 

pic = PiImageCapture(store)

# ENV - copy and fill in:  "cp dotenv-default .env.local"
load_dotenv()
# eg.
#CONNECTION_URL = "http://10.200.72.143:8090"
#SUPERUSER_EMAIL = "admin@pocketbase.local"
#SUPERUSER_PASSWORD = "pocketbasepassword"
COLLECTION_NAME = "posts"
#
CONNECTION_URL = os.getenv('POCKETBASE_CONNECTION_URL')
SUPERUSER_EMAIL = os.getenv('POCKETBASE_SUPERUSER_EMAIL')
SUPERUSER_PASSWORD = os.getenv('POCKETBASE_SUPERUSER_PASSWORD')
if CONNECTION_URL == "": raise SystemExit("POCKETBASE_CONNECTION_URL environment variable not set!")
if SUPERUSER_EMAIL == "": raise SystemExit("POCKETBASE_SUPERUSER_EMAIL environment variable not set!")
if SUPERUSER_PASSWORD == "": raise SystemExit("POCKETBASE_SUPERUSER_PASSWORD environment variable not set!")

async def callback(event: RealtimeEvent) -> None:
    """Callback function for handling Realtime events.

    Args:
        event (RealtimeEvent): The event object containing information about the record change.
    """
    # This will get called for every event
    # Lets print what is going on
    at = datetime.now().isoformat()
    print(f"[{at}] {event['action'].upper()}: {event['record']}")
    print(f"Pocketbase subscriber is running the image scan... {event['record']['image_size']} {event['record']['mask_pixel_size']}")
    pic.configure(image_size=event['record']['image_size'], mask_pixel_size=event['record']['mask_pixel_size'])
    await pic.run()



async def realtime_updates():
    """Establishes a PocketBase connection, authenticates, and subscribes to Realtime events."""
    unsubscribe = None

    try:
        # Instantiate the PocketBase connector
        #pb = PocketBase(CONNECTION_URL)
        # Authenticate as a superuser
        #await pb.collection("_superusers").auth.with_password(username_or_email=SUPERUSER_EMAIL, password=SUPERUSER_PASSWORD)
        pb = connector.connect()

        # Get the collection object
        col = pb.collection(COLLECTION_NAME)

        # Subscribe to Realtime events for the specific record ID in the collection
        unsubscribe = await col.subscribe_all(callback=callback)

        print("Pocketbase subsciber is ready")

        # Infinite loop to wait for events (adjusted from the second snippet)
        while True:
            await asyncio.sleep(60 * 60)  # Sleep for an hour to avoid hitting PocketBase's rate limits")

    except Exception as e:
        print(f"Error in Pocketbase subscriber: {e}")

    finally:
        # Unsubscribe if still active
        if unsubscribe:
            try:
                await unsubscribe()
            except Exception as e:
                print(f"Error unsubscribing: {e}")


if __name__ == "__main__":
    asyncio.run(realtime_updates())
