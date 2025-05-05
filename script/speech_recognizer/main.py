import time
from Maix import GPIO, I2S
from fpioa_manager import fm
import os, Maix, lcd, image
from speech_recognizer import isolated_word
import axp202
from machine import I2C
import gc, sys


# 初始化 LCD 打开电源通道
def init_lcd():
    i2c = I2C(I2C.I2C0, freq = 400000, scl = 30, sda = 31)
    p = None
    p = axp202.PMU(i2c, 0x35)
    p.setShutdownTime(axp202.AXP202_SHUTDOWN_TIME_4S)
    p.setLDO2Voltage(1800)
    p.enablePower(axp202.AXP192_LDO2)
    p.enablePower(6)
    p.setLDO3Mode(1)


    lcd.init(freq=15000000)
    fm.register(17,fm.fpioa.GPIO0)
    led=GPIO(GPIO.GPIO0,GPIO.OUT)
    led.value(1)



# 函数：显示提示信息
def display_message(message, color=(255, 0, 0), scale=2, mono_space=0):
    img.draw_rectangle((0, 0, 240, 240), fill=True, color=(255, 255, 255))
    img.draw_string(10, 80, message, color=color, scale=scale, mono_space=mono_space)
    lcd.display(img)

# 函数：录制语音并保存
# def record_word(index, prompt):
#     display_message(prompt, scale=2)
#     while True:
#         time.sleep_ms(50)
#         if sr.Done == sr.record(index):
#             data = sr.get(index)
#             print("Recorded data for %s :%s ",prompt,data)
#             break
#         if sr.Speak == sr.state():
#             print("Speak %s",prompt)
#     sr.set(index + 1, data)
#     display_message("get !", scale=2)
#     time.sleep_ms(10)

# # 录制三个单词
# record_word(0, "Please speak Right")
# record_word(2, "Please speak left")
# record_word(4, "Please speak go")

# # 开始识别
# display_message("Recognition begin", scale=3)
# time.sleep_ms(1000)
def record_word(target_idx, prompt_msg):
    print("say %s",prompt_msg)
    while True:
        time.sleep_ms(100)
        state = sr.state()
        if state == sr.Done:
            if sr.record(target_idx):
                data = sr.get(target_idx)
                return data
        elif state == sr.Speak:
            print("say %s",prompt_msg)

# 运行主程序
if __name__ == "__main__":

    # 初始化硬件
    sample_rate = 16000
    img = image.Image(size=(240, 240))
    fm.register(20, fm.fpioa.I2S0_IN_D0, force=True)
    fm.register(19, fm.fpioa.I2S0_WS, force=True)    # 19 on Go Board and Bit(new version)
    fm.register(18, fm.fpioa.I2S0_SCLK, force=True)  # 18 bit

    # 初始化 I2S
    rx = I2S(I2S.DEVICE_0)
    rx.channel_config(rx.CHANNEL_0, rx.RECEIVER, align_mode=I2S.STANDARD_MODE)
    rx.set_sample_rate(sample_rate)

    # 初始化语音识别器
    sr = isolated_word(dmac=2, i2s=I2S.DEVICE_0, size=10, shift=0)
    sr.set_threshold(0, 0, 10000)
    
    init_lcd()

    record_word(0, "RIGHT")
    sr.set(1, sr.get(0))

    # 录制left到模板3
    record_word(2, "left")
    sr.set(3, sr.get(2))

    # 录制go到模板5
    record_word(4, "go")
    sr.set(5, sr.get(4))

    print("start recognition...")
    sr.run()
    try:
    # 识别循环
        while True:
            time.sleep_ms(200)
            if sr.recognize() == sr.Done:
                res = sr.result()
                if res is None:
                   print("No recognition result")
                   continue
                if res[1] < 3:  # 相似度阈值
                    continue
                if res[0] == 0 or res[0] == 1:
                    print("get: RIGHT")
                    display_message("R", scale=10) 
                elif res[0] == 2 or res[0] == 3:
                    print("get: left")
                    display_message("L", scale=10) 
                elif res[0] == 4 or res[0] == 5:
                    print("get: go")    
                    display_message("GO", scale=10)
                else:
                    print("nothing")
                    print(res[0])
                del res
                gc.collect()
    except Exception as e:
        raise e
    finally:
        gc.collect()