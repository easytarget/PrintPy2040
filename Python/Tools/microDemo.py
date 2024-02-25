from serialOM import serialOM
from serial import Serial

rrf = Serial('/dev/ttyACM1',57600)
OM=serialOM(rrf, {'FFF':[],'CNC':[],'Laser':[]}, quiet=True)
print('state: ' + OM.model['state']['status'] 
     + ', up: ' + str(OM.model['state']['upTime']) + 's')
