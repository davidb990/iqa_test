import settings
import os
import iqa_lib
import time
import audio_config


class Flash:
    def __init__(self, eeprom_dir = "/home/pi/iqa_test/eeprom/"):
        dut_settings = settings.Settings()
        dut_type = dut_settings.read_setting("dut=", param_only=True)
        if dut_type is not None:
            self.dut_type = dut_type.lower()
            self.eeprom_dir = eeprom_dir
            if self.dut_type == "dacpro":
                self.eeprom_file = "Pi-DACPRO.eep"
                self.dt_overlay = "iqaudio-dacplus"
            elif self.dut_type == "dacplus":
                self.eeprom_file = "Pi-DACPlus.eep"
                self.dt_overlay = "iqaudio-dacplus"
            elif self.dut_type == "codeczero":
                self.eeprom_file = "Pi-CodecZero.eep" # Note: This file doesn't exisit yet, update when it does
                self.dt_overlay = "iqaudio-dacplus"
            elif self.dut_type == "digiamp":
                self.eeprom_file = "Pi-DigiAMP.eep"
                self.dt_overlay = "iqaudio-dacplus"
        else:
            raise Exception("DUT type has not been set in the settings.txt file.")
        self.enable = iqa_lib.Enable()

    def eeprom_exists(self) -> bool:
        try:
            os.system("sudo dtoverlay-pre")
            os.system("sudo dtoverlay {}".format(self.dt_overlay))
            os.system("sudo dtoverlay-post")
            audio = audio_config.AudioDevice()
            iq_dict = audio.find_devices("iqaudio")
            if len(iq_dict) == 0:
                return False
            else:
                return True
        except:
            print("Error cheeking if EEPROM exists, setting eeprom_exists to False")

    def write_eeprom(self, overwrite=False):
        if self.eeprom_exists() is False or overwrite is True:
            os.system("sudo {}eepflash.sh -w -f={}{} -t=24c32".format(self.eeprom_dir, self.eeprom_dir, self.eeprom_file))
            if self.dut_type == "digiamp":
                self.enable.da(False)
                time.sleep(1)
                self.enable.da(True)
            else:
                self.enable.dut(False)
                time.sleep(1)
                self.enable.dut(True)
        else:
            print("EEPROM already exists, use write_eeprom(overwrite=True) to overwrite.")
        os.system("sudo dtoverlay-pre")
        os.system("sudo dtoverlay {}".format(self.dt_overlay))
        os.system("sudo dtoverlay-post")
        time.sleep(0.5)

