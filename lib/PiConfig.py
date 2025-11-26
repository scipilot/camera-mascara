#!/usr/bin/python3

import os
import sys
import math
import time
from datetime import datetime
import numpy as np
from lib.PiHatSensor import PiHatSensor, ConfigStruct
from lib.PiImageCapture import ImageStore

# ====== DEFAULT SETTINGS ======

I2CBUS = 1


# DI  interfaxce 
class ConfigStore():
    """ INTERFACE CLASS FOR CONFIG STORE DI
    """
    def store(self, DI, PGA, SPS):
        raise NotImplementedError
    def fetch(self, DI):
        raise NotImplementedError



# ===
class PiConfig:
    def __init__(self, store: ConfigStore):
        # DI of the storage stratagey (e.g. file store, or pocketbase)
        self.store = store

        # Create a new board wrapper 
        print("Connecting to the PiHat ...", flush=True)
        self.board = PiHatSensor(I2CBUS)

    async def read(self, device):
        cs:ConfigStruct = self.board.ADCReadConfigStruct() 
        print(f"PiConfig fetched config for {device}: {cs}", flush=True)
        await self.store.store(device, cs.PGA_value, cs.SPS_value)

    async def write(self, device, pga_value, sps_value):
        print(f"PI configure: {device}, {pga_value}, {sps_value}", flush=True)
        #device = await self.store.fetch(ID, cs.PGA_value, cs.SPS_value), 
        self.board.ADCWriteConfigValues(PGA_value=pga_value, SPS_value=sps_value) 
        await self.store.store(device, pga_value, sps_value)

    def stop():
        # Close the serial connection to the Arduino
        self.board.shutdown()
        
