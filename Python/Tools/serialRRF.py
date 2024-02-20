# Import our config and local classes
try:
    from RRFconfig import config
except ModuleNotFoundError:
    from RRFconfigExample import config
    print('!! Using default config from RRFconfigExample.py')  # nag
from outputTXT import outputRRF

# Common classes between CPython and microPython
from json import loads
from gc import collect

# Libs that need to change between between CPython an microPython
#from machine import UART              # microPython
from serial import Serial
#from time import sleep_ms,ticks_ms,ticks_diff,localtime  # microPython
from time import sleep,time,localtime  # CPython: for microPython also drop local time function defs
from sys import executable,argv        # CPython
from os import execv                   # CPython
#from machine import reset             # microPython

# CPython standard libs that need to be provided locally for microPython
from itertools import zip_longest
from functools import reduce

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


# Basic time between updates (ms)
updateTime = 1000

# listen timeout for replies after sending request
rrfWait = updateTime / 2

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
    # Pause for 10 seconds, then restart
    for c in range(10,0,-1):
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

# Time functions to emulate micropython time lib (formally utime)
def ticks_ms():
    return int(time() * 1000)
def ticks_diff(first,second):
    # This should 'just work' in CPython3+
    # int's can be as 'long' as they need to be
    return int(first-second)
def sleep_ms(ms):
    sleep(ms/1000)

# send a gcode+chksum then block until it is sent, or error
def sendGcode(code):
    chksum = reduce(lambda x, y: x ^ y, map(ord, code))
    #print('SEND: ', code, chksum)
    try:
        rrf.write(bytearray(code + "*" + str(chksum) + "\r\n",'utf-8'))
    except:
        print('Write Failed')
        return False
    try:
        rrf.flush()
    except:
        print('Write Failed')
        return False
    return True

# Handle a request to the OM
def OMrequest(OMkey,OMflags):
    # Recursive/iterative merge of dict/list structures.
    # https://stackoverflow.com/questions/19378143/python-merging-two-arbitrary-data-structures#1
    def merge(a, b):
        if isinstance(a, dict) and isinstance(b, dict):
            d = dict(a)
            d.update({k: merge(a.get(k, None), b[k]) for k in b})
            return d
        if isinstance(a, list) and isinstance(b, list):
            return [merge(x, y) for x, y in zip_longest(a, b)]
        return a if b is None else b

    # Construct the command (no newline)
    cmd = 'M409 F"' + OMflags + '" K"' + OMkey + '"'

    # Send the M409 command to RRF
    if not sendGcode(cmd):
        commsFail('Serial/UART failed: Cannot write to controller')
    requestTime = ticks_ms()

    # And wait for a response
    response = []
    nest = 0;
    maybeJSON = ''
    notJSON = ''
    while (ticks_diff(ticks_ms(),requestTime) < rrfWait):
        try:
            char = rrf.read(1).decode('ascii')
        except UnicodeDecodeError:
            char = None
        except:
            commsFail('Serial/UART failed: Cannot read from controller')
        if rawLog and (char != None):
            rawLog.write(char)
        if char:
            if char in jsonChars:
                if char == '{':
                    nest += 1
                if nest > 0:
                    maybeJSON = maybeJSON + char
                else:
                    notJSON = notJSON + char
                if char == '}':
                    nest -= 1
                if nest == 0:
                    if maybeJSON:
                        notJSON = '{...}' + notJSON  # helps debug
                        response.append(maybeJSON)
                        maybeJSON = ""
                    if (notJSON[-2:] == 'ok'):
                        break
    if nonJsonLog:
        nonJsonLog.write(notJSON + '\n')
    if len(response) == 0:
        print('No sensible response from "',cmd,'" :: ',notJSON)
        return False

    # Process Json candidate lines
    for line in response:
        # Load as a json data structure
        try:
            payload = loads(line)
        except:
            # invalid JSON, skip to next line
            print('Invalid JSON:',line)
            continue
        # Update localOM data
        if 'result' in payload.keys():
            if payload['result'] == None:
                # if reult is None the key doesnt exist
                return False
            else:
                # We have a valid result, store it
                if 'v' in OMflags:
                    # Verbose output replaces the existing key
                    out.localOM[payload['key']] = payload['result']
                else:
                    # Frequent updates just refresh the existing key
                    out.localOM[payload['key']] = merge(out.localOM[payload['key']],payload['result'])
        else:
            # Valid JSON but no 'result' data in it
            return False
    # If we got here; we had a successful cycle
    return True

def seqRequest():
    # Send a 'seqs' request to the OM, updates localOM and returns
    # a list of keys where the sequence number has changed
    global OMseqcounter
    changed=[]
    if OMrequest('seqs','fnd99'):
        for key in out.verboseKeys[machineMode]:
            if OMseqcounter[key] != out.localOM['seqs'][key]:
                changed.append(key)
                OMseqcounter[key] = out.localOM['seqs'][key]
    else:
        print('Sequence key request failed')
    return changed

def firmwareRequest():
    # Use M115 to (re)establish comms andv erify firmware
    # Needs some logic to cover failures..
    try:
        rrf.write(b'\n')
    except:
        commsFail('Failed to write during comms start, UART/serial hardware error?')
    _ = rrf.read()
    sendGcode('M115')
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
        rrf = Serial(device,config.baud,timeout=(rrfWait/1000))
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

# request the boards, state and seqs keys
for key in ['state','seqs']:
    if not OMrequest(key,'vnd99'):
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
    if not OMrequest(key,'vnd99'):
        commsFail('failed to accqire initial "' + key + '" data')

'''
    Simple main loop to begin with
'''
while True:
    begin = ticks_ms()
    # Do a full 'state' tree update
    if OMrequest('state','vnd99'):
        # test for uptime or machineMode changes and reboot as needed
        if out.localOM['state']['machineMode'] != machineMode:
            restartNow('machine mode has changed')
        if out.localOM['state']['upTime'] < upTime:
            restartNow('RRF controller rebooted')
        else:
            # Record the curret uptime for the board.
            upTime = out.localOM['state']['upTime']
    else:
        print('Failed to fetch machine state')
        sleep_ms(updateTime/10)  # re-try after 1/10th of update time
        continue

    if SBCmode:
        for key in out.verboseKeys[machineMode]:
            OMrequest(key,'vnd99')
    else:
        fullupdatelist = seqRequest()
        for key in set(out.frequentKeys[machineMode]).union(fullupdatelist):
            if key in fullupdatelist:
                OMrequest(key,'vnd99')
            else:
                OMrequest(key,'fnd99')

    # output the results
    print(out.updateOutput())

    # Request cycle ended, garbagecollect and wait for next update start
    collect()
    while ticks_diff(ticks_ms(),begin) < updateTime:
        # Look for input: output toggle? System Status? Wifi Toggle? log(s) toggle?
        sleep_ms(1)
