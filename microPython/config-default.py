'''

RENAME/COPY this file to `config.py` on your device
- edit if needed, defaults are sensible ones for a XIAO2040 based device
- button definition and display swapping is done here.

'''

from machine import UART, Pin, I2C

class config():
    '''
        Hardware config:
        button:        Status button pin object
                        (set '= None' to disable)
                        eg: button = Pin(2, Pin.IN, Pin.PULL_UP)
                        see the micropython 'machine.Pin()' docs
        buttonDown:    Pin value when button depressed
        buttonTm:      debounce time (ms); keep this as low as practical
        buttonLong:    long press time (ms) for WiFi toggle, 0 to disable
        I2C_left:      I2C interface definitions for left and right screens
        I2C_right:     Currently uses default pins and hardware interfaces and
                       can be adapted with softI2C+alternate pins as needed.
    '''
    button = Pin(2, Pin.IN, Pin.PULL_UP)
    buttonDown = 0
    buttonTm = 50
    buttonLong = 500
    I2C_left = I2C(1, sda=Pin(6), scl=Pin(7))
    I2C_right = I2C(0, sda=Pin(28), scl=Pin(29))

    '''
        Display and led brightness
        display_bright: Display Brightness (float, 0 to 1)
        display_invert: Display inversion (bool)
        display_rotate: Display flip display vertically (bool)
        led_bright:     Indicator LED brightness (float, 0 to 1)
        led_bright_off: Indicator LED brightness when machine off
    '''
    display_bright = float(0.66)
    display_invert = False
    display_rotate = True
    led_bright = float(1)
    led_bright_off = float(0.5)

    '''
        Timing and timeout config:
        updateTime:     (int, ms)  Basic time interval between update cycles
        rebootDelay:    (int) Countdown in seconds when auto-restarting/rebooting printPy
    '''
    updateTime = 1000
    rebootDelay = 3

    '''
        Serial Device Config:
        device:   UART device
        baud:     (int) Serial baud rate; should match the setting used in config.g
        quiet:    (bool) suppress info messages
    '''
    device = UART(0)
    baud = 57600
    quiet = False

    '''
        Machine Config:
        net:    Default Network Interface number
                (`None` to disale network status display and functions)
    '''
    net = 0
