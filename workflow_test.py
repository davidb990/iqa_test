import uart_comms
import time

uart = uart_comms.UART("COM5")

def uart_check(timeout=2):
    uart_response = False
    t_start = time.perf_counter()
    uart.test_tx()
    while time.perf_counter() - t_start < timeout:
        if uart.test_rx():
            uart_response = True
            break
    return uart_response


def fft(l_tone, r_tone, dur, timeout=4, chunks=8):
    uart.fft_tx_w(chunk=chunks)
    timestamp = time.perf_counter()
    while time.perf_counter() - timestamp < timeout:
        try:
            fft = uart.fft_tx_r()
            if isinstance(fft, tuple):
                return fft
        except:
            pass


def relay_switch(relay, on_off):
    uart.relay_tx(relay, on_off)


def audio_out_tests(dut_type, duration=0.5):
    relay_switch("aux_out", "on")
    time.sleep(1)
    t_start = time.perf_counter()
    low_tone = fft(290, 310, duration)
    if 285 < float(low_tone[0]) < 295 and 305 < float(low_tone[1]) < 315:
        if bool(low_tone[2]) is False or bool(low_tone[3]) is False:
            pass
    else:
        pass
    if "digiamp" not in dut_type:
        relay_switch("phones", "on")
        time.sleep(1)
        low_tone = fft(290, 310, duration)
        if 285 < float(low_tone[0]) < 295 and 305 < float(low_tone[1]) < 315:
            if bool(low_tone[2]) is False or bool(low_tone[3]) is False:
                pass
        else:
            pass
    print(time.perf_counter()-t_start)

audio_out_tests("dacplus")