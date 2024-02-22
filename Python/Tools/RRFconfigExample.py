'''
    Copy this file as `RRFconfig.py`, and
    then edit the serial device path and baud rate there.
'''

class config():
    '''
        Serial Device Config:
        devices = list of devices to try when connecting
                  (a list because under linux the /dev/ttyACM* and /dev/ttyUSB*
                  devices can wander between 0 and 1 when the duet reboots.)
        baud    = Serial baud rate; should match the setting used in the config.g
                  `M575` command used to enable the serial or usb port.
        timeout = Read blocking timeout in float(seconds), returns after this even with no data
                  (should be a a few hundred ms, unless your controller is verrrry slow.)
    '''
    devices = ['/dev/ttyACM0','/dev/ttyACM1']
    baud = 57600
    timeout = 0.2

    '''
        Timing and timeout config:
        updateTime = Basic time between update cycles (ms)
        requestTimeout = maximum time to spend waiting for response after sending request
                         (can be much longer than the blocking timeout above)
        rebootDelay = Countdown in seconds when auto-restarting/rebooting
        fwCheckTimeout = delay after sending M115 to collect (all) response
    '''
    updateTime = 1000
    requestTimeout = updateTime*0.66
    rebootDelay = 8
    fwCheckTimeout = 1000

    '''
        Logging Config:
        Replace "None" with "'filename.log'" to enable.
        rawLog     = an unprocessed log of all incoming serial data as a bytearray
        outputLog  = Log file for output module, the example TXT output class
                     sends it's output there as well as to the console.
    '''
    rawLog = None
    outputLog = None
