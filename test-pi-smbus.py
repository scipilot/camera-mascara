# Purpose - this was used to initially test the SMBus2 I2C library against the ADS1110 which had issues
# due to its slightly odd protocol (no registers)
# You can still use it to configure the device or read its config manually.
# but you can now also do that via the Pocketbase API, so this is less used.


# Note you cannot use functions like bus.write_byte_data with the ADS1110 aa they select a register which it doesn't have.

from smbus2 import SMBus, i2c_msg

addr = 0x48 # The "ED0" ADS1110A0I chip address


def ADCReadData(bus, addr):
	# Read 3 bytes from address  48H
	msg = i2c_msg.read(addr, 3)
	val = bus.i2c_rdwr(msg)
	return list(msg)

def ADCWriteConfig(bus,addr):
	bus.write_byte(addr, 0x8C)

# this works, but is not useful
# only reads 1 byte
#b = bus.read_byte(addr,1)
#print(b)

# WONT WORK WITH ADS1110 as it pre-sends a write for the data-address which  overwrites the config!
# HACK: send config as data which does work!
#block = bus.read_i2c_block_data(addr, 0x8C, 4)
#print(block)


with SMBus(1) as bus:
	ADCWriteConfig(bus,addr)

#	data = ADCReadData(bus,addr)
#	print(data)

