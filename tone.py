# This library can be used to generate a tone in mono or in stereo.
# It uses pyaudio to output the tone, and numpy to generate the sine wave.


import numpy as np
import pyaudio
import time


class Tone:
    def __init__(self, device=None, data_format=pyaudio.paFloat32, rate=44100):
        self.audio = pyaudio.PyAudio()
        self.device = device
        self.data_format = data_format
        self.rate = rate

    def monotone(self, freq, duration):
        duration = float(duration)
        freq = np.float32(freq)
        tone = (np.sin(2 * np.pi * np.linspace(0, 1, self.rate) * freq)).astype(np.float32)
        stream = self.audio.open(format=self.data_format,
                                 output_device_index=self.device,
                                 channels=1,
                                 rate=self.rate,
                                 output=True)
        t_start = time.perf_counter()
        while time.perf_counter() - t_start < duration:
            stream.write(tone)
        stream.stop_stream()
        stream.close()

    def stereotone(self, l_freq, r_freq, duration):
        duration = float(duration)
        l_freq = np.float32(l_freq)
        r_freq = np.float32(r_freq)
        l_tone = (np.sin(2 * np.pi * np.linspace(0, 1, self.rate) * l_freq)).astype(np.float32)
        r_tone = (np.sin(2 * np.pi * np.linspace(0, 1, self.rate) * r_freq)).astype(np.float32)
        stereo_tone = np.array([val for pair in zip(l_tone, r_tone) for val in pair], dtype=np.float32)
        stereo_tone = bytes(stereo_tone)
        stream = self.audio.open(format=self.data_format,
                                 output_device_index=self.device,
                                 channels=2,
                                 rate=self.rate,
                                 output=True)
        t_start = time.perf_counter()
        while time.perf_counter() - t_start < duration:
            stream.write(stereo_tone)
        stream.stop_stream()
        stream.close()
