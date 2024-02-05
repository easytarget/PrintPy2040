from telnetlib import Telnet as telnet
from time import sleep
import json

''' M409 keys of interest:
    heat
    job
    sensors
    ?seqs
    state
'''

HOST = "10.0.0.30"
password = "freedumb"

tn = telnet(HOST)

print(tn.read_until(b"Please enter your password:").decode('ascii'))
print('send')
tn.write(password.encode('ascii') + b"\n")
print('sent')
print(tn.read_until(b"Log in successful!").decode('ascii'))
while True:
    # cmd= b'M409 F"fnd99" K"job"\n'
    cmd = b'M409 F"vd2"\n'
    tn.write(cmd)
    print('SEND: '+ str(cmd))
    response = tn.read_until(b"ok").decode('ascii').split()
    print(response)
    print(type(response))
    #for key in response:
    #    print("DATA: " + key + " = " + str(response[key]))
    print(len(response))
    try:
        payload = json.load(response[0])
    except:
        print("????")
        payload = []
    for key in payload['result']:
        print("DATA: " + key + " = " + str(payload['result'][key]))
    else:
        print("No Payload!")
    sleep(10)
