#!/bin/python3
# Dies ist eine Shebang-Zeile, die angibt, dass dieses Skript mit Python 3 ausgeführt werden soll.

# Importieren von erforderlichen Modulen und Bibliotheken.
import RPi.GPIO as GPIO
import dht11
import time
import curses
import board
import busio
import adafruit_character_lcd.character_lcd_i2c as character_lcd
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

# Definiere LCD Zeilen und Spaltenanzahl.
lcd_columns = 16
lcd_rows    = 2

# Initialisierung I2C Bus
i2c = busio.I2C(board.SCL, board.SDA)

# Festlegen des LCDs in die Variable LCD
lcd = character_lcd.Character_LCD_I2C(i2c, lcd_columns, lcd_rows, 0x21)

def main(stdscr):

    # Hintergrundbeleuchtung einschalten
    # lcd.backlight = True
    lcd.backlight = False

    def addDataLineToTerminal(line_number, title, data):
        stdscr.addstr(line_number, 0, title)
        stdscr.addstr(line_number, 14, data)

    def addKeyDescriptionToTerminal(line_number, key, description):
        stdscr.addstr(line_number, 0, key)
        stdscr.addstr(line_number, 10, "->")
        stdscr.addstr(line_number, 12, description)

    # Initialisiert die Anzahl der Messungen.
    measurements = 0

    # Blendet den Cursor in der Terminalausgabe aus.
    curses.curs_set(0)

    # Fügt Informationen zur Bedienung des Programms im Terminal hinzu.
    addKeyDescriptionToTerminal(4, "Strg+C", "Programm Abbrechen")
    addKeyDescriptionToTerminal(5, "Linksklick", "Konsole Pausieren (Programm läuft im Hintergrund weiter)")
    addKeyDescriptionToTerminal(6, "Rechtsklick", "Konsole Weiter")

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
        addDataLineToTerminal(0, "Temperatur:", f"{result.temperature} C")
        addDataLineToTerminal(1, "Feuchtigkeit:", f"{result.humidity} %")
        addDataLineToTerminal(2, "Messung:", f"{measurements}")
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

        lcd.message = f"Temperatur:{result.temperature}C\nFeuchte:   {result.humidity}%"


# Der Hauptteil des Codes. Hier wird die curses-Bibliothek verwendet, um das Terminal-UI zu erstellen.
if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        segment.fill(0)
        lcd.clear()
        lcd.backlight = False
