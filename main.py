#!/bin/python3
"""
main.py

this is the main python file
"""

import RPi.GPIO as GPIO
import dht11
import time
import curses
import board
from adafruit_ht16k33.segments import Seg7x4

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

instance = dht11.DHT11(pin = 4)

i2c = board.I2C()
segment = Seg7x4(i2c, address=0x70)
segment.fill(0)


def main(stdscr):
    measurements = 0

    curses.curs_set(0)

    while True:
        time.sleep(1)
        measurements += 1
        result = instance.read()

        while not result.is_valid():
            result = instance.read()

        stdscr.addstr(0, 0, "Temperatur: %-3.1f C" % result.temperature)
        stdscr.addstr(1, 0, "Feuchtigkeit: %-3.1f %%" % result.humidity)
        stdscr.addstr(2, 0, f"Messung: {measurements}")
        stdscr.refresh()

        segment[0] = str(result.temperature)[0]
        segment[1] = str(result.temperature)[1]
        segment[1] = str(result.temperature)[2]
        segment[2] = str(result.temperature)[3]
        segment[3] = 'C'


        segment.colon = False

        segment.show()
    

if __name__ == '__main__':
    curses.wrapper(main)
