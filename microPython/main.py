# main.py
#
# Place this in the root filesystem of the device, it
# examines config.py to determine whether to autostart
# printXIAO on device startup and hard reboots.

print('PrintXIAO loader')
from sys import exit
from time import sleep_ms
try:
    from config import config
except ModuleNotFoundError:
    print('Cannot find config.py')
    exit()

if config.debug > 0:
    print('Autostart: ',end='')
    for i in range(config.debug,0,-1):
        print('{}'.format(i),end='')
        sleep_ms(500)
        print('.',end='')
        sleep_ms(500)
    print('now')
    import printXIAO
print('Debug mode; not starting')