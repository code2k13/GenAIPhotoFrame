import time
import ssl
import wifi
import socketpool
import microcontroller
import adafruit_requests
import board
import busio
from adafruit_st7735r import ST7735R
import displayio
from io import BytesIO
import adafruit_imageload
import gc
import microcontroller

endpoint = ("ENDPOINT")

try:
    wifi.radio.connect("WIFI_SSID", "WIFI_PWD")
except Exception as e:
    print("Trouble connecting:\n", str(e))
    time.sleep(60)
    microcontroller.reset()

mosi_pin = board.GP11
clk_pin = board.GP10
reset_pin = board.GP17
cs_pin = board.GP18
dc_pin = board.GP16

displayio.release_displays()
spi = busio.SPI(clock=clk_pin, MOSI=mosi_pin)
display_bus = displayio.FourWire(
    spi, command=dc_pin, chip_select=cs_pin, reset=reset_pin
)
display = ST7735R(display_bus, width=128, height=160, bgr=True)
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

def get_img_group():
    response = requests.get(endpoint, stream=True)
    slide_show = displayio.Group()
    display.show(slide_show)
    gc.collect()
    image, palette = adafruit_imageload.load(
        BytesIO(response.content),
        bitmap=displayio.Bitmap,
        palette=displayio.Palette,
    )
    image_sprite = displayio.TileGrid(image, pixel_shader=palette)
    slide_show.append(image_sprite)
    gc.collect()
    return

while True:
    try:
        get_img_group()
        time.sleep(2)
    except Exception as e:
        print("Error:\n", str(e))
        time.sleep(60)
        microcontroller.reset()

