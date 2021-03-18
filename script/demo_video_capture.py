import lcd
import video
import image

lcd.init(freq=15000000)
v = video.open("/sd/badapple.avi")
print(v)
img = image.Image()
while True:
    status = v.capture(img)
    if status != 0:
        lcd.display(img)
    else:
        print("end")
        break;
v.__del__()
