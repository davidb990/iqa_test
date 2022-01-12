import numpy as np
import pyaudio
import matplotlib.pyplot as plt


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
        self.data = None
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

    def freq_range(self, freq, lower_lim: int, upper_lim: int):
        return freq[lower_lim:upper_lim]

    def psd_norm(self, psd, lower_lim: int = None, upper_lim: int = None):
        if lower_lim is not None and upper_lim is not None:
            scoped_psd = psd[lower_lim:upper_lim]
        else:
            scoped_psd = psd
        return scoped_psd / np.sum(np.abs(scoped_psd))

    def fft(self):
        self.data = np.frombuffer(self.stream.read(self.chunk), dtype=np.int16)
        self.stream.close()
        freq = self.rate * np.arange(self.chunk) / self.chunk
        scoped_freq = self.freq_range(freq, lower_lim=20, upper_lim=16000)
        l = np.arange(1, np.floor(self.chunk / 2), dtype='int')
        if self.stereo is True:
            l_data = self.data[0::2]
            r_data = self.data[1::2]
            l_fhat = np.fft.fft(l_data, self.chunk)
            r_fhat = np.fft.fft(r_data, self.chunk)
            l_psd = (l_fhat * np.conj(l_fhat)) / self.chunk
            r_psd = (r_fhat * np.conj(r_fhat)) / self.chunk
            self.l_psd = l_psd[l]
            self.r_psd = r_psd[l]
            self.l_psd_norm = self.psd_norm(l_psd, lower_lim=20, upper_lim=16000)[l]
            self.r_psd_norm = self.psd_norm(r_psd, lower_lim=20, upper_lim=16000)[l]
        else:
            fhat = np.fft.fft(self.data, self.chunk)
            psd = (fhat * np.conj(fhat)) / self.chunk
            self.mono_psd = psd[l]
            self.mono_psd_norm = self.psd_norm(psd, lower_lim=20, upper_lim=16000)[l]
        self.freq = scoped_freq[l]

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
        peak_thresh = 1 - thresh
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

    def plotter(self, title: str, scale='linear', x0=None, y0=None, x1=None, y1=None, double_plot=False):
        if not double_plot:
            fig, ax = plt.subplots()
            ax.plot(x0, y0)
            ax.set_title(title)
            if scale == 'log':
                ax.set_xscale('log')
        else:
            fig, axs = plt.subplots(2)
            fig.suptitle(title)
            axs[0].plot(x0, y1)
            axs[1].plot(x1, y1)
            if scale == 'log':
                axs[0].set_xscale('log')
                axs[1].set_xscale('log')
        plt.show()

    def fft_plot(self):
        if self.freq is None:
            self.fft()
        if self.stereo:
            self.plotter('Stereo Semilog Plot of the FFT', scale='log', x0=self.freq, x1=self.freq, y0=self.l_psd_norm,
                         y1=self.r_psd_norm, double_plot=True)
        else:
            self.plotter('Mono Semilog Plot of the FFT', scale='log', x0=self.freq, y0=self.mono_psd_norm)
