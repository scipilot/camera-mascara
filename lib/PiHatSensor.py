import time
from smbus2 import SMBus, i2c_msg
import numpy as np

# This wraps accessing the Pi Hat ADC via I2C
# Note you cannot use functions like bus.write_byte_data with the ADS1110 aa they select a register which it doesn't have.

# device address
addr = 0x48 # The "ED0" ADS1110A0I chip address

# this is default config 0x0C (could be reported back as 0x8C due to data-ready flag bit)
PGA = 1
MIN_CODE = -32768
MAX_V = 2.048
SAMPLES_PER_SECOND = 12

class PiHatSensor:
	def __init__(self, busno):
		self.bus = SMBus(busno)
		self.stdevs = []

	def ADCReadVoltage(self):
		return self.convert(self.ADCReadData())

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
		# Read 3 bytes from address  48H
		msg = i2c_msg.read(addr, 3)
		val = self.bus.i2c_rdwr(msg)
		return list(msg)

	def ADCWriteConfig(self):
		self.bus.write_byte(addr, 0x8C)

	def shutdown(self):
		self.bus.close()

	# 16 bits of data, and 1 byte of config
	# Note the config could be parsed right now to get the settings
	def convert(self, bytes):
		#print("convert bytes %d %d"%(bytes[0], bytes[1]))
		out = bytes[0] * 255 + bytes[1]
		# VIN+ = 2.048V x −1 x Min Code x PGA / Output Code
		vin = MAX_V * -1 * MIN_CODE * PGA / out
		return vin
