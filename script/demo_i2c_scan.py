from machine import I2C
import time
i2c = I2C(I2C.I2C0, freq=400000, scl=30, sda=31)
while True:
    s = i2c.scan()
    print(s)
    time.sleep(1)
