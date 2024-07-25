from time import sleep_ms,ticks_ms,ticks_diff
from machine import I2C
from ssd1306 import SSD1306_I2C
from sys import path
from config import config
# fonts
path.append('fonts')
from ezFBfont import ezFBfont
import ezFBfont_15_helvB10_ascii as heading
import ezFBfont_13_helvR08_full as heading_sub
import ezFBfont_16_open_iconic_all_2x_full as icons
import ezFBfont_18_helvB14_ascii as message
import ezFBfont_12_spleen_8x16_num as double_minor
import ezFBfont_20_spleen_12x24_num as single_minor
import ezFBfont_20_spleen_16x32_time as double_major
import ezFBfont_40_spleen_32x64_time as single_major

# define some icon chars
C_TOOL = chr(130)
C_BED = chr(168)
C_ENCL = chr(186)
C_STANDBY = chr(235)
C_REFRESH = chr(243)
C_LINK = chr(270)
C_WARN = chr(280)
C_WIFI = chr(281)
C_WRENCH = chr(282)

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

        # demo only?
        self._begin = ticks_ms()
        # internals
        self._active = True
        self._updating = False
        self._show_decimal = {}
        # hardware
        self._initDisplays()
        self._bright(1)
        self._clean()
        self._splash()
        
    def _initDisplays(self):
        i2c0 = I2C(0,sda=config.sda0, scl=config.scl0)
        i2c1 = I2C(1,sda=config.sda1, scl=config.scl1)
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
        d.icons = ezFBfont(d, icons)
        d.message = ezFBfont(d, message)
        d.s_minor = ezFBfont(d, single_minor, valign='baseline')
        d.s_major = ezFBfont(d, single_major, halign='right', valign='baseline')

    def _splash(self):
        # Should scroll a 'clean' screen in?
        self._d0.message.write('PrintPy\n2040', 63, 20, halign='center')
        self._d1.message.write('by\nOwen', 63, 20, halign='center')
        self._show()

    def _waiting(self):
        # some sort of timeout here..
        self._on()
        self._clean()
        self._d0.heading.write('Waiting', 63, 0, halign='center')
        # animate something?
        self._d1.heading.write('...', 63, 0, halign='center')
        self._show()

    def _clean(self, c=0):
        self._d0.fill_rect(0, 0, 128, 64, c)
        self._d1.fill_rect(0, 0, 128, 64, c)
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
        if self._OM['state']["status"] is not 'DEBUG':
            self._on()
            self._clean()
       # Updates the local model, returns the current status text
        if self._OM is None:
            return('no update data available\n')
        r =self._showModel() + '\n'
        if self._OM['state']["status"] is not 'DEBUG':
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
        self._updateStatus()
        self._updateNetwork()
        if self._OM['state']['status'] == 'DEBUG':
            return r
        else:
            self._updateJob()
            if self._OM['state']['machineMode'] == 'FFF':
                self._updateFFF()
            else:
                r += ', Unsupported mode: {}'.format(
                    self._OM['state']['machineMode'])
                # DO SOMETHING HERE TO DISPLAY UNSUPPORTED MODE
        r += self._updateMessages()
        # Return results
        return r

    def _updateStatus(self):
        # common items to always show
        cstate = self._OM['state']["status"]
        cstate = cstate[0].upper() + cstate[1:]
        self._d0.heading.write(cstate, 0, 1)
        
    def _updateNetwork(self):
        if len(self._OM['network']['interfaces']) == 0:
            return
        interface = self._OM['network']['interfaces'][config.net]
        net = '{}: {}'.format(interface['type'],
                             interface['state'])
        if interface['state'] in ['active', 'connected']:
            net = 'ip: {}'.format(interface['actualIP'])
            icon = C_WIFI if interface['type'] == 'wifi' else C_LINK
        elif interface['state'] in ['enabled', 'changingMode', 'establishingLink',
                                    'obtainingIP', 'starting1', 'starting2']:
            icon = C_REFRESH
        elif interface['state'] in ['idle']:
            icon = C_STANDBY
        else:
            icon = C_WARN
        x = 127 if icon is None else 110
        self._d1.heading_sub.write(net, x, 2, halign = 'right')
        self._d1.icons.write(icon, x+2, 0, halign = 'left')

    def _updateJob(self):
        # Job progress
        if self._OM['job']['build']:
            try:
                percent = self._OM['job']['filePosition'] / self._OM['job']['file']['size'] * 100
            except ZeroDivisionError:  # file size can be 0 as the job starts
                percent = 0
            job_line = '{:.1f}'.format(percent)
            self._d0.heading.write(job_line, 120, 0, halign='right')
            self._d0.heading_sub.write('%', 121, 1)
        return

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
        def showHeater(number,name,icon,display):
            if name not in self._show_decimal.keys():
                self._show_decimal[name] = False
            if self._OM['heat']['heaters'][number]['state'] == 'fault':
                display.icons.write(C_WARN, 0, 27)
                display.message.write('{} Fault'.format(name), 21, 29)
            else:
                temp = self._OM['heat']['heaters'][number]['current']
                val =int(temp)
                dec = abs(int((temp - val) * 10))
                if temp >= 100 or temp <= -10:
                    self._show_decimal[name] = False
                elif temp <= 90 and temp >= -9:
                    self._show_decimal[name] = True
                if self._OM['heat']['heaters'][number]['state'] == 'active':
                    target = '{}°'.format(int(self._OM['heat']['heaters'][number]['active']))
                    
                elif self._OM['heat']['heaters'][number]['state'] == 'standby':
                    target = '({}°)'.format(int(self._OM['heat']['heaters'][number]['standby']))
                else:
                    target = ''
                    icon = ''
                    
                # Display data from above
                display.icons.write(icon,2,18)
                display.heading.write(name, 0, 37)
                display.heading_sub.write(target, 0, 50)
                if self._show_decimal[name]:
                    display.s_minor.write('°', 100, 32)
                    display.s_major.write('{}'.format(val), 106, 63)
                    display.s_minor.write('.{:01d}'.format(dec), 104, 63)
                else:
                    display.s_minor.write('°', 119, 32)
                    display.s_major.write('{}'.format(val), 127, 63)

        # Bed
        if len(self._OM['heat']['bedHeaters']) > 0:
            if self._OM['heat']['bedHeaters'][0] != -1:
                showHeater(self._OM['heat']['bedHeaters'][0],
                           'bed', C_BED, self._d1)
        # TODO!: Chamber (Enclosure)
        #if len(self._OM['heat']['chamberHeaters']) > 0:
        #    if self._OM['heat']['chamberHeaters'][0] != -1:
        #        showHeater(self._OM['heat']['chamberHeaters'][0],
        #                   'encl', C_ENCL, self._d1)
        # Extruders
        if len(self._OM['tools']) > 0:
            # FIX to show at max 2 heaters
            for tool in self._OM['tools']:
                if len(tool['heaters']) > 0:
                    showHeater(tool['heaters'][0],
                               'e' + str(self._OM['tools'].index(tool)),
                               C_TOOL, self._d0)
                               #'encl', C_ENCL, self._d0)