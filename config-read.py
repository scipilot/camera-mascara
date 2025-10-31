from lib.PiHatSensor import PiHatSensor

I2CBUS = 1

# Create a new board wrapper - note it has some settings which control the ADC chip config (sample speed etc)
board = PiHatSensor(I2CBUS)

config = board.ADCReadConfig()
print(f"config:{config:02x}H {config}D")

# board.ADCWriteConfig()


