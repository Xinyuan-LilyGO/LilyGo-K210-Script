import touchscreen as ts
from machine import I2C
import lcd
import image
from fpioa_manager import *
from Maix import GPIO
import pcf8563
import time

lcd.init(freq=15000000)
i2c = I2C(I2C.I2C0, freq=400000, scl=30, sda=31)
r = pcf8563.PCF8563(i2c)
r.set_datetime((2019,11,13,14,3,10,3))
lcd.rotation(1)
while True:
    t = r.datetime()
    strDate = str(t[0] + 2000) + '/' + str(t[1]) +'/'+ str(t[2])
    strTime = str(t[4]) + ':' + str(t[5]) +':'+ str(t[6])
    p = strDate + '>>>' +strTime
    print(p)
    time.sleep(1)
    img = image.Image()
    img.draw_string(0, 100,p , scale=1)
    lcd.display(img)

