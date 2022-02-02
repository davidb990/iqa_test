# This script is just used for testing the libraries.


from fft_lib import FFT
from tone import Tone

#
fft = FFT(channels=1)
print(fft.det_freq())
print(fft.above_bgnd_thresh(thresh=0.75))
#
tone = Tone()
tone.monotone(440, 2)
tone.stereotone(500, 530, 2)

# fft.fft_plot()
