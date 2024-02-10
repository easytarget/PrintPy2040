from RRFconfig import port,baud
from serial import Serial
from time import sleep
from json import loads
from itertools import zip_longest
from sys import exit

'''
    This script uses Telnet to connect to my duet (I have my reasons)
    The inbuilt 'telnetlib' library it uses comes with the following warning:
    "> Deprecated since version 3.11, will be removed in version 3.13:"
    consider yourself warned ;)

    It is intended to be run on a desktop system (CPython, not microPython)
    and will be used to create a 'framework' for extracting data from
    a RRF based system using the ObjectModel.

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

    M409 K'xxx' : keys of interest:
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

# Basic time between updates
updatetime = 1

# Handle hard (eg serial or comms) errors; needs expansion ;-)
def hardfail(why):
    while True:  # BlackHole the process
        print('CRITICAL ERROR: ' + why + '\nHALTED')
        quit()

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

# This is the way...?
def OMrequest(OMkey,fullstatus=False):
    # Using a global here saves memory. ??
    global status

    # Chose the appropriate flags
    if fullstatus:
        OMflags = 'vnd99'
    else:
        OMflags = 'fnd99'

    # Construct the command
    cmd = b'M409 F"' + bytes(OMflags, 'utf8') + b'" K"' + bytes(OMkey, 'utf8') + b'"\n'
    #DEBUG:print('SEND: '+ str(cmd))

    # Send the M409 command to RRF
    try:
        rrf.write(cmd)
    except OSError:
        print('Connection Failed')
        return False

    # And wait for a response
    response = rrf.read_until(b"ok").decode('ascii').replace("\r", "\n").split('\n')

    # remove empty lines
    while '' in response:
        response.remove('')

    # Test if the list is still populated, empty == timeout
    if not response:
        print('Response timed out for : ' + cmd.decode(),end="")
        return False

    # Look for Json data in response
    for line in range(0,len(response)):
        try:
            jsonstart = response[line].index('{')
        except ValueError:
            # No JSON in the line, skip to next
            continue

        # Load as a json data structure
        try:
            payload = loads(response[line][jsonstart:])
        except:
            # invalid JSON, skip to next line
            continue

        # Update global status structure
        if 'result' in payload.keys():
            if payload['result'] == None:
                # if reult is None the key doeesnt exist
                return False
            else:
                # We have a vaalid result, store it
                if fullstatus:
                    status[payload['key']] = payload['result']
                else:
                    status[payload['key']] = merge(status[payload['key']],payload['result'])
        else:
            # Valid JSON but no result
            return False

    # If we got here; we had a successful cycle
    return True

def seqrequest():
    # Send a 'seqs' request to the OM, updates status and returns
    # a list of keys where the sequence number has changed
    global OMseqcounter
    changed=[]
    OMrequest('seqs',False)
    if status['seqs'] != None:
        for key in OMstatuskeys:
            #print(status['seqs'][key],end=' | ')
            if OMseqcounter[key] != status['seqs'][key]:
                changed.append(key)
                OMseqcounter[key] = status['seqs'][key]
        print('Changed:',changed,end=' :: ')
    return changed

def updatedisplay():
    print('status:',status['state']['status'],
          '| uptime:',status['state']['upTime'],
          '| bed:',status['heat']['heaters'][0]['current'],
          '| tool:',status['heat']['heaters'][1]['current'])


'''
    Simple control loop to begin with
'''

# Init RRF connection
try:
    rrf = Serial(port,baud,timeout=0.25)
except:
    hardfail('Connection could not be established')

# Connect and get firmware string - Needs some logic to cover failures..
rrf.write(b'\nM115\n')
response = rrf.read_until(b"ok").decode('ascii').replace("\r", "\n")
print(response)
print('PrintPy is Connected')

# request the boards, status and seqs keys
for key in ['boards','state','seqs']:
    if OMrequest(key,True):
        print('Initial "' + key + '" data acquired')
    else:
        hardfail('Failed to accqire "' + key + '" data')

#print('\nInit with: ', status, '\n')

# Determine SBC mode
if status['seqs'] == None:
    SBCmode = True
    print('Controller is in SBC mode')
else:
    SBCmode = False
    OMseqcounter = status['seqs']
    print('Controller is in standalone mode')

# Get initial data set
# - in future decide what we are getting via the mode (FFF vs CNC vs laser)
for key in OMstatuskeys:
    if OMrequest(key,True):
        print('Initial "' + key + '" data acquired')
    else:
        hardfail('Failed to accqire "' + key + '" data')

# MAIN LOOP

while True:
    if OMrequest('state',False):
        # Set the list of keys based on our state
        # If uptime has decreased do a restart
        # also restart if mode chaanges
        pass
    else:
        print('Failed to fetch machine state')
        sleep(updatetime)
        continue
    if SBCmode:
        for key in OMstatuskeys:
            OMrequest(key,True)
    else:
        fullupdatelist = seqrequest()
        for key in OMupdatekeys + fullupdatelist:
            if key in fullupdatelist:
                OMrequest(key,True)
            else:
             OMrequest(key,False)
    updatedisplay()
    sleep(updatetime)
