'''
    mPyEZfont_u8g2_helvR24_n.py : generated as part of the microPyEZfonts repository
      https://github.com/easytarget/microPyEZfonts

    Original helvR24.bdf font file was sourced from the U8G2 project:
      https://github.com/olikraus/u8g2

    This font definition can be used with the "writer" class from Peter Hinches
      micropython font-to-py tool, and was generated using his tooling from
      https://github.com/peterhinch/micropython-font-to-py

    Original Copyright Notice from source:

    COPYRIGHT "Copyright (c) 1984, 1987 Adobe Systems Incorporated. All Rights Reserved. Copyright (c) 1988, 1991 Digital Equipment Corporation. All Rights Reserved."

    Original Comments from source (may include copyright info):

    COMMENT ISO10646-1 extension by Markus Kuhn <mkuhn@acm.org>, 2001-03-20
    COMMENT 
    COMMENT +
    COMMENT  Copyright 1984-1989, 1994 Adobe Systems Incorporated.
    COMMENT  Copyright 1988, 1994 Digital Equipment Corporation.
    COMMENT
    COMMENT  Adobe is a trademark of Adobe Systems Incorporated which may be
    COMMENT  registered in certain jurisdictions.
    COMMENT  Permission to use these trademarks is hereby granted only in
    COMMENT  association with the images described in this file.
    COMMENT
    COMMENT  Permission to use, copy, modify, distribute and sell this software
    COMMENT  and its documentation for any purpose and without fee is hereby
    COMMENT  granted, provided that the above copyright notices appear in all
    COMMENT  copies and that both those copyright notices and this permission
    COMMENT  notice appear in supporting documentation, and that the names of
    COMMENT  Adobe Systems and Digital Equipment Corporation not be used in
    COMMENT  advertising or publicity pertaining to distribution of the software
    COMMENT  without specific, written prior permission.  Adobe Systems and
    COMMENT  Digital Equipment Corporation make no representations about the
    COMMENT  suitability of this software for any purpose.  It is provided "as
    COMMENT  is" without express or implied warranty.
    COMMENT -
'''

# Code generated by font_to_py.py.
# Font: helvR24.bdf Char set:  %()*+,-./0123456789:°
# Cmd: ../micropython-font-to-py/font_to_py.py -x -k ./n-char.set -e 32 ../u8g2/tools/font/bdf/helvR24.bdf 0 tmp_mPyEZfont_u8g2_helvR24_n.py
version = '0.33'

def height():
    return 33

def baseline():
    return 26

