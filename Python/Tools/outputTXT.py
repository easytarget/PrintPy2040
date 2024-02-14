from sys import exit

'''
    This is a TEXT (REPL/console) output class for serialRRF
    It will later be adapted for I2C displas etc
'''

# These are the only key sets in the OM we are interested in
#  We will always get 'state' at the start of the loop
#  We get 'seqs' each loop unless in SBC mode
# We also get 'boards' during startup to determine the machine mode

# keys to full update on startup and when sews change
OMstatuskeys = {'FFF':['heat','job','boards','network','tools'],
                'CNC':[],
                'Laser':[]}
# subset of keys to frequent update independent of SEQs
OMupdatekeys = {'FFF':['heat','job','boards'],
                'CNC':[],
                'Laser':[]}

def updateOutput(status,machineMode):
    if machineMode == 'FFF':
        updateFFF(status)
    elif machineMode == 'CNC':
        print('CNC output not yet implemented')
    elif machineMode == 'Laser':
        print('Laser output not yet implemented')

def updateFFF(status):
    def showHeater(number,name):
        if status['heat']['heaters'][number]['state'] == 'fault':
            print(' | ' + name + ': FAULT',end='')
        else:
            print(' | ' + name + ':', '%.1f' % status['heat']['heaters'][number]['current'],end='')
            if status['heat']['heaters'][number]['state'] == 'active':
                print(' (%.1f)' % status['heat']['heaters'][number]['active'],end='')
            elif status['heat']['heaters'][number]['state'] == 'standby':
                print(' (%.1f)' % status['heat']['heaters'][number]['standby'],end='')

    # Currently a one-line text status output,
    #  eventually a separate class to drive physical displays

    # Overall Status
    print('status:',status['state']['status'],
          '| uptime:',status['state']['upTime'],
          end='')

    # Voltage
    print(' | Vin: %.1f' % status['boards'][0]['vIn']['current'],end='')

    # MCU temp
    print(' | mcu: %.1f' % status['boards'][0]['mcuTemp']['current'],end='')

    # Network
    if len(status['network']['interfaces']) > 0:
        print(' | network:', status['network']['interfaces'][0]['state'],end='')

    # Temporary States
    if status['state']['status'] in ['updating','starting']:
        # display a splash while starting or updating..
        print()
        return

    # Machine Off
    if status['state']['status'] == 'off':
        # turn display off and return
        pass
    else:
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

        # Job progress
        if status['job']['build']:
            try:
                percent = status['job']['filePosition'] / status['job']['file']['size'] * 100
            except ZeroDivisionError:  # file size can be 0 as the job starts
                percent = 0
            print(' | progress:', "%.1f" % percent,end='%')

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
    print()
