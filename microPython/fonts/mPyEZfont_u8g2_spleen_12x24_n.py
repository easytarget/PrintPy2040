'''
    mPyEZfont_u8g2_spleen_12x24_n.py : generated as part of the microPyEZfonts repository
      https://github.com/easytarget/microPyEZfonts

    Original spleen-12x24.bdf font file was sourced from the U8G2 project:
      https://github.com/olikraus/u8g2

    This font definition can be used with the "writer" class from Peter Hinches
      micropython font-to-py tool, and was generated using his tooling from
      https://github.com/peterhinch/micropython-font-to-py

    Original Copyright Notice from source:

    COPYRIGHT "Copyright (c) 2018-2022, Frederic Cambus"

    Original Comments from source (may include copyright info):

    COMMENT /*
    COMMENT  * Spleen 12x24 1.9.1
    COMMENT  * Copyright (c) 2018-2022, Frederic Cambus
    COMMENT  * https://www.cambus.net/
    COMMENT  *
    COMMENT  * Created:      2018-08-15
    COMMENT  * Last Updated: 2020-10-10
    COMMENT  *
    COMMENT  * Spleen is released under the BSD 2-Clause license.
    COMMENT  * See LICENSE file for details.
    COMMENT  *
    COMMENT  * SPDX-License-Identifier: BSD-2-Clause
    COMMENT  */
'''

# Code generated by font_to_py.py.
# Font: spleen-12x24.bdf Char set:  %()*+,-./0123456789:°
# Cmd: ../micropython-font-to-py/font_to_py.py -x -k ./n-char.set -e 32 ../u8g2/tools/font/bdf/spleen-12x24.bdf 0 tmp_mPyEZfont_u8g2_spleen_12x24_n.py
version = '0.33'

def height():
    return 24

def baseline():
    return 19

def max_width():
    return 12

def hmap():
    return True

def reverse():
    return False

def monospaced():
    return False

def min_ch():
    return 32

def max_ch():
    return 176

