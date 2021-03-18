
import lcd, time

lcd.init(freq=15000000)
#lcd.direction(lcd.XY_RLDU)

lcd.clear(lcd.RED)

lcd.rotation(0)
lcd.draw_string(30, 30, "hello maixpy", lcd.WHITE, lcd.RED)
time.sleep(1)
lcd.rotation(1)
lcd.draw_string(60, 60, "hello maixpy", lcd.WHITE, lcd.RED)
time.sleep(1)
lcd.rotation(2)
lcd.draw_string(120, 60, "hello maixpy", lcd.WHITE, lcd.RED)
time.sleep(1)
lcd.rotation(3)
lcd.draw_string(120, 120, "hello maixpy", lcd.WHITE, lcd.RED)
time.sleep(1)
