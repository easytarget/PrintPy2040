# main.py
#
# Place this in the root filesystem of the device, it
# examines config.py to determine whether to autostart
# printXIAO on device startup and hard reboots.

def countDown(text, time):
    print('{}: '.format(text), end='')
    for i in range(time,0,-1):
        print('{}'.format(i), end='')
        sleep_ms(500)
        print('.', end='')
        sleep_ms(500)
    print('now')

def run():
    try:
        import printXIAO
    except Exception as e:
        print('PrintXIAO.py exited:\n{}\n'.
              format(e))
        countDown('Waiting for display watchdog', config.display_watchdog + 1)


print('PrintXIAO loader')
from time import sleep_ms
from machine import reset
try:
    from config import config
except ModuleNotFoundError:
    print('Cannot find config.py')
    print('Copy "config-default.py" to "config.py" and edit as needed')
else:
    if config.autostart is not None:
        while True:
            countDown('Autostart', config.autostart)
            run()
            reset()

# drop out to the repl prompt
print('Debug mode; (use "import printXIAO" to start)')
