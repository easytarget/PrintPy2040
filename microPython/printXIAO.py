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
from time import sleep_ms, ticks_us, ticks_diff, ticks_add, localtime

# timers are in microseconds
TIMESCALE = 1000000  # == 1 second

'''
    PrintMPy is a serialOM.py loop for MicroPython devices.
'''

# Placeholder objects for timers and IRQ's; declared here so
# that we can safely test for and disable as needed whenever we exit.
button = None
button_time = None
animator_thread = None
mood = None
heart = None

# local print function so we can suppress info messages.
def pp(*args, **kwargs):
    if config.verbose:
        print(*args, **kwargs)

def buttonPressed(_p):
    # ISR: Any button activity triggers this; does not need debouncing.
    # - we check for a long button press in the main loop.
    #global button_time     # we are in an interrupt, bring this into context
    if config.button_long > 0:
        button_time = ticks_add(ticks_us(), int(config.button_long * TIMESCALE))
    out.awake(int(config.long_awake * TIMESCALE))

def buttonLong():
    # has the button been long-pressed?
    if button_time is not None:
        if button.value() == config.button_down:
            if (ticks_diff(ticks_us(), button_time) > 0) and (config.net is not None):
                button_time = None
                networkToggle()
        else:
            button_time = None

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
    for c in range(config.reboot_delay,0,-1):
        pp(c,end=' ')
        if config.mood:
            mood.blink('err', out.standby, False)
        out.showError(message, 'Restarting\nin: {}s'.format(c))
        sleep_ms(1000)
    pp()
    out.off()
    if config.debug is not None:
        print('Debug mode: exiting to REPL')
        killAll()
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
    print('exit(): killing background')
    try:
        out.watchdog = 0   # for completeness..
        # kill the animator thread
        animator_thread.exit()
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

# Firmware with atexit() enabled might help debugging..
# but to be honest.. it doesn't really help.
# I'm not sure if the call to killAll is being made,
# it does not print() on the repl console to say it ran..
try:
    from sys import atexit
    atexit(killAll)
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
    pp('UART initialised')
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
splashend = ticks_add(ticks_us(), int(config.splash_time * TIMESCALE))

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

pp('connected to ObjectModel')

# hardware button
button_time = None
if config.button is not None:
    button = config.button
    button.irq(trigger=button.IRQ_FALLING | button.IRQ_RISING, handler=buttonPressed)
    pp('button present on:',repr(button).split('(')[1].split(',')[0])

# Show initial mood
if config.mood:
    mood.blink(mood.emote(OM.model, config.net), out.standby, True)

# Put initial data into panels (it wont be displayed until splash ends)
out.updatePanels(OM.model)

# pause for splash timeout
while ticks_diff(ticks_us(), splashend) < 0:
    sleep_ms(25)

pp('PrintPY::printXIAO is running')

# end splash,
out.off()

# Start the marquee and model output (will run in a new thread)
animator_thread = out.animator()

# Pause for long enough that the animator completes its initial cycle
sleep_ms(100)

# Show initial update
out.on()

'''
    Main loop
'''
fail_count = 0
while True:
    next_update = ticks_add(ticks_us(), int(config.update_time * TIMESCALE))
    # Do a OM update
    if config.heart:
        heart.beat(out.standby)
    have_data = False
    om_start = ticks_us()
    try:
        have_data = OM.update()
    except Exception as e:
        restartNow('Error while fetching machine state\n' + str(e),'Communication\nError')
    om_end = ticks_us()
    collect()
    # bump the marquee thread watchdog
    out.watchdog = ticks_us()
    # output the results if successful
    if have_data:
        fail_count = 0
        if config.mood:
            mood.blink(mood.emote(OM.model, config.net), out.standby, True)
        # pass the results to the output module and recieve status line
        outputText = out.updatePanels(OM.model)
        # cleanup after output (display) loop
        collect()
        if config.stats:
            om_time = int(ticks_diff(om_end, om_start) / 1000)    # report in ms
            stats = '[{} ms, {} b] '.format(om_time, str(mem_free()))
            outputText = '{:030b}'.format(ticks_us()) + stats + outputText           ############################
        if config.info:
            print('{}'.format(outputText.strip()))
    else:
        fail_count += 1
        if config.mood:
            mood.blink('err', out.standby, True)
        pp('failed to fetch ObjectModel data, #{}'.format(fail_count))
        if fail_count >= config.fail_count:
            out.updateFail(fail_count)
    # check output (display) is running, and restart if not
    if not out.running:
        restartNow('Output (display) device has failed','Output\nFailing')
    # is the button being long-pressed?
    buttonLong()
    ## Request cycle ended, wait for next whilst checking for long button press     ######################
    while ticks_diff(ticks_us(), next_update) < 0:
        buttonLong()
        sleep_us(1000)
