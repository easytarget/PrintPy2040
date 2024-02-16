from sys import exit

'''
    This is a TEXT (REPL/console) output class for serialRRF
    It will later be adapted for I2C displas etc
'''

# These are the only key sets in the OM we are interested in
# We will always get 'state' at the start of the loop
#  - We get 'seqs' each loop unless in SBC mode
#  - We also get 'boards' during startup to determine the machine mode
# All other keys need to be specified below on a per-mode basis

# keys to verbose update on startup and when seqs change
OMstatuskeys = {'FFF':['heat','tools','job','boards','network'],
                'CNC':['job','boards','network'],
                'Laser':['job','boards','network']}
# subset of keys to frequent update independent of seqs
OMupdatekeys = {'FFF':['heat','job','boards'],
                'CNC':['job','boards'],
                'Laser':['job','boards']}

def updateOutput(status,machineMode):
    # Human readable uptime
    def hms(t):
        h = int(t / 3600)
        m = int((t / 60) % 60)
        s = int(t % 60)
        if h > 0:
            hrs = str(h)  + ':'
        else:
            hrs = ''
        if m > 0:
            mins = "%02.f" % m + ':'
        else:
            mins = ''
        secs = "%02.f" % s
        return hrs+mins+secs

    # Overall Status
    print('status:',status['state']['status'], end='')
    print(' | uptime:',hms(status['state']['upTime']), end='')
    if status['state']['status'] in ['updating','starting']:
        # placeholder for display splash while starting or updating..
        print(' | Please wait')
        return
    updateCommon(status)
    if status['state']['status'] == 'off':
        pass   # Placeholder for display off code etc..
    else:
        # this is where we show mode-specific data
        if machineMode == 'FFF':
            updateFFF(status)
        elif machineMode == 'CNC':
            updateCNC(status)
        elif machineMode == 'Laser':
            updateLaser(status)
        updateJob(status)
    updateMessages(status)
    print()

def updateCommon(status):
    # Voltage
    print(' | Vin: %.1f' % status['boards'][0]['vIn']['current'],end='')
    # MCU temp
    print(' | mcu: %.1f' % status['boards'][0]['mcuTemp']['current'],end='')
    # Network
    if len(status['network']['interfaces']) > 0:
        print(' | network:', status['network']['interfaces'][0]['state'],end='')
    return True

def updateJob(status):
        # Job progress
        if status['job']['build']:
            try:
                percent = status['job']['filePosition'] / status['job']['file']['size'] * 100
            except ZeroDivisionError:  # file size can be 0 as the job starts
                percent = 0
            print(' | progress:', "%.1f" % percent,end='%')

def updateMessages(status):
    # M117 messages
    if status['state']['displayMessage']:
        print(' | message:', status['state']['displayMessage'],end='')
    # M291 messages
    if status['state']['messageBox']:
        if status['state']['messageBox']['mode'] == 0:
            print(' | info: ',end='')
        else:
            print(' | query: ',end='')
        if status['state']['messageBox']['title']:
            print('==', status['state']['messageBox']['title'],end=' == ')
        print(status['state']['messageBox']['message'],end='')

def updateFFF(status):
    # For FFF mode we want to show the Heater states
    def showHeater(number,name):
        if status['heat']['heaters'][number]['state'] == 'fault':
            print(' | ' + name + ': FAULT',end='')
        else:
            print(' | ' + name + ':', '%.1f' % status['heat']['heaters'][number]['current'],end='')
            if status['heat']['heaters'][number]['state'] == 'active':
                print(' (%.1f)' % status['heat']['heaters'][number]['active'],end='')
            elif status['heat']['heaters'][number]['state'] == 'standby':
                print(' (%.1f)' % status['heat']['heaters'][number]['standby'],end='')

    # Bed
    if len(status['heat']['bedHeaters']) > 0:
        if status['heat']['bedHeaters'][0] != -1:
            showHeater(status['heat']['bedHeaters'][0],'bed')
    # Chamber
    if len(status['heat']['chamberHeaters']) > 0:
        if status['heat']['chamberHeaters'][0] != -1:
            showHeater(status['heat']['chamberHeaters'][0],'chamber')
    # Extruders
    if len(status['tools']) > 0:
        for tool in status['tools']:
            if len(tool['heaters']) > 0:
                showHeater(tool['heaters'][0],'e' + str(status['tools'].index(tool)))

def updateCNC(status):
    print(' | CNC output not yet implemented')

def updateLaser(status):
    print(' | Laser output not yet implemented')
