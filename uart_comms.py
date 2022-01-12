import serial
import fft_lib
from tone import Tone


class UART:
    def __init__(self, com_port="/dev/ttyAMA0", connect_attempts=5):
        att_no = 0
        att_lim = connect_attempts
        while att_lim >= att_no:
            try:
                self.uart = serial.Serial(com_port, 9600, timeout=0.5)
                break
            except:
                print("Unable to connect over UART! Waiting 5 seconds and retrying.\nAttempt number {} of {}"
                      .format(att_no, att_lim))
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
            if txt[0:2] == "b'" and txt[-3:] == "'\n":
                txt = self.bytes_to_string(txt)
            elif txt[-2:] == "\n":
                txt = txt[:-2]
        except:
            print("Error turning response into string!")  # prints error but allows program to keep running
        return txt

    def close(self):
        self.uart.close()

    def fft_rx(self, rx, device=None):
        rx = rx.split(":")
        thresh = rx[1]
        fft = fft_lib.FFT(device)
        freq = fft.det_freq()
        noise_thresh = fft.above_bgnd_thresh(thresh)
        if freq is type(tuple) and noise_thresh is type(tuple):
            freq = str(freq[0])+","+str(freq[1])
            noise_thresh = str(noise_thresh[0]) + "," + str(noise_thresh[1])
        self.write("FREQ:{}:TRSH:{}\n".format(freq, noise_thresh))

    def fft_tx_w(self, thresh=0.25):
        self.write("TRSH:{}:FREQ?\n".format(thresh))

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
        rx = rx.split(":")
        freq = rx[1]
        duration = rx[3]
        Tone(freq, duration)

    def tone_tx(self, freq, duration):
        self.write("FREQ:{}:DURA:{}:TONE?\n".format(freq, duration))

    def rx_check(self):
        rx = self.readall()
        if "FREQ?" in rx:
            self.fft_rx(rx)
        elif "TONE?" in rx:
            self.tone_rx(rx)
        elif "TEST?" in rx:
            self.write("TEST\n")
