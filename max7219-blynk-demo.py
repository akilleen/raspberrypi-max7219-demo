import time
import configparser
import sys

# LED Related Libs
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219
from PIL import ImageFont

# Blynk related libs
import blynklib

# Set device params
def initialize_device():
  serial = spi(port=0, device=0, gpio=noop())
  device = max7219(serial, rotate=2, height=8, width=32, block_orientation=90)

  return serial, device

# Write config
def write_config(text_value, delay):
  print("Writing config")
  config = configparser.ConfigParser()
  config.read('config.ini')
  config.set('scroll', 'text_string', text_value)
  config.set('scroll', 'delay', str(delay))
  with open('config.ini', 'w') as configfile:
    config.write(configfile)

def read_scroll_config():
  # Parse config
  config = configparser.ConfigParser()
  config.read('config.ini')

  # Set text and delay params
  text_string = config['scroll']['text_string']
  delay = float(config['scroll']['delay'])

  return text_string, delay

def read_blynk_config():
  # Parse config
  config = configparser.ConfigParser()
  config.read('config.ini')

  blynk_auth = config['blynk']['auth_key']
  
  return blynk_auth


# Main Logic
if __name__ == "__main__":
  auth_key = read_blynk_config()
  blynk = blynklib.Blynk(auth_key)
  
  @blynk.handle_event('write V0')
  def write_delay_pin_handler(pin, value):
    text_string, delay = read_scroll_config()
    print(f"Pin: {pin}, Value: {value[0]}")
    new_delay = float(value[0])/2550
    print(f"New delay: {new_delay}")
    write_config(text_string, new_delay)
  
  @blynk.handle_event('write V2')
  def write_text_pin_handler(pin, value):
    text_string, delay = read_scroll_config()
    print(f"Pin: {pin}, Value: {value[0]}")
    write_config(value[0], delay)

  serial, device = initialize_device()

  while True:
    
    blynk.run()
    text_string, delay = read_scroll_config()
    font = ImageFont.truetype('fonts/pixelmix.ttf', 8)
    viewport_width = len(text_string) * 8 + 32
    virtual = viewport(device, width=viewport_width, height=8)

    with canvas(virtual) as draw:
      draw.text((32,0), text_string, font=font, fill='white')

    for offset in range(viewport_width - 32):
      virtual.set_position((offset, 0))
      time.sleep(delay)
