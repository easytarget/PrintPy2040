'''
    Copy this file as `RRFconfig.py`, and
    then edit the serial device path and baud rate there.
'''

class config():
    '''
        Serial Device Config:
        devices:  (list, strings) devices to try when connecting
                   - a list because under linux the /dev/ttyACM* and /dev/ttyUSB*
                     devices can wander between 0 and 1 when the duet reboots.
        baud:     (int) Serial baud rate; should match the setting used in the config.g
                  -  `M575` command used to enable the serial or usb port.
        timeout:  (float, seconds) Read blocking timeout in float(seconds)
                  - returns after this even with no data
                    should be a a few hundred ms, unless your controller is verrrry slow.
        quiet:    (bool) suppress info messages
    '''
    devices = ['/dev/ttyACM0','/dev/ttyACM1']
    baud = 57600
    timeout = 0.2
    quiet = False

    '''
        Timing and timeout config:
        updateTime:     (int, ms)  Basic time between update cycles
        requestTimeout: (int, ms)  maximum time to wait for response after sending request
                        - can be much longer than the serial blocking timeout above
        rebootDelay:    (int) Countdown in seconds when auto-restarting/rebooting
    '''
    updateTime = 1000
    requestTimeout = updateTime*0.66
    rebootDelay = 8

    '''
        Logging Config:
        - Replace "None" with "'filename.log'" to enable.
        rawLog:     An unprocessed log of all incoming serial data as a bytearray
        outputLog:  Log file for output module
                    - The example TXT output class can mirror sends it's output there
    '''
    rawLog = None
    outputLog = None

    '''
        Output Config:
    '''
