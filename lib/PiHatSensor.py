import time
from dataclasses import dataclass
from smbus2 import SMBus, i2c_msg
import numpy as np

# This wraps accessing the Pi Hat ADC (TI ADS1110) via I2C
# Note you cannot use functions like bus.write_byte_data with the ADS1110 aa they select a register which it doesn't have.

# device address
addr = 0x48 # The "ED0" ADS1110A0I chip address

# this is default config 0x0C (could be reported back as 0x8C due to data-ready flag bit)
MIN_CODE = -32768 # depends on SPS
MAX_V = 2.048
VIN_NEG = 1.97 # bias
SAMPLES_PER_SECOND = 15

# bit position in config
CFG_DRDY = 7
CFG_SC   = 4
CFG_DR1  = 3
CFG_DR2  = 2
CFG_PGA1 = 1
CFG_PGA2 = 0
# config bit masks
CFM_DRDY = 128
CFM_SC   = 16
CFM_DR   = 12
CFM_PGA  = 3
#config options
DR_240SPS = 0b00
DR_60SPS  = 0b01
DR_30SPS  = 0b10
DR_15SPS  = 0b11
PGA_GAIN_1 = 0b00
PGA_GAIN_2 = 0b01
PGA_GAIN_4 = 0b10
PGA_GAIN_8 = 0b11
# Single conversion =1, continuous =0
SC_CONT = 0
SC_SING = 1

# CURRENT COFIG - now in self
#DR = DR_15SPS
#PGA = PGA_GAIN_2
SC = SC_CONT  

# PGA is the masked setting (0,1,2,3) and PGA-VALUE is the actual gain 1,2,4,8
PGA_VALUES = {
    0: 1,
    1: 2,
    2: 4,
    3: 8,
}
# inverse mapping 
PGA_OPTIONS = {
    '1': 0,
    '2': 1,
    '4': 2,
    '8': 3,
}

#TODO - this isn't consistent now! either bitmask the values in position OR shift into place. I'm currently doing a mix of both!
# DR is the masked setting (12,8,4,6), and DR_values is the actual samples per second (15,30,60,120)
DR_VALUES = {
   12: 15,
    8: 30,
    4: 60,
    0: 240,
}
# inverse mapping
DR_OPTIONS = {
    '15':  12,
    '30':   8,
    '60':   4,
    '240':  0,
}
# max value at each DR setting, when clipping high
DR_MAX = {
   12: 0x7FFF,
    8: 0x3FFF,
    4: 0x1FFF,
    0: 0x0FFF,
}
# min value when clipping low
DR_MIN = {
   12: 0x8000,
    8: 0xC000,
    4: 0xE000,
    0: 0xF800,
}

@dataclass
class ConfigStruct:
    """ Represents the ADC configuration, externally only the _values are used  """
    PGA: int = 1            # 0,  1,  2,  3
    PGA_value: int = 1      # 1,  2,  4,  8
    SPS: int = 12           # 12,  8,  4,  0
    SPS_value: int = 15     # 15, 30, 60, 240

