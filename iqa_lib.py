# This library controls the Flags, Enables and QR code reader for the tests.


import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class Flags:
    def __init__(self, DUT3v3=11, DUT5v=5, DA_OC=13, Z2=10, DA_OV=12, DA_UV=6, CONN_CHK=4):
        self.DUT3v3 = DUT3v3
        self.DUT5v = DUT5v
        self.DA_OC = DA_OC
        self.Z2 = Z2
        self.DA_OV = DA_OV
        self.DA_UV = DA_UV
        self.CONN_CHK = CONN_CHK
        GPIO.setup(self.DUT3v3, GPIO.IN)
        GPIO.setup(self.DUT5v, GPIO.IN)
        GPIO.setup(self.DA_OC, GPIO.IN)
        GPIO.setup(self.Z2, GPIO.IN)
        GPIO.setup(self.DA_OV, GPIO.IN)
        GPIO.setup(self.DA_UV, GPIO.IN)
        GPIO.setup(self.CONN_CHK, GPIO.IN)

    def dut(self, poll_count=5) -> bool:
        for n in range(poll_count):
            if GPIO.input(self.DUT3v3) == 0 and GPIO.input(self.DUT5v) == 0:
                return True
            time.sleep(0.1)
        return False

    def da_oc(self, poll_count=5) -> bool:
        for n in range(poll_count):
            if GPIO.input(self.DA_OC) == 0:
                return True
            time.sleep(0.1)
        return False

    def z2(self, poll_count=5) -> bool:
        for n in range(poll_count):
            if GPIO.input(self.Z2) == 0:
                return True
            time.sleep(0.1)
        return False

    def da_ov(self, poll_count=5) -> bool:
        for n in range(poll_count):
            if GPIO.input(self.DA_OV) == 1:
                return True
            time.sleep(0.1)
        return False

    def da_uv(self, poll_count=5) -> bool:
        for n in range(poll_count):
            if GPIO.input(self.DA_UV) == 1:
                return True
            time.sleep(0.1)
        return False

    def conn_chk(self, poll_count=5) -> bool:
        for n in range(poll_count):
            if GPIO.input(self.CONN_CHK) == 0:
                return True
            time.sleep(0.1)
        return False


class Enable:
    def __init__(self, DUT=7, DA=9, Z2=8):
        self.DUT = DUT
        self.DA = DA
        self.Z2 = Z2
        GPIO.setup(self.DUT, GPIO.OUT)
        GPIO.setup(self.DA, GPIO.OUT)
        GPIO.setup(self.Z2, GPIO.OUT)
        GPIO.output(self.DUT, GPIO.HIGH)
        GPIO.output(self.DA, GPIO.LOW)
        GPIO.output(self.Z2, GPIO.LOW)

    def dut(self, enable_bool: bool):
        if enable_bool:
            GPIO.output(self.DUT, GPIO.LOW)
        elif not enable_bool:
            GPIO.output(self.DUT, GPIO.HIGH)
        else:
            raise Exception("Invalid argument for Enable.DUT(enable_bool)")

    def da(self, enable_bool: bool):
        if enable_bool:
            GPIO.output(self.DA, GPIO.HIGH)
        elif not enable_bool:
            GPIO.output(self.DA, GPIO.LOW)
        else:
            raise Exception("Invalid argument for Enable.DA(enable_bool)")

    def z2(self, enable_bool: bool):
        if enable_bool:
            GPIO.output(self.Z2, GPIO.LOW)
        elif not enable_bool:
            GPIO.output(self.Z2, GPIO.HIGH)
        else:
            raise Exception("Invalid argument for Enable.Z2(enable_bool)")


class LEDS:
    def __init__(self, green=26, orange=17, red=16):
        self.green = green
        self.orange = orange
        self.red = red
        GPIO.setup(self.green, GPIO.OUT)
        GPIO.setup(self.orange, GPIO.OUT)
        GPIO.setup(self.red, GPIO.OUT)
        GPIO.output(self.green, GPIO.LOW)
        GPIO.output(self.orange, GPIO.LOW)
        GPIO.output(self.red, GPIO.LOW)

    def all_off(self):
        GPIO.output(self.green, GPIO.LOW)
        GPIO.output(self.orange, GPIO.LOW)
        GPIO.output(self.red, GPIO.LOW)

    def ready(self):
        GPIO.output(self.green, GPIO.HIGH)
        GPIO.output(self.orange, GPIO.HIGH)
        GPIO.output(self.red, GPIO.HIGH)

    def passed(self):
        self.all_off()
        GPIO.output(self.green, GPIO.HIGH)

    def testing(self):
        self.all_off()
        GPIO.output(self.orange, GPIO.HIGH)

    def failed(self):
        self.all_off()
        GPIO.output(self.red, GPIO.HIGH)


class QR:
    @staticmethod
    def read():
        return input("\nPlease scan the QR code\n")
