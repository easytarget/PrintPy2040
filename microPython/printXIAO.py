# Import our local classes and config
from serialOM import serialOM
from outputI2Cx2 import outputRRF
from lumenXIAO import lumen
from heartbeatXIAO import heartbeat
from config import config
# The microPython standard libs
from sys import exit
from gc import collect, mem_free
from machine import reset
from time import sleep_ms, ticks_ms, ticks_diff, localtime

'''
    PrintMPy is a serialOM.py loop for MicroPython devices.
'''

# Placeholder objects for timers and IRQ's; declared here so
# that we can safely test for and disable as needed whyenever we exit.
button = None
animator_thread = None
mood = None
heart = None

# local print function so we can suppress info messages.
def pp(*args, **kwargs):
    if config.verbose:
        print(*args, **kwargs)

def blink(state, auto=True):
    if config.mood:
        mood.blink(state, out.standby, auto)

def buttonPressed(_p):
    # ISR: Any button activity triggers this; does not need debouncing.
    # - we check for a long button press in the main loop.
    global button_time     # we are in an interrupt, context is everything..
    if config.button_long > 0:
        button_time = ticks_ms() + config.button_long
    out.awake(config.button_awake)

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
    out.awake(config.long_awake)   # awake longer while network is changing state
    OM.sendGcode(cmd)
    out.alert()

def restartNow(why, message='PrintPY\nerror'):
    # Do a minimum drama restart/reboot, mostly useful so we
    # get a re-check-loop at startup if comms are failing
    # - really unlikely to get called otherwise..
    pp('Error: ' + why)
    pp('Restarting in ',end='')
    killAll()
    for c in range(config.reboot_delay,0,-1):
        pp(c,end=' ')
        blink('err', auto=False)
        out.showError(message, 'Restarting\nin: {}s'.format(c))
        sleep_ms(1000)
    pp()
    out.off()
    if config.debug < 0:
        print('Debug mode: exiting to REPL')
        exit()
    else:
        reset()  # Reboot module

def hardFail(why):
    # Fatal error; halt.
    pp('A critical hardware error has occured!')
    pp('- Do a full power off/on cycle and check wiring etc.\n' + why + '\n')
    while True:  # loop forever
        sleep_ms(60000)

def killAll():
    # attempt to kill the animator threads, button IRQ
    # and notification LEDs. Useful when debugging.
    try:
        # kill the animator thread
        animator_thread.exit()
        out.watchdog = 0   # for completeness..
    except:
        pass  # dont care, we are exiting
    try:
        # Remove the button IRQ
        # (allegedly.. docs not really clear about this)
        button.irq(handler=None)
    except:
        pass  # dont care, we are exiting
    # Mood and heartbeat LED's off
    try:
        mood.off()
    except:
        pass  # dont care, we are exiting
    try:
        heart.off()
    except:
        pass  # dont care, we are exiting

# Firmware with atexit() enabled helps debugging..
try:
    from sys import atexit
    atexit.register(killAll)
except:
    pp('Firmware does not support atexit() handler')


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
    hardFail('No UART device found')
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
    hardFail('Failed to start output device')
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

# Initial model fail
if OM.machineMode == '' or OM.model is None:
    restartNow('Failed to connect to controller, or unknown controller mode.',
               'Failed to\nConnect')

# hardware button
button_time = None
if config.button is not None:
    button = config.button
    button.irq(trigger=button.IRQ_FALLING | button.IRQ_RISING, handler=buttonPressed)
    pp('button present on:',repr(button).split('(')[1].split(',')[0])

# Now pause, then blink initial status, setup initial panels and destroy splash
while ticks_ms() < splashend:
    sleep_ms(25)
blink(mood.emote(OM.model, config.net))
out.updatePanels(OM.model)   # 
fail_count = 0
# end splash, output will turn on again at the next update cycle
out.off()
# Start the marquee and model output (will run in a new thread)
animator_thread = out.animator()

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
        if fail_count >= config.fail_count:
            out.updateFail(fail_count)
    # check output is running and restart if not
    if not out.running:
        restartNow('Output device has failed','Output\nFailing')
    # Request cycle ended, wait for next
    while ticks_diff(ticks_ms(),begin) < config.update_time:
        if button_time is not None:
            if button.value() == config.button_down:
                if (ticks_ms() > button_time) and (config.net is not None):
                    button_time = None
                    networkToggle()
            else:
                button_time = None
        sleep_ms(1)
