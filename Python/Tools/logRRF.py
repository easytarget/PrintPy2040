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

# local print function so we can suppress info messages.
def pp(*args, **kwargs):
    if not config.quiet:
        print(*args, **kwargs)

# Do a minimum drama restart/reboot
def restartNow(why):
    pp('Error: ' + why +'\nRestarting in ',end='')
    # Pause for a few seconds, then restart
    for c in range(config.rebootDelay,0,-1):
        pp(c,end=' ',flush=True)
        sleep_ms(1000)
    pp()
    execv(executable, ['python'] + argv)   #  CPython
    #reset() # Micropython; reboot module

# Used for critical hardware errors during initialisation on MCU's
# Unused in Cpython, instead we soft-fail, restart and try again.
# - in microPython we will be harsher with hardware errors
def hardwareFail(why):
    pp('A critical hardware error has occured!')
    pp('- Do a full power off/on cycle and check wiring etc.\n' + why + '\n')
    while True:  # loop forever
        sleep_ms(60000)

'''
    Init
'''

# Basic info
start = localtime()
startDate = str(start[0]) + '-' + str(start[1]) + '-' + str(start[2])
startTime = "%02.f" % start[3] + ':' + "%02.f" % start[4] + ':' + "%02.f" % start[5]
startText = '=== Starting: ' + startDate + ' ' + startTime

if config.quiet:
    print(startText)
else:
    print('logRRF is starting at: ' + startDate + ' ' + startTime + ' (device localtime)')

# Debug Logging
rawLog = None
if config.rawLog:
    try:
        rawLog = open(config.rawLog, "a")
    except Exception as error:
        pp('logging of raw data failed: ', error)
    else:
        pp('raw data being logged to: ', config.rawLog)
        rawLog.write('\n' + startText +  '\n')
outputLog = None
if config.outputLog:
    try:
        outputLog = open(config.outputLog, "a")
    except Exception as error:
        pp('logging of output failed: ', error)
    else:
        pp('output being logged to: ', config.outputLog)
        outputLog.write('\n' + startText + '\n')

# Get output/display device
pp('starting output')
out = outputRRF(log=outputLog)

# Init RRF USB/serial connection
rrf = None
for device in config.devices:
    try:
        # microPython: replace following with UART init
        rrf = Serial(device,config.baud,timeout=config.timeout)
    except:
        pp('device "' + device + '" not available')
    else:
        pp('device "' + device + '" available')
        sleep_ms(100)   # settle time
        break
if not rrf:
    # Loop looking for a serial device
    # For micropython we should stop here since no UART == a serious fail.
    restartNow('No USB/serial device found')

# create the OM handler
OM = serialOM(rrf, out.omKeys, config.requestTimeout, rawLog, config.quiet)

if OM.machineMode == '':
    pp('borked on startup')
    restartNow('startup error')
else:
    pp('Machine is in "' + OM.machineMode + '" mode')

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
        pp('Failed to fetch machine state')
        sleep_ms(int(config.updateTime/10))  # re-try after 1/10th of update time
        continue
    # Request cycle ended, garbagecollect and wait for next update start
    collect()
    while ticks_diff(ticks_ms(),begin) < config.updateTime:
        # Look for input: output toggle? System Status? Wifi Toggle? log(s) toggle?
        sleep_ms(1)
