import numpy as np
import pyaudio


class FFT:
    def __init__(self, device=None, data_format=pyaudio.paInt16, channels=1, rate=44100,
                 chunk_num=20, chunk_length=1024):
        self.channels = channels
        self.rate = rate
        chunk = chunk_num * chunk_length
        self.chunk = chunk
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=data_format,
                                      input_device_index=device,
                                      channels=channels,
                                      rate=rate,
                                      input=True,
                                      frames_per_buffer=chunk)
        self.mono_psd = None
        self.mono_psd_norm = None
        self.l_psd = None
        self.r_psd = None
        self.l_psd_norm = None
        self.r_psd_norm = None
        self.freq = None
        if channels == 2:
            self.stereo = True
            self.mono = False
        else:
            self.mono = True
            self.stereo = False

    def fft(self):
        data = np.frombuffer(self.stream.read(self.chunk), dtype=np.int16)
        freq = self.rate * np.arange(self.chunk) / self.chunk
        l = np.arange(1, np.floor(self.chunk / 2), dtype='int')
        if self.stereo is True:
            l_data = data[0::2]
            r_data = data[1::2]
            l_fhat = np.fft.fft(l_data, self.chunk)
            r_fhat = np.fft.fft(r_data, self.chunk)
            l_psd = (l_fhat * np.conj(l_fhat)) / self.chunk
            r_psd = (r_fhat * np.conj(r_fhat)) / self.chunk
            l_psd_norm = l_psd / np.sum(np.abs(l_psd))
            r_psd_norm = l_psd / np.sum(np.abs(r_psd))
            self.l_psd = l_psd[l]
            self.r_psd = r_psd[l]
            self.l_psd_norm = l_psd_norm[l]
            self.r_psd_norm = r_psd_norm[l]
        else:
            fhat = np.fft.fft(data, self.chunk)
            psd = (fhat * np.conj(fhat)) / self.chunk
            psd_norm = psd / np.sum(np.abs(psd))
            self.mono_psd = psd[l]
            self.mono_psd_norm = psd_norm[l]
        self.freq = freq[l]

    def det_freq(self):
        if self.freq is None:
            self.fft()
        if self.stereo is True:
            return self.freq[np.argmax(self.l_psd)], self.freq[np.argmax(self.r_psd)]
        else:
            return self.freq[np.argmax(self.mono_psd)]

    def above_bgnd_thresh(self, thresh=0.25):
        if self.freq is None:
            self.fft()
        peak_thresh = 1-thresh
        if self.stereo is True:
            if peak_thresh > self.l_psd_norm[np.argmax(self.l_psd)]:
                l_pass = False
            else:
                l_pass = True
            if peak_thresh > self.r_psd_norm[np.argmax(self.r_psd)]:
                r_pass = False
            else:
                r_pass = True
            return l_pass, r_pass
        else:
            if peak_thresh > self.mono_psd_norm[np.argmax(self.mono_psd)]:
                return False
            else:
                return True