def max_width():
    return 29

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
b'\x09\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x09\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x1d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\x00\x0f\x80'\
b'\x38\x00\x3f\xc0\x30\x00\x39\xe0\x70\x00\x70\x60\x60\x00\x60\x70'\
b'\xe0\x00\x60\x70\xc0\x00\x60\x71\xc0\x00\x70\x61\x80\x00\x39\xe3'\
b'\x80\x00\x3f\xc3\x00\x00\x0f\x87\x00\x00\x00\x06\x00\x00\x00\x0e'\
b'\x1f\x00\x00\x0c\x3f\xc0\x00\x1c\x79\xc0\x00\x18\x60\xe0\x00\x38'\
b'\xe0\x60\x00\x30\xe0\x60\x00\x70\xe0\x60\x00\x60\x60\xe0\x00\xe0'\
b'\x71\xc0\x00\xc0\x3f\xc0\x01\xc0\x1f\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x01\x80'\
b'\x03\x00\x03\x00\x06\x00\x06\x00\x0e\x00\x0c\x00\x1c\x00\x1c\x00'\
b'\x1c\x00\x18\x00\x38\x00\x38\x00\x38\x00\x38\x00\x38\x00\x38\x00'\
b'\x38\x00\x38\x00\x38\x00\x18\x00\x1c\x00\x1c\x00\x1c\x00\x0c\x00'\
b'\x0e\x00\x06\x00\x06\x00\x03\x00\x03\x00\x01\x80\x00\x00\x00\x00'\
b'\x0b\x00\x00\x00\x00\x00\x60\x00\x30\x00\x30\x00\x18\x00\x18\x00'\
b'\x1c\x00\x0c\x00\x0e\x00\x0e\x00\x0e\x00\x06\x00\x07\x00\x07\x00'\
b'\x07\x00\x07\x00\x07\x00\x07\x00\x07\x00\x07\x00\x06\x00\x06\x00'\
b'\x0e\x00\x0e\x00\x0c\x00\x0c\x00\x1c\x00\x18\x00\x38\x00\x30\x00'\
b'\x30\x00\x60\x00\x00\x00\x00\x00\x0d\x00\x06\x00\x06\x00\x26\x40'\
b'\x76\xe0\x3f\xc0\x1f\x80\x0f\x00\x1f\x80\x39\xc0\x70\xe0\x20\x40'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x13\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe0\x00'\
b'\x00\xe0\x00\x00\xe0\x00\x00\xe0\x00\x00\xe0\x00\x00\xe0\x00\x00'\
b'\xe0\x00\x7f\xff\xc0\x7f\xff\xc0\x7f\xff\xc0\x00\xe0\x00\x00\xe0'\
b'\x00\x00\xe0\x00\x00\xe0\x00\x00\xe0\x00\x00\xe0\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x09\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x1c\x00\x1c\x00\x1c\x00\x1c\x00\x04\x00'\
b'\x0c\x00\x0c\x00\x18\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x7f\x80\x7f\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x09\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x1c\x00\x1c\x00\x1c\x00\x1c\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x09\x00\x00\x00\x00\x00\x01\x80\x01\x80\x01\x80\x03\x00\x03\x00'\
b'\x03\x00\x06\x00\x06\x00\x06\x00\x0c\x00\x0c\x00\x0c\x00\x08\x00'\
b'\x18\x00\x18\x00\x18\x00\x30\x00\x30\x00\x30\x00\x60\x00\x60\x00'\
b'\x60\x00\xc0\x00\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x12\x00\x00\x00\x00\x00\x00\x00'\
b'\x03\xe0\x00\x0f\xf8\x00\x1f\xfc\x00\x1e\x3c\x00\x3c\x1e\x00\x38'\
b'\x0e\x00\x38\x0e\x00\x70\x07\x00\x70\x07\x00\x70\x07\x00\x70\x07'\
b'\x00\x70\x07\x00\x70\x07\x00\x70\x07\x00\x70\x07\x00\x70\x07\x00'\
b'\x70\x07\x00\x38\x0e\x00\x38\x0e\x00\x38\x1e\x00\x1e\x3c\x00\x1f'\
b'\xfc\x00\x0f\xf8\x00\x03\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x12\x00\x00\x00\x00\x00\x00\x00\x00\x60\x00\x00\xe0\x00\x00\xe0'\
b'\x00\x01\xe0\x00\x07\xe0\x00\x1f\xe0\x00\x1f\xe0\x00\x00\xe0\x00'\
b'\x00\xe0\x00\x00\xe0\x00\x00\xe0\x00\x00\xe0\x00\x00\xe0\x00\x00'\
b'\xe0\x00\x00\xe0\x00\x00\xe0\x00\x00\xe0\x00\x00\xe0\x00\x00\xe0'\
b'\x00\x00\xe0\x00\x00\xe0\x00\x00\xe0\x00\x00\xe0\x00\x00\xe0\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x12\x00\x00\x00\x00\x00\x00\x00'\
b'\x03\xe0\x00\x0f\xf8\x00\x1f\xfc\x00\x3c\x1e\x00\x38\x0e\x00\x78'\
b'\x07\x00\x70\x07\x00\x70\x07\x00\x00\x07\x00\x00\x0e\x00\x00\x1e'\
b'\x00\x00\x3c\x00\x00\x78\x00\x01\xf0\x00\x03\xe0\x00\x0f\x80\x00'\
b'\x1e\x00\x00\x3c\x00\x00\x38\x00\x00\x70\x00\x00\x70\x00\x00\x7f'\
b'\xff\x00\x7f\xff\x00\x7f\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x12\x00\x00\x00\x00\x00\x00\x00\x03\xe0\x00\x0f\xf8\x00\x1f\xfc'\
b'\x00\x1c\x1c\x00\x38\x0e\x00\x38\x0e\x00\x38\x0e\x00\x38\x0e\x00'\
b'\x00\x0e\x00\x00\x1c\x00\x01\xfc\x00\x01\xf8\x00\x01\xfc\x00\x00'\
b'\x1e\x00\x00\x0f\x00\x00\x07\x00\x70\x07\x00\x70\x07\x00\x70\x07'\
b'\x00\x38\x0e\x00\x3c\x1e\x00\x1f\xfc\x00\x0f\xf8\x00\x03\xe0\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x12\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x18\x00\x00\x38\x00\x00\x78\x00\x00\x78\x00\x00\xf8\x00\x01'\
b'\xf8\x00\x03\xb8\x00\x03\xb8\x00\x07\x38\x00\x0e\x38\x00\x0e\x38'\
b'\x00\x1c\x38\x00\x38\x38\x00\x38\x38\x00\x70\x38\x00\xe0\x38\x00'\
b'\xff\xff\x00\xff\xff\x00\xff\xff\x00\x00\x38\x00\x00\x38\x00\x00'\
b'\x38\x00\x00\x38\x00\x00\x38\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x12\x00\x00\x00\x00\x00\x00\x00\x1f\xfe\x00\x1f\xfe\x00\x1f\xfe'\
b'\x00\x1c\x00\x00\x1c\x00\x00\x1c\x00\x00\x38\x00\x00\x38\x00\x00'\
b'\x3b\xe0\x00\x3f\xf8\x00\x3f\xfc\x00\x3c\x3e\x00\x38\x0e\x00\x00'\
b'\x0f\x00\x00\x07\x00\x00\x07\x00\x00\x07\x00\x70\x07\x00\x70\x0f'\
b'\x00\x78\x0e\x00\x3c\x3e\x00\x3f\xfc\x00\x1f\xf8\x00\x07\xc0\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x12\x00\x00\x00\x00\x00\x00\x00'\
b'\x01\xe0\x00\x07\xf8\x00\x0f\xfc\x00\x1e\x1c\x00\x1c\x0e\x00\x38'\
b'\x0e\x00\x38\x00\x00\x38\x00\x00\x30\x00\x00\x71\xe0\x00\x77\xf8'\
b'\x00\x7f\xfc\x00\x7c\x1e\x00\x78\x0e\x00\x78\x07\x00\x70\x07\x00'\
b'\x70\x07\x00\x30\x07\x00\x38\x07\x00\x38\x0e\x00\x1c\x1e\x00\x1f'\
b'\xfc\x00\x0f\xf8\x00\x03\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x12\x00\x00\x00\x00\x00\x00\x00\x7f\xff\x00\x7f\xff\x00\x7f\xff'\
b'\x00\x00\x07\x00\x00\x0e\x00\x00\x0c\x00\x00\x1c\x00\x00\x38\x00'\
b'\x00\x38\x00\x00\x70\x00\x00\x70\x00\x00\xe0\x00\x00\xe0\x00\x01'\
b'\xc0\x00\x01\xc0\x00\x03\x80\x00\x03\x80\x00\x03\x80\x00\x07\x00'\
b'\x00\x07\x00\x00\x07\x00\x00\x0e\x00\x00\x0e\x00\x00\x0e\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x12\x00\x00\x00\x00\x00\x00\x00'\
b'\x03\xe0\x00\x0f\xf8\x00\x1f\xfc\x00\x1c\x1e\x00\x38\x0e\x00\x38'\
b'\x0e\x00\x38\x0e\x00\x38\x0e\x00\x3c\x1e\x00\x1e\x3c\x00\x0f\xf8'\
b'\x00\x07\xf0\x00\x1f\xfc\x00\x3c\x1e\x00\x38\x0e\x00\x70\x07\x00'\
b'\x70\x07\x00\x70\x07\x00\x70\x07\x00\x78\x0e\x00\x3c\x1e\x00\x1f'\
b'\xfc\x00\x0f\xf8\x00\x03\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x12\x00\x00\x00\x00\x00\x00\x00\x03\xe0\x00\x0f\xf8\x00\x1f\xfc'\
b'\x00\x3c\x3e\x00\x38\x1e\x00\x78\x0e\x00\x70\x0f\x00\x70\x07\x00'\
b'\x70\x07\x00\x70\x07\x00\x70\x0f\x00\x70\x0f\x00\x38\x1f\x00\x3f'\
b'\xff\x00\x1f\xf7\x00\x07\xe7\x00\x00\x07\x00\x00\x0e\x00\x70\x0e'\
b'\x00\x78\x1e\x00\x3c\x3c\x00\x1f\xf8\x00\x1f\xf0\x00\x07\xc0\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x09\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0e\x00\x0e\x00\x0e\x00'\
b'\x0e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x0e\x00\x0e\x00\x0e\x00\x0e\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x0d\x00\x00\x00\x00\x00\x0f\x80\x1f\xc0\x38\xe0\x30\x60\x30\x60'\
b'\x30\x60\x38\xe0\x1f\xc0\x0f\x80\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'\
b'\x00\x00\x00\x00'

_sparse =\
b'\x20\x00\x09\x00\x25\x00\x12\x00\x28\x00\x23\x00\x29\x00\x2c\x00'\
b'\x2a\x00\x35\x00\x2b\x00\x3e\x00\x2c\x00\x4b\x00\x2d\x00\x54\x00'\
b'\x2e\x00\x5d\x00\x2f\x00\x66\x00\x30\x00\x6f\x00\x31\x00\x7c\x00'\
b'\x32\x00\x89\x00\x33\x00\x96\x00\x34\x00\xa3\x00\x35\x00\xb0\x00'\
b'\x36\x00\xbd\x00\x37\x00\xca\x00\x38\x00\xd7\x00\x39\x00\xe4\x00'\
b'\x3a\x00\xf1\x00\xb0\x00\xfa\x00'

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

    next_offs = doff + 2 + ((width - 1)//8 + 1) * 33
    return _mvfont[doff + 2:next_offs], 33, width
 
