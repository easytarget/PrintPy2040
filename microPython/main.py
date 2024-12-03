import config
from time import sleep_ms
if not config.debug == 0:
    import printXIAO
elif config.debug > 0:
    for i in range(config.debug,0,-1):
        print('{}'.format(i),end='')
        sleep_ms(500)
        print('.',end='')
    print()
    import printXIAO
