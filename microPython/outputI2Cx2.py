from time import sleep_ms, ticks_ms, ticks_diff
from ssd1306 import SSD1306_I2C
from framebuf import FrameBuffer, MONO_VLSB
from sys import path
from config import config
import _thread
from gc import collect
# fonts
path.append('fonts')
from ezFBfont import ezFBfont
from ezFBmarquee import ezFBmarquee
import ezFBfont_helvB10_ascii_15 as heading
import ezFBfont_helvR08_ascii_11 as subhead
import ezFBfont_open_iconic_all_2x_0x0_0xFFF_16 as icons
import ezFBfont_helvB14_ascii_18 as message
import ezFBfont_spleen_6x12_num_10 as target
import ezFBfont_spleen_8x16_num_12 as double_minor
import ezFBfont_spleen_12x24_num_20 as single_minor
import ezFBfont_spleen_16x32_time_20 as double_major
import ezFBfont_spleen_32x64_time_40 as single_major

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

    Note: We use a seperate pair of 'Panel' framebuffers to draw the model
        data onto whenever we get an update.
        This is then blitted onto the display framebuffers when it changes
        and, with the marquee message panel, displayed by a fast animation
        loop running on the second CPU
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
    # CNC and Laser mode are not supported..but these are the
    # keys you would probably need (at present)
    omKeys = {'FFF':['heat','tools','job','network'],
              'CNC':['job','move','spindles','network'],
              'Laser':['job','move','network']}

    def __init__(self):
        self.standby = True
        # internals
        self._OM = None
        self.running = False
        self.watchdog = ticks_ms() + 10000
        self._state = ''
        self._message = ''
        self._panels_updated = False
        self._show_decimal = {}
        self._fail_count = 0
        self._off_timer = ticks_ms() config.off_time
        self._notify = False
        # Init hardware
        self._initDisplays()
        # Marquee
        self._status_string = ''
        self._marquee = ezFBmarquee(self._left, heading, pause=config.marquee_pause)
        # Threading lock for display
        self._display_lock = _thread.allocate_lock()
        # Spare framebuffers used for on/off slide animation
        self._lbuf = FrameBuffer(bytearray(16 * 64), 128, 64, MONO_VLSB)
        self._rbuf = FrameBuffer(bytearray(16 * 64), 128, 64, MONO_VLSB)
        # Panel framebuffers used for updating without locking display
        self._tpanel = FrameBuffer(bytearray(16 * 16), 128, 16, MONO_VLSB)
        self._lpanel = FrameBuffer(bytearray(16 * 48), 128, 48, MONO_VLSB)
        self._rpanel = FrameBuffer(bytearray(16 * 48), 128, 48, MONO_VLSB)
        # Init Panels
        self._initPanels()
        # set the 'so far, so good' flag.
        self.running = True

    def _initDisplays(self):
        def fonts(d):
            return {
                'heading' : ezFBfont(d, heading),
                'message' : ezFBfont(d, message, vgap=2),
                }
        self._left = SSD1306_I2C(128, 64, config.I2C_left, addr=0x3c)
        self._right = SSD1306_I2C(128, 64, config.I2C_right, addr=0x3c)
        self._left.invert(config.display_invert)
        self._right.invert(config.display_invert)
        self._left.rotate(config.display_rotate)
        self._right.rotate(config.display_rotate)
        self._bright(config.display_bright)
        self._clean()
        self._left_fonts = fonts(self._left)
        self._right_fonts = fonts(self._right)

    def _initPanels(self):
        def fonts(d):
            return {
                'heading' : ezFBfont(d, heading),
                'subhead' : ezFBfont(d, subhead),
                'icons'   : ezFBfont(d, icons),
                'message' : ezFBfont(d, message, vgap=2),
                'target' : ezFBfont(d, target, tkey=0),
                's_major' : ezFBfont(d, single_major, halign='right', valign='baseline', tkey=0),
                's_minor' : ezFBfont(d, single_minor, valign='baseline', tkey=0),
                'd_major' : ezFBfont(d, double_major, halign='right', valign='baseline', tkey=0),
                'd_minor' : ezFBfont(d, double_minor, valign='baseline', tkey=0),
                }
        self._clean()
        self._tpanel_fonts = fonts(self._tpanel)
        self._lpanel_fonts = fonts(self._lpanel)
        self._rpanel_fonts = fonts(self._rpanel)

    def _dhms(self, t):
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
        return days + hrs + mins + secs

    def _show(self):
        self._left.show()
        self._right.show()

    def _powerOn(self):
        self._left.poweron()
        self._right.poweron()

    def _powerOff(self):
        self._left.poweroff()
        self._right.poweroff()

    def _bright(self, bright):
        bright = int(bright * 255)
        self._left.contrast(bright)
        self._right.contrast(bright)

    def _clean(self, c=0):
        self._left.fill(c)
        self._right.fill(c)

    def _cleanPanels(self):
        self._tpanel.fill(0)
        self._lpanel.fill(0)
        self._rpanel.fill(0)

    def _swipeOn(self):
        with self._display_lock:
            self._powerOn()
            s = 16
            self._lbuf.blit(self._left,0,0)
            self._rbuf.blit(self._right,0,0)
            self._clean()
            for x in range(0, 129, s):
                self._left.blit(self._lbuf, 128 - x, 0)
                self._right.blit(self._rbuf, -128 + x, 0)
                self._show()

    def _swipeOff(self):
        with self._display_lock:
            s = 16
            for x in range(0, 129, 8):
                self._left.scroll(s, 0)
                self._left.rect(0, 0, s, 64, 0, True)
                self._right.scroll(-s, 0)
                self._right.rect(128 - s, 0, s, 64, 0, True)
                self._show()
            self._powerOff()

    def _awakeOnOff(self):
        if not self._OM['state']["status"] in config.off_states:
            self.awake()
        if ticks_diff(ticks_ms(), self._off_timer) < :
            self.on()
        else:
            self.off()

    def _runMarquee(self):
        def panels():
            '''
                Run by the animation loop (in a seperate thread on second CPU)
                - blits the contents of the update panels onto the main display
            '''
            if self._panels_updated:
                self._left.blit(self._lpanel,0,16)
                self._right.blit(self._rpanel,0,16)
                self._right.blit(self._tpanel,0,0)
                self._panels_updated = False

        def frame():
            '''
                Run by animator loop
                - Follows the contents of self._status_string
                - Step animates the status and message marquee
            '''
            if self._marquee.string != self._status_string:
                self.awake()
                self._marquee.start(self._status_string)
            if self._marquee.step(config.marquee_step):
                self._marquee.pause(config.marquee_pause)

        def notify():
            '''
                Flashes the display inverse briefly to acknowlege button.
                - invert() is instant, you do not need to call show()
            '''
            if self._notify:
                self._notify = False
                self._left.invert(not config.display_invert)
                self._right.invert(not config.display_invert)
                sleep_ms(50)
                self._left.invert(config.display_invert)
                self._right.invert(config.display_invert)

        # Start the animation loop
        '''
            Runs continually on the second CPU core; handles the marquee and
            notifications.
            Has a watchdog to ensure it dies after the main thread.
        '''
        while self.watchdog > ticks_ms():
            nextFrame = ticks_ms() + config.animation_interval
            with self._display_lock:
                panels()
                frame()
                self._show()
                notify()
            while ticks_ms() < nextFrame:
                sleep_ms(1)
        self.running = False
        print('Animator exiting due to watchdog')

    def animator(self):
        return _thread.start_new_thread(self._runMarquee, ())

    def on(self, force = False):
        if self.standby or force:
            self._swipeOn()
            self.standby = False

    def off(self):
        if not self.standby:
            self._swipeOff()
            self.standby = True

    def awake(self, ontime=config.off_time):
        self._off_time = max(self._off_time, ticks_ms() + ontime)

    def alert(self):
        # Request a notification 'flash' from the marquee animation loop
        self._notify = True

    def splash(self):
        self._clean()
        self._left_fonts['message'].write('PrintPy\n2040', 63, 16, halign='center')
        self._right_fonts['message'].write('by Owen    ', 63, 16, halign='center')
        self._right_fonts['heading'].write('easytarget.org', 0, 36)
        self.on(True)

    def showError(self, ltext, rtext):
        with self._display_lock:
            self._clean()
            self._left_fonts['message'].write(ltext, 63, 16, halign='center')
            self._right_fonts['message'].write(rtext, 63, 16, halign='center')
            self._powerOn()
            self._show()

    def updateFail(self, count):
        ptext = 'Attempt: {:g}'.format(count)
        htext = ' Error: Cannot communicate with controller; check that it '
        htext += 'is running correctly; and that all wiring is secure.'
        if self._marquee.string != htext:
            self._status_string = htext
        self._cleanPanels()
        self._tpanel_fonts['subhead'].write(ptext, 63, 2, halign = 'center')
        self._lpanel_fonts['message'].write('Connection', 63, 8, halign='center')
        self._rpanel_fonts['message'].write('Failed', 63, 8, halign='center')
        self._panels_updated = True
        # Turn screen on when first called
        if count == config.fail_count:
            self._clean()
            self.awake(config.long_awake)        # ?????????????
        self._awakeOnOff()

    def updatePanels(self, model):
        # Update the local model
        self._OM = model
        # Put the model data on panels
        out = self._putModel()
        self._panels_updated = True
        # Set the string for the marquee
        self._status_string = self._state + self._message
        # Turn screen on/off as needed
        self._awakeOnOff()
        # Return the last generated status line
        return out + '\n'

    '''
        All the routines below tediously walk/grok the OM and update the
        display panel framebuffer(s) for later display by the animation loop.
        Also returns a status string for logging or REPL output
    '''

    def _putModel(self):
        #  Constructs the twin-panel model status display
        #  and puts it on the panel framebuffers
        #  - also returns a text summary of status
        if self._OM is None:
            # No data == no viable output
            return('No data available')
        # clean the panel display area
        self._cleanPanels()
        # Construct panels and the results string
        r = 'Up: {}'.format(self._dhms(self._OM['state']["upTime"]))
        r += self._putStatus()
        if self._state in ['Halted','Updating','Starting']:
            return r   # Nothing to output, model may be incomplete
        r += self._putJob()
        if self._OM['state']['machineMode'] == 'FFF':
            self._putFFF()
        else:
            mode = self._OM['state']['machineMode']
            self._lpanel_fonts['message'].write('\'{}\'\nmode'.format(mode), 63, 6, halign='center')
            self._rpanel_fonts['message'].write('not yet\nsupported', 63, 6, halign='center')
            r += ', Unsupported mode: {}'.format(mode)
        m = self._putMessages()
        r += self._putNetwork()
        # return the console text line
        return r + m

    def _putStatus(self):
        state = self._OM['state']["status"]
        self._state = state[0].upper() + state[1:]
        return ' | {}'.format(self._state)

    def _putMessages(self):
        # M117 messages
        msg = self._OM['state']['displayMessage']
        r = '' if msg == '' else ' | {}'.format(msg)
        # M291 messages
        inf = ''
        if self._OM['state']['messageBox']:
            if self._OM['state']['messageBox']['title']:
                inf += '=' + self._OM['state']['messageBox']['title'] + '= '
            inf += self._OM['state']['messageBox']['message']
        r += '' if inf == '' else ' | {}'.format(inf)
        self._message = r.replace('|',':')
        return r

    def _putNetwork(self):
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
        self._tpanel_fonts['icons'].write(icon, 112, 0, halign = 'left')
        if not self._OM['job']['build']:
            self._tpanel_fonts['subhead'].write(net, 108, 2, halign = 'right')
        return ' | {}'.format(net)

    def _putJob(self):
        # Job progress
        if self._OM['job']['build']:
            try:
                percent = self._OM['job']['filePosition'] / self._OM['job']['file']['size'] * 100
            except ZeroDivisionError:  # file size can be reported as Zero during job start
                percent = 0
            job_line = '{:.1f}'.format(percent) if percent < 100 else '100'
            xoff, _ = self._tpanel_fonts['s_minor'].size(job_line)
            self._tpanel_fonts['s_minor'].write(job_line, 0, 14)
            self._tpanel_fonts['heading'].write('%', xoff+2, 4)
            return ' | Job: {}%'.format(job_line)
        return ''

    def _putFFF(self):
        # a local function to return state and temperature details for a heater
        def showHeater(number, name, icon, display, position):
            if name not in self._show_decimal.keys():
                self._show_decimal[name] = False
            if self._OM['heat']['heaters'][number]['state'] == 'fault':
                panelfault(name, display, position)
                return
            else:
                temp = self._OM['heat']['heaters'][number]['current']
                val = int(temp)
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
                panelhalf(name, icon, target, val, dec, display, True)
            elif position == 'lower':
                panelhalf(name, icon, target, val, dec, display, False)
            collect()

        def panelfull(name, icon, target, val, dec, panel_fonts):
                # Full panel heater display
                panel_fonts['heading'].write(name, 0, 0)
                panel_fonts['target'].write(target, 1, 17)
                panel_fonts['icons'].write(icon,2,32)
                if self._show_decimal[name]:
                    panel_fonts['s_minor'].write('°', 102, 16)
                    panel_fonts['s_major'].write('{}'.format(val), 106, 45)
                    panel_fonts['s_minor'].write('.{:01d}'.format(dec), 104, 45)
                else:
                    panel_fonts['s_minor'].write('°', 119, 15)
                    panel_fonts['s_major'].write('{}'.format(val), 127, 45)

        def panelhalf(name, icon, target, val, dec, panel_fonts, top):
                # Half panel heater display
                y = 0 if top else 24
                panel_fonts['heading'].write(name, 0, y)
                panel_fonts['target'].write(target, 1, y + 14)
                panel_fonts['icons'].write(icon, 38, y + 4)
                if self._show_decimal[name]:
                    panel_fonts['d_minor'].write('°', 108, y + 10)
                    panel_fonts['d_major'].write('{}'.format(val), 108, y + 19)
                    panel_fonts['d_minor'].write('.{:01d}'.format(dec), 108, y + 19)
                else:
                    panel_fonts['d_minor'].write('°', 121, y + 10)
                    panel_fonts['d_major'].write('{}'.format(val), 121, y + 19)


        def panelfault(name, panel_fonts, position):
                # Display 'fault!' in a heater panel
                if position == 'upper':
                    panel_fonts['message'].write('{} FAULT'.format(name), 18, 2)
                    panel_fonts['icons'].write(C_BOLT, 0, 2)
                elif position == 'lower':
                    panel_fonts['message'].write('{} FAULT'.format(name), 18, 26)
                    panel_fonts['icons'].write(C_BOLT, 0, 26)
                else:
                    panel_fonts['message'].write('{}'.format(name), 21, 6)
                    panel_fonts['icons'].write(C_BOLT, 0, 14)
                    panel_fonts['message'].write('FAULT', 21, 26)

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
        '''This is how to add fake devices for testing multi-panel stuff..
        extruders.append((extruders[0][0],'E1',C_TOOL))
        heaters.append((heaters[0][0],'encl',C_ENCL))'''
        # Display extruder heaters (max 2)
        if len(extruders) == 0:
            self._lpanel_fonts['icons'].write(C_WARN, 64, 2, halign='center')
            self._lpanel_fonts['message'].write('no extruders?', 64, 22, halign='center')
        if len(extruders) == 1:
            showHeater(*extruders[0], self._lpanel_fonts, 'full')
        if len(extruders) >= 2:
            showHeater(*extruders[0], self._lpanel_fonts, 'upper')
            showHeater(*extruders[1], self._lpanel_fonts, 'lower')

        # Display bed and chamber heaters
        if len(heaters) == 0:
            self._rpanel_fonts['icons'].write(C_WARN, 64, 2, halign='center')
            self._rpanel_fonts['message'].write('no heaters?', 64, 22, halign='center')
        if len(heaters) == 1:
            showHeater(*heaters[0], self._rpanel_fonts, 'full')
        if len(heaters) >= 2:
            showHeater(*heaters[0], self._rpanel_fonts, 'upper')
            showHeater(*heaters[1], self._rpanel_fonts, 'lower')
