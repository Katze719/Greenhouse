#!/bin/python3
"""
main.py

this is the main python file
"""

import RPi.GPIO as GPIO
import dht11
import time
import board
from adafruit_ht16k33.segments import Seg7x4

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

instance = dht11.DHT11(pin = 4)

i2c = board.I2C()
segment = Seg7x4(i2c, address=0x70)
segment.fill(0)


while True:
    time.sleep(1)

    result = instance.read()

    while not result.is_valid():
        result = instance.read()

    print("Temperatur: %-3.1f C" % result.temperature)
    print("Feuchtigkeit: %-3.1f %%" % result.humidity)

    segment[0] = str(result.temperature)[0]
    segment[1] = str(result.temperature)[1]
    segment[1] = str(result.temperature)[2]
    segment[2] = str(result.temperature)[3]
    segment[3] = 'C'


    segment.colon = False

    segment.show()
    