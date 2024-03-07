#!/bin/python3
# Dies ist eine Shebang-Zeile, die angibt, dass dieses Skript mit Python 3 ausgeführt werden soll.

# Importieren von erforderlichen Modulen und Bibliotheken.
import RPi.GPIO as GPIO
import dht11
import time
import logging
import board
import busio
import smbus
import adafruit_character_lcd.character_lcd_i2c as character_lcd
from adafruit_ht16k33.segments import Seg7x4
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('debug.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(relativeCreated)6d - %(threadName)s - %(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

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
lcd_rows = 2

# Initialisierung I2C Bus
i2c = busio.I2C(board.SCL, board.SDA)

# Festlegen des LCDs in die Variable LCD
lcd = character_lcd.Character_LCD_I2C(i2c, lcd_columns, lcd_rows, 0x21)

if(GPIO.RPI_REVISION == 1):
    bus = smbus.SMBus(0)
else:
    bus = smbus.SMBus(1)

class LightSensor():

    def __init__(self):
        # Definiere Konstante vom Datenblatt
        self.DEVICE = 0x5c # Standart I2C Geräteadresse

        self.POWER_DOWN = 0x00 # Kein aktiver zustand
        self.POWER_ON = 0x01 # Betriebsbereit
        self.RESET = 0x07 # Reset des Data registers

        # Starte Messungen ab 4 Lux.
        self.CONTINUOUS_LOW_RES_MODE = 0x13
        # Starte Messungen ab 1 Lux.
        self.CONTINUOUS_HIGH_RES_MODE_1 = 0x10
        # Starte Messungen ab 0.5 Lux.
        self.CONTINUOUS_HIGH_RES_MODE_2 = 0x11
        # Starte Messungen ab 1 Lux.
        # Nach messung wird Gerät in einen inaktiven Zustand gesetzt.
        self.ONE_TIME_HIGH_RES_MODE_1 = 0x20
        # Starte Messungen ab 0.5 Lux.
        # Nach messung wird Gerät in einen inaktiven Zustand gesetzt.
        self.ONE_TIME_HIGH_RES_MODE_2 = 0x21
        # Starte Messungen ab 4 Lux.
        # Nach messung wird Gerät in einen inaktiven Zustand gesetzt.
        self.ONE_TIME_LOW_RES_MODE = 0x23


    def convertToNumber(self, data):
        # Einfache Funktion um 2 Bytes Daten
        # in eine Dezimalzahl umzuwandeln
        # https://github.com/claws/BH1750 begründung zu den / 1.2
        return ((data[1] + (256 * data[0])) / 1.2)

    def readLight(self):
        data = bus.read_i2c_block_data(self.DEVICE,self.ONE_TIME_HIGH_RES_MODE_1)
        return round(self.convertToNumber(data))

class Matrix():
    def __init__(self, cascaded, block_orientation, rotate) -> None:
        self.serial = spi(port=0, device=1, gpio=noop())
        self.device = max7219(self.serial, cascaded=cascaded or 1, block_orientation=block_orientation, rotate=rotate or 0)

    def showPattern(self, direction):
        # Definition von Pattern
        arrows = {
            'up': [
                0b00011000,
                0b00111100,
                0b01111110,
                0b11111111,
                0b00011000,
                0b00011000,
                0b00011000,
                0b00011000,
            ],
            'down': [
                0b00011000,
                0b00011000,
                0b00011000,
                0b00011000,
                0b11111111,
                0b01111110,
                0b00111100,
                0b00011000,
            ],
            'smiley': [
                0b00111100,
                0b01000010,
                0b10100101,
                0b10000001,
                0b10100101,
                0b10011001,
                0b01000010,
                0b00111100,
            ]
        }

        # Macht alle Großbuchstaben klein
        arrow_pattern = arrows.get(direction.lower())

        if arrow_pattern:
            # Zeige das Bild auf der Matrix an
            with canvas(self.device) as draw:
                for i in range(8):
                    for j in range(8):
                        if arrow_pattern[i] & (1 << (7 - j)):
                            draw.point((j, i), fill="white")

def main():

    # Hintergrundbeleuchtung einschalten
    lcd.backlight = True

    # Initialisiert die Anzahl der Messungen.
    measurements = 0

    # Eine Variable, um zwischen Temperatur und Feuchtigkeit auf dem 7-Segment-Display zu wechseln.
    change = 0

    # Speichert die Zeit der letzten Anzeigeaktualisierung.
    last_display_time = time.time()

    light_sensor = LightSensor()

    matrix_field = Matrix(cascaded=1, block_orientation=90, rotate=0)

    while True:        
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
            logger.debug("DHT11 Messwerte ungültig!")
            result = instance.read()
            time.sleep(0.1)

        lux = light_sensor.readLight()

        # Zeigt die gemessenen Werte im Terminal an.
        logger.debug(f"Temperatur: {result.temperature} C")
        logger.debug(f"Feuchtigkeit: {result.humidity} %")
        logger.debug(f"Heligkeit: {lux} lx")
        logger.debug(f"Messung: {measurements}")

        if lux > 50000:
            matrix_field.showPattern("up")
        elif lux < 35000:
            matrix_field.showPattern("down")
        else:
            matrix_field.showPattern("smiley")


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
            segment.set_digit_raw(3, 0b01110011)
        segment.show()

        lcd.message = f"Temperatur:{result.temperature}C\nFeuchte:   {result.humidity}%"

        # Verzögert die Schleife um 1 Sekunde.
        time.sleep(1)


# Der Hauptteil des Codes. Hier wird die curses-Bibliothek verwendet, um das Terminal-UI zu erstellen.
if __name__ == '__main__':
    try:
        logger.info("Programm start")
        main()
    except KeyboardInterrupt:
        segment.fill(0)
        lcd.clear()
        lcd.backlight = False
        logger.info("Programm ende")
    except Exception as e:
        logger.error(f"Fehler im Programm: {str(e)}")
