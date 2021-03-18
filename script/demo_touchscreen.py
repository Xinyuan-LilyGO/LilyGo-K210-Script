import touchscreen as ts
from machine import I2C
import lcd, image
from board import board_info
from fpioa_manager import fm
from Maix import GPIO

fm.register(board_info.BOOT_KEY, fm.fpioa.GPIO1, force=True)
btn_clear = GPIO(GPIO.GPIO1, GPIO.IN)


lcd.init(freq=15000000)
i2c = I2C(I2C.I2C0, freq=400000, scl=30, sda=31)
ts.init(i2c,ts.FT62XX)
#ts.calibrate()
lcd.clear()
img = image.Image()
status_last = ts.STATUS_IDLE
x_last = 0
y_last = 0
lcd_rotation = 2
draw = False
while True:
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

    print(status, x, y)
    if draw:
        img.draw_line((x_last, y_last, x, y))
    if status_last!=status:
        if (status==ts.STATUS_PRESS or status == ts.STATUS_MOVE):
            draw = True
        else:
            draw = False
        status_last = status
    lcd.display(img)
    x_last = x
    y_last = y

    if btn_clear.value() == 0:
        img.clear()


