from telnetlib import Telnet as telnet
from time import sleep

HOST = "10.0.0.30"
password = "superKrib"

tn = telnet(HOST)

print(tn.read_until(b"Please enter your password:").decode('ascii'))
print('send')
tn.write(password.encode('ascii') + b"\n")
print('sent')
print(tn.read_until(b"Log in successful!").decode('ascii'))
while True:
    tn.write(b'M409 F"fnd99"\n')
    print('M409 sent')
    print(tn.read_until(b"ok").decode('ascii'))
    sleep(10)
