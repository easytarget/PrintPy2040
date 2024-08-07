### Same Idea; different MCU

# Proudly Presenting the PrintPy.

**A Work In Progress!**

* the case is done and printed
* the XIAO RP2040 board is in place
* wiring is complete
* Code prototyping is done
  * MICROPYTHON coding is ongoing.

# Hardware
This repo is principally about the hardware, code development is ongoing in https://github.com/easytarget/serialOM, released code will be placed here for reference.

See the [README](microPython/README.md) in the '[microPython](microPython/)' folder for more.

## Case
The case needs care when slicing and printing, some of the clearances are very tight. use a slicer with adaptive layer height features to make sure the screens and PCB's fit correctly.

![Case Render](Case/front.png) ![Case Render](Case/rear.png)

## Wiring
![Hookup Guide](Docs/printpy_bb.svg)

There is no PCB needed for this, the circuit should be wired + soldered directly in-place (this is fiddly, but possible)

## Connection
Take care with wiring this, it is important that the 5V supply does not contact the (3v3) TX/RX lines! The connector allows the plug to be reversed to swap TX/RX lines quickly and safely.

![Duet2 Loom](Docs/wireviz_uart_duet2.svg)
(Serial connection loom diagram generated by [wireviz](https://github.com/wireviz/WireViz) from the `.yaml` description [here](Docs/wireviz_uart_duet2.yaml))

## Alternate connections/deployments
### RP2040 I2C pins
If using an alternate RP2040 board please check the table below to determine which pins the I2C interfaces can be accessed on; and make sure the pins are correctly defined in the code.
```
I2C0 – SDA : GP0 / GP4 / GP8  / GP12 / GP16 / GP20
I2C0 – SCL : GP1 / GP5 / GP9  / GP13 / GP17 / GP21
I2C1 – SDA : GP2 / GP6 / GP10 / GP14 / GP18 / GP26
I2C1 – SCL : GP3 / GP7 / GP11 / GP15 / GP19 / GP27
```
