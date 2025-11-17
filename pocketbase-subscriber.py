# Purpose: this is the main "service" script  which can perform all the functions (scan, meter, config)
# via the Pocketbase API. It listens to "job" requests and processes the job accordingly, e.g. 
# taking a photo at the specified resolution and saving the resulting image in the database.
# or running the light-meter and updating the corresponding device record.
# Most of these functions have manual scripts too, but this is the "lights-out" wrapper service.

print("Pocketbase subscriber is starting...")
import asyncio
import os
from datetime import datetime

from pocketbase import PocketBase
from pocketbase.models.dtos import RealtimeEvent
from dotenv import load_dotenv

from lib.PiImageCapture import PiImageCapture
from lib.ImageStore import NPZImageStore
from lib.ImageStore.PocketbaseImageStore import PocketbaseImageStore
from lib.Pocketbase.Connector import Connector 
from lib.PiLightMeter import PiLightMeter
from lib.Meters.PocketbaseBrightnessMeter import  PocketbaseBrightnessMeter
from lib.ConfigStore.PocketbaseConfigStore import PocketbaseConfigStore
from lib.PiConfig import PiConfig

connector = Connector()

# Storage Strategy 1 - save data in NPZ file
#data_path = '/home/pip/CameraMascara/camera-mascara/data/pixels.npz'
#store = NPZImageStore(data_path)

# Storage Strategy 2 - save output into Pocketbase for GUI and API
store = PocketbaseImageStore(connector) 
pic = PiImageCapture(store)

confStore = PocketbaseConfigStore(connector)
pc = PiConfig(confStore)

# Storage Strategy 1 -  log?

# Storage Strategy 2 - save output into Pocketbase for GUI and API
meter = PocketbaseBrightnessMeter(connector)
plm = PiLightMeter(meter)


# ENV - copy and fill in:  "cp dotenv-default .env.local"
load_dotenv()
# eg.
#CONNECTION_URL = "http://10.200.72.143:8090"
#SUPERUSER_EMAIL = "admin@pocketbase.local"
#SUPERUSER_PASSWORD = "pocketbasepassword"
COLLECTION_NAME = "jobs"
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
    at = datetime.now().isoformat()
    print(f"[{at}] {event['action'].upper()}: {event['record']}")
    # onky service "requests" as the record is updated by the job itself (and would recurse!)
    if event['record']['state'] == 'requested':
        if event['record']['job'] == 'capture':
            await handleCapture(event)
        elif event['record']['job'] == 'meter':
            await handleMeter(event)
        elif event['record']['job'] == 'adc.config.read':
            await handleADCConfigRead(event)
        elif event['record']['job'] == 'adc.config.write':
            await handleADCConfigWrite(event)
        else:
            print(f"Unknown job { event['record']['job'] }")

async def handleCapture(event: RealtimeEvent) -> None:
    print(f"Pocketbase subscriber is running the image scan... {event['record']['image_size']} {event['record']['mask_pixel_size']} for {event['record']['camera']}")
    await pic.configure(image_size=event['record']['image_size'], mask_pixel_size=event['record']['mask_pixel_size'], mask_type=event["record"]["mask_type"])
    await update_job(event, "running")
    await pic.run()
    await update_job(event, "ended")


async def handleMeter(event: RealtimeEvent) -> None:
    print(f"Pocketbase subscriber is running the meter for {event['record']['camera']}")
    #await update_job(event, "starting")
    await plm.configure(device=event["record"]["camera"])
    await update_job(event, "running")
    await plm.run()
    await update_job(event, "ended")

async def handleADCConfigRead(event: RealtimeEvent) -> None:
    print(f"Pocketbase subscriber is running the handleADCConfigRead for {event['record']['camera']}")
    await update_job(event, "running")
    await pc.read(device=event["record"]["camera"])
    await update_job(event, "ended")

async def handleADCConfigWrite(event: RealtimeEvent) -> None:
    print(f"Pocketbase subscriber is running the handleADCConfigWrite for {event['record']['camera']}")
    await update_job(event, "running")
    await pc.write(device=event["record"]["camera"], pga_value=event["record"]["pga"], sps_value=event["record"]["sps"])
    await update_job(event, "ended")


async def update_job(event: RealtimeEvent, state):
    pb = await connector.connect()
    col = pb.collection(COLLECTION_NAME)
    updated = await col.update(record_id=event["record"]["id"], params={"state": state})
    # also update the client denormalisation
    await update_client(pb, event, state)

async def update_client(pb, event: RealtimeEvent, state):
    if state == "ended":
        # remove the job from this device
        setJob = ""
    else: 
        setJob = event["record"]["id"]
    col = pb.collection("cameras")
    updated = await col.update(record_id=event["record"]["camera"], params={"job": setJob})

async def realtime_updates():
    """Establishes a PocketBase connection, authenticates, and subscribes to Realtime events."""
    unsubscribe = None

    try:
        # Instantiate the PocketBase connector
        #pb = PocketBase(CONNECTION_URL)
        # Authenticate as a superuser
        #await pb.collection("_superusers").auth.with_password(username_or_email=SUPERUSER_EMAIL, password=SUPERUSER_PASSWORD)
        pb = await connector.connect()

        # Get the collection object
        col = pb.collection(COLLECTION_NAME)

        # Subscribe to Realtime events for the specific record ID in the collection
        unsubscribe = await col.subscribe_all(callback=callback)

        print("Pocketbase subscriber is ready")

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
                print(f"Error in Pocketbase subscriber: unsubscribing: {e}")


if __name__ == "__main__":
    asyncio.run(realtime_updates())
