import numpy as np
import pyaudio
import time


class Tone:
    def __init__(self, freq, duration, output=None, data_format=pyaudio.paFloat32, channels=1,
                 rate=44100):
        audio = pyaudio.PyAudio()
        tone = (np.sin(2 * np.pi * np.linspace(0, 1, rate) * freq)).astype(np.float32)
        stream = audio.open(format=data_format,
                            output_device_index=output,
                            channels=channels,
                            rate=rate,
                            output=True)
        t_start = time.perf_counter()
        while time.perf_counter() - t_start < duration:
            stream.write(tone)
        stream.stop_stream()
        stream.close()
