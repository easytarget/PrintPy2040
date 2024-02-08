from RRFconfig import host,port,password
from telnetlib import Telnet as telnet
from time import sleep
import json
import itertools

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

# A global dict. of the all OM keys we see when running state and update checks
#status = {'state':{'status':'undefined'},'seqs':{}}
status = {'state':{'status':'undefined'}}

# These are the only key sets in the OM we are interested in
#  This could be expanded as needed.
OMstatuskeys = ['seqs','state','heat','job','sensors','network','tools']  # all keys
OMupdatekeys = ['seqs','state','heat','job']  # subset of keys to always update

# Used when the 'seqs' keys are not available (eg SBC mode)
# force full status fetches and assume the controller can keep up..
forcestatus = False

# Handle hard (eg serial or comms) errors; needs expansion ;-)
def hardfail():
    while true:  # BlackHole the process
        print('CRITICAL ERROR: HALTED')
        sleep(60)

# Init telnet connection
try:
    rrf = telnet(host,port)
except:
    print('Connection could not be established')
    hardfail()

# Log in - Needs some logic to cover failures..
print('Connected')
response = rrf.read_until(b"Please enter your password:").decode('ascii').replace("\r", "").split('\n')
rrf.write(password.encode('ascii') + b"\n")
print('Password sent')
response = rrf.read_until(b"Log in successful!").decode('ascii').replace("\r", "").split('\n')
print('Logged in')

# Recursive/iterative merge of dict/list structures.
# https://stackoverflow.com/questions/19378143/python-merging-two-arbitrary-data-structures#1
def merge(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        d = dict(a)
        d.update({k: merge(a.get(k, None), b[k]) for k in b})
        return d

    if isinstance(a, list) and isinstance(b, list):
        return [merge(x, y) for x, y in itertools.zip_longest(a, b)]

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
    response = rrf.read_until(b"ok",timeout=0.25).decode('ascii').replace("\r", "").split('\n')

    # remove empty lines
    while '' in response:
        response.remove('')

    if not response:
        print('Failed response on : ' + cmd.decode(),end="")
        return False

    # load as a json data structure
    try:
       payload = json.loads(response[0])
    except:
        print("NOT VALID JSON: ")
        print(response[0])
        return False

	# This is where we update our local status structure
    if 'result' in payload.keys():
        if fullstatus:
            status[payload['key']] = payload['result']
        else:
            #print(OMkey + ":")
            #print(status[payload['key']])
            #print(payload['result'])
            #print(merge(status[payload['key']],payload['result']))
            status[payload['key']] = merge(status[payload['key']],payload['result'])
    else:
        print("No Payload!")
        return False

    # If we got here; we had a successful cycle
    return True

def seqrequest():
    # Send a 'seqs' request to the OM, updates status and returns
    # a list of keys where the sequence number has changed
    print(status['seqs'])

def updatedisplay():
    print('status:',status['state']['status'],
          '| uptime:',status['state']['upTime'],
          '| bed:',status['heat']['heaters'][0]['current'],
          '| tool:',status['heat']['heaters'][1]['current'])

# simple control loop
updatefullstate = True
while True:
    if updatefullstate:
        for key in OMstatuskeys:
            OMrequest(key,True)
        #print("Status fetch cycle complete")
        updatefullstate = False
    else:
        for key in OMupdatekeys:
            OMrequest(key,False)
        #print("Update fetch cycle complete")
    #print(len(str(status)),status)
    updatedisplay()
    sleep(10)
