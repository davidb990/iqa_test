# This is an automated install script for the IQ Audio Test Pi4 and Zero2. Run as Sudo when first setting up the test.
# This script will install all necessary python dependancies, update the Pi/Zero, set up the UART, configure the DUT or
# codec zero, make the zero 2 loop begin on start-up, and prepare the tools for reading & writing the EEPROM of the DUT.


import os
import sys
import codec_mode
import settings


#
# Ensure this code is run as sudo when editting config.txt!
#


def install():
    try:
        os.system("sudo apt update -y")
    except:
        sys.exit("Failed to update the Pi")

    try:
        os.system("sudo apt-get install -y python-pyaudio")
        os.system("sudo apt-get install -y python3-pyaudio")
    except:
        sys.exit("\n\nUnable to install pyaudio and/or dependancies\n\n")

    try:
        os.system("sudo apt install -y python3-matplotlib")  # Numpy is a dependancy of matplotlib, and will be installed alongside.
    except:
        sys.exit("\n\nUnable to install numpy & matplotlib\n\n")
    try:
        os.system("sudo apt install -y pip")
    except:
        sys.exit("\n\nUnable to install pip\n\n")
    try:
        os.system("sudo pip3 install pyserial")
    except:
        sys.exit("\n\nUnable to install pyserial\n\n")
    try:
        os.system("sudo pip3 install smbus2")
    except:
        sys.exit("\n\nUnable to install smbus2\n\n")
    try:
        os.system("sudo apt full-upgrade -y")
    except:
        sys.exit("Unable to upgrade the Pi")


def uart_config(config_file="/boot/config.txt", cmdline_file="/boot/cmdline.txt"):
    with open(config_file, 'r') as file:
        uart_configed = False
        bt_disabled = False
        for line in file:
            line.rstrip("\n")
            if line == "uart_enable=1":
                uart_configed = True
            elif line == "dtoverlay=disable-bt":
                bt_disabled = True
    if not uart_configed:
        with open(config_file, 'a') as file:
            file.write("\nuart_enable=1")
    if not bt_disabled:
        with open(config_file, 'a') as file:  # This frees up the UART, thus the mini-UART (less stable) isn't used
            file.write("\ndtoverlay=disable-bt")
    os.system("sudo systemctl disable hciuart")
    with open(cmdline_file, 'r') as file:
        line_list = file.read().splitlines()
        param_list = line_list[0].split(" ")
        if "console=serial0,115200" in param_list:
            param_list.remove("console=serial0,115200")  # Prevents the console printing the CLI to UART
        line_list.clear()
        line_list.append(' '.join(param_list))
    with open(cmdline_file, 'w') as file:
        for line in line_list:
            file.write(line)


def startup_config(service="loop_wrap.service"):
    # This function uses systemd to make sure the zero 2 loop runs on startup
    # To stop the program from the Zero 2, run "sudo systemctl stop loop_wrap.service" from the command line
    os.system("sudo cp /home/pi/iqa_test/{} /lib/systemd/system/".format(service))
    os.system("sudo systemctl daemon-reload")
    os.system("sudo systemctl enable {}".format(service))


def hat_config(config_file="/boot/config.txt"):
    with open(config_file, 'r') as file:
        line_list = []
        for line in file:
            if line == "dtparam=audio=on\n" or line == "dtparam=audio=on":
                line_list.append("#dtparam=audio=on\n")  # stops the Pi from defaulting to system audio
            else:
                line_list.append(line)
    with open(config_file, 'w') as file:
        for line in line_list:
            file.write(line)


def codec_zero_config(mode_file='IQaudIO_Codec_AUXIN_record_and_HP_playback.state'):
    codec_mode.CodecMode(mode_file=mode_file)  # configues the codec zero ALSA state file


def reboot():
    while True:
        reboot = input("Install complete, would you like to reboot to apply changes?\n(y/n): ")
        if reboot.lower() == 'y':
            os.system("sudo reboot")
            break
        elif reboot.lower() == 'n':
            print("Skipping reboot; reboot later to apply changes.")
            break
        else:
            print("Invalid input, please enter either y or n.")


def dut_settings(dut: str, settings_file='/home/pi/iqa_test/settings.txt'):
    # Calls the settings library to set the dut type
    test_settings = settings.Settings(settings_file=settings_file)
    test_settings.set_dut(dut)


def eeprom_exe(eepflash='/home/pi/iqa_test/eepflash.sh'):
    # Makes eepflash.sh executable
    os.system("sudo raspi-config nonint do_i2c 0")  # Not sure if this line is needed, it enables I2C, but it seems like a good idea
    os.system("chmod +x {}".format(eepflash))


class Zero2:
    def __init__(self):
        print("Installing Zero 2")
        install()
        uart_config()
        hat_config()
        codec_zero_config()
        startup_config()
        reboot()


class Pi4:
    def __init__(self, DigiAmp=False, DACPlus=False, CodecZero=False):
        if CodecZero is True:
            print("Installing Pi4 Codec Zero")
            codec_zero_config(mode_file="IQaudIO_Codec_Playback_Only.state")
            dut_settings("codeczero")
        elif DigiAmp is False and DACPlus is False:
            print("Setup not completed, please call the class again specifying a DUT, e.g. Pi4(DACPlus=True).")
        else:
            if DACPlus is True:
                print("Installing Pi4 DACPlus")
                dut_settings("dacplus")
            elif DigiAmp is True:
                print("Installing Pi4 DigiAmp")
                dut_settings("digiamp")
        install()
        hat_config()
        uart_config()
        eeprom_exe()
        reboot()


while True:
    install_option = input("Welcome to the IQaudIO test installer. What device are you installing onto?"
                           "\n  1 - Zero 2\n  2 - Pi 4 (DACPlus)\n  3 - Pi 4 (DigiAmp)\n"
                           "  4 - Pi 4 (Codec Zero)\nDevice number: ")
    try:
        install_option = int(install_option)
    except:
        print("Error! Please enter either 1,2,3 or 4")
        continue
    if install_option == 1:
        Zero2()
        break
    elif install_option == 2:
        Pi4(DACPlus=True)
        break
    elif install_option == 3:
        Pi4(DigiAmp=True)
        break
    elif install_option == 4:
        Pi4(CodecZero=True)
        break
    else:
        print("Error! Please enter either 1,2,3 or 4")
