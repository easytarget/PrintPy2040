from RRFconfig import port,baud
from outputTXT import outputRRF

from serial import Serial
from time import sleep,time           # <---- CPython: for micropython use ticks_ms and ticks_diff directly
from json import loads
from itertools import zip_longest
from sys import exit,executable,argv # <---- CPython
from functools import reduce
from os import execv                  # <---- CPython
#from machine import reset            # MicroPython
from gc import collect

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
    print('Restarting: ' + why + '\n')
    execv(executable, ['python'] + argv)   #  <----  CPython
    # Micropython; reboot module
    #reset()

# Handle (transient) serial or comms errors; needs expansion ;-)
def commsFail(why):
    print('Communications error: ' + why + '\nWaiting for Controller to respond.\n')
    while True:
        # Re-check the comms port (M115) looking for life..
        sleep(6)
        print('>',end='')
        if firmwareRequest():
            print()
            restartNow('Communications lost then re-established')

# Used for critical hardware errors during initialisation
def hardwareFail(why):
    print('A Critical Hardware error has occured!')
    print('Do a full power off/on cycle and check wiring etc..:\n' + why + '\n')
    quit()     #  <----  CPython, just exit...`
    # Micropython; hang...
    #while True:  # loop forever
    #    sleep(60)

# CPython only: Replace this with micropython inbuilt ticks_ms))(
def ticks_ms():
    return int(time() * 1000)

# send a gcode+chksum then block until it is sent, or error
def sendGcode(code):
    chksum = reduce(lambda x, y: x ^ y, map(ord, code))
    #print('SEND: ', code, chksum)
    try:
        rrf.write(bytearray(code + "*" + str(chksum) + "\r\n",'utf-8'))
    except OSError:
        print('Connection Failed')
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
    while ((ticks_ms()-requestTime) < rrfWait):  # CPython; for micropython use ticks_diff()
        try:
            char = rrf.read(1).decode('ascii')
        except UnicodeDecodeError:
            char = None
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
        hardwareFail('Failed to write during comms start, UART/serial hardware error?')
    _ = rrf.read()
    sendGcode('M115')
    response = rrf.read_until(b"ok").decode('ascii')
    print(response)
    if not 'RepRapFirmware' in response:
        return False
    return True

'''
    Simple control loop to begin with
'''

print('serialRRF is starting')

# Get output device
out = outputRRF(initialOM={'state':{'status':'undefined'},'seqs':None}, refresh=0.5)

# Init RRF connection
try:
    rrf = Serial(port,baud,timeout=(rrfWait/1000))
except:
    hardwareFail('UART/serial could not be initialised')

print('checking for connected controller\n> M115')
if firmwareRequest():
    print('serialRRF is connected')
else:
    commsFail('failed to get Firmware string')

# request the boards, state and seqs keys
for key in ['boards','state','seqs']:
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

# MAIN LOOP

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
        sleep(updateTime/10000)  # re-try after 1/10th of update time
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
    out.updateOutput()
    collect()
    sleep(updateTime/1000)
