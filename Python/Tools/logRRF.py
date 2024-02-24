# Import our config and local classes
from serialOM import serialOM
from outputTXT import outputRRF
try:
    from RRFconfig import config
except ModuleNotFoundError:
    from RRFconfigExample import config
    print('!! Using default config from RRFconfigExample.py')  # nag

# Common classes between CPython and microPython
from gc import collect

# Libs that need to change between between CPython an microPython
#from machine import UART              # microPython
from serial import Serial
#from time import sleep_ms,ticks_ms,ticks_diff,localtime # microPython
from timeStubs import sleep_ms,ticks_ms,ticks_diff # CPython
from time import localtime                         # CPython
#from machine import reset             # microPython
from sys import executable,argv        # CPython
from os import execv                   # CPython

'''
    serialOM.py demo

    This is intended to be run on a desktop system (CPython, not microPython)
    that connects via serial or USBserial to a RRF 3.x based controller.
'''

# Do a minimum drama restart/reboot
def restartNow(why):
    print('Error: ' + why +'\nRestarting in ',end='')
    # Pause for a few seconds, then restart
    for c in range(config.rebootDelay,0,-1):
        print(c,end=' ',flush=True)
        sleep_ms(1000)
    print()
    execv(executable, ['python'] + argv)   #  CPython
    #reset() # Micropython; reboot module

# Used for critical hardware errors during initialisation on MCU's
# Unused in Cpython, instead we soft-fail, restart and try again.
# - in microPython we will be harsher with hardware errors
def hardwareFail(why):
    print('A critical hardware error has occured!')
    print('- Do a full power off/on cycle and check wiring etc.\n' + why + '\n')
    while True:  # loop forever
        sleep_ms(60000)

'''
    Init
'''

# Basic info
start = localtime()
startDate = str(start[0]) + '-' + str(start[1]) + '-' + str(start[2])
startTime = "%02.f" % start[3] + ':' + "%02.f" % start[4] + ':' + "%02.f" % start[5]
startText = '\n=== Starting: ' + startDate + ' ' + startTime + '\n'

print('logRRF is starting at: ' + startDate + ' ' + startTime + ' (device localtime)')

# Debug Logging
rawLog = None
if config.rawLog:
    try:
        rawLog = open(config.rawLog, "a")
        print('raw data being logged to: ', config.rawLog)
        rawLog.write(startText)
    except Exception as error:
        print('logging of raw data failed: ', error)
outputLog = None
if config.outputLog:
    try:
        outputLog = open(config.outputLog, "a")
        print('output being logged to: ', config.outputLog)
        outputLog.write(startText)
    except Exception as error:
        print('logging of output failed: ', error)

# Get output/display device
out = outputRRF(log=outputLog)

# Init RRF USB/serial connection
rrf = None
for device in config.devices:
    try:
        # microPython: replace following with UART init
        rrf = Serial(device,config.baud,timeout=config.timeout)
    except:
        print('device "' + device + '" not available')
    else:
        print('device "' + device + '" available')
        sleep_ms(100)   # settle time
        break
if not rrf:
    # Loop looking for a serial device
    # For micropython we should stop here since no UART == a serious fail.
    restartNow('No USB/serial device found')

# create the OM handler
OM = serialOM(rrf, out.omKeys, config.requestTimeout, rawLog)

if OM == None:
    print('borked on startup')
    restartNow('startup error')

'''
    Main loop
'''
while True:
    begin = ticks_ms()
    # Do a OM update
    if OM.update():
        # output the results
        print(out.updateOutput(OM.model))
    else:
        print('Failed to fetch machine state')
        sleep_ms(int(config.updateTime/10))  # re-try after 1/10th of update time
        continue
    # Request cycle ended, garbagecollect and wait for next update start
    collect()
    while ticks_diff(ticks_ms(),begin) < config.updateTime:
        # Look for input: output toggle? System Status? Wifi Toggle? log(s) toggle?
        sleep_ms(1)
