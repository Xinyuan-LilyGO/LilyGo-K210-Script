# Face Tracking

# Hardware

[T-Bao K210 version](https://www.aliexpress.com/item/1005001511367578.html)

# Firmware

The following firmware needs to be uploaded to esp32 and k210 respectively:

- ESP32 Firmware: [ESP32_AT_Firmware_UART1_SGPIO.bin](../../firmware/ESP32_AT_Firmware_UART1_SGPIO.bin)

- K210 Firmware: [maixpy_twatch_v0.6.2-75-g973361c0d-dirty.bin](../..//firmware/maixpy_twatch_v0.6.2-75-g973361c0d-dirty.bin)

- face model: [face_model_at_0x300000.kfpkg](./face_model_at_0x300000.kfpkg)

# Start

- Get an sd card You can usually use the sd card that came with your purchase

- Open the K210 terminal and input `os.listdir("/")`, if you see `['flash', 'sd']`, it means the SD card has been successfully detected. If the SD card cannot be read, you can try using the card shown in the image

![San Disk](/image/image.png)

` !  Note: If you use your own sd card, you may not be able to read it`

` ! Ensure that the disk format of the sd card is FAT32 and the disk partition table type is MBR and that the sd card supports the spi protocol`

- Put `up.jpg` `down.jpg` `left.jpg` `right.jpg` `stop.jpg` `lilygo.jpg` `drv8833.py` and `main.py` on a USB flash drive or you can download them to the board's memory via the MaixPy IDE

`The second method may affect the speed of memory reading and the space consumption of large files, so the first method is used here`

