from config import config
from time import sleep_ms
if config.debug == 0:
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
