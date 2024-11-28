from machine import Timer,Pin
'''
    Heartbeat (RGB LED Indicator) for the Seeedstudio XIAO RP2040
'''

class heartbeat:
    def __init__(self, bright, standby):
        '''
            start RGB heartbeat led

            properties:
                bright = float(0..1), intensity
                standby = float(0..1), intensity when off
        '''
        self.bright = bright
        self.standby = standby

        # RGB mini status Led, default off
        self._rgbR = Pin(17,Pin.OUT)
        self._rgbG = Pin(16,Pin.OUT)
        self._rgbB = Pin(25,Pin.OUT)
        self._rgbstate = (True,False,False)
        self._setRGB()   # start off

    def _setRGB(self,state=(False,False,False)):
        # sets onboard rgb status led (heartbeat led)
        self._rgbR.value(not state[0])   # pins are inverted
        self._rgbG.value(not state[1])
        self._rgbB.value(not state[2])

    def beat(self):
        '''
            Shows comms activity using the spare RGB led on the Xiao board
            cycling R->G->B->etc every time a request is sent
        '''
        self._setRGB(self._rgbstate)
        # Rotate the onboard RGB heartbeat
        self._rgbstate = (self._rgbstate[2],self._rgbstate[0],self._rgbstate[1])
