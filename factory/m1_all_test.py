import touchscreen as ts
from machine import I2C
import lcd, image,time,utime,sensor,network,pcf8563,os
from fpioa_manager import *
from Maix import GPIO
from modules import ws2812

HW_ESP32 = False
HW_CAMERA = False
HW_RTC = False
HW_TOUCH = False

color_map= [(0xff,0,0),(0,0xff,0),(0,0,0xff),(0xff,0xff,0),(0xff,0,0xff),(0x40,0,80)]

lcd_rotation = 2
widht = 320
height = 240
x_last = 0
y_last = 0
datetime_str = ' '
color_index = 0
ver_str = ''

img = image.Image(size=(widht, height))

lcd.init(freq=15000000)
lcd.clear(lcd.RED)

# backlight part
fm.register(17, fm.fpioa.GPIO0)
bl = GPIO(GPIO.GPIO0, GPIO.OUT)
bl.value(1)

class_ws2812 = ws2812(22,1)

print(os.listdir('/'))
if 'sd' in os.listdir('/'):
    img.draw_string(0,0, 'SdCard in...',color=(0,0xFF,0))
    img.draw_string(0,16,'SdCard in...',color=(0,0xFF,0))
    img.draw_string(0,32,'SdCard in...',color=(0,0xFF,0))
    img.draw_string(0,48,'SdCard in...',color=(0,0xFF,0))
    lcd.display(img)
else:
    img.draw_string(0,0, 'SdCard lost...',color=(0xFF,0,0))
    img.draw_string(0,16,'SdCard lost...',color=(0xFF,0,0))
    img.draw_string(0,32,'SdCard lost...',color=(0xFF,0,0))
    img.draw_string(0,48,'SdCard lost...',color=(0xFF,0,0))
    lcd.display(img)

time.sleep(1)


# button part
fm.register(board_info.BOOT_KEY, fm.fpioa.GPIO1)
button = GPIO(GPIO.GPIO1, GPIO.IN)


try:
    i2c = I2C(I2C.I2C0, freq=400000, scl=30, sda=31)
    ts.init(i2c,ts.FT62XX)
    HW_TOUCH = True
except:
    print('HAL TOUCH FAILED')

try:
    rtc = pcf8563.PCF8563(i2c)
    rtc.set_datetime((2021,3,1,12,0,0,3))
    HW_RTC = True
except:
    print('HAL RTC FAILED')


img.clear()
img.draw_string(0,0,'Starting Camera ...',color=(0xFF,0,0))
img.draw_string(0,16,'Starting Camera ...',color=(0xFF,0,0))
img.draw_string(0,32,'Starting Camera ...',color=(0xFF,0,0))
img.draw_string(0,48,'Starting Camera ...',color=(0xFF,0,0))
lcd.display(img)
img.__del__

# esp32 part
fm.register(25,fm.fpioa.GPIOHS10)#cs
fm.register(8,fm.fpioa.GPIOHS11)#rst
fm.register(9,fm.fpioa.GPIOHS12)#rdy
fm.register(28,fm.fpioa.GPIOHS13)#mosi
fm.register(26,fm.fpioa.GPIOHS14)#miso
fm.register(27,fm.fpioa.GPIOHS15)#sclk

try:
    nic = network.ESP32_SPI(cs=fm.fpioa.GPIOHS10,
                            rst=fm.fpioa.GPIOHS11,
                            rdy=fm.fpioa.GPIOHS12,
                            mosi=fm.fpioa.GPIOHS13,
                            miso=fm.fpioa.GPIOHS14,
                            sclk=fm.fpioa.GPIOHS15)
    HW_ESP32 = True
except:
    print('HAL ESP32 FAILED')

try:
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(time=2000)
    HW_CAMERA = True
except:
    print('HAL CAMERA FAILED')

millis = utime.ticks_ms();

while True:
    if button.value()==0:
        while button.value()==0:
            pass
        lcd_rotation += 1
        lcd_rotation %= 4
        lcd.rotation(lcd_rotation)

    status = 0
    x=0
    y=0
    if HW_TOUCH:
        (status, x, y) = ts.read()
        if (status == ts.STATUS_PRESS or status == ts.STATUS_MOVE):
            if lcd_rotation == 0:
                widht,height = lcd.width(),lcd.height()
                x,y = y,x
                x = lcd.width() - x

            elif lcd_rotation == 1:
                widht,height = lcd.width(),lcd.height()

            elif lcd_rotation == 2:
                widht,height = lcd.width(),lcd.height()
                x,y = y,x
                y = lcd.height() - y

            elif lcd_rotation == 3:
                widht,height = lcd.width(),lcd.height()
                x = widht - x
                y = height - y

    img = image.Image(size=(widht, height))

    if HW_CAMERA:
        img = sensor.snapshot()

    if lcd_rotation == 1 or lcd_rotation == 3:
        new = img.resize(240,320)
        img = new

    point = 'rotation:%d-x:%03d-y:%03d' % (lcd_rotation,x,y)

    img.draw_string(0,0,point,color=(0xFF,0,0))

    if x != 0 and y != 0:
        img.draw_line((x_last, y_last, x, y))


    if utime.ticks_ms() - millis > 1000:
        millis = utime.ticks_ms()
        class_ws2812.set_led(0,color_map[color_index])
        color_index = color_index + 1
        color_index %= len(color_map)
        class_ws2812.display()
        if HW_RTC:
            datetime = rtc.datetime()
            datetime_str='%d/%02d/%02d-%02d:%02d:%02d' % (datetime[0] + 2000,datetime[1],datetime[2],datetime[4],datetime[5],datetime[6])
        else:
            datetime_str='RTC ERROR'

        if HW_ESP32:
            ver_str = 'ESP32 ver_strion: %s'% (nic.version())
        else:
            ver_str = 'ESP32 ver_strion: ERROR'


    img.draw_string(0,16,datetime_str,color=(0xFF,0,0))
    img.draw_string(0,36,ver_str,color=(0xFF,0,0))
    lcd.display(img)
    img.__del__

    x_last = x
    y_last = y

