import sensor, image, lcd, time
import KPU as kpu
import gc, sys
import drv8833
import time

d = None

def lcd_Show_display():

    lcd.init()
    img = image.Image()
    img.draw_string(20,100,"LilyGO running ...",scale=2)
    time.sleep(2)
    img = image.Image("/sd/lilygo.jpg")
    lcd.display(img)
    #lcd.init()
    #lcd.draw_string(100,100,"LilyGO running ...",lcd.RED,lcd.BLACK)

def start_runnig():
    d.left_after()
    time.sleep(3)
    d.right_after()
    time.sleep(3)
    d.forward()
    time.sleep(3)
    d.brake()

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


#Abnormal data display
def lcd_show_except(e):
    import uio
    err_str = uio.StringIO()
    sys.print_exception(e, err_str)
    err_str = err_str.getvalue()
    img = image.Image(size=(224,224))
    img.draw_string(0, 10, err_str, scale=1, color=(0xff,0x00,0x00))
    lcd.display(img)

def main(model_addr=0x300000, lcd_rotation=0, sensor_hmirror=False, sensor_vflip=False):
    try:
        sensor.reset(dual_buff=True)
    except Exception as e:
        raise Exception("sensor reset fail, please check hardware connection, or hardware damaged! err: {}".format(e))
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.set_hmirror(sensor_hmirror)
    sensor.set_vflip(sensor_vflip)
    sensor.run(1)

    lcd.init(type=1)
    lcd.rotation(lcd_rotation)
    #lcd.mirror(True)
    lcd.clear(lcd.WHITE)
    global d

    anchors = (1.889, 2.5245, 2.9465, 3.94056, 3.99987, 5.3658, 5.155437, 6.92275, 6.718375, 9.01025)
    try:
        status = "None"
        task = None
        task = kpu.load(model_addr)
        kpu.init_yolo2(task, 0.5, 0.3, 5, anchors) # threshold:[0,1], nms_value: [0, 1]
        while(True):
            img = sensor.snapshot()
            t = time.ticks_ms()
            objects = kpu.run_yolo2(task, img)
            t = time.ticks_ms() - t
            if objects:
                for obj in objects:
                    location = obj.rect()
                    img.draw_rectangle(location)
                    x = location[0] + int(location[2]/2)
                    y = location[1] + int(location[3]/2)
                    #print("x: {}, y: {}".format(x, y))
                    if x < 120 and y < 80:
                        d.left_after() # 1 left_after
                        img = image.Image("/sd/Right.jpg")
                        status = "Right"
                    elif x >= 120 and x < 200 and y < 115:
                        d.reverse() # 2 reverse
                        img = image.Image("/sd/Up.jpg")
                        status = "Reverse"
                    elif x >= 200 and y < 80:
                        d.right_after() # 3
                        img = image.Image("/sd/Left.jpg")
                        status = "Left"
                    elif x < 120 and y >= 80 and y < 160:
                        d.left_after() # 4
                        img = image.Image("/sd/Right.jpg")
                        status = "Right"
                    elif x >= 120 and x < 200 and y >= 115 and y < 160:
                        d.brake() # 5
                        img = image.Image("/sd/Stop.jpg")
                        status = "Brake"
                    elif x >= 200 and y >= 80 and y < 160:
                        d.right_after() # 6
                        img = image.Image("/sd/Left.jpg")
                        status = "Left"
                    elif x < 120 and y >= 160:
                        d.turn_right() # 7
                        img = image.Image("/sd/Right.jpg")
                        status = "Right"
                    elif x >= 120 and x < 200 and y >= 160:
                        d.forward() # 8
                        img = image.Image("/sd/Down.jpg")
                        status = "Forward"
                    elif x >= 200 and y >= 160:
                        d.turn_left() # 9
                        img = image.Image("/sd/Left.jpg")
                        status = "Left"
                    img.draw_string(obj.x(),obj.y(),status,color=(255,0,0),scale=2)
            else:
                d.coast()
                img = image.Image("/sd/Stop.jpg")
            img.draw_string(0, 200, "t:%dms" %(t), scale=2)
            lcd.display(img)

    except Exception as e:
        d.avtive(False)
        raise e
    finally:
        if not task is None:
            kpu.deinit(task)


if __name__ == "__main__":
    lcd_Show_display()
    d = drv8833.DRV8833(2, 22, 21, 15, 13)
    d.avtive(True)
    d.brake()
    start_runnig()
    try:
        main( model_addr=0x300000, lcd_rotation=2, sensor_hmirror=False, sensor_vflip=False)
    except Exception as e:
        sys.print_exception(e)
        lcd_show_except(e)
    finally:
        gc.collect()