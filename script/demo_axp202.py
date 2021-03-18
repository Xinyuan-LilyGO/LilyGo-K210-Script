import axp202
import time
from machine import I2C

i2c = I2C(I2C.I2C0, freq=400000, scl=30, sda=31)
a = axp202.PMU(i2c,0x35)
a.setChgLEDMode(axp202.AXP20X_LED_BLINK_1HZ)

a.enableADC(axp202.AXP202_ADC1, axp202.AXP202_VBUS_VOL_ADC1)
a.enableADC(axp202.AXP202_ADC1, axp202.AXP202_VBUS_CUR_ADC1)
a.enableADC(axp202.AXP202_ADC1, axp202.AXP202_BATT_VOL_ADC1)
a.enableADC(axp202.AXP202_ADC1, axp202.AXP202_BATT_CUR_ADC1)

while True:
    voltage = a.getVbusVoltage()
    current = a.getVbusCurrent()
    battCurrent = a.getBattChargeCurrent()
    perce = a.getBattPercentage()
    print("isChargeing: V: %f C:%f  BC:%f  perce:%d" % (voltage, current, battCurrent,perce))
    time.sleep(1)
