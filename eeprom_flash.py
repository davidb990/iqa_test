# This script manages the eeprom parts of the test. It needs eepflash.sh to work, furthermore eepflash.sh must be made
# executable. The eepflash.sh on the IQ Audio git is out of date and will not work,
# use https://github.com/raspberrypi/hats/blob/master/eepromutils/eepflash.sh instead.


import settings
import os
import iqa_lib
import time
import audio_config
import eepflash


class Flash:
    def __init__(self, eeprom_dir = "/home/pi/iqa_test/"):
        self.eep = eepflash.EepFlash()
        dut_settings = settings.Settings()
        dut_type = dut_settings.read_setting("dut=", param_only=True)
        self.eep_exists = None
        if dut_type is not None:
            self.dut_type = dut_type.lower()
            self.eeprom_dir = eeprom_dir
            self.enable = iqa_lib.Enable()  # Can't write to the DUT if it's turned off
            if "dacpro" in self.dut_type:
                self.eeprom_file = "Pi-DACPRO.eep"
                self.dt_overlay = "iqaudio-dacplus"
                self.enable.dut(True)
            elif "dacplus" in self.dut_type:
                self.eeprom_file = "Pi-DACPlus.eep"
                self.dt_overlay = "iqaudio-dacplus"
                self.enable.dut(True)
            elif "codeczero" in self.dut_type:
                self.eeprom_file = "Pi-CodecZero.eep" # Note: This file doesn't exist yet,
                # update when it does - Edit 020222: file exists, check email.
                # If you're not me and I forgot to put the .eep somewhere useful, use eeprom_exists()
                # to copy the eeprom from an already programmed Codec Zero.
                self.dt_overlay = "iqaudio-codec"
                self.enable.dut(True)
            elif "digiamp" in self.dut_type:
                self.eeprom_file = "Pi-DigiAMP.eep"
                self.dt_overlay = "iqaudio-dacplus unmute-amp=1"
                self.enable.da(True)
        else:
            raise Exception("DUT type has not been set in the settings.txt file.")


    def eeprom_exists(self):
        try:
            # this won't work if eepflash hasn't been made executable - make sure install.py
            # is run first, or use "sudo bash eepflash.sh ....."
            os.system("sudo {}eepflash.sh -r -f={}dump.eep -t=24c32 -y".format(self.eeprom_dir, self.eeprom_dir))  # copies the eeprom from the DUT to dump.eep
            # if needed, use 'hexdump dump.eep' in the terminal to inspect
            if os.path.getsize("{}dump.eep".format(self.eeprom_dir)) > 500:  # Checks that the eeprom on the DUT has more than 500 bytes (not empty)
                self.eep_exists = True
            else:
                self.eep_exists = False
        except:
            print("Error cheeking if EEPROM exists, setting eeprom_exists to False")
            self.eep_exists = False

    def write_eeprom(self, overwrite=False):
        if self.eep_exists is None:
            self.eeprom_exists()
        if self.eep_exists is False or overwrite is True:
            self.eep.eep_write(file=self.eeprom_dir+self.eeprom_file)
            if "digiamp" in self.dut_type:
                self.enable.da(False)
                time.sleep(1)
                self.enable.da(True)
            else:
                self.enable.dut(False)
                time.sleep(1)
                self.enable.dut(True)
        else:
            print("EEPROM already exists, use write_eeprom(overwrite=True) to overwrite.")
        # The next section 'manually' enables the dtoverlay for the IQ Audio board, as for it to detect
        # automatically the Pi must be restarted (not ideal)
        # That being said, it makes the Codec Zero throw a wobbly, and it seems to be fine without for some reason
        if "codeczero" not in self.dut_type:
            os.system("sudo dtoverlay -R")
            os.system("sudo dtoverlay-pre")
            os.system("sudo dtoverlay {}".format(self.dt_overlay))
            os.system("sudo dtoverlay-post")
            time.sleep(0.5)

