from fpioa_manager import fm
from machine import UART
import time
import utime

fm.register(6, fm.fpioa.UART1_TX)
fm.register(7, fm.fpioa.UART1_RX)

Serial = UART(UART.UART1, 115200, 8, None, 1, timeout=1000, read_buf_len=4096)

clock = time.clock()
tick = utime.ticks_ms()
while True:
    if (utime.ticks_ms() - tick) > 3000:
        Serial.write('AT\r\n')
        s = Serial.read()
        print(s)
        tick = utime.ticks_ms()
    