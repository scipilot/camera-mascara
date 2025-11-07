import asyncio
from lib.PiLightMeter import PiLightMeter
from lib.Pocketbase.Connector import Connector 
from lib.Meters.PocketbaseBrightnessMeter import  PocketbaseBrightnessMeter

DEVICE = "l23p04fh17l051m"


# Storage Strategy 1 -  log?

# Storage Strategy 2 - save output into Pocketbase for GUI and API
connector = Connector()
meter = PocketbaseBrightnessMeter(connector)

it = PiLightMeter(meter, DEVICE)
asyncio.run(it.run())

