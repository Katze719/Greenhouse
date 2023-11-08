#!/bin/python3
"""
main.py

Hier beginnt und hört das Programm auf
"""

import RPi.GPIO as GPIO
import dht11
import time
import curses
import board
from adafruit_ht16k33.segments import Seg7x4

# GPIO einrichten
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

# DHT11 erstellen
instance = dht11.DHT11(pin = 4)

# 7 segment anzeige einrichten
i2c = board.I2C()
segment = Seg7x4(i2c, address=0x70)
segment.fill(0)
segment.colon = False

# main funktion
def main(stdscr):
    # zähler für die anzahl der erfolgten messungen
    measurements = 0

    curses.curs_set(0)

    # bedienelemente mit in die konsole schreiben
    stdscr.addstr(4, 0, "Strg+C")
    stdscr.addstr(4, 12, "-> Programm Abbrechen")
    stdscr.addstr(5, 0, "Linksklick")
    stdscr.addstr(5, 12, "-> Konsole Pausieren (Programm läuft im Hintergrund weiter)")
    stdscr.addstr(6, 0, "Rechtsklick")
    stdscr.addstr(6, 12, "-> Konsole Weiter")
    
    # loop für das messen und anzeigen der daten
    while True:
        # eine sekunde warten, sollte reichen (zeit kann verringert werden wenn nötig)
        time.sleep(1)

        # anzahl der messungen um eins erhöhen
        measurements += 1

        # daten vom dht11 lesen
        result = instance.read()

        # prüfen ob die daten valid sind, wenn nicht nochmal lesen
        while not result.is_valid():
            result = instance.read()

        # Temperatur in den Konsolen buffer schreiben, auf zeile eins
        stdscr.addstr(0, 0, "Temperatur:")
        stdscr.addstr(0, 14, f"{result.temperature} C")

        # Feuchtigkeit in den Konsolen buffer schreiben, auf zeile zwei
        stdscr.addstr(1, 0, "Feuchtigkeit:")
        stdscr.addstr(1, 14, f"{result.humidity} %")

        # Messungs zähler in den Konsolen buffer schreiben, auf zeile drei
        stdscr.addstr(2, 0, f"Messung:")
        stdscr.addstr(2, 14, f"{measurements}")
        # Buffer flushen (anzeigen in der Konsole)
        stdscr.refresh()

        # Temperatur in den buffer von der 7 segment anzeige schreiben 
        segment[0] = str(result.temperature)[0]
        segment[1] = str(result.temperature)[1]
        segment[1] = str(result.temperature)[2]
        segment[2] = str(result.temperature)[3]
        segment[3] = 'C'

        # Daten auf der 7 segment anzeige aktuallisieren (anzeigen)
        segment.show()

# Funktion main wird aufgerufen wenn das script direkt in der konsole gestartet wird
if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        segment.fill(0)    
