from machine import Timer, PWM
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
        self.bright = int(bright * 65535)
        self.standby = int(standby * 65535)

        # RGB mini status Led, default off, inverted wiring
        self._rgbR = PWM(17, freq=5000, duty_u16=0, invert = True)
        self._rgbG = PWM(16, freq=5000, duty_u16=0, invert = True)
        self._rgbB = PWM(25, freq=5000, duty_u16=0, invert = True)
        self._setRGB((0,0,0),0)     # start off
        self._rgbstate = (0, 1, 1)  # we will 'cycle' this tuple

    def _setRGB(self, state, bright):
        self._rgbR.duty_u16(state[0] * bright)
        self._rgbG.duty_u16(state[1] * bright)
        self._rgbB.duty_u16(state[2] * bright)

    def beat(self, dim=False):
        '''
            Shows comms activity using the spare RGB led on the Xiao board
            Two leds are illuminated at all times
            cycling GB->BR->RG->etc every time a request is sent
        '''
        bright = self.standby if dim else self.bright
        self._setRGB(self._rgbstate, bright)
        # Rotate the state tuple
        self._rgbstate = (self._rgbstate[2],self._rgbstate[0],self._rgbstate[1])
