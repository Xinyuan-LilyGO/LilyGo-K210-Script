# Face Tracking

# Hardware

[T-Bao K210 version](https://www.aliexpress.com/item/1005001511367578.html)

# Firmware

The following firmware needs to be uploaded to esp32 and k210 respectively:

- ESP32 Firmware: [ESP32_AT_Firmware_UART1_SGPIO.bin](../../firmware/ESP32_AT_Firmware_UART1_SGPIO.bin)

- K210 Firmware: [maixpy_twatch_v0.6.2-75-g973361c0d-dirty.bin](../..//firmware/maixpy_twatch_v0.6.2-75-g973361c0d-dirty.bin)

- face model: [face_model_at_0x300000.kfpkg](./face_model_at_0x300000.kfpkg)

# Script

Upload drv8833.py and main.py 
Upload up.jpg,down.jpg,left.jpg,right.jpg & stop.jpg 
