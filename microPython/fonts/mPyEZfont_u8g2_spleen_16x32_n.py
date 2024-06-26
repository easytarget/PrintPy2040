'''
    mPyEZfont_u8g2_spleen_16x32_n.py : generated as part of the microPyEZfonts repository
      https://github.com/easytarget/microPyEZfonts

    Original spleen-16x32.bdf font file was sourced from the U8G2 project:
      https://github.com/olikraus/u8g2

    This font definition can be used with the "writer" class from Peter Hinches
      micropython font-to-py tool, and was generated using his tooling from
      https://github.com/peterhinch/micropython-font-to-py

    Original Copyright Notice from source:

    COPYRIGHT "Copyright (c) 2018-2022, Frederic Cambus"

    Original Comments from source (may include copyright info):

    COMMENT /*
    COMMENT  * Spleen 16x32 1.9.1
    COMMENT  * Copyright (c) 2018-2022, Frederic Cambus
    COMMENT  * https://www.cambus.net/
    COMMENT  *
    COMMENT  * Created:      2018-08-12
    COMMENT  * Last Updated: 2020-10-10
    COMMENT  *
    COMMENT  * Spleen is released under the BSD 2-Clause license.
    COMMENT  * See LICENSE file for details.
    COMMENT  *
    COMMENT  * SPDX-License-Identifier: BSD-2-Clause
    COMMENT  */
'''

# Code generated by font_to_py.py.
# Font: spleen-16x32.bdf Char set:  %()*+,-./0123456789:°
# Cmd: ../micropython-font-to-py/font_to_py.py -x -k ./n-char.set -e 32 ../u8g2/tools/font/bdf/spleen-16x32.bdf 0 tmp_mPyEZfont_u8g2_spleen_16x32_n.py
version = '0.33'

def height():
    return 32

def baseline():
    return 26

