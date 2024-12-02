from time import sleep_ms,ticks_ms,ticks_diff
from ssd1306 import SSD1306_I2C
from framebuf import FrameBuffer, MONO_VLSB
from sys import path
from config import config
from machine import mem32
from gc import collect
import _thread
# fonts
path.append('fonts')
from ezFBfont import ezFBfont
import ezFBfont_15_helvB10_ascii as heading
import ezFBfont_13_helvR08_full as subhead
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

    Note: We use a seperate pair of 'Panel' framebuffers to draw the model
        data onto whenever we get an update.
        This is then blitted onto the display framebuffers when it changes
        and, with the marquee message panel, displayed by a fast animation
        loop. [ TODO: on the second CPU??!]
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
        self.pause = False
        self.running = False
        self.watchdog = ticks_ms() + 10000
        self._lastOut = ''
        self._updating = False
        self._message = ''
        self._marquee = None
        self._show_decimal = {}
        self._failcount = 0
        # hardware
        self._initDisplays()
        self._initPanels()
        self._bright(config.display_bright)
        self._clean()
        print('display init: ', mem32[0xd0000000])
        _thread.start_new_thread(self.animate, ())
        self.running = True

    def _initDisplays(self):
        def fonts(d):
            return {
                'heading' : ezFBfont(d, heading),
                'message' : ezFBfont(d, message),
                }
        self._l_display = SSD1306_I2C(128, 64, config.I2C_left, addr=0x3c)
        self._r_display = SSD1306_I2C(128, 64, config.I2C_right, addr=0x3c)
        self._l_display.invert(config.display_invert)
        self._r_display.invert(config.display_invert)
        self._l_display.rotate(config.display_rotate)
        self._r_display.rotate(config.display_rotate)
        self._l_display_fonts = fonts(self._l_display)
        self._r_display_fonts = fonts(self._r_display)


    def _initPanels(self):
        def fonts(p):
            return {
                'heading' : ezFBfont(p, heading),
                'subhead' : ezFBfont(p, subhead),
                'icons'   : ezFBfont(p, icons),
                'message' : ezFBfont(p, message),
                's_major' : ezFBfont(p, single_major, halign='right', valign='baseline'),
                's_minor' : ezFBfont(p, single_minor, valign='baseline'),
                'd_major' : ezFBfont(p, double_major, halign='right', valign='baseline'),
                'd_minor' : ezFBfont(p, double_minor, valign='baseline'),
                }
        self._l_panel = FrameBuffer(bytearray(16 * 64), 128, 64, MONO_VLSB)
        self._r_panel = FrameBuffer(bytearray(16 * 64), 128, 64, MONO_VLSB)
        self._l_panel_fonts = fonts(self._l_panel)
        self._r_panel_fonts = fonts(self._r_panel)

    def _bright(self, bright):
        bright = int(bright * 255)
        self._l_display.contrast(bright)
        self._r_display.contrast(bright)

    def _clean(self, c=0):
        self._l_display.fill_rect(0, 0, 128, 64, c)
        self._r_display.fill_rect(0, 0, 128, 64, c)

    def _show(self):
        self._l_display.show()
        self._r_display.show()

    def _swipeOff(self):
        self.pause = True
        s = 16
        for x in range(0, 129, 8):
            self._l_display.scroll(s, 0)
            self._l_display.rect(0, 0, s, 64, 0, True)
            self._r_display.scroll(-s, 0)
            self._r_display.rect(128 - s, 0, s, 64, 0, True)
            self._show()
        self.pause = False

    def _swipeOn(self):
        self.pause = True
        s = 16
        l_fb = FrameBuffer(bytearray(16 * 64), 128, 64, MONO_VLSB)
        r_fb = FrameBuffer(bytearray(16 * 64), 128, 64, MONO_VLSB)
        l_fb.blit(self._l_display,0,0)
        r_fb.blit(self._r_display,0,0)
        self._clean()
        for x in range(0, 129, s):
            self._l_display.blit(l_fb, 128 - x, 0)
            self._r_display.blit(r_fb, -128 + x, 0)
            self._show()
        del(l_fb, r_fb)
        self.pause = False

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
            self._l_display.poweron()
            self._r_display.poweron()
            self._swipeOn()
            self.standby = False
            

    def off(self):
        if not self.standby:
            self._swipeOff()
            self._l_display.poweroff()
            self._r_display.poweroff()
            self.standby = True

    def splash(self):
        self.showText('PrintPy\n2040', 'by Owen    ')
        self._r_display_fonts['heading'].write('easytarget.org', 0, 36)

    def showText(self, left, right):
        self._clean()
        self._l_display_fonts['message'].write(left, 63, 16, halign='center')
        self._r_display_fonts['message'].write(right, 63, 16, halign='center')

    def animate(self):
        print('animation call: ', mem32[0xd0000000])
        def frame():
            '''
                Run by the animation loop (in a seperate thread on second CPU)
                - Copies (updated) model display panel to main display when available
                - Animates the status and message marquee on the main display
                - Show job progress as needed
                Can be paused when we are doing 'on/off/waiting' animations
            '''
            if self.pause or (self._OM is None):
                return
            if not self._updating:
                print('+',end='')
                # copy panels in only when they are complete
                self._l_display.blit(self._l_panel, 0, 0)
                self._r_display.blit(self._r_panel, 0, 0)
            else:
                print('-',end='')
            # Job progress bar TODO:
            # Status and message marquee. TODO:
            #if self._marquee is not None:
            #    # step marquee and add a pause whenever it rolls over
            #    if self._marquee.step(config.marquee_step):
            #        self._marquee.pause(config.marquee_pause)
            self._show()
            collect()

        # Start the animation loop
        nextFrame = ticks_ms() + config.animation_interval
        while self.watchdog > ticks_ms():
            frame()
            while ticks_ms() < nextFrame:
                sleep_ms(1)
            nextFrame = ticks_ms() + config.animation_interval
        print('animation exit')
        self.running = False

    def updatePanels(self, model):
        self._updating = True  # simple mutex lock
        if model is None:
            self._failcount += 1
            if self._failcount > config.failcount:
                # TODO: fix the fail counter..   IN MAIN LOOP?????
                self.showText('no\nresponse','retrying\n...')
                self._show()
                self._updating = False
                return('update data unavailable\n')
        else:
            self._failcount = 0

        # Update the local model
        self._OM = model
        self._putModel()
        self._updating = False

        # Turn screen on/off as needed    TODO: Move to main loop?
        show = not self._OM['state']["status"] in config.offstates
        if show:
            self.on()
        else:
            self.off()

        # Return the last generated status line
        return self._lastOut + '\n'

    '''
        All the routines below tediously walk/grok the OM and update the
        display panel framebuffer(s) for later display by the animation loop.
        Also returns a status string for logging or REPL output
    '''

    def _putModel(self):
        #  Constructs the twin-panel model status display
        #  and puts it on the panel framebuffers
        #  also returns a text summary of status
        if self._OM is None:
            # No data == no viable output
            return('No data available')
        # Construct results string
        r = 'Up: {}'.format(self._dhms(self._OM['state']["upTime"]))
        if self._OM['state']['status'] in ['halted','updating','starting']:
            # Maybe display splash while starting or updating..
            r += ' | please wait'
            return r
        r += self._putStatus()
        r += self._putJob()
        if self._OM['state']['machineMode'] == 'FFF':
            self._putFFF()
        else:
            mode = self._OM['state']['machineMode']
            r += ', Unsupported mode: {}'.format(mode)
            self.showText('\'{}\'\nmode'.format(mode), 'not\nsupported')
        m = self._putMessages()
        r += self._putNetwork()
        # Return results
        return r + m

    def _putStatus(self):
        # common items to always show
        cstate = self._OM['state']["status"]
        cstate = cstate[0].upper() + cstate[1:]
        if cstate == 'Simulating':
            cstate = 'Processing'
        self._l_panel_fonts['heading'].write(cstate, 0, 1)
        return ' | {}'.format(cstate)

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
        self._r_panel_fonts['icons'].write(icon, 112, 0, halign = 'left')
        if self._message == '':
            # only show detailed network info when no messages are displaying
            self._r_panel_fonts['subhead'].write(net, 110, 3, halign = 'right')
        return ' | {}'.format(net)

    def _putJob(self):
        # Job progress
        if self._OM['job']['build']:
            try:
                percent = self._OM['job']['filePosition'] / self._OM['job']['file']['size'] * 100
            except ZeroDivisionError:  # file size might be 0 as the job starts
                percent = 0
            job_line = ' {:.1f}'.format(percent) if percent < 100 else '100'
            self._l_panel_fonts['d_minor'].write(job_line, 120, 12, halign='right')  # TODO:
            #self._l_panel_fonts['heading'].write(job_line, 120, 0, halign='right')  # decide which to use
            self._l_panel_fonts['subhead'].write('%', 121, 2)
            return ' | Job: {}%'.format(job_line)
        return ''

    def _putMessages(self):
        # M117 messages
        r = ''
        self._message = self._OM['state']['displayMessage']
        if self._message != '':
            r += ' | message: ' +  self._message
            self._r_panel_fonts['heading'].write(self._message, 0, 0)
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

        def panelfull(name, icon, target, val, dec, panel_fonts):
                # Full panel heater display
                panel_fonts['heading'].write(name, 0, 16)
                panel_fonts['icons'].write(icon,2,48)
                panel_fonts['subhead'].write(target, 0, 30)
                if self._show_decimal[name]:
                    panel_fonts['s_minor'].write('°', 102, 32)
                    panel_fonts['s_major'].write('{}'.format(val), 106, 61)
                    panel_fonts['s_minor'].write('.{:01d}'.format(dec), 104, 61)
                else:
                    panel_fonts['s_minor'].write('°', 119, 31)
                    panel_fonts['s_major'].write('{}'.format(val), 127, 61)

        def panelhalf(name, icon, target, val, dec, panel_fonts, top):
                # Half panel heater display
                y = 16 if top else 40
                panel_fonts['heading'].write(name, 0, y)
                panel_fonts['icons'].write(icon, 38, y + 4)
                panel_fonts['subhead'].write(target, 2, y + 12)
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
                    panel_fonts['icons'].write(C_BOLT, 0, 18)
                    panel_fonts['message'].write('{} FAULT'.format(name), 18, 18)
                elif position == 'lower':
                    panel_fonts['icons'].write(C_BOLT, 0, 42)
                    panel_fonts['message'].write('{} FAULT'.format(name), 18, 42)
                else:
                    panel_fonts['icons'].write(C_BOLT, 0, 30)
                    panel_fonts['message'].write('{}'.format(name), 21, 22)
                    panel_fonts['message'].write('FAULT', 21, 42)

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
            self._l_panel_fonts['icons'].write(C_WARN, 64, 18, halign='center')
            self._l_panel_fonts['message'].write('no extruders?', 64, 38, halign='center')
        if len(extruders) == 1:
            showHeater(*extruders[0], self._l_panel_fonts, 'full')
        if len(extruders) >= 2:
            showHeater(*extruders[0], self._l_panel_fonts, 'upper')
            showHeater(*extruders[1], self._l_panel_fonts, 'lower')

        # Display bed and chamber heaters
        if len(heaters) == 0:
            self._r_panel_fonts['icons'].write(C_WARN, 64, 18, halign='center')
            self._r_panel_fonts['message'].write('no heaters?', 64, 38, halign='center')
        if len(heaters) == 1:
            showHeater(*heaters[0], self._r_panel_fonts, 'full')
        if len(heaters) >= 2:
            showHeater(*heaters[0], self._r_panel_fonts, 'upper')
            showHeater(*heaters[1], self._r_panel_fonts, 'lower')
