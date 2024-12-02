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
        Serial Device Config:
        device:   UART device
        baud:     (int) Serial baud rate; should match the setting used in config.g
                  eg: TODO!!!!
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
        Display settings
        display_bright: Display Brightness (float, 0 to 1)
        display_invert: Display inversion (bool)
        display_rotate: Display flip display vertically (bool)
    '''
    display_bright = float(0.66)
    display_invert = False
    display_rotate = True

    '''
        NeiPixel 'mood' illumination
        mood:          (bool)  Indicate status via onboard Neopixel
        mood_bright:    (float) Indicator LED brightnessx (0 to 1)
        mood_standby:   (float) Indicator LED brightness when machine off
        mood_flash:     (int)   Mood indicator flash time (ms)
    '''
    mood = True
    mood_bright = float(1.0)
    mood_standby = float(0.33)
    mood_flash = 66

    '''
        Communications heartbeat on auxillary RGB
        heart          (bool)  Show comms heartbeat
        heart_bright:  (float) Heartbeat LED brightness (0 to 1)
        heart_standby: (float) Heartbeat LED brightness when machine off
    '''
    heart = True
    heart_bright = float(1.0)
    heart_standby = float(0.5)

    '''
        Timing and timeout config:
        updateTime:  (int) Basic time interval between update cycles (ms)
        rebootDelay: (int) Countdown in seconds when auto-restarting/rebooting printPy
        failcount:   (int) Number of failed update cycles before declaring comms fail
    '''
    updateTime = 1000
    rebootDelay = 5
    failcount = 5

    '''
        UI:
        splashtime: (int) splash screen time in milliseconds
        offtime:    (int) screen off delay in seconds
        offstates:  (list) states where the screen should turn off
    '''
    splashtime = 2000
    offtime = 16
    offstates = ['off']
    
    '''
        Display animation:
        - 
        animation_interval: (int) Display animation interval, ms
        marquee_step:       (int) Number of pixels moved for each marquee step
        marquee_pause:      (int) Number of step cycles to pause for when scrolling long text
    '''
    animation_interval = 1000
    marquee_step = 2
    marquee_pause = 20

    '''
        REPL output Options:
        - For development you want these all on (probably...)
        - Turn off for production use
        info:   (bool) Show machine status lines in REPL console
        stats:  (bool) Show printPy fetch speed and memory stats when info=True
        verbose: (bool) Show init and serialOM comms info messages
    '''
    info = False
    stats = False
    verbose = False
