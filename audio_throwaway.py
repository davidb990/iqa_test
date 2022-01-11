from audio_config import AudioDevice
from pprint import pprint
from fft_lib import FFT
from tone import Tone
#
fft = FFT(channels=1)
print(fft.det_freq())
print(fft.above_bgnd_thresh(thresh=0.75))
#
Tone(440, 1)
Tone(220, 1)
Tone(880, 1)

devices = AudioDevice()

pprint(devices.supported_device("", "input"))
