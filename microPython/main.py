# main.py
#
# Place this in the root filesystem of the device, it
# examines config.py to determine whether to autostart
# printXIAO on device startup and hard reboots.

print('PrintXIAO loader')
from time import sleep_ms
try:
    from config import config
except ModuleNotFoundError:
    print('Cannot find config.py')
    print('Copy "config-default.py" to "config.py" and edit as needed')
else:
    if config.debug is None:
        import printXIAO
    elif config.debug > 0:
        print('Autostart: ',end='')
        for i in range(config.debug,0,-1):
            print('{}'.format(i),end='')
            sleep_ms(500)
            print('.',end='')
            sleep_ms(500)
        print('now')
        import printXIAO
# Otherwise, just drop out to the repl prompt
print('Debug mode; not starting')
