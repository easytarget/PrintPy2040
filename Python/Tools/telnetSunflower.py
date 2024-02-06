from duetconfig import host,password
from telnetlib import Telnet as telnet
from time import sleep
import json

''' 
    This script uses Telnet to connect to my duet (I have my reasons)
    The inbuilt 'telnetlib' library it uses comes with the following warning:
    > Deprecated since version 3.11, will be removed in version 3.13:
    consider yourself warned ;)

    It is intended to be run on a desktop system (CPython, not microPython)
    and will be used to create a 'framework' for extracting data from
    a RRF based system using the ObjectModel.

    M409 keys of interest:
    heat
    job
    sensors
    state
    ?seqs
'''

OMstatuskeys = ['heat','sensors']
OMupdatekeys = ['state','job','heat','seqs']

# Init telnet and log in
rrf = telnet(host)
print("Connected")

print(rrf.read_until(b"Please enter your password:").decode('ascii'))
print('[password sent]',end='')

rrf.write(password.encode('ascii') + b"\n")
print(rrf.read_until(b"Log in successful!").decode('ascii'))

# This is the way...
def OMrequest(OMkey,OMflags="fnd99"):
    cmd = b'M409 F"' + bytes(OMflags, 'utf8') + b'" K"' + bytes(OMkey, 'utf8') + b'"\n'
    print('SEND: '+ str(cmd))
    rrf.write(cmd)
    try:
        response = rrf.read_until(b"ok",timeout=0.5).decode('ascii').replace("\r", "").split('\n')
    except:
        response = ['timeout']
    for line in response:
        if line == '':
            response.pop(response.index(line))
    #DEBUG:print(response, type(response), len(response))
    try:
       payload = json.loads(response[0])
    except:
        print("NOT VALID JSON: ")
        print(response[0])
        payload = {}
    #DEBUG:print(payload, type(payload), len(payload))
    if 'result' in payload.keys():
	# This is where we need to update our internal status map !!!!
        for key in payload['result']:    # Just dump for now.
            print("  DATA: " + payload['key'] + '.' + key + " = " + str(payload['result'][key]))
    else:
        print("No Payload!")
    if response[0] == 'timeout':
        print('TIMEOUT: ')

# simple control loop
fullstateknown = False
while True:
    if not fullstateknown:
        for key in OMstatuskeys:
           OMrequest(key,"vnd99")
        print("Full status fetch cycle complete")
        fullstateknown = True
    for key in OMupdatekeys:
        OMrequest(key)
    print("Update fetch cycle complete")
    sleep(60)