_font =\
b'\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x38\xc0'\
b'\x6d\x80\x6d\x80\x3b\x00\x03\x00\x06\x00\x06\x00\x0c\x00\x0d\xc0'\
b'\x1b\x60\x1b\x60\x31\xc0\x30\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\xe0'\
b'\x01\x80\x03\x00\x06\x00\x0c\x00\x0c\x00\x18\x00\x18\x00\x18\x00'\
b'\x18\x00\x18\x00\x18\x00\x18\x00\x18\x00\x0c\x00\x0c\x00\x06\x00'\
b'\x03\x00\x01\x80\x00\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x0c\x00\x00\x00\x00\x00\x70\x00\x18\x00\x0c\x00\x06\x00\x03\x00'\
b'\x03\x00\x01\x80\x01\x80\x01\x80\x01\x80\x01\x80\x01\x80\x01\x80'\
b'\x01\x80\x03\x00\x03\x00\x06\x00\x0c\x00\x18\x00\x70\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x30\xc0\x19\x80\x0f\x00'\
b'\x06\x00\x7f\xe0\x06\x00\x0f\x00\x19\x80\x30\xc0\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x06\x00\x06\x00\x06\x00\x3f\xc0\x06\x00\x06\x00'\
b'\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x06\x00\x06\x00'\
b'\x0c\x00\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3f\xc0\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x06\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x0c\x00\x00\x00\x00\x00\x00\x30\x00\x30\x00\x60\x00\x60\x00\xc0'\
b'\x00\xc0\x01\x80\x01\x80\x03\x00\x03\x00\x06\x00\x06\x00\x0c\x00'\
b'\x0c\x00\x18\x00\x18\x00\x30\x00\x30\x00\x60\x00\x60\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x1f\x80\x30\xc0\x60\x60\x60\x60\x60\xe0\x61\xe0\x63\x60'\
b'\x66\x60\x6c\x60\x78\x60\x70\x60\x60\x60\x60\x60\x30\xc0\x1f\x80'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0e\x00\x1e\x00\x36\x00'\
b'\x26\x00\x06\x00\x06\x00\x06\x00\x06\x00\x06\x00\x06\x00\x06\x00'\
b'\x06\x00\x06\x00\x06\x00\x3f\xc0\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x1f\x80\x30\xc0\x60\x60\x00\x60\x00\x60\x00\x60\x00\xc0'\
b'\x01\x80\x03\x00\x06\x00\x0c\x00\x18\x00\x30\x00\x60\x60\x7f\xe0'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\x80\x30\xc0\x60\x60'\
b'\x00\x60\x00\x60\x00\xc0\x0f\x80\x00\xc0\x00\x60\x00\x60\x00\x60'\
b'\x00\x60\x60\x60\x30\xc0\x1f\x80\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x60\x00\x60\x00\x60\x00\x61\x80\x61\x80\x61\x80\x61\x80'\
b'\x61\x80\x61\x80\x61\x80\x7f\xe0\x01\x80\x01\x80\x01\x80\x01\x80'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x7f\xe0\x60\x60\x60\x00'\
b'\x60\x00\x60\x00\x60\x00\x7f\x80\x00\xc0\x00\x60\x00\x60\x00\x60'\
b'\x00\x60\x60\x60\x30\xc0\x1f\x80\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x1f\xc0\x30\x60\x60\x00\x60\x00\x60\x00\x60\x00\x7f\x80'\
b'\x60\xc0\x60\x60\x60\x60\x60\x60\x60\x60\x60\x60\x30\xc0\x1f\x80'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x7f\xe0\x60\x60\x00\x60'\
b'\x00\x60\x00\x60\x00\xc0\x01\x80\x03\x00\x06\x00\x0c\x00\x0c\x00'\
b'\x0c\x00\x0c\x00\x0c\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x1f\x80\x30\xc0\x60\x60\x60\x60\x60\x60\x30\xc0\x1f\x80'\
b'\x30\xc0\x60\x60\x60\x60\x60\x60\x60\x60\x60\x60\x30\xc0\x1f\x80'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\x80\x30\xc0\x60\x60'\
b'\x60\x60\x60\x60\x60\x60\x60\x60\x30\x60\x1f\xe0\x00\x60\x00\x60'\
b'\x00\x60\x00\x60\x60\xc0\x3f\x80\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00'\
b'\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x06\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x0c\x00\x00\x00\x00\x00\x00\x00\x0f\x00\x19\x80\x19\x80\x19\x80'\
b'\x19\x80\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00'

_sparse =\
b'\x20\x00\x07\x00\x25\x00\x0e\x00\x28\x00\x15\x00\x29\x00\x1c\x00'\
b'\x2a\x00\x23\x00\x2b\x00\x2a\x00\x2c\x00\x31\x00\x2d\x00\x38\x00'\
b'\x2e\x00\x3f\x00\x2f\x00\x46\x00\x30\x00\x4d\x00\x31\x00\x54\x00'\
b'\x32\x00\x5b\x00\x33\x00\x62\x00\x34\x00\x69\x00\x35\x00\x70\x00'\
b'\x36\x00\x77\x00\x37\x00\x7e\x00\x38\x00\x85\x00\x39\x00\x8c\x00'\
b'\x3a\x00\x93\x00\xb0\x00\x9a\x00'

_mvfont = memoryview(_font)
_mvsp = memoryview(_sparse)
ifb = lambda l : l[0] | (l[1] << 8)

def bs(lst, val):
    while True:
        m = (len(lst) & ~ 7) >> 1
        v = ifb(lst[m:])
        if v == val:
            return ifb(lst[m + 2:])
        if not m:
            return 0
        lst = lst[m:] if v < val else lst[:m]

def get_ch(ch):
    doff = bs(_mvsp, ord(ch)) << 3
    width = ifb(_mvfont[doff : ])

    next_offs = doff + 2 + ((width - 1)//8 + 1) * 24
    return _mvfont[doff + 2:next_offs], 24, width
 
