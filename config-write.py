# Purpose - inititally used to configure the ADC chip
# REDUNDANT - I think this won't work now as the config is now dynamic int he PiHatSensor class?
# Alternate method - use the API to configure the ADC gain and samples per second

from lib.PiHatSensor import PiHatSensor

I2CBUS = 1

# Create a new board wrapper - note it has some settings which control the ADC chip config (sample speed etc)
board = PiHatSensor(I2CBUS)

config = board.ADCWriteConfig()



