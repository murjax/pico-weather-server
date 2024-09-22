import network
import socket
from time import sleep
from picozero import pico_led
import machine
import dht
from ST7735 import TFT
from sysfont import sysfont

ssid = 'SSID_HERE'
password = 'PASSWORD_HERE'

sensor = dht.DHT22(machine.Pin(16))

spi = machine.SPI(1, baudrate=1000000, polarity=0, phase=0, sck=machine.Pin(10), mosi=machine.Pin(11))
tft = TFT(spi, 12, 13, 14)

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection')
        sleep(1)

    print(wlan.ifconfig())
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def open_socket(ip):
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return connection

def get_reading():
    sensor.measure()
    temp = sensor.temperature()
    temp_f = temp * (9/5) + 32.0
    humidity = sensor.humidity()
    formatted_temp = f"{temp_f:.2f} F"
    formatted_humidity = f"{humidity:.2f} %"
    return (formatted_temp, formatted_humidity)

def setup_screen():
    tft.initr()
    tft.rgb(True)
    tft.rotation(1)
    tft.fill(TFT.BLACK)

def update_screen(temperature, humidity):
    tft.fill(TFT.BLACK)
    tft.text((40, 50), temperature, TFT.YELLOW, sysfont, 2, nowrap=True)
    tft.text((40, 70), humidity, TFT.YELLOW, sysfont, 2, nowrap=True)

def webpage(temperature, humidity, state):
    with open('template.html', 'r') as file:
        template = file.read()

    html = template.format(
        temperature = temperature,
        humidity = humidity,
        state = state
    )

    return html

def serve_file(client, file_name, content_type):
    with open(file_name, 'rb') as file:
        content = file.read()

    headers = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n\r\n"
    client.send(headers.encode())
    client.sendall(content)

def serve_page(client, state):
    (temperature, humidity) = get_reading()
    update_screen(temperature, humidity)
    html = webpage(temperature, humidity, state)
    client.send(html)

def serve(connection):
    state = 'OFF'
    pico_led.off()

    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)

        try:
            request = request.split()[1]
        except IndexError:
            pass

        print(request)

        if request == '/':
            serve_page(client, state)
        elif request == '/lighton?':
            pico_led.on()
            state = 'ON'
            serve_page(client, state)
        elif request =='/lightoff?':
            pico_led.off()
            state = 'OFF'
            serve_page(client, state)
        elif request.endswith('.js'):
            print('serving js file')
            print(request[1:])
            serve_file(client, request[1:], 'application/javascript')

        client.close()

try:
    setup_screen()
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()
