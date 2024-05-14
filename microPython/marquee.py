from machine import Pin, I2C, SoftI2C
from ssd1306 import SSD1306_I2C
from ezFBfont import ezFBfont
from sys import path
from time import sleep_ms,ticks_ms

from framebuf import FrameBuffer, MONO_HLSB
from uctypes import bytearray_at, addressof

# fonts
path.append('fonts')
import mPyEZfont_u8g2_spleen_12x24_r
import mPyEZfont_u8g2_spleen_16x32_n
import mPyEZfont_u8g2_helvR14_r

'''
Marquee buildup; wip.
'''

# pins
#I2C0_SDA_PIN = 21  # default esp32
#I2C0_SCL_PIN = 22  # default esp32
I2C0_SDA_PIN = 28  # default rp2040
I2C0_SCL_PIN = 29  # default rp2040

# I2C
# Wiring is important, you need good connections and pullup resisitors on the lines.
#  If you see continual 'OSError: with 'ENODEV' or 'ETIMEDOUT' you can try the SoftI2C
#  function instead, it is more tolerant of timing errors.
#  You can also play with frequency and timeout values, default:
#  freq=400000, timeout= 50000
#i2c0=SoftI2C(sda=Pin(I2C0_SDA_PIN), scl=Pin(I2C0_SCL_PIN),  freq=200000, timeout=100000)
i2c0=I2C(0,sda=Pin(I2C0_SDA_PIN), scl=Pin(I2C0_SCL_PIN))

# Display
d0 = SSD1306_I2C(128, 64, i2c0, addr=0x3c)
d0.invert(False)  # as needed
d0.rotate(1)      # as needed
d0.contrast(128)  # as needed

# Marquee class
class marquee():
    # Marquee class
    def __init__(self,
                 device,
                 font,
                 message,
                 y,
                 interval=0.25,
                 step = 1,
                 fg = None,
                 bg = None,
                 verbose = True):

        self.device = device
        self.font = font;
        self.msg = message
        self.x = 0
        self.y = y
        self.interval = interval
        self.step = step
        self.running = False
        self._scrollpos = 0
        self._stopping = False
        self._font_format = MONO_HLSB
        self._verbose = verbose
        self.name = font.__name__

        if verbose:
            print('starting marquee for font: {}'.format(self.name))
            if interval is None:
                print('step = {}, manual stepping'.format(step))
            else:
                print('step = {}, interval =  {}'.format(step, interval))

        # briefly create a font on the display to get colors and the message size
        tfont = ezFBfont(device, font, fg=fg, bg=bg)
        self.fg = tfont.fg
        self.bg = tfont.bg
        self.msg_w, self.msg_h = tfont.size(message)
        self.h = self.msg_h
        self.w = device.width
        del tfont
        if verbose:
            print('Message: {}\nText Size: {} {}'.format(self.msg, self.msg_w, self.msg_h))
        if verbose:
            print('{} * {} box at: {}, {}'.format(self.w, self.h, self.x, self.y))

        # Work out the 'pad' scheme we can use, default to 50% msgbox.
        # Consider messages /shorter/ then box width.. they need padding to the box size.
        # May need to write the string twice..

        # A buffer to hold the message + padding
        scroll_buf_w = (self.msg_w * 2) + self.w
        scroll_buf_h = self.msg_h
        scroll_buf_px = scroll_buf_w * scroll_buf_h
        scroll_buf_size = scroll_buf_px // 8
        # TODO: research how FB buffers size works..
        scroll_buf = bytearray(scroll_buf_size + scroll_buf_h)
        # Fill the buffer with the scrill contents
        self.fill()
        # need a different length here...
        print(scroll_buf)
        frame_fb = FrameBuffer(scroll_buf,  scroll_buf_w, scroll_buf_h, self._font_format)
        print(frame_fb)
        device.blit(frame_fb, self.x, self.y)

        # From phinches color writer..
        #
        #buf = bytearray_at(addressof(self.glyph), len(self.glyph))
        #fbc = FrameBuffer(buf, self.clip_width, self.char_height, self.map)
        # and..
        #charbuf = FrameBuffer(buf, char_width, char_height, self._font_format)
        #self._device.blit(charbuf, x, y, tkey, palette)

        # .. otherwise save resources.
        self.animating = True

    def stop(self, now=False):
        # stop requested, message will finish animation unless now=True
        if verbose:
            if now:
                print('exiting marquee {}'.format(self.name))
            else:
                print('stopping marquee {}'.format(self.name))
        self._stopping = True
        if now:
            self.display.rect(self.x, self.y, self.w, self.h, self.bg)
            self.animating = False

    def _fill_buf(self)
        # A temporary framebuffer to write the message with
        scroll_fb = FrameBuffer(self.scroll_buf, scroll_buf_w, scroll_buf_h, self._font_format)
        # A font writer for that
        temp_font = ezFBfont(scroll_fb, font, fg=self.fg, bg=self.bg)
        temp_font.write(message, 0, 0)
        temp_font.write(message, self.msg_w + self.pad, 0)
        # and fill the padded area with background
        scroll_fb.rect(self.msg_w, 0, self.pad,self.msg_h, self.bg)
        del temp_font
        # scroll_buf now has 'message + padding + message'


# Font Init
heading = ezFBfont(d0, mPyEZfont_u8g2_helvR14_r)

minutes = ezFBfont(d0, mPyEZfont_u8g2_spleen_16x32_n, halign='right', valign='baseline')
seconds = ezFBfont(d0, mPyEZfont_u8g2_spleen_12x24_r, valign='baseline')

print('start')
# frame
#d0.rect(0, 24, 127, 38, 1)
marquee(d0, mPyEZfont_u8g2_helvR14_r, 'Hello World', 0, 0)

print('started')
d0.show()

'''

sleep_ms(1000)

print('loop')

x = 86
y = 53
# loop
while True:
    upsecs = int(ticks_ms() / 1000)
    secs = upsecs % 60
    mins = int(upsecs / 60) % 60
    hrs = int(upsecs / 3600) % 24
    minutes.write('%d:%02.d' % (hrs, mins), x, y)
    seconds.write('.%02.d' % secs, x, y)
    d0.show()
# fin
'''
