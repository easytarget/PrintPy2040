from time import sleep_ms,ticks_ms,ticks_diff
from machine import Pin,I2C
from ssd1306 import SSD1306_I2C
from sys import path
from config import config
# fonts
path.append('fonts')
from ezFBfont import ezFBfont
import ezFBfont_33_helvR24_num
import ezFBfont_16_helvR12_num
import ezFBfont_15_helvB10_ascii as heading
import ezFBfont_13_helvR08_full as heading_sub
import ezFBfont_15_helvR10_ascii as heading_info

'''
    This is a I2C twin 128x64 OLED display out put class for PrintMPY
        It keeps a 'local' OM so that displays can be refreshed
        independently of the main OM update loop
    See the comments in the printPy 'README.md' for more
'''


class outputRRF:
    '''
        arguments:
            log : log file object or None to disable.

        methods:
            update(model) : Updates the local model copy and
                returns a string with the human-readable machine state info.
                Writes to logfile with timestamp if required.
            showStatus(model) : Updates the local model copy and
                returns a 'status' block.
                Aimed at display devices to show extra info when triggered.

        properties:
            omKeys       : see below
            running      : (bool) can be set False if the output device fails
            statusActive : (bool) set True while a status is being displayed
'''

    # ObjectModel keys for each supported mode
    # We will always get the 'state' key from serialOM
    # All other keys need to be specified below
    omKeys = {'FFF':['heat','tools','job','boards','network'],
              'CNC':['spindles','tools','move','job','boards','network'],
              'Laser':['move','job','boards','network']}

    def __init__(self, log=None, net=None):
        self._log = log  # Find a way to use this for display debugging
        self._OM = None
        # If running I2C displays etc this should reflect their status
        self.running = True
        self._counter = 0

        # demo only?
        self._begin = ticks_ms()

        # I2C
        self._initDisplays()
        self._bright(1)
        self._clean()
        self._splash()
        self._active = True
        self._updating = False
        
    def _initDisplays(self):
        i2c0 = I2C(0,sda=Pin(config.I2C0_SDA_PIN), scl=Pin(config.I2C0_SCL_PIN))
        i2c1 = I2C(1,sda=Pin(config.I2C1_SDA_PIN), scl=Pin(config.I2C1_SCL_PIN))
        self._d0 = SSD1306_I2C(128, 64, i2c0, addr=0x3c)
        self._d1 = SSD1306_I2C(128, 64, i2c1, addr=0x3c)
        self._d0.invert(False)
        self._d1.invert(False)
        self._d0.rotate(1)
        self._d1.rotate(1)
        self._fontSetup(self._d0)
        self._fontSetup(self._d1)


    def _fontSetup(self,d):
        d.heading = ezFBfont(d, heading)
        d.heading_sub = ezFBfont(d, heading_sub)
        d.heading_info = ezFBfont(d, heading_info)
        d.tens  = ezFBfont(d, ezFBfont_33_helvR24_num, halign='right', valign='baseline')
        d.units = ezFBfont(d, ezFBfont_16_helvR12_num, valign='baseline')


    def _splash(self):
        # Should scroll a 'clean' screen in?
        self._d0.heading.write('serialOM', 63, 0, halign='center')
        self._d1.heading.write('demo', 63, 0, halign='center')
        self._show()

    def _waiting(self):
        # some sort of timeout here..
        self._on()
        self._clean()
        self._d0.heading.write('Waiting', 63, 0, halign='center')
        # animate something?
        self._d1.heading.write('...', 63, 0, halign='center')
        self._show()

    def _clean(self):
        self._d0.fill_rect(0, 0, 128, 64, 0)
        self._d1.fill_rect(0, 0, 128, 64, 0)
        self._updating = True

    def _on(self):
        if not self._active:
            self._d0.poweron()
            self._d1.poweron()
            self._active = True

    def _off(self):
        if self._active:
            self._d0.poweroff()
            self._d1.poweroff()
            self._active = False

    def _show(self):
        self._d0.show()
        self._d1.show()
        self._updating = False

    def _bright(self,bright):
        bright = int(bright * 255)
        self._d0.contrast(bright)
        self._d1.contrast(bright)
        
    def _dhms(self,t):
        # A local function to provide human readable uptime
        d = int(t / 86400)
        h = int((t / 3600) % 24)
        m = int((t / 60) % 60)
        s = int(t % 60)
        if d > 0:
            days = str(d)  + 'd:'
        else:
            days = ''
        if h > 0 or d > 0:
            hrs = str(h)  + 'h:'
        else:
            hrs = ''
        mins = "%02.f" % m + ':'
        secs = "%02.f" % s
        return days+hrs+mins+secs


    def update(self,model=None):
        # Need to handle failed starts,
        # - Display 'waiting for data' if model=None for more than a set time.
        if model is not None:
            self._OM = model
        if self._OM is None:
            self._waiting()
            return('Initial update data unavailable\n')
        if self._OM['state']["status"] is not 'off':
            self._on()
            self._clean()
       # Updates the local model, returns the current status text
        if self._OM is None:
            return('no update data available\n')
        r =self._showModel() + '\n'
        if self._OM['state']["status"] is not 'off':
            self._show()
        else:
            self._off()
        return r

    '''
        All the routines below tediously walk/grok the OM and return
        a stringlet with the data they find, this is then concatenated
        into a string that is passed back to the caller.
    '''

    def _showModel(self):
        #  Constructs and returns the model data in human-readable form.
        #  copies to outputLog if one is specified


        if self._OM is None:
            # No data == no viable output
            return('No data available')
        # Construct results string
        r = 'up: {}, status: {}'.format(
            self._dhms(self._OM['state']["upTime"]),
            self._OM['state']["status"])
        if self._OM['state']['status'] in ['halted','updating','starting']:
            # placeholder for display splash while starting or updating..
            r += ' | please wait'
            return r
        r += self._updateCommon()
        if self._OM['state']['status'] == 'off':
            return r
        else:
            r += self._updateJob()
            if self._OM['state']['machineMode'] == 'FFF':
                r += self._updateFFF()
            elif self._OM['state']['machineMode']  == 'CNC':
                r += self._updateAxes()
                r += self._updateCNC()
            elif self._OM['state']['machineMode']  == 'Laser':
                r += self._updateAxes()
                r += self._updateLaser()
        r += self._updateMessages()
        # Return results
        return r

    def _updateCommon(self):
        # common items to always show
        cstate = self._OM['state']["status"]
        cstate = cstate[0].upper() + cstate[1:]
        if len(cstate) < 8:
            status_line = ' ' + cstate
        else:
            status_line = cstate
        self._d0.heading.write(status_line, 0, 0)
        
        if len(self._OM['network']['interfaces']) > 0:
            interface = self._OM['network']['interfaces'][0]
            if interface['state'] != 'active':
                net = 'ip: {}'.format(interface['state'])
            else:
                net = 'ip: {}'.format(interface['actualIP'])
        else:
            net = ''

        if self._OM['state']['displayMessage']:
            info_line = self._OM['state']['displayMessage']
        #elif self._counter == 0:
        #    self._counter = 1
        #    info_line = 'up: {}'.format(self._dhms(self._OM['state']["upTime"]))
        else:
            #self._counter = 0 
            info_line = net if len(net) > 0 else ''

        self._d1.heading_info.write(info_line, 127, 0, halign = 'right')
        return ', ' + net

    def _updateJob(self):
        # Job progress
        r = ''
        if self._OM['job']['build']:
            try:
                percent = self._OM['job']['filePosition'] / self._OM['job']['file']['size'] * 100
            except ZeroDivisionError:  # file size can be 0 as the job starts
                percent = 0
            job_line = '{:.1f}'.format(percent)
            self._d0.heading.write(job_line, 120, 0, halign='right')
            self._d0.heading_sub.write('%', 121, 1)
        return r

    def _updateAxes(self):
        # Display all configured axes values (workplace and machine), plus state.
        ws = self._OM['move']['workplaceNumber']
        r = ' | axes: '
        m = ''      # machine pos
        offset = False   # is the workspace offset from machine co-ordinates?
        homed = False   # are any of the axes homed?
        if self._OM['move']['axes']:
            for axis in self._OM['move']['axes']:
                if axis['visible']:
                    if axis['homed']:
                        homed = True
                        r += ' ' + axis['letter'] + ':' + "%.2f" % (axis['machinePosition'] - axis['workplaceOffsets'][ws])
                        m += ' ' + "%.2f" % (axis['machinePosition'])
                        if axis['workplaceOffsets'][ws] != 0:
                            offset = True
                    else:
                        r += ' ' + axis['letter'] + ':?'
                        m += ' ?'
            if homed:
                # Show which workspace we have selected when homed
                r += ' (' + str(ws + 1) + ')'
            if offset:
                # Show machine position if workspace is offset
                r += '(' + m[1:] + ')'
        return r

    def _updateMessages(self):
        # M117 messages
        r = ''
        if self._OM['state']['displayMessage']:
            r += ' | message: ' +  self._OM['state']['displayMessage']
        # M291 messages
        if self._OM['state']['messageBox']:
            if self._OM['state']['messageBox']['mode'] == 0:
                r += ' | info: '
            else:
                r += ' | query: '
            if self._OM['state']['messageBox']['title']:
                r += '== ' + self._OM['state']['messageBox']['title'] + ' == '
            r += self._OM['state']['messageBox']['message']
        return r

    def _updateFFF(self):
        # a local function to return state and temperature details for a heater
        def showHeater(number,name,display):
            r = ''
            if self._OM['heat']['heaters'][number]['state'] == 'fault':
                r += ' | ' + name + ': FAULT'
            else:
                temp = self._OM['heat']['heaters'][number]['current']
                units=int(temp)
                dec = int((temp - units) * 10)
                if self._OM['heat']['heaters'][number]['state'] == 'active':
                    target = ' {}°'.format(int(self._OM['heat']['heaters'][number]['active']))
                elif self._OM['heat']['heaters'][number]['state'] == 'standby':
                    target = '({}°)'.format(int(self._OM['heat']['heaters'][number]['standby']))
                else:
                    target = ' off'
                display.heading.write(name, 0, 24)
                display.heading_sub.write(target, 0, 38)
                display.tens.write('{}.'.format(units), 106, 48)
                display.tens.write('°', 106, 48, tkey=0, halign='center')
                display.units.write(' {:01d}'.format(dec), 106, 48)
            return r

        r = ''
        # For FFF mode we want to show all the Heater states
        # Bed
        if len(self._OM['heat']['bedHeaters']) > 0:
            if self._OM['heat']['bedHeaters'][0] != -1:
                r += showHeater(self._OM['heat']['bedHeaters'][0],
                                'bed', self._d1)
        # Chamber
        if len(self._OM['heat']['chamberHeaters']) > 0:
            if self._OM['heat']['chamberHeaters'][0] != -1:
                r += showHeater(self._OM['heat']['chamberHeaters'][0],
                                'chamber')
        # Extruders
        if len(self._OM['tools']) > 0:
            for tool in self._OM['tools']:
                if len(tool['heaters']) > 0:
                    r += showHeater(tool['heaters'][0],
                                    'E' + str(self._OM['tools'].index(tool)),
                                    self._d0)
        #display
        return r

    def _updateCNC(self):
        # a local function to return spindle name + state, direction and speed
        def showSpindle(name,spindle):
            r = ' | ' + name + ': '
            if self._OM['spindles'][spindle]['state'] == 'stopped':
                r += 'stopped'
            elif self._OM['spindles'][spindle]['state'] == 'forward':
                r += '+' + str(self._OM['spindles'][spindle]['current'])
            elif self._OM['spindles'][spindle]['state'] == 'reverse':
                r += '-' + str(self._OM['spindles'][spindle]['current'])
            return r

        # Show details for all configured spindles
        r = ''
        if len(self._OM['tools']) > 0:
            for tool in self._OM['tools']:
                if tool['spindle'] != -1:
                    r += showSpindle(tool['name'],tool['spindle'])
        if len(r) == 0:
            r += ' | spindle: not configured'
        return r

    def _updateLaser(self):
        # Show laser info; not much to show since there is no seperate laser 'tool' (yet)
        if self._OM['move']['currentMove']['laserPwm'] is not None:
            pwm = '%.0f%%' % (self._OM['move']['currentMove']['laserPwm'] * 100)
        else:
            pwm = 'not configured'
        return ' | laser: ' + pwm
