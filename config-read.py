# Purpose - manual script to read the raw config from the ADC chip.
# SUPERSEDED - use the API instead. 
# Also the PiHatSensor class now has friendlier functions which parse the result 
#  and return a structured represenation of the gain, data rate etc.


from lib.PiHatSensor import PiHatSensor

I2CBUS = 1

# Create a new board wrapper - note it has some settings which control the ADC chip config (sample speed etc)
board = PiHatSensor(I2CBUS)

config = board.ADCReadConfig()
print(f"config:{config:02x}H {config}D")

# board.ADCWriteConfig()


