# Reference firmware package from micropython download site

A copy is kept here for reference; this is the current firmware I am using on my RP2040, and the code has ben extensively tested on this.

```
SEEED_XIAO_RP2040-20260824-v1.29.0.uf2
```

This Upstream (vanilla) firmware was downloaded from the MicroPython downloads page:
https://micropython.org/download/SEEED_XIAO_RP2040/

The `SEEED_XIAO_RP2040-20260824-v1.29.0.atexit.uf2` firmware was built by me; it enables the `atexit()` function within micropython for catching all `exit()` events. This is handy for stopping threads, cores and timers in multi-thread code such as PrintPY; and is detected and used to give smoother debugging if available.

Now this project is released I do not intend to track, upgrade and test every new MicroPythoin release.
