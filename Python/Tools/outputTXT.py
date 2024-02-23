from time import time

'''
    This is a TEXT (REPL/console) output class for logRRF
    It will later be adapted for I2C displays etc
'''

# These are the only key sets in the OM we are interested in
# We will always get the 'state' key at the start of the loop
# All other keys need to be specified below

class outputRRF:
    # ObjectModel keys for each supported mode
    omKeys = {'FFF':['heat','tools','job','boards','network'],
              'CNC':['spindles','tools','move','job','boards','network'],
            'Laser':['move','job','boards','network']}

    def __init__(self, initialOM, log=None):
        self.localOM = initialOM
        self.log = log
        print('output is starting')

    def updateOutput(self):
        # A local function to provide human readable uptime
        def dhms(t):
            d = int(t / 86400)
            h = int((t / 3600) % 24)
            m = int((t / 60) % 60)
            s = int(t % 60)
            if d > 0:
                days = str(d)  + ':'
            else:
                days = ''
            if h > 0 or d > 0:
                hrs = str(h)  + ':'
            else:
                hrs = ''
            mins = "%02.f" % m + ':'
            secs = "%02.f" % s
            return days+hrs+mins+secs

        # Construct results string
        r = 'status: ' + self.localOM['state']['status']
        r += ' | uptime: ' + dhms(self.localOM['state']['upTime'])
        if self.localOM['state']['status'] in ['updating','starting']:
            # placeholder for display splash while starting or updating..
            r += ' | please wait'
            return r
        r += self._updateCommon()
        if self.localOM['state']['status'] == 'off':
            pass   # Placeholder for display off code etc..
        else:
            r += self._updateJob()
            if self.localOM['state']['machineMode'] == 'FFF':
                r += self._updateFFF()
            elif self.localOM['state']['machineMode']  == 'CNC':
                r += self._updateAxes()
                r += self._updateCNC()
            elif self.localOM['state']['machineMode']  == 'Laser':
                r += self._updateAxes()
                r += self._updateLaser()
        r += self._updateMessages()
        # Return results
        if self.log:
            self.log.write('[' + str(int(time())) + '] ' + r + '\n')
        return r

    def _updateCommon(self):
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

    def _updateJob(self):
        # Job progress
        r = ''
        if self.localOM['job']['build']:
            try:
                percent = self.localOM['job']['filePosition'] / self.localOM['job']['file']['size'] * 100
            except ZeroDivisionError:  # file size can be 0 as the job starts
                percent = 0
            r += ' | progress: ' + "%.1f%%" % percent
        return r

    def _updateAxes(self):
        # Display all configured axes workplace and machine position, plus state.
        ws = self.localOM['move']['workplaceNumber']
        r = ' | axes: W' + str(ws + 1)
        m = ''      # machine pos
        offset = False   # workspace offset from Machine Pos?
        if self.localOM['move']['axes']:
            for axis in self.localOM['move']['axes']:
                if axis['visible']:
                    if axis['homed']:
                       r += ' ' + axis['letter'] + ':' + "%.2f" % (axis['machinePosition'] - axis['workplaceOffsets'][ws])
                       m += ' ' + "%.2f" % (axis['machinePosition'])
                       if axis['workplaceOffsets'][ws] != 0:
                           offset = True
                    else:
                       r += ' ' + axis['letter'] + ':?'
                       m += ' ?'
            if offset:
                r += ' (' + m[1:] + ')'
        return r

    def _updateMessages(self):
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

    def _updateFFF(self):
        # a local function to return state and temperature details for a heater
        def showHeater(number,name):
            r = ''
            if self.localOM['heat']['heaters'][number]['state'] == 'fault':
                r += ' | ' + name + ': FAULT'
            else:
                r += ' | ' + name + ': ' + '%.1f' % self.localOM['heat']['heaters'][number]['current']
                if self.localOM['heat']['heaters'][number]['state'] == 'active':
                    r += ' (%.1f)' % self.localOM['heat']['heaters'][number]['active']
                elif self.localOM['heat']['heaters'][number]['state'] == 'standby':
                    r += ' (%.1f)' % self.localOM['heat']['heaters'][number]['standby']
            return r

        r = ''
        # For FFF mode we want to show all the Heater states
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

    def _updateCNC(self):
        # a local function to return spindle name + state, direction and speed
        def showSpindle(name,spindle):
            r = ' | ' + name + ': '
            if self.localOM['spindles'][spindle]['state'] == 'stopped':
                r += 'stopped'
            elif self.localOM['spindles'][spindle]['state'] == 'forward':
                r += '+' + str(self.localOM['spindles'][spindle]['current'])
            elif self.localOM['spindles'][spindle]['state'] == 'reverse':
                r += '-' + str(self.localOM['spindles'][spindle]['current'])
            return r

        # Show details for all configured spindles
        r = ''
        if len(self.localOM['tools']) > 0:
            for tool in self.localOM['tools']:
                if tool['spindle'] != -1:
                    r += showSpindle(tool['name'],tool['spindle'])
        return r

    def _updateLaser(self):
        # Show laser info; not much to show since there is no seperate laser 'tool' (yet)
        if self.localOM['move']['currentMove']['laserPwm'] != None:
            pwm = '%.0f%%' % (self.localOM['move']['currentMove']['laserPwm'] * 100)
        else:
            pwm = 'not configured'
        return ' | laser: ' + pwm
