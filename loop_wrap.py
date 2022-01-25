import time
import os
import matplotlib.pyplot

os.system("sudo raspi-config nonint do_audio 1")

time.sleep(5)

import zero2_loop