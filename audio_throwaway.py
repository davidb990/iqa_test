# This script is just used for testing the libraries.


import iqa_lib
import os


enable = iqa_lib.Enable()

enable.dut(True)
os.system("sudo dtoverlay iqaudio-codec")
os.system("sudo alsactl -f codeczero.state")
