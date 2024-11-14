# 面部跟踪

# Hardware

[T-Bao K210版本](https://www.aliexpress.com/item/1005001511367578.html)

# Firmware

esp32和k210需要分别上传以下固件:

- ESP32固件:[ESP32_AT_Firmware_UART1_SGPIO.bin](../../firmware/ESP32_AT_Firmware_UART1_SGPIO.bin)

- K210固件:[maixpy_twatch_v0.6.2-75-g973361c0d-dirty.bin](../..//firmware/maixpy_twatch_v0.6.2-75-g973361c0d-dirty.bin)

- 面部模型:[face_model_at_0x300000.kfpkg](./face_model_at_0x300000.kfpkg)

# Start

- 买一张sd卡你通常可以使用购买时附带的sd卡

- 打开K210终端，输入`os.listdir("/")`,出现` ['flash', 'sd'] `即成功检测到SD卡,若无法读取到SD卡可使用下图的卡。

![San Disk](/image/image.png)

` ! 注意:如果您使用自己的sd卡，您可能无法读取它`

` ! 请确保sd卡的磁盘格式为FAT32，磁盘分区表类型为MBR，且支持spi协议`

- 将` up.jpg ` ` down.jpg ` ` left.jpg ` ` right.jpg ` ` stop.jpg ` ` lilygo.jpg ` ` drv8833.py `和` main.py `放在SD卡中，或者您可以通过MaixPy IDE将它们下载到主板的内存中

`第二种方法可能会影响内存读取的速度和大文件的空间消耗，所以这里使用第一种方法`