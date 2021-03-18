import audio
from Maix import I2S, GPIO
from fpioa_manager import *

fm.register(34,fm.fpioa.I2S0_OUT_D1)
fm.register(35,fm.fpioa.I2S0_SCLK)
fm.register(33,fm.fpioa.I2S0_WS)
wav_dev = I2S(I2S.DEVICE_0)
player = audio.Audio(path = '/sd/play.wav')
player.volume(20)
wav_info = player.play_process(wav_dev)
print("wav file head information: ", wav_info)
# wav_dev.channel_config(wav_dev.CHANNEL_1, I2S.TRANSMITTER,resolution = I2S.RESOLUTION_16_BIT ,cycles = I2S.SCLK_CYCLES_32, align_mode = I2S.RIGHT_JUSTIFYING_MODE)
wav_dev.channel_config(wav_dev.CHANNEL_1, I2S.TRANSMITTER,resolution = I2S.RESOLUTION_16_BIT ,cycles = I2S.SCLK_CYCLES_32, align_mode = I2S.LEFT_JUSTIFYING_MODE)
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