# The microPython standard libs
from sys import exit
from time import sleep_ms, ticks_ms

# Import config
try:
    from config import config
except Exception as e:
    print('Failed to find config; copy config-default.py to config.py, edit of necesscary and try again')
    print(e)
    exit()

'''
    Test the Hardware for the XIAO204 version of PrintMPy
'''
print('Testing printXIAO comms, screen, pixel and button')

# pixel
from neopixel import NeoPixel
pixelVcc = config.pixel_power   # Pixel VCC pin
pixelVcc.value(1)               # turn on immediately
pixel = NeoPixel(config.pixel_pin,1)  # data pin
pixel[0]=(0,0,0)
pixel.write()

# UART connection
rrf = config.device
rrf.init(baudrate=config.baud, timeout = 25, timeout_char = 25, rxbuf = 2048)
if not rrf:
    print('No UART device found')
    exit()
else:
    print('UART initialised')
# UART port and buffer will be in a unknown state; there may be junk in it
# So; send a newline, then wait a bit (display init), then empty the buffer
rrf.write('\n')
rrf.flush()

# hardware button
def buttonPressed():
    print('Button Pressed')
    sleep_ms(100)   # crude debounce

if config.button is not None:
    button = config.button
    button.irq(trigger=button.IRQ_FALLING | button.IRQ_RISING, handler=buttonPressed)
    print('Button present on:', repr(button).split('(')[1].split(',')[0])
else:
    print('No Button')

# Get output/display device
try:
    from ssd1306 import SSD1306_I2C
    left = SSD1306_I2C(128, 64, config.I2C_left, addr=0x3c)
    right = SSD1306_I2C(128, 64, config.I2C_right, addr=0x3c)
except Exception as e:
    print('Failed to start displays!\n{}'.format(e))
    exit()
# And display something
left.invert(config.display_invert)
right.invert(config.display_invert)
left.rotate(config.display_rotate)
right.rotate(config.display_rotate)
left.contrast(int(config.bright * 255))
right.contrast(int(config.bright * 255))
left.fill(0)
right.fill(0)
left.rect(0, 0, 128, 64, 1, False)
right.rect(0, 0, 128, 64, 1, False)
left.text(16, 48, 'Left')
right.text(16, 48, 'Right')
left.show()
right.show()
left.poweron()
right.poweron()

rgb = (0, 255, 0)
# Now read+print from the UART while flashing the neopixel
# (and taking interrupts from the button)
while True:
    end = ticks_ms() + 1000
    rrf.send('M122\n')
    pixel[0] = rgb
    pixel.write()
    rgb = (rgb[2],rgb[0],rgbs[1])
    # wait for a second showing anything incoming on UART
    while ticks_ms < end:
        print(rrf.read())
        sleep_ms(10)