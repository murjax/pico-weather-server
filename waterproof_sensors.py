from machine import SPI,Pin,Timer
from ST7735 import TFT
from sysfont import sysfont
from time import sleep, sleep_ms
import onewire, ds18x20

tempSensor = ds18x20.DS18X20(onewire.OneWire(Pin(16)))
rainSensor = Pin(20, Pin.IN)

spi = machine.SPI(1, baudrate=1000000, polarity=0, phase=0, sck=machine.Pin(10), mosi=machine.Pin(11))
tft = TFT(spi, 12, 13, 14)
tft.initr()
tft.rgb(True)
tft.rotation(1)

tft.fill(TFT.BLACK)

formatted_temp = ""
rain_status = ""

roms = tempSensor.scan()

while True:
  try:
    tempSensor.convert_temp()
    sleep_ms(750)
    for rom in roms:
        temp = tempSensor.read_temp(rom)
        temp_f = temp * (9/5) + 32.0

        tft.text((40, 50), formatted_temp, TFT.BLACK, sysfont, 2, nowrap=True)
        tft.text((40, 70), rain_status, TFT.BLACK, sysfont, 2, nowrap=True)

        formatted_temp = f"{temp_f:.2f} F"

        tft.text((40, 50), formatted_temp, TFT.YELLOW, sysfont, 2, nowrap=True)

    if rainSensor.value() == 0:
        rain_status = "Currently raining"
    else:
        rain_status = "Not raining"

    tft.text((40, 70), rain_status, TFT.YELLOW, sysfont, 2, nowrap=True)

    sleep(10)
  except OSError as e:
    print('Failed to read sensors.')
