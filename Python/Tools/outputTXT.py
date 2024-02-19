from sys import exit

'''
    This is a TEXT (REPL/console) output class for serialRRF
    It will later be adapted for I2C displas etc
'''

# These are the only key sets in the OM we are interested in
# We will always get 'state' at the start of the loop
#  - We get 'seqs' each loop unless in SBC mode
# All other keys need to be specified below

class outputRRF:
    # keys to verbose update on startup and when seqs change
    verboseKeys = {'FFF':['heat','tools','job','boards','network'],
                    'CNC':['spindles','tools','move','job','boards','network'],
                    'Laser':['move','job','boards','network']}
    # subset of keys to frequent update independent of seqs
    frequentKeys = {'FFF':['heat','job','boards'],
                    'CNC':['spindles','tools','move','job','boards'],
                    'Laser':['move','job','boards']}

    def __init__(self, initialOM):
        self.localOM = initialOM
        print('output is starting')

    def updateOutput(self):
        # Human readable uptime
        def dhms(t):
            d = int(t / 86400)
            h = int((t / 3600) % 24)
            m = int((t / 60) % 60)
            s = int(t % 60)
            if d > 0:
                days = str(d)  + ':'
            else:
                days = ''
            if h > 0:
                hrs = str(h)  + ':'
            else:
                hrs = ''
            if m > 0:
                mins = "%02.f" % m + ':'
            else:
                mins = ''
            secs = "%02.f" % s
            return days+hrs+mins+secs

        # Overall Status
        print('status:',self.localOM['state']['status'], end='')
        print(' | uptime:',dhms(self.localOM['state']['upTime']), end='')
        if self.localOM['state']['status'] in ['updating','starting']:
            # placeholder for display splash while starting or updating..
            print(' | Please wait')
            return
        self.updateCommon()
        if self.localOM['state']['status'] == 'DEBUGoff':
            pass   # Placeholder for display off code etc..
        else:
            # this is where we show mode-specific data
            if self.localOM['state']['machineMode'] == 'FFF':
                self.updateFFF()
            elif self.localOM['state']['machineMode']  == 'CNC':
                self.updateAxes()
                self.updateCNC()
            elif self.localOM['state']['machineMode']  == 'Laser':
                self.updateAxes()
                self.updateLaser()
            self.updateJob()
        self.updateMessages()
        print()

    def updateCommon(self):
        # Voltage
        print(' | Vin: %.1f' % self.localOM['boards'][0]['vIn']['current'],end='')
        # MCU temp
        print(' | mcu: %.1f' % self.localOM['boards'][0]['mcuTemp']['current'],end='')
        # Network
        if len(self.localOM['network']['interfaces']) > 0:
            print(' | network:', self.localOM['network']['interfaces'][0]['state'],end='')
        return True

    def updateJob(self):
            # Job progress
            if self.localOM['job']['build']:
                try:
                    percent = self.localOM['job']['filePosition'] / self.localOM['job']['file']['size'] * 100
                except ZeroDivisionError:  # file size can be 0 as the job starts
                    percent = 0
                print(' | progress:', "%.1f" % percent,end='%')

    def updateAxes(self):
        # Display all configured axes and homed state.
        # TODO: Show workspace in use and adjust reported axis position to suit
        #       Currently we show Machine Position, not workspace relative
        print(' | axes:',end='')
        if self.localOM['move']['axes']:
            for axis in self.localOM['move']['axes']:
                if axis['visible']:
                    if axis['homed']:
                       print(' ' + axis['letter'] + ':' + str(axis['machinePosition']),end='')
                    else:
                       print(' ' + axis['letter'] + ':?',end='')

    def updateMessages(self):
        # M117 messages
        if self.localOM['state']['displayMessage']:
            print(' | message:', self.localOM['state']['displayMessage'],end='')
        # M291 messages
        if self.localOM['state']['messageBox']:
            if self.localOM['state']['messageBox']['mode'] == 0:
                print(' | info: ',end='')
            else:
                print(' | query: ',end='')
            if self.localOM['state']['messageBox']['title']:
                print('==', self.localOM['state']['messageBox']['title'],end=' == ')
            print(self.localOM['state']['messageBox']['message'],end='')

    def updateFFF(self):
        # For FFF mode we want to show the Heater states
        def showHeater(number,name):
            if self.localOM['heat']['heaters'][number]['state'] == 'fault':
                print(' | ' + name + ': FAULT',end='')
            else:
                print(' | ' + name + ':', '%.1f' % self.localOM['heat']['heaters'][number]['current'],end='')
                if self.localOM['heat']['heaters'][number]['state'] == 'active':
                    print(' (%.1f)' % self.localOM['heat']['heaters'][number]['active'],end='')
                elif self.localOM['heat']['heaters'][number]['state'] == 'standby':
                    print(' (%.1f)' % self.localOM['heat']['heaters'][number]['standby'],end='')

        # Bed
        if len(self.localOM['heat']['bedHeaters']) > 0:
            if self.localOM['heat']['bedHeaters'][0] != -1:
                showHeater(self.localOM['heat']['bedHeaters'][0],'bed')
        # Chamber
        if len(self.localOM['heat']['chamberHeaters']) > 0:
            if self.localOM['heat']['chamberHeaters'][0] != -1:
                showHeater(self.localOM['heat']['chamberHeaters'][0],'chamber')
        # Extruders
        if len(self.localOM['tools']) > 0:
            for tool in self.localOM['tools']:
                if len(tool['heaters']) > 0:
                    showHeater(tool['heaters'][0],'e' + str(self.localOM['tools'].index(tool)))

    def updateCNC(self):
        def showSpindle(name,spindle):
            print(' | ' + name + ': ',end='')
            if self.localOM['spindles'][spindle]['state'] == 'stopped':
                print('stopped',end='')
            elif self.localOM['spindles'][spindle]['state'] == 'forward':
                print('fwd:', str(self.localOM['spindles'][spindle]['current']),end='rpm')
            elif self.localOM['spindles'][spindle]['state'] == 'reverse':
                print('rev:', str(self.localOM['spindles'][spindle]['current']),end='rpm')

        # Display spindle state, direction and speed
        if len(self.localOM['tools']) > 0:
            for tool in self.localOM['tools']:
                if tool['spindle'] != -1:
                    showSpindle(tool['name'],tool['spindle'])


    def updateLaser(self):
        # Show laser info; unfortunately not much to show; no seperate laser 'tool'
        if self.localOM['move']['currentMove']['laserPwm'] != None:
            pwm = str(self.localOM['move']['currentMove']['laserPwm'])
        else:
            pwm = 'not configured'
        print(' | laser PWM: ' + pwm,end='')
