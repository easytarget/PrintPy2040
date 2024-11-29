from time import sleep_ms,ticks_ms,ticks_diff
from ssd1306 import SSD1306_I2C
from framebuf import FrameBuffer, MONO_VLSB
from sys import path
from config import config
from machine import Timer
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
C_BOLT = chr(96)
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
            None

        methods:
            update(model) : Updates the local model copy and
                returns a string with the human-readable machine state info.
                Writes to logfile with timestamp if required.
            showStatus(model) : Updates the local model copy and
                returns a 'status' block.
                Aimed at display devices to show extra info when triggered.

        properties:
            omKeys  : see below
            running : (bool) set False if the output device fails
            standby : (bool) set True when the display is off
'''

    # ObjectModel keys for each supported mode
    # We will always get the 'state' key from serialOM
    # All other keys need to be specified below
    #omKeys = {'FFF':['heat','tools','job','boards','network'],
    omKeys = {'FFF':['heat','tools','job','network'],
              'CNC':['network'],
              'Laser':['network']}

    def __init__(self):
        self.standby = True
        # internals
        self._OM = None
        self._pause = False
        self._lastOut = ''
        self._updating = False
        self._message = ''
        self._marquee = None
        self._show_decimal = {}
        self._failcount = 0
        # hardware
        self._initDisplays()
        self._bright(config.display_bright)
        self._clean()
        self._animate()
        self.running = True

    def _initDisplays(self):
        self._left = SSD1306_I2C(128, 64, config.I2C_left, addr=0x3c)
        self._right = SSD1306_I2C(128, 64, config.I2C_right, addr=0x3c)
        self._left.invert(config.display_invert)
        self._right.invert(config.display_invert)
        self._left.rotate(config.display_rotate)
        self._right.rotate(config.display_rotate)
        self._fontSetup(self._left)
        self._fontSetup(self._right)

    def _fontSetup(self, d):
        d.heading = ezFBfont(d, heading)
        d.heading_sub = ezFBfont(d, heading_sub)
        d.icons = ezFBfont(d, icons)
        d.message = ezFBfont(d, message)
        d.s_major = ezFBfont(d, single_major, halign='right', valign='baseline')
        d.s_minor = ezFBfont(d, single_minor, valign='baseline')
        d.d_major = ezFBfont(d, double_major, halign='right', valign='baseline')
        d.d_minor = ezFBfont(d, double_minor, valign='baseline')

    def _animate(self):
        # Callback function
        def frame(t):
            if self._pause:
                return
            if self._OM is None:
                return
            print('timer.start....',end='')
            self._clean()
            self._lastOut = self._showModel()
            if self._marquee is not None:
                # step marquee and add a pause whenever it rolls over
                if self._marquee.step(2):
                    self._marquee.pause(20)
            print('timer.end ',end='')
            self._show()

        # Start the marquee timer, update 5 times a second
        #self._timer = Timer()
        #self._timer.init(period=200, mode=Timer.PERIODIC, callback=show)
        Timer(period=400, mode=Timer.PERIODIC, callback=frame)

    def _bright(self, bright):
        bright = int(bright * 255)
        self._left.contrast(bright)
        self._right.contrast(bright)

    def _clean(self, c=0):
        self._left.fill_rect(0, 0, 128, 64, c)
        self._right.fill_rect(0, 0, 128, 64, c)

    def _show(self):
        self._left.show()
        self._right.show()

    def _swipeOff(self):
        self._pause = True
        s = 16
        for x in range(0, 129, 8):
            self._left.scroll(s, 0)
            self._left.rect(0, 0, s, 64, 0, True)
            self._right.scroll(-s, 0)
            self._right.rect(128 - s, 0, s, 64, 0, True)
            self._show()
        self._pause = False

    def _swipeOn(self):
        self._pause = True
        s = 16
        lfb = FrameBuffer(bytearray(16 * 64), 128, 64, MONO_VLSB)
        rfb = FrameBuffer(bytearray(16 * 64), 128, 64, MONO_VLSB)
        lfb.blit(self._left,0,0)
        rfb.blit(self._right,0,0)
        self._clean()
        for x in range(0, 129, s):
            self._left.blit(lfb, 128 - x, 0)
            self._right.blit(rfb, -128 + x, 0)
            self._show()
        del(lfb,rfb)
        self._pause = False

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

    def on(self):
        if self.standby:
            self._left.poweron()
            self._right.poweron()
            self._swipeOn()
            self.standby = False
        else:
            self._show()

    def off(self):
        if not self.standby:
            self._swipeOff()
            self._left.poweroff()
            self._right.poweroff()
            self.standby = True

    def splash(self):
        self.showText('PrintPy\n2040', 'by Owen    ')
        self._right.heading.write('easytarget.org', 0, 36)

    def showText(self, left, right):
        self._clean()
        self._left.message.write(left, 63, 16, halign='center')
        self._right.message.write(right, 63, 16, halign='center')

    def update(self, model):
        self._updating = True
        # TODO: Need to test and handle failed starts,
        # TODO: Display 'waiting for data' if model=None for more than a set time.
        if model is None:
            self._failcount += 1
            if self._failcount > config.failcount:
                self.showText('no\nresponse','retrying\n...')
                # TODO: show a fail counter..
                self._show()
                self._updating = False
                return('update data unavailable\n')
        else:
            self._failcount = 0
            self._OM = model
        if self._OM is None:
            self._updating = False
            return('initial update data unavailable\n')
        show = not self._OM['state']["status"] in config.offstates
        if show:
            self.on()
        self._clean()
        r = self._showModel() + '\n'
        if show:
            self._show()
        else:
            self.off()
        self._updating = False
        return r

    def updateNG(self, model):
        if model is None:
            self._failcount += 1
            if self._failcount > config.failcount:
                self.showText('no\nresponse','retrying\n...')
                # TODO: show a fail counter..
                self._show()
                self._updating = False
                return('update data unavailable\n')
        else:
            self._failcount = 0

        # Update the local model
        self._OM = model

        # Turn screen on/off as needed
        show = not self._OM['state']["status"] in config.offstates
        if show:
            self.on()
        else:
            self.off()
            
        # Return the last generated status line
        return self._lastOut + '\n'

    '''
        All the routines below tediously walk/grok the OM update the
        display as appropriate and return a stringlet with the data
        they find, this is then concatenated into a string that is
        passed back to the caller.
    '''

    def _showModel(self):
        #  Constructs and returns the model data in human-readable form.
        #  returns a text summary of status
        if self._OM is None:
            # No data == no viable output
            return('No data available')
        # Construct results string
        r = 'Up: {}'.format(self._dhms(self._OM['state']["upTime"]))
        if self._OM['state']['status'] in ['halted','updating','starting']:
            # placeholder for display splash while starting or updating..
            r += ' | please wait'
            return r
        r += self._showStatus()
        r += self._showJob()
        if self._OM['state']['machineMode'] == 'FFF':
            self._showFFF()
        else:
            mode = self._OM['state']['machineMode']
            r += ', Unsupported mode: {}'.format(mode)
            self.showText('\'{}\'\nmode'.format(mode), 'not\nsupported')
        m = self._showMessages()
        r += self._showNetwork()
        # Return results
        return r + m

    def _showStatus(self):
        # common items to always show
        cstate = self._OM['state']["status"]
        cstate = cstate[0].upper() + cstate[1:]
        if cstate == 'Simulating':
            cstate = 'Processing'
        self._left.heading.write(cstate, 0, 1)
        return ' | {}'.format(cstate)

    def _showNetwork(self):
        if config.net is None:
            return ''
        if len(self._OM['network']['interfaces']) == 0:
            return ' | Offline'
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
        self._right.icons.write(icon, 112, 0, halign = 'left')
        if self._message == '':
            # only show detailed network info when no messages are displaying
            self._right.heading_sub.write(net, 110, 3, halign = 'right')
        return ' | {}'.format(net)

    def _showJob(self):
        # Job progress
        if self._OM['job']['build']:
            try:
                percent = self._OM['job']['filePosition'] / self._OM['job']['file']['size'] * 100
            except ZeroDivisionError:  # file size might be 0 as the job starts
                percent = 0
            job_line = ' {:.1f}'.format(percent) if percent < 100 else '100'
            self._left.d_minor.write(job_line, 120, 12, halign='right')
            #self._left.heading.write(job_line, 120, 0, halign='right')
            self._left.heading_sub.write('%', 121, 2)
            return ' | Job: {}%'.format(job_line)
        return ''

    def _showMessages(self):
        # M117 messages
        r = ''
        self._message = self._OM['state']['displayMessage']
        if self._message != '':
            r += ' | message: ' +  self._message
            self._right.heading.write(self._message, 0, 0)
            # Set up Marquee
        #else:
            # stop Marquee
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

    def _showFFF(self):
        # a local function to return state and temperature details for a heater
        def showHeater(number, name, icon, display, position):
            if name not in self._show_decimal.keys():
                self._show_decimal[name] = False
            if self._OM['heat']['heaters'][number]['state'] == 'fault':
                panelfault(name, display, position)
                return
            else:
                temp = self._OM['heat']['heaters'][number]['current']
                val =int(temp)
                dec = abs(int((temp - val) * 10))
                # Note the following, it builds hysterisys into turning decimal display on/off
                if temp >= 100 or temp <= -10:
                    self._show_decimal[name] = False
                elif temp <= 90 and temp >= -9:
                    self._show_decimal[name] = True
                if self._OM['heat']['heaters'][number]['state'] == 'active':
                    target = '{}°'.format(int(self._OM['heat']['heaters'][number]['active']))
                elif self._OM['heat']['heaters'][number]['state'] == 'standby':
                    target = '({}°)'.format(int(self._OM['heat']['heaters'][number]['standby']))
                    icon = ''
                else:  # heater is off
                    target = ''
                    icon = ''
            # Display in correct position
            if position == 'full':
                panelfull(name, icon, target, val, dec, display)
            elif position == 'upper':
                panelhalf(name, icon, target, val, dec, display,0)
            elif position == 'lower':
                panelhalf(name, icon, target, val, dec, display,1)

        def panelfull(name, icon, target, val, dec, display):
                # Full panel heater display
                display.heading.write(name, 0, 16)
                display.icons.write(icon,2,48)
                display.heading_sub.write(target, 0, 30)
                if self._show_decimal[name]:
                    display.s_minor.write('°', 102, 32)
                    display.s_major.write('{}'.format(val), 106, 61)
                    display.s_minor.write('.{:01d}'.format(dec), 104, 61)
                else:
                    display.s_minor.write('°', 119, 31)
                    display.s_major.write('{}'.format(val), 127, 61)

        def panelhalf(name, icon, target, val, dec, display, pos):
                # Half panel heater display
                y = 16 if pos == 0 else 40
                display.heading.write(name, 0, y)
                display.icons.write(icon, 38, y + 4)
                display.heading_sub.write(target, 2, y + 12)
                #display.text(target.replace('°',''), 0, y+14)
                if self._show_decimal[name]:
                    display.d_minor.write('°', 108, y + 10)
                    display.d_major.write('{}'.format(val), 108, y + 19)
                    display.d_minor.write('.{:01d}'.format(dec), 108, y + 19)
                else:
                    display.d_minor.write('°', 121, y + 10)
                    display.d_major.write('{}'.format(val), 121, y + 19)


        def panelfault(name, display, position):
                # Display 'fault!' in a heater panel
                if position == 'upper':
                    display.icons.write(C_BOLT, 0, 18)
                    display.message.write('{} FAULT'.format(name), 18, 18)
                elif position == 'lower':
                    display.icons.write(C_BOLT, 0, 42)
                    display.message.write('{} FAULT'.format(name), 18, 42)
                else:
                    display.icons.write(C_BOLT, 0, 30)
                    display.message.write('{}'.format(name), 21, 22)
                    display.message.write('FAULT', 21, 42)

        extruders = []
        heaters = []
        # Extruders (tools)
        if len(self._OM['tools']) > 0:
            for tool in self._OM['tools']:
                if len(tool['heaters']) > 0:
                    # only record the first heater for each tool
                    extruders.append((tool['heaters'][0],
                                      'E' + str(self._OM['tools'].index(tool)), C_TOOL))
        # Bed and Chamber, only take first of each!
        if len(self._OM['heat']['bedHeaters']) > 0:
            if self._OM['heat']['bedHeaters'][0] != -1:
                heaters.append((self._OM['heat']['bedHeaters'][0], 'bed', C_BED))
        if len(self._OM['heat']['chamberHeaters']) > 0:
            if self._OM['heat']['chamberHeaters'][0] != -1:
                heaters.append((self._OM['heat']['chamberHeaters'][0], 'enc', C_ENCL))

        # This is how to add fake devices for testing multi-panel stuff..
        #extruders.append((extruders[0][0],'E1',C_TOOL))
        #heaters.append((heaters[0][0],'encl',C_ENCL))

        # Display extruder heaters (max 2)
        if len(extruders) == 0:
            self._left.icons.write(C_WARN, 64, 18, halign='center')
            self._left.message.write('no extruders?', 64, 38, halign='center')
        if len(extruders) == 1:
            showHeater(*extruders[0], self._left, 'full')
        if len(extruders) >= 2:
            showHeater(*extruders[0], self._left, 'upper')
            showHeater(*extruders[1], self._left, 'lower')

        # Display bed and chamber heaters
        if len(heaters) == 0:
            self._right.icons.write(C_WARN, 64, 18, halign='center')
            self._right.message.write('no heaters?', 64, 38, halign='center')
        if len(heaters) == 1:
            showHeater(*heaters[0], self._right, 'full')
        if len(heaters) >= 2:
            showHeater(*heaters[0], self._right, 'upper')
            showHeater(*heaters[1], self._right, 'lower')