def max_width():
    return 16

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
b'\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0c'\
b'\x0e\x0c\x1b\x18\x1b\x18\x1b\x30\x0e\x30\x00\x60\x00\x60\x00\xc0'\
b'\x00\xc0\x01\x80\x01\x80\x03\x00\x03\x00\x06\x38\x06\x6c\x0c\x6c'\
b'\x0c\x6c\x18\x38\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x3c\x00\xfc\x01\xe0\x03\x80\x07\x00\x06\x00\x0e\x00\x0c\x00'\
b'\x1c\x00\x18\x00\x18\x00\x18\x00\x18\x00\x18\x00\x18\x00\x18\x00'\
b'\x18\x00\x1c\x00\x0c\x00\x0e\x00\x06\x00\x07\x00\x03\x80\x01\xe0'\
b'\x00\xfc\x00\x3c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x10\x00\x00\x00\x00\x00\x00\x00\x3c\x00\x3f\x00\x07\x80\x01\xc0'\
b'\x00\xe0\x00\x60\x00\x70\x00\x30\x00\x38\x00\x18\x00\x18\x00\x18'\
b'\x00\x18\x00\x18\x00\x18\x00\x18\x00\x18\x00\x38\x00\x30\x00\x70'\
b'\x00\x60\x00\xe0\x01\xc0\x07\x80\x3f\x00\x3c\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\x18'\
b'\x1c\x38\x0e\x70\x07\xe0\x03\xc0\x03\xc0\x7f\xfe\x7f\xfe\x03\xc0'\
b'\x03\xc0\x07\xe0\x0e\x70\x1c\x38\x18\x18\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x80\x01\x80\x01\x80'\
b'\x01\x80\x1f\xf8\x1f\xf8\x01\x80\x01\x80\x01\x80\x01\x80\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x01\x80\x01\x80\x01\x80\x03\x80\x07\x00'\
b'\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x3f\xfc\x3f\xfc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x01\x80\x01\x80\x01\x80\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x10\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x06\x00\x0c\x00\x0c'\
b'\x00\x18\x00\x18\x00\x30\x00\x30\x00\x60\x00\x60\x00\xc0\x00\xc0'\
b'\x01\x80\x01\x80\x03\x00\x03\x00\x06\x00\x06\x00\x0c\x00\x0c\x00'\
b'\x18\x00\x18\x00\x30\x00\x30\x00\x60\x00\x60\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x0f\xf0\x1f\xf8\x38\x1c\x30\x0c\x30\x0c'\
b'\x30\x1c\x30\x3c\x30\x7c\x30\xec\x31\xcc\x33\x8c\x37\x0c\x3e\x0c'\
b'\x3c\x0c\x38\x0c\x30\x0c\x30\x0c\x38\x1c\x1f\xf8\x0f\xf0\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x80'\
b'\x07\x80\x0d\x80\x19\x80\x11\x80\x01\x80\x01\x80\x01\x80\x01\x80'\
b'\x01\x80\x01\x80\x01\x80\x01\x80\x01\x80\x01\x80\x01\x80\x01\x80'\
b'\x01\x80\x1f\xf8\x1f\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x0f\xf0\x1f\xf8\x38\x1c\x30\x0c\x00\x0c'\
b'\x00\x0c\x00\x0c\x00\x18\x00\x30\x00\x60\x00\xc0\x01\x80\x03\x00'\
b'\x06\x00\x0c\x00\x18\x00\x30\x0c\x30\x0c\x3f\xfc\x3f\xfc\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\xf0'\
b'\x1f\xf8\x38\x1c\x30\x0c\x00\x0c\x00\x0c\x00\x0c\x00\x18\x07\xf0'\
b'\x07\xf0\x00\x18\x00\x0c\x00\x0c\x00\x0c\x00\x0c\x00\x0c\x30\x0c'\
b'\x38\x1c\x1f\xf8\x0f\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x30\x00\x30\x00\x30\x00\x30\x00\x30\x30'\
b'\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x3f\xfc'\
b'\x3f\xfc\x00\x30\x00\x30\x00\x30\x00\x30\x00\x30\x00\x30\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3f\xfc'\
b'\x3f\xfc\x30\x0c\x30\x0c\x30\x00\x30\x00\x30\x00\x30\x00\x3f\xf0'\
b'\x3f\xf8\x00\x1c\x00\x0c\x00\x0c\x00\x0c\x00\x0c\x00\x0c\x30\x0c'\
b'\x38\x1c\x1f\xf8\x0f\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x0f\xf0\x1f\xf8\x38\x1c\x30\x0c\x30\x00'\
b'\x30\x00\x30\x00\x30\x00\x3f\xf0\x3f\xf8\x30\x1c\x30\x0c\x30\x0c'\
b'\x30\x0c\x30\x0c\x30\x0c\x30\x0c\x38\x1c\x1f\xf8\x0f\xf0\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3f\xfc'\
b'\x3f\xfc\x30\x0c\x30\x0c\x00\x0c\x00\x0c\x00\x0c\x00\x18\x00\x30'\
b'\x00\x60\x00\xc0\x01\x80\x03\x00\x03\x00\x03\x00\x03\x00\x03\x00'\
b'\x03\x00\x03\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x0f\xf0\x1f\xf8\x38\x1c\x30\x0c\x30\x0c'\
b'\x30\x0c\x30\x0c\x18\x18\x0f\xf0\x0f\xf0\x18\x18\x30\x0c\x30\x0c'\
b'\x30\x0c\x30\x0c\x30\x0c\x30\x0c\x38\x1c\x1f\xf8\x0f\xf0\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\xf0'\
b'\x1f\xf8\x38\x1c\x30\x0c\x30\x0c\x30\x0c\x30\x0c\x30\x0c\x30\x0c'\
b'\x38\x0c\x1f\xfc\x0f\xfc\x00\x0c\x00\x0c\x00\x0c\x00\x0c\x30\x0c'\
b'\x38\x1c\x1f\xf8\x0f\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x01\x80\x01\x80\x01\x80\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x01\x80\x01\x80\x01\x80\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xc0\x07\xe0'\
b'\x0e\x70\x0c\x30\x0c\x30\x0c\x30\x0e\x70\x07\xe0\x03\xc0\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00'

_sparse =\
b'\x20\x00\x09\x00\x25\x00\x12\x00\x28\x00\x1b\x00\x29\x00\x24\x00'\
b'\x2a\x00\x2d\x00\x2b\x00\x36\x00\x2c\x00\x3f\x00\x2d\x00\x48\x00'\
b'\x2e\x00\x51\x00\x2f\x00\x5a\x00\x30\x00\x63\x00\x31\x00\x6c\x00'\
b'\x32\x00\x75\x00\x33\x00\x7e\x00\x34\x00\x87\x00\x35\x00\x90\x00'\
b'\x36\x00\x99\x00\x37\x00\xa2\x00\x38\x00\xab\x00\x39\x00\xb4\x00'\
b'\x3a\x00\xbd\x00\xb0\x00\xc6\x00'

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

    next_offs = doff + 2 + ((width - 1)//8 + 1) * 32
    return _mvfont[doff + 2:next_offs], 32, width
 
