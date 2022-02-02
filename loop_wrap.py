# This exists because zero2_loop wasn't running properly on start up, but having this be called, then calling the
# zero2_loop seems to work much better. Not completely sure why, probably something to do with the UART
# starting too early?


import time
import os
import matplotlib.pyplot  # Importing pyplot now allows the cashe to build before getting into the bulk of the script.

os.system("sudo raspi-config nonint do_audio 1")

time.sleep(5)

import zero2_loop  # Runs the zero2_loop
