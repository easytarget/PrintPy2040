# Reference firmware package from micropython download site
Kept here for reference; this is the firmware I tested against.

### Vanilla
The Upstream (vanilla) firmware was downloaded from the MicroPython downloads page:

'''
RPI_PICO-20241025-v1.24.0.uf2
'''

### Debug
But I compiled a version of this with just one change; I enabled the `sys.atexit()` option to assist in debugging while running my multi-threaded code. This firmware is here:

'''
RPI_PICO-v1.24.0-115-gbdda91fe7-atexit.uf2
'''

You do not need to use this for your board; it was mainly for debugging. And not very useful as it turns out; the RP2040 micropython threading issues are deeper than this.
