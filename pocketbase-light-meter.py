# Purpose: this is a manualy entrypoint for the light-meter which stores the results into Pocketbase
# it's probably redundant now that you can do this via the API subscriber
# another alternative is the light-meter.py script which simply prints the levels to screen.

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

