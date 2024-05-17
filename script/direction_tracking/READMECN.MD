# 面部跟踪

# Hardware

[T-Bao K210版本](https://www.aliexpress.com/item/1005001511367578.html)

# Firmware

esp32和k210需要分别上传以下固件:

- ESP32固件:[ESP32_AT_Firmware_UART1_SGPIO.bin](../../firmware/ESP32_AT_Firmware_UART1_SGPIO.bin)

- K210固件:[maixpy_twatch_v0.6.2-75-g973361c0d-dirty.bin](../..//firmware/maixpy_twatch_v0.6.2-75-g973361c0d-dirty.bin)

- 方向模型:[Identify_Direction_model.kmodel](./Identify_Direction_model.kmodel)

# Start

- 使用您平常时使用的sd卡或者可以使用购买时附带的sd卡
` ! 注意 : 如果您使用自己的sd卡，您可能无法读取它`

` ! 请确保sd卡的磁盘格式为FAT32，磁盘分区表类型为MBR，且支持spi协议`

- 将`drv8833.py ` ` main.py `和` Identify_Direction_model.kmodel `存放到SD卡内或者你可以通过MaixPy IDE将它们下载到主板的内存中

`第二种方法可能会影响内存读取的速度和大文件的空间消耗，所以这里使用第一种方法`