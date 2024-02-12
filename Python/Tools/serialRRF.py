from RRFconfig import port,baud
from serial import Serial
from time import sleep,time  # CPython: for micropython use ticks_ms and  ticks_diff
from json import loads,JSONDecoder
from itertools import zip_longest
from sys import exit
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

    M409 K'xxx' : keys of interest:                  <---------- WIP!
    state   : Status and Update - machine state and uptime
    heat    : Status and Update - Temperatures and tool type
    job     : Status and Update - print progress monitoring
    network : ??? Status only - connected/disconnected
    sensors : Status only - ??? need in order to 'name' the sensors
    tools   : Status only - tool names

    See:
    https://docs.duet3d.com/User_manual/Reference/Gcodes#m409-query-object-model
    https://github.com/Duet3D/RepRapFirmware/wiki/Object-Model-Documentation
'''

# A global dict. structure of the all OM keys we see when running state and update checks
status = {'state':{'status':'undefined'},'seqs':None}

# These are the only key sets in the OM we are interested in
#  This could be expanded as needed.
OMstatuskeys = ['heat','job','sensors','network','tools']  # all keys
OMupdatekeys = ['heat','job','network']  # subset of keys to always update

# Basic time between updates (ms)
updateTime = 5000
# listen time for replies after sending request
rrfWait = updateTime / 2

# string of valid ascii chars for JSON response body
jsonChars = bytearray(range(0x20,0x7F)).decode('ascii')

# Handle hard (eg serial or comms) errors; needs expansion ;-)
def hardfail(why):
    while True:  # BlackHole the process
        print('CRITICAL ERROR: ' + why + '\nHALTED')
        quit()

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

# Handle a request to the OM
def OMrequest(OMkey,fullstatus=False):

    # CPython only: Replace this with micropython inbuilt time_ms()
    def time_ms():
        return int(time() * 1000)

    # Using a global here saves memory. ??
    global status

    # Chose the appropriate flags
    if fullstatus:
        OMflags = 'vnd99'
    else:
        OMflags = 'fnd99'

    # Construct the command (no newline)
    cmd = 'M409 F"' + OMflags + '" K"' + OMkey + '"'

    # Send the M409 command to RRF
    if not sendGcode(cmd):
        hardfail('Serial/UART failed: Cannot write to controller')

    #print('Sent: ' + cmd)
    requestTime = time_ms()

    # And wait for a response
    response = []
    nest = 0;
    maybeJSON = ''
    notJSON= ''
    while ((time_ms()-requestTime) < rrfWait):  # CPython; for micropython use ticks_diff()
        char = rrf.read(1).decode('ascii')
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
                        response.append(maybeJSON)
                        maybeJSON = ""
                    if (notJSON[:2] == 'ok'):
                        break

    if notJSON[:2] != 'ok':
        print('Timed out waiting for "ok": ',cmd)

    if len(response) == 0:
        print("No sensible response from: ",cmd)
        return False

    #for item in response:
    #    print('JSON: ' + item)

    # Process Json lines
    for line in response:
        # Load as a json data structure
        try:
            payload = loads(line)
        except:
            # invalid JSON, skip to next line
            print('Invalid JSON:',line)
            continue
        # Update global status structure
        if 'result' in payload.keys():
            if payload['result'] == None:
                # if reult is None the key doesnt exist
                return False
            else:
                # We have a valid result, store it
                if fullstatus:
                    status[payload['key']] = payload['result']
                else:
                    status[payload['key']] = merge(status[payload['key']],payload['result'])
        else:
            # Valid JSON but no 'result' data in it
            return False
    # If we got here; we had a successful cycle
    return True

def seqrequest():
    # Send a 'seqs' request to the OM, updates status and returns
    # a list of keys where the sequence number has changed
    global OMseqcounter
    changed=[]
    if OMrequest('seqs',False):
        for key in OMstatuskeys:
            if OMseqcounter[key] != status['seqs'][key]:
                changed.append(key)
                OMseqcounter[key] = status['seqs'][key]
    else:
        print('Sequence key request failed')
    return changed

def updatedisplay():
    def showHeater(number,name):
        if status['heat']['heaters'][number]['state'] == 'fault':
            print(' | ' + name + ': HEATER FAULT',end='')
        else:
            print(' | ' + name + ':', '%.1f' % status['heat']['heaters'][number]['current'],end='')
            if status['heat']['heaters'][number]['state'] == 'active':
                print(' (%.1f)' % status['heat']['heaters'][number]['active'],end='')
            elif status['heat']['heaters'][number]['state'] == 'standby':
                print(' (%.1f)' % status['heat']['heaters'][number]['standby'],end='')

    # Currently a one-line text status output,
    #  eventually a separate class to drive physical displays
    print('status:',status['state']['status'],
          '| uptime:',status['state']['upTime'],
          end='')
    if status['state']['status'] in ['updating','starting']:
        # display a splash while starting or updating..
        pass
    elif status['state']['status'] == 'off':
        # turn display off
        print()
        return
    showHeater(0,'bed')
    showHeater(1,'E0')
    if status['job']['build']:
        percent = status['job']['filePosition'] / status['job']['file']['size'] * 100
        print(' | progress:', "%.1f" % percent,end='%')
    print()

'''
    Simple control loop to begin with
'''

# Init RRF connection
try:
    rrf = Serial(port,baud,timeout=(rrfWait/1000))
except:
    hardfail('Connection could not be established')

# Connect and get firmware string - Needs some logic to cover failures..
rrf.write(b'\nM115\n')
response = rrf.read_until(b"ok").decode('ascii')
print(response)
print('PrintPy is Connected')

# request the boards, status and seqs keys
for key in ['boards','state','seqs']:
    if not OMrequest(key,True):
        hardfail('Failed to accqire "' + key + '" data')

#print('\nInit with: ', status, '\n')

# Determine SBC mode
if status['seqs'] == None:
    SBCmode = True
    print('Controller is in SBC mode')
else:
    SBCmode = False
    OMseqcounter = status['seqs']
    print('Controller is standalone')

# Determine machine mode (FFF,CNC or Laser)
machineMode = status['state']['machineMode']
if machineMode != 'FFF':
    hardfail('We currently do not support "' + machineMode + '" controller mode, sorry.')
print(machineMode + ' machine mode detected')

# Get initial data set
# - in future decide what we are getting via the mode (FFF vs CNC vs laser)
for key in OMstatuskeys:
    if not OMrequest(key,True):
        hardfail('Failed to accqire "' + key + '" data')

# MAIN LOOP

#print(status)

while True:
    if OMrequest('state',False):
        # Set the list of keys based on our state
        # If uptime has decreased do a restart
        # also restart if mode chaanges
        pass
    else:
        print('Failed to fetch machine state')
        sleep(updateTime/1000)
        continue
    if SBCmode:
        for key in OMstatuskeys:
            OMrequest(key,True)
    else:
        fullupdatelist = seqrequest()
        for key in set(OMupdatekeys).union(fullupdatelist):
            if key in fullupdatelist:
                OMrequest(key,True)
            else:
                OMrequest(key,False)
    updatedisplay()
    sleep(updateTime/1000)
