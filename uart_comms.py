import serial
import fft_lib
from tone import Tone
import time


class UART:
    def __init__(self, com_port="/dev/ttyAMA0", connect_attempts=5):
        att_no = 0
        att_lim = connect_attempts
        while att_lim >= att_no:
            try:
                self.uart = serial.Serial(com_port, baudrate=115200, timeout=0.5)
                break
            except:
                print("Unable to connect over UART! Waiting 1 second and retrying.\nAttempt number {} of {}"
                      .format(att_no, att_lim))
                time.sleep(1)
                att_no += 1

    def bytes_to_string(self, txt: str) -> str:
        txt = txt[2:]  # removes the b' from the bytes syntax
        txt = txt[:-3]  # removes the final '\n from the bytes syntax
        return txt

    def write(self, txt: str):
        txt = txt.encode("ascii")  # UART can only understand ASCII, so information sent must be encoded to ASCII
        return self.uart.write(txt)

    def readall(self) -> str:
        txt = self.uart.readall()
        try:
            txt = str(txt)  # tries to make the information a string to allow for easier manipulation
            if txt[0:2] == "b'" and txt[-2:] == "\r'":
                txt = self.bytes_to_string(txt)
            elif txt[0:2] == "b'" and txt[-3:] == "\\r'":
                txt = txt[2:-3]
        except:
            print("Error turning response into string!")  # prints error but allows program to keep running
        return txt

    def close(self):
        self.uart.close()

    def rx_conf(self):
        self.write("RGR\r")

    def conf_tx(self) -> bool:
        readback = self.readall()
        if "RGR" in str(readback):
            return True
        else:
            return False

    def fft_rx(self, rx, device=None, channels=2):
        self.rx_conf()
        rx = rx.split(":")
        thresh = rx[1]
        fft = fft_lib.FFT(device=device, channels=channels)
        freq = fft.det_freq()
        noise_thresh = fft.above_bgnd_thresh(float(thresh))
        if isinstance(freq, tuple) and isinstance(noise_thresh, tuple):
            freq = str(freq[0]) + "," + str(freq[1])
            noise_thresh = str(noise_thresh[0]) + "," + str(noise_thresh[1])
        time.sleep(0.4)
        self.write("FREQ:{}:TRSH:{}\r".format(freq, noise_thresh))

    def fft_tx_w(self, thresh=0.25):
        self.write("TRSH:{}:FREQ?\r".format(thresh))

    def fft_tx_r(self):
        tx_r = self.readall()
        tx_r = tx_r.split(":")
        freq = tx_r[1]
        above_thresh = tx_r[3]
        freq_list = freq.split(",")
        thresh_list = above_thresh.split(",")
        if len(freq_list) == 2 and len(thresh_list) == 2:
            return freq_list[0], freq_list[1], thresh_list[0], thresh_list[1]
        else:
            return freq, above_thresh

    def tone_rx(self, rx):
        self.rx_conf()
        tone = Tone()
        rx = rx.split(":")
        freq = rx[1]
        duration = rx[3]
        if "," in freq:
            freq.split(",")
            l_freq = float(freq[0])
            r_freq = float(freq[1])
            tone.stereotone(l_freq, r_freq, duration)
        else:
            freq = float(freq)
            tone.monotone(freq, duration)

    def tone_tx(self, freq, duration):
        if isinstance(freq, list) or isinstance(freq, tuple):
            freq = str(freq[0]) + "," + str(freq[1])
        self.write("FREQ:{}:DURA:{}:TONE?\r".format(freq, duration))

    def rx_check(self):
        rx = self.readall()
        if "FREQ?" in rx:
            self.fft_rx(rx)
        elif "TONE?" in rx:
            self.tone_rx(rx)
        elif "TEST?" in rx:
            self.write("TEST\r")
