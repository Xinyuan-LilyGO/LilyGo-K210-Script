import touchscreen as ts
from machine import I2C
import lcd, image,time,utime,sensor,network,pcf8563,os,audio
from fpioa_manager import *
from Maix import I2S, GPIO, FFT

HW_ESP32 = False
HW_MPU6050 = False
HW_CAMERA = False
HW_RTC = False
HW_TOUCH = False

mpu6050_addr = 0x68

def bytes_toint(firstbyte, secondbyte):
    if not firstbyte & 0x80:
        return firstbyte << 8 | secondbyte
    return - (((firstbyte ^ 255) << 8) | (secondbyte ^ 255) + 1)

def get_values():
    vals = {}
    try:
        raw_ints = i2c.readfrom_mem(mpu6050_addr, 0x3B, 14)
        vals["AcX"] = bytes_toint(raw_ints[0], raw_ints[1])
        vals["AcY"] = bytes_toint(raw_ints[2], raw_ints[3])
        vals["AcZ"] = bytes_toint(raw_ints[4], raw_ints[5])
        vals["Tmp"] = bytes_toint(raw_ints[6], raw_ints[7]) / 340.00 + 36.53
        vals["GyX"] = bytes_toint(raw_ints[8], raw_ints[9])
        vals["GyY"] = bytes_toint(raw_ints[10], raw_ints[11])
        vals["GyZ"] = bytes_toint(raw_ints[12], raw_ints[13])
    except:
        vals["AcX"] = 0
        vals["AcY"] = 0
        vals["AcZ"] = 0
        vals["Tmp"] = 0
        vals["GyX"] = 0
        vals["GyY"] = 0
        vals["GyZ"] = 0
    return vals  # returned in range of Int16




def play_music(filename):
    fm.register(34,fm.fpioa.I2S1_OUT_D1)
    fm.register(35,fm.fpioa.I2S1_SCLK)
    fm.register(33,fm.fpioa.I2S1_WS)
    wav_dev = I2S(I2S.DEVICE_1)
    player = audio.Audio(path = filename)
    player.volume(20)
    wav_info = player.play_process(wav_dev)
    print("wav file head information: ", wav_info)
    wav_dev.channel_config(wav_dev.CHANNEL_1,
                            I2S.TRANSMITTER,
                            resolution = I2S.RESOLUTION_16_BIT ,
                            cycles = I2S.SCLK_CYCLES_32,
                            align_mode = I2S.LEFT_JUSTIFYING_MODE)
    wav_dev.set_sample_rate(wav_info[1])
    while True:
        ret = player.play()
        if ret == None:
            print("format error")
            break
        elif ret==0:
            print("end")
            break
    player.finish()
    player.__deinit__()
    wav_dev.__deinit__()



lcd_rotation = 1
widht = 240
height = 240
x_last = 0
y_last = 0
datetime_str = ' '
ver_str = ' '
pir_str = ' '

img = image.Image(size=(widht, height))

lcd.init(freq=15000000)
#lcd.rotation(lcd_rotation)
lcd.clear(lcd.RED)

# backlight part
fm.register(17, fm.fpioa.GPIO0)
bl = GPIO(GPIO.GPIO0, GPIO.OUT)
bl.value(1)


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

# led part
fm.register(22, fm.fpioa.GPIO2)
led = GPIO(GPIO.GPIO2, GPIO.OUT)
led.value(1)

# pir part
fm.register(23, fm.fpioa.GPIO3)
pir = GPIO(GPIO.GPIO3, GPIO.IN)



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


# microphone part
fm.register(20, fm.fpioa.I2S0_IN_D0)
fm.register(19, fm.fpioa.I2S0_WS)
fm.register(18, fm.fpioa.I2S0_SCLK)
mic = I2S(I2S.DEVICE_0)
mic.channel_config(mic.CHANNEL_0, mic.RECEIVER,align_mode=I2S.STANDARD_MODE)
mic.set_sample_rate(38640)


try:
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(time=2000)
    HW_CAMERA = True
except:
    print('HAL CAMERA FAILED')

millis = utime.ticks_ms();

try:
    i2c.writeto(mpu6050_addr, bytearray([107, 0]))
    HW_MPU6050 = True
except:
    HW_MPU6050 = False
    print('HAL MPU6050 FAILED')

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
        new = img.copy(roi=(0, 0, 239, 239))
        img = new



    audio = mic.record(1024)
    fft_res = FFT.run(audio.to_bytes(), 512)
    fft_amp = FFT.amplitude(fft_res)
    x_shift = 0
    for i in range(50):
        if fft_amp[i] > 240:
            hist_height = 240
        else:
            hist_height = fft_amp[i]
        hist_width = int(240 / 50)
        img.draw_rectangle((x_shift, 240-hist_height, hist_width, hist_height),
                           [255, 255, 255],
                           2,
                           True)
        x_shift = x_shift + hist_width
    fft_amp.clear()

    point = 'rotation:%d-x:%03d-y:%03d' % (lcd_rotation,x,y)


    img.draw_string(0,0,point,color=(0xFF,0,0))

    if x != 0 and y != 0:
        img.draw_line((x_last, y_last, x, y))

    if HW_MPU6050:
        data = get_values()
        accel_str = 'ACC: \n x:%06f\n y:%06f\n z:%06f' % (data['AcX'],data['AcY'],data['AcZ'])
        gyro_str  = 'Gyr: \n x:%06f\n y:%06f\n z:%06f' % (data['GyX'],data['GyY'],data['GyZ'])
    else:
        accel_str = 'ACC: \n x:0\n y:0\n z:0 ERROR!!'
        gyro_str  = 'Gyr: \n x:0\n y:0\n z:0 ERROR!!'

    img.draw_string(0,32,accel_str,color=(0xFF,0,0))
    img.draw_string(0,96,gyro_str,color=(0xFF,0,0))

    if utime.ticks_ms() - millis > 1000:
        millis = utime.ticks_ms();
        if HW_RTC:
            datetime = rtc.datetime()
            datetime_str='%d/%02d/%02d-%02d:%02d:%02d' % (datetime[0] + 2000,datetime[1],datetime[2],datetime[4],datetime[5],datetime[6])
        else:
            datetime_str='RTC ERROR'

        if HW_ESP32:
            ver_str = 'ESP32 ver_strion: %s'% (nic.version())
        else:
            ver_str = 'ESP32 ver_strion: ERROR'

    if pir.value():
        pir_str = 'PIR TRIGGER'
        led.value(0)
    else:
        pir_str = 'PIR STATIC'
        led.value(1)

    img.draw_string(0,16,datetime_str,color=(0xFF,0,0))
    img.draw_string(0,156,ver_str,color=(0xFF,0,0))
    img.draw_string(0,176,pir_str,color=(0xFF,0,0))
    lcd.display(img)
    img.__del__

    x_last = x
    y_last = y
    #print(point)





