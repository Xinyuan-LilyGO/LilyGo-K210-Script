import sensor, image, lcd, time
import KPU as kpu
import gc, sys
import drv8833
import time
import os
input_size = (224, 224)
d = None
labels = ['left', 'back', 'right', 'forward']
anchors = [1.25, 1.5, 5.16, 6.78, 5.81, 4.81, 2.81, 2.97, 6.69, 3.06]

def lcd_Show_display():

    lcd.init()
    img = image.Image()
    img.draw_string(20,100,"LilyGO running ...",scale=2)
    time.sleep(2)
    img = image.Image("/sd/lilygo.jpg")
    lcd.display(img)
    #lcd.init()
    #lcd.draw_string(100,100,"LilyGO running ...",lcd.RED,lcd.BLACK)

#Abnormal data display
def lcd_show_except(e):
    print(os.listdir("/"))
    import uio
    err_str = uio.StringIO()
    sys.print_exception(e, err_str)
    err_str = err_str.getvalue()
    img = image.Image(size=input_size)
    img.draw_string(0, 10, err_str, scale=1, color=(0xff,0x00,0x00))
    lcd.display(img)

def main(anchors, labels = None, model_addr="/sd/Identify_Direction_model.kmodel", sensor_window=input_size, lcd_rotation=2, sensor_hmirror=False, sensor_vflip=False):
    try:
        sensor.reset(dual_buff=True)
    except Exception as e:
        raise Exception("sensor reset fail, please check hardware connection, or hardware damaged! err: {}".format(e))
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.set_windowing(sensor_window)
    sensor.set_hmirror(sensor_hmirror)
    sensor.set_vflip(sensor_vflip)
    sensor.run(1)

    lcd.init(type=1)
    lcd.rotation(lcd_rotation)
    #lcd.mirror(True)
    lcd.clear(lcd.WHITE)
    global d

    try:
        status = None
        task = kpu.load(model_addr)
        kpu.init_yolo2(task, 0.5, 0.3, 5, anchors) # threshold:[0,1], nms_value: [0, 1]
        while(True):
            img = sensor.snapshot()
            t = time.ticks_ms()
            objects = kpu.run_yolo2(task, img)
            t = time.ticks_ms() - t
            if objects:
                for obj in objects:
                    pos = obj.rect()
                    img.draw_rectangle(pos)
                    img.draw_string(pos[0], pos[1], "%s : %.2f" %(labels[obj.classid()], obj.value()), scale=2, color=(255, 0, 0))
                    if labels[obj.classid()] == 'forward':
                        d.forward() # 1 left_after
                    elif labels[obj.classid()] == 'back':
                        d.reverse()
                    elif labels[obj.classid()] == 'left':
                        d.left_after()
                    elif labels[obj.classid()] == 'right':
                        d.right_after()
            else:
                d.coast()
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
    try:
        main(anchors = anchors, labels=labels, model_addr="/sd/Identify_Direction_model.kmodel")
    except Exception as e:
        sys.print_exception(e)
        lcd_show_except(e)
    finally:
        gc.collect()
