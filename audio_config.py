import pyaudio


class AudioDevice:
    def __init__(self):
        self.audio = pyaudio.PyAudio()

    def all_devices(self):
        dev_dict = {}
        dev_count = self.audio.get_device_count()
        for n in range(dev_count):
            dev_dict.update({n: self.audio.get_device_info_by_index(n).get("name")
                             })
        return dev_dict

    def find_devices(self, dev_type: str):
        dev_dict = self.all_devices()
        found_dict = {}
        for n in dev_dict:
            if dev_type.lower() in dev_dict[n].lower():
                found_dict.update({n: dev_dict[n]})
        return found_dict

    def supported_device(self, dev_type: str, input_output: str, rate=44100, channels=1,
                         input_format=pyaudio.paInt16, output_format=pyaudio.paFloat32, chunk=1024):
        found_dict = self.find_devices(dev_type)
        supp_dict = {}
        for n in found_dict:
            print(n)
            if input_output.lower() == "input":
                try:
                    stream = self.audio.open(format=input_format,
                                             input_device_index=n,
                                             channels=channels,
                                             rate=rate,
                                             input=True,
                                             frames_per_buffer=chunk)
                    supp_dict.update({n: found_dict[n]})
                    stream.stop_stream()
                    stream.close()
                except:
                    pass
            elif input_output.lower() == "output":
                try:
                    stream = self.audio.open(format=output_format,
                                             output_device_index=n,
                                             channels=channels,
                                             rate=rate,
                                             output=True)
                    supp_dict.update({n: found_dict[n]})
                    stream.stop_stream()
                    stream.close()
                except:
                    pass
            else:
                raise Exception("Invalid input_output string, use either 'input' or 'output'")
        return supp_dict
