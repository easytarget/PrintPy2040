'''
    Copy this file as `RRFconfig.py`, and
    then edit the serial device path and baud rate there.

    devices = list of devices to try when connecting
              (a list because under linux the /dev/ttyACM* and /dev/ttyUSB*
              devices can wander between 0 and 1 when the duet reboots.)
    baud    = Serial baud rate; should match the setting used in the config.g
              `M575` command used to enable the serial or usb port.
'''
devices = ['/dev/ttyACM0','/dev/ttyACM1']
baud = 57600
