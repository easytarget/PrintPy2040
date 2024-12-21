# Micropython code
PrintPY is coded in micropython; and is intended to be uploaded by the user from a suitable IDE (tested with thonny, but ViperIDE is also nice for more experienced developers).

# Architecture
`printXIAO.py` is the main program; it runs a continual loop that queries the RRF controller to fetch the current objectModel (machine state). It then calls two output class modules to display data from the objectModel:
- `lumenXIAO.py` : Shows the controller status using the onboard NeoPixel on the Xiao RP2040 board.
- `heartbeatXIAO.py` : Shows a communication 'heartbeat' using the auxillary RGB led on the board.
- `outputI2Cx2.py` : Displays the machine state on a twin OLED display, showing the overall status; current temperatures and heater statuses; job status (when active), messages and network status.
  - The display is built entirely out of fonts (using symbol fonts where necesscary) and uses my own microPython fonts, font writer and marquee.
  - Single or Twin extruders are supported, as are systems with enclosures.
![Alpha demo](Docs/3-heaters-alpha3.jpg)

# Requirements:
There are no external dependencies or requirements needed, this folder contains the
`printXIAO` code itself and the external libraries it uses.

## SerialOM and EZfont Libraries
Development of the communications code happens in the `serialOM` repo:
https://github.com/easytarget/serialOM

Development of the Font display system (Font Writer, Marquee and the Fonts themselves) happens in the `microPyEZfonts` repo:
https://github.com/easytarget/microPyEZfonts

# Install
I do all development using the [**Thonny**](https://thonny.org/) IDE, this is a fairly simple tool, but I quite like it because of this it matches my needs. You can also use ViperIDE or any other development environment you are familiar with.

The 'Firmware' folder just contains the latest reference firmware; the image I am using and have tested with. This is just a copy of the generic firmware from the main microPython downloads site. There is no 'precompiled firmware' available for PrintPy2040.

Simply put the whole contents of this folder (/microPython/) excluding the 'Firmware' folder) in to the root of your device, keeping the directory structure.

## Config
You need to copy `config-default.py` to `config.py` in the root folder of your device.

Then make any changes you need (there are not many 'options' and the hardware defaults are set up for the XIAO 2040 board used here.
* The most important option here is the Baud rate for the serial port; you must match the speed here with the speed onfigured on your RRF controller. The default baud rate for PrintXIAO is :FINISH!

.. todo .. 'off' state list, Wifi mode settings, ?anything else..?

# Comissioning
You can run `printXIAO.py` from the REPL console to test.
