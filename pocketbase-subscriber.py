# Purpose: this is the main "service" script  which can perform all the functions (scan, meter, config)
# via the Pocketbase API. It listens to "job" requests and processes the job accordingly, e.g. 
# taking a photo at the specified resolution and saving the resulting image in the database.
# or running the light-meter and updating the corresponding device record.
# Most of these functions have manual scripts too, but this is the "lights-out" wrapper service.
#
# the API is: POST a Job with "requested" and it will start processing
#           Cancel the job, but PUTTING the same job( ID and state) with "cancel" state
#           poll the Job state and related Job.Camera state
#           Query the result, e.g. images

print("Pocketbase subscriber is starting...", flush=True)
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

# TODO NOTE each service has its own PiHATSensorBoard so they have to refresh their own config.
# IT MIGHT be better to inject one so it stays in sync?

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


pb = None

# Singleton Job cache for cancellation
jobId = None
jobState = None
jobCancel = False

async def callbackRouter(event: RealtimeEvent) -> None:
    if event['record']['state'] == 'requested':
        await callbackRequest(event)
    elif event['record']['state'] == 'cancel':
        await callbackCacnel(request)

# This will get called for every job event
async def callbackRequest(event: RealtimeEvent) -> None:
    """Callback function for handling Realtime events.
    Args:
        event (RealtimeEvent): The event object containing information about the record change.
    """
    global pb, jobId
    at = datetime.now().isoformat()
    print(f"CB REQUEST [{at}] {event['action'].upper()}: {event['record']}", flush=True)
    # only service "request" or "abort" as the record is updated by the job itself (and would recurse!)
    if event['record']['state'] == 'requested':
        if jobId != None:
            # don't allow concurrent jobs
            print(f"ERROR: Job is already running. Cannot start job:{ event['record']['job'] }", flush=True)
            return

        if event['record']['job'] == 'capture':
            await handleCapture(event, pb)
        elif event['record']['job'] == 'meter':
            await handleMeter(event, pb)
        elif event['record']['job'] == 'adc.config.read':
            await handleADCConfigRead(event, pb)
        elif event['record']['job'] == 'adc.config.write':
            await handleADCConfigWrite(event, pb)
        else:
            print(f"ERROR: Unknown job { event['record']['job'] }", flush=True)

async def callbackCancel(event: RealtimeEvent) -> None:
    global jobId
    at = datetime.now().isoformat()
    print(f"CB CANCEL [{at}] {event['action'].upper()}: {event['record']}", flush=True)
    if event['record']['state'] == 'cancel':
        if jobId != None:
            await handleCancel(event, pb)
        else:
            print(f"WARNING: No Job is running. Cannot cancel job:{ event['record']['job'] }", flush=True)
            return

async def handleCancel(event: RealtimeEvent, pb) -> None:
    print(f"handleCancel")
    global jobCancel
    # if there's a cancellable job running, flag it for stoppage
    if jobId != None:
            jobCancel = True

def queryCancelCB():
    global jobCancel
    #print(f"queryCancelC{jobCancel=}")
    return jobCancel

async def handleCapture(event: RealtimeEvent, pb) -> None:
    print(f"Capture: running image scan... {event['record']['image_size']} {event['record']['mask_point_size']} {event['record']['mask_point_shape']} for {event['record']['camera']}", flush=True)
    global jobCancel
    await pic.configure(image_size=event['record']['image_size'], mask_point_size=event['record']['mask_point_size'], mask_point_shape=event['record']['mask_point_shape'], mask_type=event["record"]["mask_type"])
    jobCancel = False
    await update_job(event, "running", pb)
    await pic.run(queryCancelCB)
    await update_job(event, "ended", pb)


async def handleMeter(event: RealtimeEvent, pb) -> None:
    print(f"Running the meter for {event['record']['camera']}", flush=True)
    #await update_job(event, "starting")
    await plm.configure(device=event["record"]["camera"])
    await update_job(event, "running", pb)
    await plm.run()
    await update_job(event, "ended", pb)

async def handleADCConfigRead(event: RealtimeEvent, pb) -> None:
    print(f"Running ADCConfigRead for {event['record']['camera']}", flush=True)
    await update_job(event, "running", pb)
    await pc.read(device=event["record"]["camera"])
    await update_job(event, "ended", pb)

async def handleADCConfigWrite(event: RealtimeEvent, pb) -> None:
    print(f"Running ADCConfigWrite for {event['record']['camera']}", flush=True)
    await update_job(event, "running", pb)
    await pc.write(device=event["record"]["camera"], pga_value=event["record"]["pga"], sps_value=event["record"]["sps"])
    await update_job(event, "ended", pb)


async def update_job(event: RealtimeEvent, state, pb):
    global jobId, jobState
    # update local cache
    jobId = event["record"]["id"]
    jobState = state

    # update database
    col = pb.collection(COLLECTION_NAME)
    updated = await col.update(record_id=event["record"]["id"], params={"state": state})
    # also update the client denormalisation
    await update_client(event, state, pb)

async def update_client(event: RealtimeEvent, state, pb):
    if state == "ended":
        # remove the job from this device
        setJob = ""
    else: 
        setJob = event["record"]["id"]
    col = pb.collection("cameras")
    updated = await col.update(record_id=event["record"]["camera"], params={"job": setJob})

async def realtime_updates(callback):
    """Establishes a PocketBase connection, authenticates, and subscribes to Realtime events."""
    global pb
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

        print("Pocketbase subscriber is ready", flush=True)

        # Infinite loop to wait for events (adjusted from the second snippet)
        while True:
            await asyncio.sleep(60 * 60)  # Sleep for an hour to avoid hitting PocketBase's rate limits")

    except Exception as e:
        print(f"Error in Pocketbase subscriber: {e}", flush=True)

    finally:
        # Unsubscribe if still active
        if unsubscribe:
            try:
                await unsubscribe()
            except Exception as e:
                print(f"Error in Pocketbase subscriber: unsubscribing: {e}", flush=True)


async def main():
    # Run two parallel "threads" to allow jobs to be cancelled concurrently
    async with asyncio.TaskGroup() as tg:
        tg.create_task(realtime_updates(callbackRequest))
        tg.create_task(realtime_updates(callbackCancel))

if __name__ == "__main__":
    asyncio.run(main())


