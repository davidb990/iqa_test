import RPi.GPIO as GPIO
import sys

GPIO.setmode(GPIO.BCM)


class Relay:
    def __init__(self, relay0=8, relay1=7, relay2=9, relay3=10, relay4=11, relay5=26):
        self.aux_out = relay0
        self.rca = relay1
        self.phones = relay2
        self.xlr = relay3
        self.aux_in = relay5
        self.mic = relay4
        self.all = [self.aux_out, self.rca, self.phones, self.xlr, self.aux_in, self.mic]
        for n in self.all:
            GPIO.setup(n, GPIO.OUT)
            GPIO.output(n, GPIO.LOW)

    def relay(self, relay: str, on_off: str):
        relay_list = ["aux_out", "rca", "phones", "xlr", "aux_in",
                      "mic"]  # note: relays must have the same index as in self.all
        if relay.lower() in relay_list and on_off.lower() == "on":
            index = relay_list.index(relay)
            GPIO.output(self.all[index], GPIO.HIGH)
        elif relay.lower() in relay_list and on_off.lower() == "off":
            index = relay_list.index(relay)
            GPIO.output(self.all[index], GPIO.LOW)
        elif relay.lower() == "all" and on_off.lower() == "on":
            for n in self.all:
                GPIO.output(n, GPIO.HIGH)
        elif relay.lower() == "all" and on_off.lower() == "off":
            for n in self.all:
                GPIO.output(n, GPIO.LOW)
        else:
            sys.exit("Invalid Relay.relay(relay, on_off) params, relay must be one of:"
                     "\naux_out\nrca\nphones\nxlr\naux_in\nmic\nall\non_off must be either 'on' or 'off'")
