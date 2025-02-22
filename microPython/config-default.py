'''

RENAME/COPY this file to `config.py` on your device
- edit if needed, defaults are sensible ones for a XIAO2040 based device
- button definition and display swapping is done here.

'''

from machine import UART, Pin, I2C

class config():
    '''
        UI:
        button_long:  (int) long press time (ms) for WiFi toggle, 0 to disable
        off_states:   (list) states where the screen should turn off
                      - set to an empty list '[]' to keep permanently on
                      - set to '['off','idle']' to only turn on when active
        off_time:     (int) screen standby off time (ms)
        button_awake: (int) keep screen awake this long after button press
        long_awake:   (int) awake for longer when wifi or comms status changes
        splash_time:  (int) splash screen time in milliseconds
    '''
    button_long  = 2 * 1000
    off_states   = ['off']
    off_time     = 15 * 1000
    button_awake = off_time * 2
    long_awake    = off_time * 4
    splash_time  = 3 * 1000

    '''
        Hardware config:
        button:      Status button pin object
                     (set '= None' to disable)
        button_down: Pin value when button depressed
        I2C_left:    I2C interface definitions for left and right screens
        I2C_right:   Currently uses default pins and hardware interfaces and
                     can be adapted with softI2C+alternate pins as needed.
        pixel_pin:   Onboard NeoPixel pin
        pixel_power: Neopixel VCC is turned on via this pin on the XIAO
    '''
    button      = Pin(2, Pin.IN, Pin.PULL_UP)
    button_down = 0
    I2C_left    = I2C(1, sda=Pin(6), scl=Pin(7))
    I2C_right   = I2C(0, sda=Pin(28), scl=Pin(29))
    pixel_pin   = Pin(12)
    pixel_power = Pin(11,Pin.OUT)

    '''
        Serial Device Config:
        device: UART device
        baud:   (int) Serial baud rate; should match the setting used in config.g
                - for example: M575 P1 B230400 S0
    '''
    device = UART(0)
    baud   = 230400

    '''
        Network Config:

        NOTE: Defaults here assume a WiFi enabled board that connects to a client network.
              You will need to adjust as needed if you have an Ethernet board (no -1 disabled state..),
              connect to a specific network (the 'P' option to M552) or run as an Access Point.

        net:      (int) Default Network Interface number
                  - (`None` to disable network status display and functions)
        net_map: (dict) defines the 'wifi toggle' button press command
                  to be sent to the machine for each wifi state defined in the OM
                  - The '{NET}' will be replaced by the network number given above
                  - The list of possible states is defined in:
                    https://github.com/Duet3D/RepRapFirmware/wiki/Object-Model-Documentation#networkinterfacesstate
                  - If the network state is not specifically matched the DEFAULT entry will be used.
                  - https://docs.duet3d.com/User_manual/Reference/Gcodes#m552-set-ip-address-enabledisable-network-interface
    '''
    net     = 0
    net_map = { 'disabled' : 'M552 I{NET} S1',
                 'DEFAULT' : 'M552 I{NET} S-1',}

    '''
        Display hardware settings
        display_bright: (float) Display Brightness (0 to 1)
        display_invert: (bool) Invert display colors
        display_rotate: (bool) Flip display vertically
    '''
    display_bright = float(0.66)
    display_invert = False
    display_rotate = True

    '''
        NeiPixel 'mood' illumination
        mood:         (bool)  Indicate status via onboard Neopixel
        mood_bright:  (float) Indicator LED brightnessx (0 to 1)
        mood_standby: (float) Indicator LED brightness when machine off
        mood_flash:   (int)   Mood indicator flash time (ms)
    '''
    mood         = True
    mood_bright  = float(1.0)
    mood_standby = float(0.2)
    mood_flash   = 66

    '''
        Communications heartbeat on auxillary RGB
        heart          (bool)  Show comms heartbeat
        heart_bright:  (float) Heartbeat LED brightness (0 to 1)
        heart_standby: (float) Heartbeat LED brightness when machine off
    '''
    heart         = True
    heart_bright  = float(1.0)
    heart_standby = float(0.33)

    '''
        Timing and timeout config:
        Note: these values are good for the RP2040 version of printPY, I do
          not recommend lowering the update interval. It currently takes
          approx. 500ms to fetch and ingest the OM, then another 150ms to
          update the display buffer.
        update_time:  (int) Basic time interval between update cycles (ms)
        reboot_delay: (int) Countdown in seconds when auto-restarting/rebooting printPy
        fail_count:   (int) Number of failed update cycles before declaring comms fail
    '''
    update_time  = 1000
    reboot_delay = 5
    fail_count   = 5

    '''
        Display animation:
        - These are tuned for the XIAO2040 + two I2C OLED's
        - Animation interval will cause lockups and races if too low.
        animation_interval: (int) Display animation interval, ms
        marquee_step:       (int) Number of pixels moved for each marquee step
        marquee_pause:      (int) Number of step cycles to pause for when scrolling long text
    '''
    animation_interval = 100
    marquee_step       = 3
    marquee_pause      = 8

    '''
        Console output Options:
        - For development you want these all on (probably...)
        - Turn off for production use
        debug:   (int)  if > 0 count down to start (so you can keyboard interrupt)
                        if 0 drop immediately to REPL (debug)
        info:    (bool) Show machine status lines in REPL console
        stats:   (bool) Show printPy fetch speed and memory stats when info=True
        verbose: (bool) Show init and serialOM comms info messages
    '''
    debug   = 0
    info    = True
    stats   = True
    verbose = True
    '''
    THE ABOVE DEFAULTS ARE FOR COMISSIONING:

    Once programmed and tested you should set debug
    to '5' so that printpy starts after a 5 second countdown

    The other options are less important but there is
    no point in generating lots of REPL output outside
    of testing and developing the code.

    debug   = 5
    info    = False
    stats   = False
    verbose = False
    '''
