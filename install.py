import os
import sys
import codec_mode


#
# Ensure this code is run as sudo when editting config.txt!
#


def install():
    try:
        os.system("sudo apt update")
    except:
        sys.exit("Failed to update the Pi")
    try:
        os.system("sudo apt-get install python-pyaudio")
        os.system("sudo apt-get install python3-pyaudio")
    except:
        sys.exit("\n\nUnable to install pyaudio and/or dependancies\n\n")

    try:
        os.system("sudo apt install python3-matplotlib")
    except:
        sys.exit("\n\nUnable to install numpy & matplotlib\n\n")

    try:
        os.system("sudo pip3 install pyserial")
    except:
        sys.exit("\n\nUnable to install pyserial\n\n")


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
        with open(config_file, 'a') as file:
            file.write("\ndtoverlay=disable-bt")
    os.system("sudo systemctl disable hciuart")
    with open(cmdline_file, 'r') as file:
        line_list = file.read().splitlines()
        param_list = line_list[0].split(" ")
        if "console=serial0,115200" in param_list:
            param_list.remove("console=serial0,115200")
        line_list.clear()
        line_list.append(' '.join(param_list))
    with open(cmdline_file, 'w') as file:
        for line in line_list:
            file.write(line)


def hat_config(config_file="/boot/config.txt"):
    with open(config_file, 'r') as file:
        line_list = []
        for line in file:
            if line == "dtparam=audio=on\n" or line == "dtparam=audio=on":
                line_list.append("#dtparam=audio=on\n")
            else:
                line_list.append(line)
    with open(config_file, 'w') as file:
        for line in line_list:
            file.write(line)


def codec_zero_config(mode_file='IQaudIO_Codec_AUXIN_record_and_HP_playback.state'):
    codec_mode.CodecMode(mode_file=mode_file)


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


class Zero2:
    def __init__(self):
        print("Installing Zero 2")
        install()
        uart_config()
        hat_config()
        codec_zero_config()
        reboot()


class Pi4:
    def __init__(self, DigiAmp=False, DACPlus=False, CodecZero=False):
        if CodecZero is True:
            print("Installing Pi4 Codec Zero")
            codec_zero_config(mode_file="IQaudIO_Codec_Playback_Only.state")
        elif DigiAmp is False and DACPlus is False:
            print("Setup not completed, please call the class again specifying a DUT, e.g. Pi4(DACPlus=True).")
        else:
            if DACPlus is True:
                print("Installing Pi4 DACPlus")
            elif DigiAmp is True:
                print("Installing Pi4 DigiAmp")
        install()
        uart_config()
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

