# Import our config and local classes
try:
    from RRFconfig import config
except ModuleNotFoundError:
    from RRFconfigExample import config
    print('!! Using default config from RRFconfigExample.py')  # nag
from outputTXT import outputRRF
from handleOM import sendGcode,OMrequest,seqRequest

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


# string of valid ascii chars for JSON response body
jsonChars = bytearray(range(0x20,0x7F)).decode('ascii')

# Do a minimum drama restart/reboot
def restartNow(why):
    print('Restarting: ' + why)
    execv(executable, ['python'] + argv)   #  CPython
    #reset() # Micropython; reboot module

# Handle (transient) serial or comms errors; needs expansion ;-)
def commsFail(why):
    print('Communications error: ' + why +'\nRestarting in ',end='')
    # Pause for 8 seconds, then restart
    for c in range(8,0,-1):
        print(c,end=' ',flush=True)
        sleep_ms(1000)
    print()
    restartNow('Communications lost')

# Used for critical hardware errors during initialisation on MCU's
# Unused in Cpython
def hardwareFail(why):
    print('A critical hardware error has occured!')
    print('- Do a full power off/on cycle and check wiring etc.\n' + why + '\n')
    while True:  # loop forever
        sleep_ms(60000)

def firmwareRequest():
    # Use M115 to (re)establish comms and verify firmware
    try:
        rrf.write(b'\n')
    except:
        commsFail('Failed to write during comms start, UART/serial hardware error?')
    # (USB) serial buffer can be dirty after a restart
    while len(rrf.readline()) > 0:
        sleep_ms(50)
    # Send the M115 info request and look for a sensible reply
    sendGcode(rrf,'M115')
    response = rrf.read_until(b"ok").decode('ascii')
    print(response)
    if not 'RepRapFirmware' in response:
        return False
    return True

'''
    Init
'''

# Basic info
start = localtime()
startDate = str(start[0]) + '-' + str(start[1]) + '-' + str(start[2])
startTime = "%02.f" % start[3] + ':' + "%02.f" % start[4] + ':' + "%02.f" % start[5]
startText = '=== Starting: ' + startDate + ' ' + startTime + '\n'

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

nonJsonLog = None
if config.nonJsonLog:
    try:
        nonJsonLog = open(config.nonJsonLog, "a")
        print('non-JSON data being logged to: ', config.nonJsonLog)
        nonJsonLog.write(startText)
    except Exception as error:
        print('logging of non-JSON data failed: ', error)

outputLog = None
if config.outputLog:
    try:
        outputLog = open(config.outputLog, "a")
        print('output being logged to: ', config.outputLog)
        outputLog.write(startText)
    except Exception as error:
        print('logging of output failed: ', error)

# Get output/display device
out = outputRRF(initialOM={'state':{'status':'undefined'},'seqs':None},log=outputLog)

# Init RRF USB/serial connection
rrf = None
for device in config.devices:
    try:
        # microPython: replace following with UART init
        rrf = Serial(device,config.baud,timeout=config.updateTime/1000)
    except:
        print('device "' + device + '" not available')
    else:
        print('device "' + device + '" available')
        sleep_ms(100)   # settle time
        break

if not rrf:
    # Loop looking for a serial device
    # For micropython we should stop here since no UART == a serious fail.
    restartNow('USB/serial could not be initialised')

print('checking for connected controller\n> M115')
if firmwareRequest():
    print('serialRRF is connected')
else:
    commsFail('failed to get Firmware string')

# request the initial state and seqs keys
for key in ['state','seqs']:
    if not OMrequest(out,rrf,key,'vnd99',rawLog,nonJsonLog):
        commsFail('failed to accqire "' + key + '" data')

# Determine SBC mode
if out.localOM['seqs'] == None:
    SBCmode = True
    print('RRF controller is in SBC mode')
else:
    SBCmode = False
    OMseqcounter = out.localOM['seqs']
    print('RRF controller is standalone')

# Determine and record the machine mode (FFF,CNC or Laser)
machineMode = out.localOM['state']['machineMode']
if machineMode in out.verboseKeys.keys():
    print(machineMode + ' machine mode detected')
else:
    restartNow('we currently do not support "' + machineMode + '" controller mode, sorry.')

# Record the curret uptime for the board.
upTime = out.localOM['state']['upTime']

# Get initial data set
# - in future decide what we are getting via the mode (FFF vs CNC vs laser)
for key in out.verboseKeys[machineMode]:
    if not OMrequest(out,rrf,key,'vnd99',rawLog,nonJsonLog):
        commsFail('failed to accqire initial "' + key + '" data')

'''
    Simple main loop to begin with
'''
while True:
    begin = ticks_ms()
    # Do a full 'state' tree update
    if OMrequest(out,rrf,'state','vnd99',rawLog,nonJsonLog):
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

    if SBCmode:
        for key in out.verboseKeys[machineMode]:
            OMrequest(out,rrf,key,'vnd99',rawLog,nonJsonLog)
    else:
        fullupdatelist = seqRequest(out,rrf,OMseqcounter,rawLog,nonJsonLog,machineMode)
        for key in set(out.frequentKeys[machineMode]).union(fullupdatelist):
            if key in fullupdatelist:
                OMrequest(out,rrf,key,'vnd99',rawLog,nonJsonLog)
            else:
                OMrequest(out,rrf,key,'fnd99',rawLog,nonJsonLog)

    # output the results
    print(out.updateOutput())

    # Request cycle ended, garbagecollect and wait for next update start
    collect()
    while ticks_diff(ticks_ms(),begin) < config.updateTime:
        # Look for input: output toggle? System Status? Wifi Toggle? log(s) toggle?
        sleep_ms(1)
