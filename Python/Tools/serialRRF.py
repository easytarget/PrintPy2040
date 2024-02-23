# Import our config and local classes
try:
    from RRFconfig import config
except ModuleNotFoundError:
    from RRFconfigExample import config
    print('!! Using default config from RRFconfigExample.py')  # nag
from outputTXT import outputRRF
from handleOM import handleOM

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
    This is intended to be run on a desktop system (CPython, not microPython)
    that connects via serial or USBserial to a RRF 3.x based controller.

    It will be used to create a 'framework' for extracting data from
    RRF based systems using the ObjectModel.

    We make two different types of request:
      Status requests to read the full tree
      Update requests that just return the frequently changing values
    Status requests are more 'expensive' in terms of processor and data use,
    so we only make these when we need to. The Update requests give us the
    temperature, tool state and job progress values we need to continually
    update.

    There is a special key returned by M409; `seqs`, which returns an
    incremental count of changes to the values /not/ returned with the
    simple update requests. We use this key to trigger status updates
    when necessary for all the keys we monitor. As will any 'reset' of
    the uptime status.

    See:
    https://docs.duet3d.com/User_manual/Reference/Gcodes#m409-query-object-model
    https://github.com/Duet3D/RepRapFirmware/wiki/Object-Model-Documentation
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

print('serialRRF is starting at: ' + startDate + ' ' + startTime + ' (device localtime)')

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
out = outputRRF(initialOM={'state':{'status':'undefined'},'seqs':None}, log=outputLog)

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
OM = handleOM(rrf, config, rawLog, hardFail=False)

# check for a valid response to a firmware version query
print('checking for connected RRF controller')
retries = 10
while not OM.firmwareRequest():
    retries -= 1
    if retries == 0:
        restartNow('Failing to get Firmware string during startup')
    print('Failed to get Firmware string, retrying')
    sleep_ms(1000)
print('serialRRF is connected')
sleep_ms(1000)  # helps the controller 'settle' after reboots etc.

# Do the initial state and seq fetch
machineMode = OM.firstRequest(out)
if machineMode == None:
    restartNow('Failed to fetch initial data sets.')
print(machineMode + ' machine mode detected')

# Record the current uptime for the board.
upTime = out.localOM['state']['upTime']

'''
    Main loop
'''
while True:
    begin = ticks_ms()
    # Do a OM update
    if OM.update(out):
        # test for uptime or machineMode changes and reboot as needed
        if out.localOM['state']['machineMode'] != machineMode:
            restartNow('machine mode has changed')
        elif out.localOM['state']['upTime'] < upTime:
            restartNow('RRF controller rebooted')
        else:
            # Record the latest uptime for the board.
            upTime = out.localOM['state']['upTime']
    else:
        print('Failed to fetch machine state')
        sleep_ms(config.updateTime/10)  # re-try after 1/10th of update time
        continue
    # output the results
    print(out.updateOutput())
    # Request cycle ended, garbagecollect and wait for next update start
    collect()
    while ticks_diff(ticks_ms(),begin) < config.updateTime:
        # Look for input: output toggle? System Status? Wifi Toggle? log(s) toggle?
        sleep_ms(1)
