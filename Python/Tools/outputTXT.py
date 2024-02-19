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
        r = ""
        r += 'status: ' + self.localOM['state']['status']
        r += ' | uptime: ' + dhms(self.localOM['state']['upTime'])
        if self.localOM['state']['status'] in ['updating','starting']:
            # placeholder for display splash while starting or updating..
            r += '  | Please wait'
            return r
        r += self.updateCommon()
        if self.localOM['state']['status'] == 'off':
            pass   # Placeholder for display off code etc..
        else:
            # this is where we show mode-specific data
            if self.localOM['state']['machineMode'] == 'FFF':
                r += self.updateFFF()
            elif self.localOM['state']['machineMode']  == 'CNC':
                r += self.updateAxes()
                r += self.updateCNC()
            elif self.localOM['state']['machineMode']  == 'Laser':
                r += self.updateAxes()
                r += self.updateLaser()
            r += self.updateJob()
        r += self.updateMessages()
        return r

    def updateCommon(self):
        # common items to always show
        r = ' | Vin: %.1f' % self.localOM['boards'][0]['vIn']['current']
        r += ' | mcu: %.1f' % self.localOM['boards'][0]['mcuTemp']['current']
        if len(self.localOM['network']['interfaces']) > 0:
            for interface in self.localOM['network']['interfaces']:
                r += ' | ' + interface['type'] + ': '
                if interface['state'] != 'active':
                    r += interface['state']
                else:
                    r += interface['actualIP']
        return r

    def updateJob(self):
        # Job progress
        r = ''
        if self.localOM['job']['build']:
            try:
                percent = self.localOM['job']['filePosition'] / self.localOM['job']['file']['size'] * 100
            except ZeroDivisionError:  # file size can be 0 as the job starts
                percent = 0
            r += ' | progress:' + "%.1f" % percent + '%'
        return r

    def updateAxes(self):
        # Display all configured axes and homed state.
        # TODO: Show workspace in use and adjust reported axis position to suit
        #       Currently we show Machine Position, not workspace relative
        r = ' | axes:'
        if self.localOM['move']['axes']:
            for axis in self.localOM['move']['axes']:
                if axis['visible']:
                    if axis['homed']:
                       r += ' ' + axis['letter'] + ':' + str(axis['machinePosition'])
                    else:
                       r += ' ' + axis['letter'] + ':?'
        return r

    def updateMessages(self):
        # M117 messages
        r = ''
        if self.localOM['state']['displayMessage']:
            r += ' | message: ' +  self.localOM['state']['displayMessage']
        # M291 messages
        if self.localOM['state']['messageBox']:
            if self.localOM['state']['messageBox']['mode'] == 0:
                r += ' | info: '
            else:
                r += ' | query: '
            if self.localOM['state']['messageBox']['title']:
                r += '== ' + self.localOM['state']['messageBox']['title'] + ' == '
            r += self.localOM['state']['messageBox']['message']
        return r

    def updateFFF(self):
        # For FFF mode we want to show the Heater states
        def showHeater(number,name):
            r = ''
            if self.localOM['heat']['heaters'][number]['state'] == 'fault':
                r += ' | ' + name + ': FAULT'
            else:
                r += ' | ' + name + ':' + '%.1f' % self.localOM['heat']['heaters'][number]['current']
                if self.localOM['heat']['heaters'][number]['state'] == 'active':
                    r += ' (%.1f)' % self.localOM['heat']['heaters'][number]['active']
                elif self.localOM['heat']['heaters'][number]['state'] == 'standby':
                    r += ' (%.1f)' % self.localOM['heat']['heaters'][number]['standby']
            return r

        r = ''
        # Bed
        if len(self.localOM['heat']['bedHeaters']) > 0:
            if self.localOM['heat']['bedHeaters'][0] != -1:
                r += showHeater(self.localOM['heat']['bedHeaters'][0],'bed')
        # Chamber
        if len(self.localOM['heat']['chamberHeaters']) > 0:
            if self.localOM['heat']['chamberHeaters'][0] != -1:
                r += showHeater(self.localOM['heat']['chamberHeaters'][0],'chamber')
        # Extruders
        if len(self.localOM['tools']) > 0:
            for tool in self.localOM['tools']:
                if len(tool['heaters']) > 0:
                    r += showHeater(tool['heaters'][0],'e' + str(self.localOM['tools'].index(tool)))
        return r

    def updateCNC(self):
        def showSpindle(name,spindle):
            r = ' | ' + name + ': '
            if self.localOM['spindles'][spindle]['state'] == 'stopped':
                r += 'stopped'
            elif self.localOM['spindles'][spindle]['state'] == 'forward':
                r += 'fwd:' + str(self.localOM['spindles'][spindle]['current']) + 'rpm'
            elif self.localOM['spindles'][spindle]['state'] == 'reverse':
                r += 'rev:' + str(self.localOM['spindles'][spindle]['current']) + 'rpm'
            return r

        # Display spindle state, direction and speed
        r = ''
        if len(self.localOM['tools']) > 0:
            for tool in self.localOM['tools']:
                if tool['spindle'] != -1:
                    r += showSpindle(tool['name'],tool['spindle'])
        return r


    def updateLaser(self):
        # Show laser info; unfortunately not much to show; no seperate laser 'tool'
        if self.localOM['move']['currentMove']['laserPwm'] != None:
            pwm = str(self.localOM['move']['currentMove']['laserPwm'])
        else:
            pwm = 'not configured'
        return ' | laser PWM: ' + pwm