""" After instantiating, you should call selfConfigure to set the local parameters to match the ADC chip. (Or WriteConfig will do the same.)  """
class PiHatSensor:
    def __init__(self, busno):
        self.bus = SMBus(busno)
        self.stdevs = []
        self.waits = []
        self.PGA = 0
        self.DR = 0
        self.min = 0
        self.max = 0

    def selfConfigure(self):
        """Configures this object instance parameters from the ADC chip config"""
        cs = self.ADCReadConfigStruct()
        self.PGA = cs.PGA
        self.DR = cs.SPS

    def ADCReadVoltage(self):
        [v, c] = self.convert(self.ADCReadData())
        return [v, c]

    def ADCReadNewVoltage(self):
        [v, c] =  self.convert(self.ADCReadNewData())
        return [v, c] 

    def ADCReadVoltageWithData(self):
        sample = self.ADCReadData()
        [voltage, clip]  = self.convert(sample)
        return [voltage, clip, sample]

    def ADCReadNewVoltageWithData(self):
        sample = self.ADCReadNewData()
        [voltage, clip]  = self.convert(sample)
        return [voltage, clip, sample]

    def getConfig(self):
        return [self.PGA, MIN_CODE, MAX_V, VIN_NEG, self.DR]

    def printConfig(self):
        print(f"PGA={self.PGA}, MIN_CODE={MIN_CODE}, MAX_V={MAX_V}, VIN_NEG={VIN_NEG}, DR={self.DR}")

    def ADCReadVoltageAverage(self, no_samples, interval):
        samples = []
        for n in range(no_samples):
            sample = self.ADCReadVoltage()
            samples.append(sample)
            #print(f"{n} {sample}")
            time.sleep(interval)
        avg = np.mean(samples)
        self.stdevs.append(np.std(samples))
        return avg

    # Returns the [mean, stddev] of all the stdevs of each sample
    def getStdev(self):
        return [np.mean(self.stdevs), np.std(self.stdevs)]

    def ADCReadData(self):
        # Read 3 bytes from device
        msg = i2c_msg.read(addr, 3)
        val = self.bus.i2c_rdwr(msg)
        return list(msg)

    # Ensures the voltage reading is new (unread) by waiting for DRDY
    def ADCReadNewData(self):
        wait = 0
        read = True
        while(read):
            # Read 3 bytes from device (16bit data and config)
            bytes = self.ADCReadData()
            #print(list(bytes))
            NDRDY = bytes[2] & CFM_DRDY
            read = NDRDY == 128
            #print(f"NDRDY={NDRDY} read={read}")
            wait = wait + 1
        self.waits.append(wait-1)
        return bytes

    # Returns the [waits, mean, stddev] of all the waits for each "new data" read
    def getWaits(self):
        #print(self.waits)
        return [self.waits, np.mean(self.waits), np.std(self.waits)]

    def ADCReadConfig(self):
        data = self.ADCReadData()
        return data[2]

    def ADCReadConfigStruct(self):
        """Reads the ADC config and returns it as a Config structure, does not sync the local params"""
        conf = self.ADCReadConfig()
        PGA = conf & CFM_PGA
        DR = conf & CFM_DR
        print("read conf byte 0x%x %d PGA=#%d DR=#%d"%(conf, conf, PGA, DR))
        return ConfigStruct(PGA=PGA, PGA_value=PGA_VALUES[PGA], SPS=DR, SPS_value=DR_VALUES[DR])

    #def ADCWriteConfig(self):
    #    # TODO calculate config from settings!
    #    conf = PGA | (DR << 2) | (SC <<4)
    #    print(f"write H/C conf={conf:02x}H")
    #    self.bus.write_byte(addr, conf)

    def ADCWriteConfigValues(self, PGA_value, SPS_value):
        """ Updates the ADC chip config, and syncs the local params """
        self.PGA = PGA_OPTIONS[PGA_value]
        self.DR = DR_OPTIONS[SPS_value]
        conf = self.PGA | self.DR | SC
        print(f"write PGA={self.PGA} DR={self.DR} SC={SC} conf={conf:02x}H")
        self.bus.write_byte(addr, conf)

    def shutdown(self):
        self.bus.close()

    # code = 16 bits of data, and 1 byte of config
    # Note the config could be parsed right now to get the settings
    # returns [vin, clip] where vin is the sampled voltage and clip = None, -1 or +1 
    def convert(self, bytes):
        #print("convert bytes %d %d"%(bytes[0], bytes[1]))
        out = bytes[0] * 256 + bytes[1]

        # Convert from two's complement (0-7FFF is the positive range, 8000-FFFF is the negatve range)
        #print("  twos   out:%x %d"%(out, out))
        uout = unsignedToSigned(out, 2)
        #print("  signed out:%d"%(out))

        # Recalculate VIN from the output code equation in the datasheet
        # Output Code = −1 x Min Code x PGA x ( (VIN+ - VIN-) / 2.048V )
        # VIN+ = ( Output Code * MAXV / (−1 x Min Code x PGA)) + VIN-
        vin = (uout * MAX_V / ( -1 * MIN_CODE * PGA_VALUES[self.PGA])) + VIN_NEG
        #print(f"{vin} = ({out} * {MAX_V} / ( -1 * {MIN_CODE} * {PGA_VALUES[self.PGA]})) + {VIN_NEG} ")


        if out == DR_MAX[self.DR]: 
            clip = +1    
        elif out == DR_MIN[self.DR]: 
            clip = -1
        else: 
            clip = None
            #print("self.DR", self.DR, "DR_MIN[self.DR]:", DR_MIN[self.DR], "vin", vin, "out", out, "uout", uout, "clip", clip)

        return [vin, clip]


def unsignedToSigned(n, byte_count):
    return int.from_bytes(n.to_bytes(byte_count, 'little', signed=False), 'little', signed=True)


