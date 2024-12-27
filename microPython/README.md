# Micropython code
PrintPY is coded in micropython; and is intended to be uploaded by the user from a suitable IDE (tested with Thonny, but ViperIDE is also nice for more experienced developers).

As with the Hardware I assume you can set up and connect to your device with MicroPython; if this is new to you I suggest you start with the XIAO setup guide from SeeedStudio, and use Thonny as an IDE.

# RRF config:
You need to set the Comms port you are using on the Duet/RRF board correctly for the speed; 230400 baud by default.
* For a Duet2 or 3 machine using the default (panelDue) uart interface yur `config.g` needs to include the following:
  `M575 P1 B230400 S0`
* This can normally go after the USB port setting (*M575 P0 ....*) line, you can also send it from the console for testing.

# Commissioning:
Start your micropython environment (Thonny, Viper, etc..) and connect to the XIAO.
* Flash with the Firmware in the 'Firmware' folder.
  * ..or a later firmware from the main MicroPython site
  * the version in this repo is the Firmware I have tested with
* You want to be sitting at the REPL console in your environement; eg:
```python
  MicroPython v1.24.0 on 2024-10-25; Raspberry Pi Pico with RP2040
  Type "help()" for more information.
  >>> 
```
Upload the whole of this folder ('micropython') and ('micropython/fonts') onto the root of your device.
* copy `config-default.py` to 'config.py` on the device
* run `hwTest.py`:
```python
  Testing printXIAO comms, screen, pixel and button
  UART initialised
  Button present on: GPIO2
  etc.. TODO!
```
* You should see the displays showing 'left' and 'right' as appropriate; the NeoPixel shuld be cycling R->G->B, if you press the button you should see a message on REPL console.
* The script sends [`M115`](https://docs.duet3d.com/User_manual/Reference/Gcodes#m115-get-firmware-version-and-capabilities) every second to the connected RRF machine; and then returns the output to the REPL console:

If you do not see any serial output the first thing to do is test (swap) the polarity of the RX and TX lines by reversing the connector on the PrintPY.
* The second thing to test is that both the PrintPy and RRF controller have the baud rate configured properly.

Once the test script is running you can try running 'printXIAO.py' directly from the IDE. You should now see everything running.
```
TODO:
```

If you want to change screen brightnesses or timeouts look at the settings in the onfig file.

Once happy with operation enable running at boot time by editing the last four lines of the config as described in the comments. Then mount on your machine, close the case, and enjoy seeing your printers status at-a-glance.

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

## SerialOM and EZfont Libraries and fonts are in the `fonts` folder
Development of the communications code happens in the `serialOM` repo:
https://github.com/easytarget/serialOM

Development of the Font display system (Font Writer, Marquee and the Fonts themselves) happens in the `microPyEZfonts` repo:
https://github.com/easytarget/microPyEZfonts

# Install (see [comissioning above](#Comissioning:))
I do all development using the [**Thonny**](https://thonny.org/) IDE, this is a fairly simple tool, but I quite like it because of this it matches my needs. You can also use ViperIDE or any other development environment you are familiar with.

The 'Firmware' folder just contains the latest reference firmware; the image I am using and have tested with. This is just a copy of the generic firmware from the main microPython downloads site. There is no 'precompiled firmware' available for PrintPy2040.

Simply put the whole contents of this folder (/microPython/) excluding the 'Firmware' folder) in to the root of your device, keeping the directory structure.

## Config
You need to copy `config-default.py` to `config.py` in the root folder of your device.

Then make any changes you need (there are not many 'options' and the hardware defaults are set up for the XIAO 2040 board used here.
* You can set the list of states where the Display should turn off;
  * OLED displays can [burn in](https://forum.makerforums.info/t/oled-display-burn-in-the-evidence/90223) if left on all the time, making the output look reaaly ugly!
  * Turning the displays off when the Printer is `off` is a very good idea.
  * If your printer is permanently on it may be a good idea to add `[idle]` as well as `[off]` to the list of screen off states.
* Another important option here is the Baud rate for the serial port; you must match the speed here with the speed onfigured on your RRF controller. The default baud rate for PrintXIAO is 230400 baud, no parity.
* Only mess with the Hardware settings if you are using alternate wiring or boards etc..
* Do not try to 'speed up' the main (once per second by default) fetch/update cycle too much, the cpu needs at least 600ms to do each fetch/update cycle.
* NeoPixel and display brightnesses can be set, you may want to reduce these for a very dim workshop.


.. todo .. 'off' state list, Wifi mode settings, ?anything else..?
