import RPi.GPIO as GPIO
import time


class Buzz:
    def __init__(self, buzzer_pin=21):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.buzzer = buzzer_pin
        GPIO.setup(self.buzzer, GPIO.OUTPUT)
        GPIO.output(self.buzzer, GPIO.LOW)

    def buzz(self, duration: float):
        GPIO.output(self.buzzer, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(self.buzzer, GPIO.LOW)
