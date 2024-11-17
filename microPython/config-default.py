'''

RENAME/COPY this file to `config.py` on your device
- edit if needed
- button definition and display swapping is done here.

'''

from machine import Pin

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
        swap_displays: whether left display is I2C0 (false) or I2C1 (true)
    '''
    button = Pin(2, Pin.IN, Pin.PULL_UP)
    buttonDown = 0
    buttonTm = 50
    buttonLong = 500
    swap_displays = False

    '''
        Timing and timeout config:
        updateTime:     (int, ms)  Basic time interval between update cycles
        rebootDelay:    (int) Countdown in seconds when auto-restarting/rebooting printPy
    '''
    updateTime = 1000
    rebootDelay = 3

    '''
        Serial Device Config:
        device:   (int) UART device (0 or 1)
        baud:     (int) Serial baud rate; should match the setting used in config.g
        quiet:    (bool) suppress info messages
    '''
    device = 0
    baud = 57600
    quiet = False

    '''
        Machine Config:
        net:    Default Network Interface number
    '''
    net = 0