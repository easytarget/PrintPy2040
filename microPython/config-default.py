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
        Display settings
        display_bright: Display Brightness (float, 0 to 1)
        display_invert: Display inversion (bool)
        display_rotate: Display flip display vertically (bool)
    '''
    display_bright = float(0.66)
    display_invert = False
    display_rotate = True

    '''
        LED 'mood' illumination
        illuminate:  Use onboard LED(s) for mood and heartbeat (bool)
        led_bright:  Indicator LED brightness (float, 0 to 1)
        led_standby: Indicator LED brightness when machine off
        led_flash:   Mood indicator flash time (int, ms)
    '''
    illuminate = True
    led_bright = float(1.0)
    led_standby = float(0.33)
    led_flash = 66

    '''
        Timing and timeout config:
        updateTime:     (int, ms)  Basic time interval between update cycles
        rebootDelay:    (int) Countdown in seconds when auto-restarting/rebooting printPy
    '''
    updateTime = 1000
    rebootDelay = 3

    '''
        UI
        splashtime: (int) splash screen time in milliseconds
    '''
    splashtime = 2000

    '''
        Serial Device Config:
        device:   UART device
        baud:     (int) Serial baud rate; should match the setting used in config.g
    '''
    device = UART(0)
    baud = 57600

    '''
        Machine Config:
        net:    Default Network Interface number
                (`None` to disable network status display and functions)
    '''
    net = 0

    '''
        REPL output Options:
        info:   (bool) Show machine status lines in REPL console
        stats:  (bool) Show printPy fetch speed and memory stats when info=True
        quiet:  (bool) Suppress init and serialOM comms info messages
    '''
    info = True
    stats = False
    quiet = False
