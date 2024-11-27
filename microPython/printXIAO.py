# Import our local classes and config
from serialOM import serialOM
from outputI2Cx2 import outputRRF
from lumenXIAO2040 import lumen
from config import config
# The microPython standard libs
from sys import exit
from gc import collect, mem_free
from machine import reset, disable_irq, enable_irq
from time import sleep_ms, ticks_ms, ticks_diff, localtime

'''
    PrintMPy is a serialOM.py loop for MicroPython devices.
'''

# local print function so we can suppress info messages.
def pp(*args, **kwargs):
    if not config.quiet:
        print(*args, **kwargs)

# Do a minimum drama restart/reboot
def restartNow(why):
    pp('Error: ' + why)
    # Countdown and restart
    pp('Restarting in ',end='')

    for c in range(config.rebootDelay,0,-1):
        pp(c,end=' ')
        blink('err')
        sleep_ms(1000)
    pp()
    #exit()   # Useful while debugging, drop to REPL
    reset() # Micropython; reboot module

def hardwareFail(why):
    pp('A critical hardware error has occured!')
    pp('- Do a full power off/on cycle and check wiring etc.\n' + why + '\n')
    while True:  # loop forever
        sleep_ms(60000)

def buttonDown(_p):
    # Button event IRQ handler
    state = button.value()
    now = ticks_ms()
    sleep_ms(config.buttonTm)
    if button.value() == state:
        buttonPressed(now)

def buttonPressed(irqTime):
    global buttonTime
    if button.value() == config.buttonDown:
        buttonTime = irqTime
        print('+',end='')
        outputText = 'PrintPy Free Memory: ' + str(mem_free())
        if outputText:
            print(outputText,end='')
    else:
        print('-',end='')
        # This should really require a second press /while/ the status is showing.
        if config.buttonLong > 0 and buttonTime is not None:
            if ticks_diff(ticks_ms(),buttonTime) > config.buttonLong:
                print('WIFI TRIGGER') # TODO: Wifi enable/disable cycle
        buttonTime = None

def blink(state):
    if led is not None:
        led.blink(state)

'''
    Init
'''

# Basic info
start = localtime()
startDate = str(start[0]) + '-' + str(start[1]) + '-' + str(start[2])
startTime = "%02.f" % start[3] + ':' + "%02.f" % start[4] + ':' + "%02.f" % start[5]
startText = '=== Starting: ' + startDate + ' ' + startTime

if config.quiet:
    print(startText)
else:
    print('printMPy is starting at: ' + startDate + ' ' + startTime + ' (device localtime)')

# Illumination/mood LEDs
if config.illuminate:
    led = lumen(config.led_bright, config.led_standby, config.led_flash)
else:
    led = None

# Init RRF UART connection
rrf = config.device
rrf.init(baudrate=config.baud)
if not rrf:
    hardwareFail('No UART device found')
else:
    print('UART connected')

# Get output/display device, hard fail if not available
pp('starting output')
out = outputRRF()
if not out.running:
    hardwareFail('Failed to start output device')
else:
    sleep_ms(333)
out.splash()
splashend = ticks_ms() + config.splashtime

# create the OM handler
try:
    OM = serialOM(rrf, out.omKeys, quiet=config.quiet, noCheck=True)
except Exception as e:
    restartNow('Failed to start ObjectModel communications\n' + str(e))

if OM.machineMode == '':
    restartNow('Failed to connect to controller, or unsupported controller mode.')

# hardware button
buttonTime = None
if config.button:
    button = config.button
    button.irq(trigger=button.IRQ_FALLING | button.IRQ_RISING, handler=buttonDown)
    pp('button present on:',repr(button).split('(')[1].split(',')[0])

# Now pause, then blink initial status and destroy splash after timeout
while ticks_ms() < splashend:
    sleep_ms(25)
blink(led.emote(OM.model,config.net))
out.swipeclean()
out.update(OM.model)

'''
    Main loop
'''
while True:
    collect()  # do this before every loop because.. microPython
    begin = ticks_ms()
    # Do a OM update
    if led is not None:
        led.heartbeat()
    haveData = False
    omstart = ticks_ms()
    try:
        haveData = OM.update()
    except Exception as e:
        restartNow('Error while fetching machine state\n' + str(e))
    omend = ticks_ms()
    # output the results if successful
    if haveData:
        blink(led.emote(OM.model, config.net))
        # pass the results to the output module and print any response
        outputText = out.update(OM.model)
        if config.stats:
            omtime = omend - omstart
            stats = '[{}ms, {}b] '.format(omtime, str(mem_free()))
            outputText = stats + outputText
        if config.info:
            print('{}'.format(outputText.strip()))
    else:
        blink('err')
        pp('failed to fetch ObjectModel data')
    # check output is running and restart if not
    if not out.running:
        restartNow('Output device has failed')
    # Request cycle ended, wait for next
    while ticks_diff(ticks_ms(),begin) < config.updateTime:
        sleep_ms(1)
