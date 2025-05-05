import machine
import time
from fpioa_manager import fm
from machine import UART
import time
import utime

fm.register(6, fm.fpioa.UART1_TX)
fm.register(7, fm.fpioa.UART1_RX)

Serial = UART(UART.UART1, 115200, 8, None, 1, timeout=1000, read_buf_len=4096)

def send_at_coommand(command):
    Serial.write(command)
    print(command+ ' send')
    time.sleep(1)
    response = Serial.read()
    return response

class DRV8833():
    def __init__(self, EN, AIN1, AIN2, BIN1, BIN2):
        #self.en = machine.Pin(EN, machine.Pin.OUT)
        #self.ain1 = machine.Pin(AIN1, machine.Pin.OUT)
        #self.ain2 = machine.Pin(AIN2, machine.Pin.OUT)
        #self.bin1 = machine.Pin(BIN1, machine.Pin.OUT)
        #self.bin2 = machine.Pin(BIN2, machine.Pin.OUT)
        self.en = EN
        self.ain1 = AIN1
        self.ain2 = AIN2
        self.bin1 = BIN1
        self.bin2 = BIN2
        Serial.write('AT+DRVPWMINIT=1000,8,{},{},{},{}\r\n'.format(AIN1, AIN2, BIN1, BIN2))
        Serial.readline()
        Serial.readline()
        Serial.readline()
        self.avtive(False)
        self.status = False

    def avtive(self, is_active):
        if is_active == True:
            Serial.write('AT+SGPIO={},{}\r\n'.format(self.en, 1))
            Serial.readline()
            Serial.readline()
            Serial.readline()
            self.status = True
        else:
            #pass
            Serial.write('AT+SGPIO={},{}\r\n'.format(self.en, 0))
            Serial.readline()
            Serial.readline()
            Serial.readline()
            self.status = False

        return self.status
    def forward(self):
        if self.status:
            #Serial.print("forward")
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.ain1, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.ain2, 1))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.bin1, 1))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.bin2, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            Serial.write('AT+DRVPWMDUTY={},{},{},{}\r\n'.format(0,60,60,0))
            Serial.readline()
            Serial.readline()
            Serial.readline()
            # self.ain1.value(0)
            # self.ain2.value(1)
            # self.bin1.value(1)
            # self.bin2.value(0)
    def reverse(self):
        if self.status:
            #Serial.print("reverse")
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.ain1, 1))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.ain2, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.bin1, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.bin2, 1))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            Serial.write('AT+DRVPWMDUTY={},{},{},{}\r\n'.format(60, 0, 0, 60))
            Serial.readline()
            Serial.readline()
            Serial.readline()
            #self.ain1.value(1)
            #self.ain2.value(0)
            #self.bin1.value(0)
            #self.bin2.value(1)

    def coast(self):
        if self.status:
            #Serial.print("coast")
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.ain1, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.ain2, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.bin1, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.bin2, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            Serial.write('AT+DRVPWMDUTY={},{},{},{}\r\n'.format(0, 0, 0, 0))
            Serial.readline()
            Serial.readline()
            Serial.readline()
            #self.ain1.value(0)
            #self.ain2.value(0)
            #self.bin1.value(0)
            #self.bin2.value(0)

    def brake(self):
        if self.status:
            #Serial.print("brake")
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.ain1, 1))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.ain2, 1))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.bin1, 1))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.bin2, 1))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            Serial.write('AT+DRVPWMDUTY={},{},{},{}\r\n'.format(255, 255, 255, 255))
            Serial.readline()
            Serial.readline()
            Serial.readline()
            #self.ain1.value(1)
            #self.ain2.value(1)
            #self.bin1.value(1)
            #self.bin2.value(1)

    def turn_left(self):
        if self.status:
            #Serial.print("turn_left")
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.ain1, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.ain2, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.bin1, 1))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.bin2, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            Serial.write('AT+DRVPWMDUTY={},{},{},{}\r\n'.format(0, 0, 80, 0))
            Serial.readline()
            Serial.readline()
            Serial.readline()
            #self.ain1.value(0)
            #self.ain2.value(0)
            #self.bin1.value(1)
            #self.bin2.value(0)

    def turn_right(self):
        if self.status:
            #Serial.print("turn_right")
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.ain1, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.ain2, 1))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.bin1, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.bin2, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            Serial.write('AT+DRVPWMDUTY={},{},{},{}\r\n'.format(0, 80, 0, 0))
            Serial.readline()
            Serial.readline()
            Serial.readline()
            #self.ain1.value(0)
            #self.ain2.value(1)
            #self.bin1.value(0)
            #self.bin2.value(0)

    def left_after(self):
        if self.status:
            #Serial.print("left_after")
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.ain1, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.ain2, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.bin1, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.bin2, 1))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            Serial.write('AT+DRVPWMDUTY={},{},{},{}\r\n'.format(0, 0, 0, 80))
            Serial.readline()
            Serial.readline()
            Serial.readline()
            #self.ain1.value(0)
            #self.ain2.value(0)
            #self.bin1.value(0)
            #self.bin2.value(1)

    def right_after(self):
        if self.status:
            #Serial.print("right_after")
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.ain1, 1))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.ain2, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.bin1, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            #Serial.write('AT+SGPIO=0,{},1,{}\r\n'.format(self.bin2, 0))
            #Serial.readline()
            #Serial.readline()
            #Serial.readline()
            Serial.write('AT+DRVPWMDUTY={},{},{},{}\r\n'.format(80, 0, 0, 0))
            Serial.readline()
            Serial.readline()
            Serial.readline()
            #self.ain1.value(1)
            #self.ain2.value(0)

            #self.bin1.value(0)
            #self.bin2.value(0)

if __name__ == "__main__":
    '''
    T-WATCH V1.7:
        3V3  --- nSLEEP
        IO26 --- AIN1 # left motor
        IO25 --- AIN2 # left motor
        IO13 --- BIN1 # right motor
        IO15 --- BIN2 $ right motor
    '''
    d = DRV8833(2, 22, 21, 15, 13)
    d.avtive(True)
    d.reverse()
    time.sleep(5)
    d.brake()
    d.avtive(False)



