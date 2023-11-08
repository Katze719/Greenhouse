#!/bin/python3
# Dies ist eine Shebang-Zeile, die angibt, dass dieses Skript mit Python 3 ausgeführt werden soll.

# Importieren von erforderlichen Modulen und Bibliotheken.
import RPi.GPIO as GPIO
import dht11
import time
import curses
import board
from adafruit_ht16k33.segments import Seg7x4

# Deaktiviert GPIO-Warnungen.
GPIO.setwarnings(False)

# Legt den Modus des GPIO-Pins auf den Broadcom SOC channel-Namen fest.
GPIO.setmode(GPIO.BCM)

# Bereinigt die GPIO-Pin-Konfiguration.
GPIO.cleanup()

# Initialisiert den DHT11-Sensor und weist ihm den GPIO-Pin 4 zu.
instance = dht11.DHT11(pin=4)

# Initialisiert das 7-Segment-Display für die Anzeige der Sensorwerte.
i2c = board.I2C()
segment = Seg7x4(i2c, address=0x70)
segment.fill(0)
segment.colon = False

def main(stdscr):
    # Initialisiert die Anzahl der Messungen.
    measurements = 0

    # Blendet den Cursor in der Terminalausgabe aus.
    curses.curs_set(0)

    # Fügt Informationen zur Bedienung des Programms im Terminal hinzu.
    stdscr.addstr(4, 0, "Strg+C")
    stdscr.addstr(4, 12, "-> Programm Abbrechen")
    stdscr.addstr(5, 0, "Linksklick")
    stdscr.addstr(5, 12, "-> Konsole Pausieren (Programm läuft im Hintergrund weiter)")
    stdscr.addstr(6, 0, "Rechtsklick")
    stdscr.addstr(6, 12, "-> Konsole Weiter")

    # Eine Variable, um zwischen Temperatur und Feuchtigkeit auf dem 7-Segment-Display zu wechseln.
    change = 0

    # Speichert die Zeit der letzten Anzeigeaktualisierung.
    last_display_time = time.time()

    while True:
        # Verzögert die Schleife um 1 Sekunde.
        time.sleep(1)

        # Speichert die aktuelle Zeit.
        current_time = time.time()

        # Wechselt alle 5 Sekunden zwischen Temperatur und Feuchtigkeit.
        if current_time - last_display_time >= 5:
            change = (change + 1) % 2
            last_display_time = current_time

        # Inkrementiert die Messanzahl.
        measurements += 1

        # Liest die Daten vom DHT11-Sensor.
        result = instance.read()

        # Wiederholt das Lesen, bis gültige Daten vorliegen.
        while not result.is_valid():
            result = instance.read()

        # Zeigt die gemessenen Werte im Terminal an.
        stdscr.addstr(0, 0, "Temperatur:")
        stdscr.addstr(0, 14, f"{result.temperature} C")
        stdscr.addstr(1, 0, "Feuchtigkeit:")
        stdscr.addstr(1, 14, f"{result.humidity} %")
        stdscr.addstr(2, 0, f"Messung:")
        stdscr.addstr(2, 14, f"{measurements}")
        stdscr.refresh()

        # Aktualisiert das 7-Segment-Display mit den Sensorwerten.
        if change == 0:
            segment[0] = str(result.temperature)[0]
            segment[1] = str(result.temperature)[1]
            segment[1] = str(result.temperature)[2]
            segment[2] = str(result.temperature)[3]
            segment[3] = 'C'
        else:
            segment[0] = str(result.humidity)[0]
            segment[1] = str(result.humidity)[1]
            segment[1] = str(result.humidity)[2]
            segment[2] = str(result.humidity)[3]
            segment.set_digit_raw(3, 0b11110011)
        segment.show()

# Der Hauptteil des Codes. Hier wird die curses-Bibliothek verwendet, um das Terminal-UI zu erstellen.
if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        segment.fill(0)
