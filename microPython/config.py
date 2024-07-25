from machine import Pin
'''
    Set the serial device path and baud rate here, etc.
'''

class config():
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
        Timing and timeout config:
        updateTime:     (int, ms)  Basic time interval between update cycles
        rebootDelay:    (int) Countdown in seconds when auto-restarting/rebooting printPy
        animate:        (int, ms) Display animation update frequency
    '''
    updateTime = 1000
    rebootDelay = 3
    animate = 200

    '''
        Hardware config:
        button:     Status button pin object, (or None)
                        eg: button = Pin(2, Pin.IN, Pin.PULL_UP)
                        see the micropython 'machine.Pin()' docs
        buttonDown: Pin value when button depressed
        buttonTm:   debounce time (ms); keep this as low as practical
        buttonLong: long press time (ms) for WiFi toggle, 0 to disable
        I2C pins:   SDA and SCK for each I2C interface
    '''
    button = Pin(2, Pin.IN, Pin.PULL_UP)
    buttonDown = 0
    buttonTm = 50
    buttonLong = 500
    sda0 = Pin(28)
    scl0 = Pin(29)
    sda1 = Pin(6)
    scl1 = Pin(7)

    '''
        Duet Config:
        net:    Default Network Interface number
    '''
    net = 0