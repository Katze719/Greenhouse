#/bin/python3
"""
main.py

this is the main python file
"""

import RPi.GPIO as GPIO
import dht11
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

instance = dht11.DHT11(pin = 4)

while True:
    time.sleep(1)

    result = instance.read()

    while not result.is_valid():
        result = instance.read()

    print("Temperatur: %-3.1f C" % result.temperature)
    print("Feuchtigkeit: %-3.1f %%" % result.humidity)
    