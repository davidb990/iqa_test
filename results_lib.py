import time
import csv


class Save:
    def __init__(self, qr_code: str, dut_type: str, error_code: int, test_time: float,  timestamp=str(time.time())):
        self.descriptor = ["QR Code", "Error Code", "DUT Type", "Timestamp", "Test Duration"]
        self.data_list = [qr_code, error_code, dut_type, timestamp, test_time]

    def to_file(self):
        with open("/results/{}_{}_{}.csv".format(self.data_list[2], self.data_list[0], self.data_list[3]), "w") as file:
            writer = csv.writer(file)
            writer.writerow(self.descriptor)
            writer.writerow(self.data_list)
