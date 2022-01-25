import os.path


class Settings:
    def __init__(self, settings_file='/home/pi/iqa_test/settings.txt'):
        self.settings_file = settings_file
        if os.path.exists(settings_file) is False:
            with open(self.settings_file, 'w') as file:
                pass

    def read_setting(self, setting: str, param_only=False):
        setting = setting.lower()
        with open(self.settings_file, 'r') as file:
            for line in file:
                line.rstrip("\n")
                if setting in line and param_only is False:
                    return line
                elif setting in line and param_only is True:
                    line_list = line.split("=")
                    return str(line_list[1])
        return None

    def set_dut(self, dut: str):
        dut = dut.lower()
        if dut == "dacpro" or dut == "dacplus" or dut == "codeczero" or dut == "digiamp":
            dut_set = False
            with open(self.settings_file, 'r') as file:
                new_file = []
                for line in file:
                    line.rstrip("\n")
                    if "dut=" in line:
                        new_file.append("dut={}".format(dut))
                        dut_set = True
                    else:
                        new_file.append(line)
            with open(self.settings_file, 'w') as file:
                if dut_set:
                    file.writelines(new_file)
                else:
                    file.write("dut={}\n".format(dut))
        else:
            raise Exception("Invalid DUT string!")
