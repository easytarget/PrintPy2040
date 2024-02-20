'''
    Copy this file as `RRFconfig.py`, and
    then edit the serial device path and baud rate there.
'''

class config():
    '''
        devices = list of devices to try when connecting
                  (a list because under linux the /dev/ttyACM* and /dev/ttyUSB*
                  devices can wander between 0 and 1 when the duet reboots.)
        baud    = Serial baud rate; should match the setting used in the config.g
                  `M575` command used to enable the serial or usb port.
    '''
    devices = ['/dev/ttyACM0','/dev/ttyACM1']
    baud = 57600

    '''
        Debug logging. replace "None" with "'filename.log'" to enable.
        rawLog     = an unprocessed log of all incoming serial data as a bytearray
        nonJsonLog = same as the raw log, but with all potential JSON blocks
                     replaced with '{...}' as a placeholder
        outputLog  = Log file for output module, the example TXT output class
                     sends it's output there as well as to the console.
    '''
    rawLog = None
    nonJsonLog = None
    outputLog = None
