import time
from smbus2 import SMBus, i2c_msg
import numpy as np

# This wraps accessing the Pi Hat ADC via I2C
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

# CURRENT COFIG
DR = DR_15SPS
PGA = PGA_GAIN_4
SC = SC_CONT  

class PiHatSensor:
    def __init__(self, busno):
        self.bus = SMBus(busno)
        self.stdevs = []
        self.waits = []

    def ADCReadVoltage(self):
        return self.convert(self.ADCReadData())

    def ADCReadNewVoltage(self):
        return self.convert(self.ADCReadNewData())

    def ADCReadVoltageWithData(self):
        sample = self.ADCReadData()
        voltage = self.convert(sample)
        return [voltage, sample]

    def ADCReadNewVoltageWithData(self):
        sample = self.ADCReadNewData()
        voltage = self.convert(sample)
        return [voltage, sample]

    def getConfig(self):
        return [PGA, MIN_CODE, MAX_V, VIN_NEG, SAMPLES_PER_SECOND]

    def printConfig(self):
        print(f"PGA={PGA}, MIN_CODE={MIN_CODE}, MAX_V={MAX_V}, VIN_NEG={VIN_NEG}, SAMPLES_PER_SECOND={SAMPLES_PER_SECOND}")

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
            NDRDY = bytes[2] & 1 << CFG_DRDY
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

    def ADCWriteConfig(self):
        # TODO calculate config from settings!
        conf = PGA | (DR << 2) | (SC <<4)
        print(f"conf={conf:02x}H")
        self.bus.write_byte(addr, conf)

    def shutdown(self):
        self.bus.close()

    # code = 16 bits of data, and 1 byte of config
    # Note the config could be parsed right now to get the settings
    def convert(self, bytes):
        #print("convert bytes %d %d"%(bytes[0], bytes[1]))
        out = bytes[0] * 255 + bytes[1]

        # Convert from two's complement (0-7FFF is the positive range, 8000-FFFF is the negatve range)
                                     #print("  twos   out:%d"%(out))
        out = unsignedToSigned(out, 2)
        #print("  signed out:%d"%(out))

        # Recalculate VIN from the output code equation in the datasheet
        # Output Code = −1 x Min Code x PGA x ( (VIN+ - VIN-) / 2.048V )
        # VIN+ = ( Output Code * MAXV / (−1 x Min Code x PGA)) + VIN-
        vin = (out * MAX_V / ( -1 * MIN_CODE * PGA)) + VIN_NEG
        return vin


def unsignedToSigned(n, byte_count):
    return int.from_bytes(n.to_bytes(byte_count, 'little', signed=False), 'little', signed=True)


