import time
import os

os.system("sudo raspi-config nonint do_audio 1")

time.sleep(5)

import zero2_loop