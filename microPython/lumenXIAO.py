from machine import Timer, Pin
from neopixel import NeoPixel
'''
    Lumen (LED Indicator) for the Seeedstudio XIAO RP2040
    Drives the onboard NeoPixel with moods
    The additional RGB 'user' led is cycled RGB to indocate send events
'''

class lumen:
    def __init__(self, bright, standby, flash):
        '''
            start led/neopixel etc

            properties:
                bright = float(0..1), intensity
                standby = float(0..1), intensity when off
                flash  = int(), flash duration in ms
        '''
        self.bright = bright
        self.standby = standby
        self.flash = flash
        self._timer = None   # otherwise timer gets garbage collected..
        self._moods = {'off':(255,128,0),
                      'idle':(0,255,0),
                      'busy':(255,255,255),
                       'job':(255,0,255),
                    'paused':(0,0,255),
                       'err':(255,0,0)}

        # Neopixel
        self._pixelVcc = Pin(11,Pin.OUT)   # Power on pin 11
        self._pixelVcc.value(1)            # turn on immediately
        self._pixel = NeoPixel(Pin(12),1)  # data on pin 12
        self._pixel[0]=(0,0,0)
        self._pixel.write()

    def blink(self, mood, dim=False, auto=True):
        '''
            flash the mood after an update finishes
            if auto=True it uses an interrupt timer
            to turn off after 'self.flash' time
        '''
        def unblink(t):
            # called by timer
            self._pixel[0] = (0,0,0)
            self._pixel.write()

        if mood is None:
            return
        bright = self.standby if dim else self.bright
        neo = self._moods[mood]
        self._pixel[0] = (int(neo[0]*bright),
                          int(neo[1]*bright),
                          int(neo[2]*bright))
        self._pixel.write()
        if auto:
            self._timer = Timer(period=self.flash, mode=Timer.ONE_SHOT, callback=unblink)

    def emote(self,model,net=None):
        '''
            Use the model to find our mood by mapping the
            status to colors, crudely.
        '''

        if model is None:
            return('err')
        if net is not None:
            interface = model['network']['interfaces'][net]
            online = True if interface['state'] is 'active' else False
        else:
            # If no netwok; set online=True so that we do not signal 'error' when off or idle
            online = True
        if model['state']['machineMode'] == '':
           return('err')
        status = model['state']['status']
        if status in ['disconnected','halted']:
            return('err')
        if status in ['off','idle']:
            return status if online else 'err'
        if status in ['starting','updating','busy','changingTool']:
            return('busy')
        if status in ['pausing','paused','resuming','cancelling']:
            return('paused')
        if status in ['processing','simulating']:
            return('job')
        return None
