# This is the highest level script on the Pi4, which brings all the test elements together into one workflow.


import iqa_lib
import uart_comms
import time
import sys
import settings as sett
import eeprom_flash
import tone as play_tone
import os
import codec_mode
import fft_lib

print("\n==========================================\nInitialising Test\n==========================================\n")

led = iqa_lib.LEDS()
enable = iqa_lib.Enable()
uart = uart_comms.UART()
flags = iqa_lib.Flags()
settings = sett.Settings()
tone = play_tone.Tone()

print("\n==========================================\nInitialisation Complete\n==========================================\n")


def dut_type():
    dut_type = settings.read_setting("dut", param_only=True)
    if dut_type is None:
        sys.exit("DUT type not set; has the install script been run?")
    return dut_type


def uart_check(timeout=2):
    # Checks for a response over UART from the Zero 2
    uart_response = False
    t_start = time.perf_counter()
    uart.test_tx()
    while time.perf_counter() - t_start < timeout:
        if uart.test_rx():
            uart_response = True
            break
    return uart_response


def relay_switch(relay, on_off):
    uart.relay_tx(relay, on_off)


def z2_reboot():
    z2_reset = False
    enable.z2(False)
    time.sleep(2)
    enable.z2(True)
    z2_en_time = time.perf_counter()
    z2_on_delay = 150
    while time.perf_counter() - z2_en_time < z2_on_delay:
        if uart.zero_on_rx() is True:
            print("Zero 2 is ready for testing.")
            z2_reset = True
            break
        time.sleep(0.05)
    if z2_reset is False:
        print("Zero 2 has failed to reset within {} seconds".format(z2_on_delay))
        sys.exit("Exitting: debugging required. Consider restarting the whole test system.")


def setup(dut_type):
    led.all_off()
    enable.da(False)
    enable.dut(False)
    relay_switch("all", "off")
    if uart_check() is False:
        print("Zero 2 not responding, restarting the Zero 2.")
        z2_reboot()
    print("Device under test: {}".format(dut_type))
    led.ready()
    qr_code = input("\n\n\nPlace and lock the device under test (DUT) into the test jig, and lock in place."
                    "\n\nOnce the DUT is locked in, scan the QR code on the DUT.\n")
    os.system("sudo dtoverlay -R")
    print("QR Code: {}\nBeginning tests".format(qr_code))
    return qr_code


def common_test(dut_type):
    # These tests are common accross all types - current testing & eeprom reading/writing
    led.testing()
    if flags.conn_chk(poll_count=1):
        led.failed()
        return 3
    if "digiamp" in dut_type:
        enable.da(True)
        if flags.da_oc():
            led.failed()
            return 4
        if flags.da_uv():
            led.failed()
            return 5
        if flags.da_ov():
            led.failed()
            return 6
    else:
        enable.dut(True)
        if flags.dut():
            led.failed()
            return 4
    flash = eeprom_flash.Flash()
    try:
        flash.write_eeprom()
    except:
        return 7
    if flash.eep_exists is None:
        flash.eeprom_exists()
    elif flash.eep_exists is False:
        return 8
    return 0


def fft_req(l_tone, r_tone, dur, timeout=4, chunks=8):
    # Requests an FFT from the Zero 2 and plays a tone out of the DUT
    uart.fft_tx_w(chunk=chunks)
    tone.stereotone(l_tone, r_tone, dur)
    timestamp = time.perf_counter()
    while time.perf_counter() - timestamp < timeout:
        fft = uart.fft_tx_r()
        if isinstance(fft, tuple):
            return fft


def audio_out_tests(dut_type, duration=2.5):
    # Output tests for all DUTs
    if "codeczero" in dut_type:
        codec_mode.CodecMode(mode_file='IQaudIO_Codec_OnboardMIC_record_and_SPK_playback.state')
    if uart_check() is False:
        z2_reboot()
    relay_switch("aux_out", "on")
    time.sleep(1)
    lo_hi = fft_req(300, 13000, duration)
    if 295 < float(lo_hi[0]) < 305 and 12995 < float(lo_hi[1]) < 13005:
        if bool(lo_hi[2]) is False or bool(lo_hi[3]) is False:
            return 9
    elif "codeczero" in dut_type and 295 < float(lo_hi[0]) < 305:
        if bool(lo_hi[2]) is False:
            return 9
    else:
        return 9
    if "digiamp" not in dut_type:
        relay_switch("phones", "on")
        time.sleep(1)
        hi_lo = fft_req(13000, 300, duration)
        if 12995 < float(hi_lo[0]) < 13005 and 295 < float(hi_lo[1]) < 305:
            if bool(hi_lo[2]) is False or bool(hi_lo[3]) is False:
                return 10
        elif "codeczero" in dut_type and 12995 < float(hi_lo[0]) < 13005:
            if bool(hi_lo[2]) is False:
                return 10
        else:
            return 10
    return 0


def audio_in_tests(duration=2.5):
    # Input tests for the Codec Zero
    buzz_fft = fft_lib.FFT(channels=1)
    mic_fft = fft_lib.FFT(channels=2)
    uart.buzz_tx(duration)
    time.sleep(1)
    loud_noise = buzz_fft.above_bgnd_thresh(thresh=0.2)
    if loud_noise is False:
        return 15
    codec_mode.CodecMode(mode_file="IQaudIO_Codec_StereoMIC_record_and_HP_playback.state")  # loading the correct ALSA file
    relay_switch("mic", "on")
    time.sleep(1)
    uart.tone_tx([13000, 300], duration)
    time.sleep(1)
    fft_reading = mic_fft.fft()
    bgnd_check = mic_fft.above_bgnd_thresh()
    if 12995 < float(fft_reading[0]) < 13005 and 295 < float(fft_reading[1]) < 305:
        if bool(bgnd_check[0]) is False or bool(bgnd_check[1]) is False:
            return 13
    else:
        return 13
    return 0


def test_end(dut_type, error_code):
    err_dict = {0: "Passed",
                3: "Connection check failed",
                4: "DUT overcurrent",
                5: "DigiAmp+ backpower undervolt",
                6: "DigiAmp+ backpower overvolt",
                7: "EEPROM write failure",
                8: "Hat not detected on EEPROM restart",
                9: "Balanced audio/aux out outside limits",
                10: "Headphone jack/speaker out outside limits",
                13: "Codec Zero external mic failure",
                15: "Codec Zero MEMS mic failure"}

    if "digiamp" in dut_type:
        enable.da(False)
    else:
        enable.dut(False)
    if error_code == 0:
        led.passed()
        print("\n\nDUT passed.")
    else:
        led.failed()
        print("\n\nDUT failed with error code {}: {}".format(error_code, err_dict[error_code]))
    print("\nMoving onto next device.\n\n==========================================\n")


while True:
    dut = dut_type()
    setup(dut)
    error_code = common_test(dut)
    if error_code == 0:
        error_code = audio_out_tests(dut)
        if "codeczero" in dut and error_code == 0:
            error_code = audio_in_tests()
    test_end(dut, error_code)
