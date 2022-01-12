import os


# Might need to restart the codec zero when changing modes,
# but as of 07/01/22, testing suggests it manages without a restart.
# If restating the codec is required, use the iqa_lib to disable
# then enable the DUT.


class CodecMode:
    file_list = ["IQaudIO_Codec_AUXIN_record_and_HP_playback.state",
                 "IQaudIO_Codec_OnboardMIC_record_and_SPK_playback.state",
                 "IQaudIO_Codec_Playback_Only.state",
                 "IQaudIO_Codec_StereoMIC_record_and_HP_playback.state"]

    def set_mode(self, mode_file: str):
        try:
            os.system("git clone https://github.com/iqaudio/Pi-Codec.git")
            os.system("sudo alsactl restore -f Pi-Codec/" + str(mode_file))
        except:
            os.system("sudo alsactl restore -f Pi-Codec/" + str(mode_file))

    def __init__(self, aux_in=False, aux_out=False, playback=False,
                 mems=False, stereo_mic=False, mode_file=None):
        if mode_file in self.file_list:
            self.set_mode(mode_file)
        elif aux_in is True:
            self.set_mode(self.file_list[0])
        elif aux_out is True:
            self.set_mode(self.file_list[0])
        elif playback is True:
            self.set_mode(self.file_list[2])
        elif mems is True:
            self.set_mode(self.file_list[1])
        elif stereo_mic is True:
            self.set_mode(self.file_list[3])
        else:
            print("Invalid set_mode input")
