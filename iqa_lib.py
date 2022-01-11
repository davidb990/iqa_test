# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 15:28:23 2021

@author: David Bell
"""

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)


class Flags:
    def __init__(self, DUT3v3=11, DUT5v=5, DA_OC=13, Z2=10, DA_OV=12, DA_UV=6):
        self.DUT3v3 = DUT3v3
        self.DUT5v = DUT5v
        self.DA_OC = DA_OC
        self.Z2 = Z2
        self.DA_OV = DA_OV
        self.DA_UV = DA_UV
        GPIO.setup(self.DUT3v3, GPIO.IN)
        GPIO.setup(self.DUT5v, GPIO.IN)
        GPIO.setup(self.DA_OC, GPIO.IN)
        GPIO.setup(self.Z2, GPIO.IN)
        GPIO.setup(self.DA_OV, GPIO.IN)
        GPIO.setup(self.DA_UV, GPIO.IN)

    def DUT(self, poll_count=5):
        for n in range(poll_count):
            if GPIO.input(self.DUT3v3) == 0 and GPIO.input(self.DUT5v) == 0:
                return True
            time.sleep(0.1)
        return False

    def DA_OC(self, poll_count=5):
        for n in range(poll_count):
            if GPIO.input(self.DA_OC) == 0:
                return True
            time.sleep(0.1)
        return False

    def Z2(self, poll_count=5):
        for n in range(poll_count):
            if GPIO.input(self.Z2) == 0:
                return True
            time.sleep(0.1)
        return False

    def DA_OV(self, poll_count=5):
        for n in range(poll_count):
            if GPIO.input(self.DA_OV) == 1:
                return True
            time.sleep(0.1)
        return False

    def DA_UV(self, poll_count=5):
        for n in range(poll_count):
            if GPIO.input(self.DA_UV) == 1:
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
        GPIO.output(self.Z2, GPIO.HIGH)

    def DUT(self, enable_bool):
        if enable_bool:
            GPIO.output(self.DUT, GPIO.LOW)
        elif not enable_bool:
            GPIO.output(self.DUT, GPIO.HIGH)
        else:
            raise Exception("Invalid argument for Enable.DUT(enable_bool)")

    def DA(self, enable_bool):
        if enable_bool:
            GPIO.output(self.DA, GPIO.HIGH)
        elif not enable_bool:
            GPIO.output(self.DA, GPIO.LOW)
        else:
            raise Exception("Invalid argument for Enable.DA(enable_bool)")

    def Z2(self, enable_bool):
        if enable_bool:
            GPIO.output(self.Z2, GPIO.LOW)
        elif not enable_bool:
            GPIO.output(self.Z2, GPIO.HIGH)
        else:
            raise Exception("Invalid argument for Enable.Z2(enable_bool)")
