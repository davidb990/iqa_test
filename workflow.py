import iqa_lib
import uart_comms
import time
import sys
import settings as sett
import eeprom_flash
import tone as play_tone
import os

led = iqa_lib.LEDS()
enable = iqa_lib.Enable()
uart = uart_comms.UART()
flags = iqa_lib.Flags()
settings = sett.Settings()


def dut_type():
    dut_type = settings.read_setting("dut", param_only=True)
    if dut_type is None:
        sys.exit("DUT type not set; has the install script been run?")
    return dut_type


def setup(dut_type, z2_timeout=5):
    led.all_off()
    enable.da(False)
    enable.dut(False)
    uart.test_tx()
    z2_on = False
    for n in range(z2_timeout):
        if uart.test_rx() is True:
            z2_on = True
            break
        time.sleep(0.1)
    if z2_on is not True:
        z2_reset = False
        print("Zero 2 not responding, restarting the Zero 2.")
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

    print("Device under test: {}".format(dut_type))
    led.ready()
    qr_code = input("\n\n\nPlace and lock the device under test (DUT) into the test jig, and lock in place."
                    "\n\nOnce the DUT is locked in, scan the QR code on the DUT.\n")
    os.system("sudo dtoverlay -R")
    print("QR Code: {}\nBeginning tests".format(qr_code))
    return qr_code


def common_test(dut_type):
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
    if flash.eeprom_exists() is False:
        return 8
    return 0


def fft(l_tone, r_tone, dur):
    tone = play_tone.Tone()
    uart.fft_tx_w()
    conf_ts = time.perf_counter()
    confirmation = False
    while time.perf_counter() - conf_ts < 2:
        if uart.conf_tx():
            tone.stereotone(l_tone, r_tone, dur)
            confirmation = True
            timestamp = time.perf_counter()
            while time.perf_counter() - timestamp < 4:
                fft = uart.fft_tx_r()
                if isinstance(fft, tuple):
                    return fft
    if confirmation is False:
        print("Zero 2 failed to confirm receipt of command.")
        sys.exit()


def relay_switch(relay, on_off):
    uart.relay_tx(relay, on_off)
    conf_ts = time.perf_counter()
    confirmation = False
    while time.perf_counter() - conf_ts < 2:
        if uart.conf_tx():
            confirmation = True
            break
    if confirmation is False:
        print("Zero 2 failed to confirm receipt of command.")
        sys.exit()


def audio_out_tests(dut_type):
    relay_switch("all", "off")
    relay_switch("aux_out", "on")
    low_tone = fft(290, 310, 1)
    if 285 < float(low_tone[0]) < 295 and 305 < float(low_tone[1]) < 315:
        if bool(low_tone[2]) is False or bool(low_tone[3]) is False:
            return 9
    else:
        return 9
    high_tone = fft(12990, 13010, 1)
    if 12985 < float(high_tone[0]) < 12995 and 13005 < float(high_tone[1]) < 13015:
        if bool(high_tone[2]) is False or bool(high_tone[3]) is False:
            return 10
    else:
        return 10
    if "digiamp" not in dut_type:
        relay_switch("aux_out", "off")
        relay_switch("phones", "on")
        low_tone = fft(290, 310, 1)
        if 285 < float(low_tone[0]) < 295 and 305 < float(low_tone[1]) < 315:
            if bool(low_tone[2]) is False or bool(low_tone[3]) is False:
                return 11
        else:
            return 11
        high_tone = fft(12990, 13010, 1)
        if 12985 < float(high_tone[0]) < 12995 and 13005 < float(high_tone[1]) < 13015:
            if bool(high_tone[2]) is False or bool(high_tone[3]) is False:
                return 12
        else:
            return 12
    return 0


def audio_in_tests():
    return 0


def test_end(dut_type, error_code):
    err_dict = {0: "Passed",
                3: "Connection check failed",
                4: "DUT overcurrent",
                5: "DigiAmp+ backpower undervolt",
                6: "DigiAmp+ backpower overvolt",
                7: "EEPROM write failure",
                8: "Hat not detected on EEPROM restart",
                9: "Balanced audio/aux out lowtone outside limits",
                10: "Headphone jack/speaker out lowtone outside limits",
                11: "Balanced audio/aux out hightone outside limits",
                12: "Headphone jack/speaker out hightone outside limits",
                13: "Codec Zero external mic failure",
                14: "Codec Zero stereo line in failure",
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
