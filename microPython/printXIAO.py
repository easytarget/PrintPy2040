# Import our local classes and config
from serialOM import serialOM
from outputI2Cx2 import outputRRF
from lumenXIAO import lumen
from heartbeatXIAO import heartbeat
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
    if not config.verbose:
        print(*args, **kwargs)

# Do a minimum drama restart/reboot
def restartNow(why, display='error'):
    pp('Error: ' + why)
    # Countdown and restart
    pp('Restarting in ',end='')

    for c in range(config.rebootDelay,0,-1):
        pp(c,end=' ')
        blink('err')
        out.showText(display, 'restarting\n{}'.format(c))
        out.on()
        sleep_ms(1000)
    pp()
    #exit()   # Useful while debugging, drops to REPL
    reset()  # Reboot module

def hardwareFail(why):
    # Fatal error; halt.
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
    if config.mood:
        mood.blink(state, out.standby)

def exit():
    # Kill timer..
    pass

'''
    Init
'''

# Always log that we are starting to console.
print('printXIAO is starting')

# LEDs
if config.mood:
    mood = lumen(config.mood_bright, config.mood_standby, config.mood_flash)
if config.heart:
    heart = heartbeat(config.heart_bright, config.heart_standby)

# UART connection
rrf = config.device
rrf.init(baudrate=config.baud)
if not rrf:
    hardwareFail('No UART device found')
else:
    print('UART connected')
# UART port and buffer will be in a unknown state; there may be junk in it
# So; send a newline, then wait a bit (display init), then empty the buffer
rrf.write('\n')
rrf.flush()

# Get output/display device, hard fail if not available
pp('starting output')
out = outputRRF()
if not out.running:
    hardwareFail('Failed to start output device')
#else:
#    sleep_ms(333)
out.splash()
out.on()
splashend = ticks_ms() + config.splashtime

# Now that the display is running we read+discard from the UART until it stays empty
while rrf.any()
    rrf.read(128)
    sleep_ms(100)

# create the OM handler and get initial status
try:
    OM = serialOM(rrf, out.omKeys, quiet=config.verbose, noCheck=True)
except Exception as e:
    restartNow('Failed to start ObjectModel communications\n' + str(e))

# TODO: handle this better?
if OM.machineMode == '' or OM.model is None:
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
blink(mood.emote(OM.model, config.net))
out.off()
out.showText('Starting','...')
out.on()
sleep_ms(500)
out.updateNG(OM.model)

'''
    Main loop
'''
while True:
    collect()  # do this before every loop because.. microPython
    begin = ticks_ms()
    # Do a OM update
    if config.heart:
        heart.beat(out.standby)
    have_data = False
    om_start = ticks_ms()
    try:
        have_data = OM.update()
    except Exception as e:
        restartNow('Error while fetching machine state\n' + str(e))
    om_end = ticks_ms()
    # output the results if successful
    if have_data:
        blink(mood.emote(OM.model, config.net))
        # pass the results to the output module and print any response
        outputText = out.updatePanels(OM.model)
        if config.stats:
            om_time = om_end - om_start
            stats = '[{}ms, {}b] '.format(om_time, str(mem_free()))
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
