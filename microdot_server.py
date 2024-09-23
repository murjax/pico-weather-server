import network
from time import sleep
from picozero import pico_led
import machine
import dht
from ST7735 import TFT
from sysfont import sysfont

import asyncio
from microdot import Microdot, send_file

ssid = 'SSID'
password = 'PASSWORD'

sensor = dht.DHT22(machine.Pin(16))

spi = machine.SPI(1, baudrate=1000000, polarity=0, phase=0, sck=machine.Pin(10), mosi=machine.Pin(11))
tft = TFT(spi, 12, 13, 14)

global temperature
global humidity

temperature = ''
humidity = ''

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print(wlan.status)
        print('Waiting for connection')
        sleep(1)

    print(wlan.ifconfig())
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def get_reading():
    sensor.measure()
    temp = sensor.temperature()
    temp_f = temp * (9/5) + 32.0
    humidity = sensor.humidity()
    formatted_temp = f"{temp_f:.2f} F"
    formatted_humidity = f"{humidity:.2f} %"
    return (formatted_temp, formatted_humidity)

async def update_reading():
    while True:
        global temperature
        global humidity
        (temperature, humidity) = get_reading()

        update_screen()

        await asyncio.sleep(5)

def setup_screen():
    tft.initr()
    tft.rgb(True)
    tft.rotation(1)
    tft.fill(TFT.BLACK)

def update_screen():
    tft.fill(TFT.BLACK)
    tft.text((40, 50), temperature, TFT.YELLOW, sysfont, 2, nowrap=True)
    tft.text((40, 70), humidity, TFT.YELLOW, sysfont, 2, nowrap=True)

def build_webpage(led_state):
    with open('template.html', 'r') as file:
        template = file.read()

    html = template.format(
        temperature = temperature,
        humidity = humidity,
        led_state = led_state
    )

    return html

pico_led.off()
setup_screen()
connect()

app = Microdot()

@app.get('/')
async def root(request):
    led_state = 'ON' if pico_led.value == 1 else 'OFF'

    return build_webpage(led_state), 200, {'Content-Type': 'text/html'}

@app.get('/lighton')
async def lighton(request):
    pico_led.on()

    return build_webpage('ON'), 200, {'Content-Type': 'text/html'}

@app.get('/lightoff')
async def lighton(request):
    pico_led.off()

    return build_webpage('OFF'), 200, {'Content-Type': 'text/html'}

@app.get('/app.js')
async def index(request):
    return send_file('app.js')

async def main():
    # start the server in a background task
    server = asyncio.create_task(app.start_server(port=80))

    asyncio.create_task(update_reading())
    # ... do other asynchronous work here ...

    # cleanup before ending the application
    await server

asyncio.run(main())

# while True:
#     global temperature
#     global humidity
#     (temperature, humidity) = get_reading()
#     update_screen()
#     sleep(10)
