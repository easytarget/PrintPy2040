from serialOM import serialOM
from serial import Serial
from time import sleep
from datetime import timedelta
from sys import argv

rrf = Serial(argv[1],57600)
OM=serialOM(rrf, {'FFF':['network'],
                  'CNC':['network'],
                  'Laser':['network']})
while True:
    print(OM.model['network']['name'] + ' :: state: '
          + OM.model['state']['status'] + ', up: '
          + str(timedelta(seconds=OM.model['state']['upTime'])),end='')
    if OM.model['state']['displayMessage']:
        print(', message: ' + OM.model['state']['displayMessage'],end='')
    print()
    sleep(1)
    OM.update()
