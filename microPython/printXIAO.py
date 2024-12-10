# Import our local classes and config
from serialOM import serialOM
from outputI2Cx2 import outputRRF
from lumenXIAO import lumen
from heartbeatXIAO import heartbeat
from config import config
# The microPython standard libs
from sys import exit

from gc import collect, mem_free
from machine import reset, mem32
from time import sleep_ms, ticks_ms, ticks_diff, localtime

'''
    PrintMPy is a serialOM.py loop for MicroPython devices.
'''

# local print function so we can suppress info messages.
def pp(*args, **kwargs):
    if config.verbose:
        print(*args, **kwargs)

# Do a minimum drama restart/reboot
def restartNow(why, display='PrintPY\nerror'):
    pp('Error: ' + why)
    pp('Restarting in ',end='')
    out.watchdog = 0   # kill the marquee
    for c in range(config.reboot_delay,0,-1):
        pp(c,end=' ')
        blink('err', auto=False)
        out.showText(display, 'Restarting\nin: {}s'.format(c))
        sleep_ms(1000)
    pp()
    out.off()
    if config.debug < 0:
        exit()   # drop to REPL
    reset()  # Reboot module

def hardwareFail(why):
    # Fatal error; halt.
    pp('A critical hardware error has occured!')
    pp('- Do a full power off/on cycle and check wiring etc.\n' + why + '\n')
    while True:  # loop forever
        sleep_ms(60000)

def buttonPressed(_p):
    # Any button activity triggers this.
    # - we look for a long button press in the main loop.
    global button_time     # we are in an interrupt, context is everything..
    button_time = ticks_ms() + config.button_long
    out.awake(config.button_awake)  # wake for longer than default off_time

def networkToggle():
    if OM.model is None:
        return
    if len(OM.model['network']['interfaces']) == 0:
        return
    interface = OM.model['network']['interfaces'][config.net]
    if interface['state'] in config.net_map.keys():
        cmd = config.net_map[interface['state']]
    else:
        cmd = config.net_map['DEFAULT']
    cmd = cmd.replace('{NET}',str(config.net))
    net = interface['type']
    pp('{} change requested via button: {}'.format(net, cmd))
    out.awake(config.net_awake)   # awake longer while network is changing state
    OM.sendGcode(cmd)
    out.alert()

def blink(state, auto=True):
    if config.mood:
        mood.blink(state, out.standby, auto)

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
    pp('UART connected')
# UART port and buffer will be in a unknown state; there may be junk in it
# So; send a newline, then wait a bit (display init), then empty the buffer
rrf.write('\n')
rrf.flush()

# Get output/display device, hard fail if not available
pp('starting output')
out = outputRRF()
if not out.running:
    hardwareFail('Failed to start output device')
out.splash()
out.on()
splashend = ticks_ms() + config.splash_time

# Now that the display is running we read+discard from the UART until it stays empty
while rrf.any():
    rrf.read(128)
    sleep_ms(100)

# create the OM handler and get initial status
try:
    OM = serialOM(rrf, out.omKeys, quiet=config.verbose, noCheck=True)
except Exception as e:
    restartNow('Failed to start ObjectModel communications\n' + str(e),
               'Connection\nError')

# hardware button
button_time = None
if config.button is not None:
    button = config.button
    button.irq(trigger=button.IRQ_FALLING | button.IRQ_RISING, handler=buttonPressed)
    pp('button present on:',repr(button).split('(')[1].split(',')[0])

# Now pause, then blink initial status and destroy splash after timeout
while ticks_ms() < splashend:
    sleep_ms(25)
out.off()
# Initial comms fail (Reversed RX/TX?)
if OM.machineMode == '' or OM.model is None:
    restartNow('Failed to connect to controller, or unknown controller mode.',
               'Failed to\nConnect')

blink(mood.emote(OM.model, config.net))
out.updatePanels(OM.model)
fail_count = 0

'''
    Main loop
'''
while True:
    begin = ticks_ms()
    # Do a OM update
    if config.heart:
        heart.beat(out.standby)
    have_data = False
    om_start = ticks_ms()
    try:
        have_data = OM.update()
    except Exception as e:
        restartNow('Error while fetching machine state\n' + str(e),'Communication\nError')
    om_end = ticks_ms()
    collect()
    # bump the marquee thread watchdog
    out.watchdog = ticks_ms() + (3 * config.update_time)
    # output the results if successful
    if have_data:
        fail_count = 0
        blink(mood.emote(OM.model, config.net))
        # pass the results to the output module and collect status line
        outputText = out.updatePanels(OM.model)
        collect()
        if config.stats:
            om_time = om_end - om_start
            stats = '[{}ms, {}b] '.format(om_time, str(mem_free()))
            outputText = stats + outputText
        if config.info:
            print('{}'.format(outputText.strip()))
    else:
        fail_count += 1
        blink('err')
        pp('failed to fetch ObjectModel data, #{}'.format(fail_count))
        if fail_count > config.fail_count:
            out.showFail(fail_count)
    # check output is running and restart if not
    if not out.running:
        restartNow('Output device has failed','Output\nFailing')
    # Request cycle ended, wait for next
    while ticks_diff(ticks_ms(),begin) < config.update_time:
        # button...
        if button_time is not None:
            if button.value() == config.button_down:
                if (ticks_ms() > config.button_time) and config.net:
                    button_time = 0
                    toggleNetwork()
            else:
                button_time = None
        sleep_ms(1)
