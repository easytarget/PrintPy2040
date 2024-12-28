# Micropython code
PrintPY is coded in [MicroPython](https://micropython.org/); and is intended to be uploaded by the user from a suitable IDE (tested with Thonny, but ViperIDE is also nice for more experienced developers).

As with the Hardware document assuming you can 3d Print, solder and read a wiring diagram, this document assumes you can set up and connect to your device with MicroPython without needing step-by-step instructions.
* If this is new to you I suggest you start with the [XIAO2040 micropython guide](https://wiki.seeedstudio.com/XIAO-RP2040-with-MicroPython/) from SeeedStudio, and use [**Thonny**](https://thonny.org/) as an IDE.

# RRF config:
You need to set up the Comms port on your printer correctly to 'no CRC/checksum, 230400 baud'.
* For testing you can use the console to send:
* `M575 P1 B230400 S0`
* For a Duet2 or 3 machine using the default (panelDue) serial (UART) interface your `config.g` needs to include ths line:
* This can normally go after the USB port setting (*M575 P0 ....*) line.
* Later Duet models have additional UART ports that could be used; you will need to adjust ['M575'](https://docs.duet3d.com/User_manual/Reference/Gcodes#m575-set-serial-comms-parameters) as necesscary for them.
* Do not change the `S0` parameter; PrintPY is not compatible with CRC or Checksumming.

# Commissioning:
Start your micropython environment (Thonny, Viper, etc..) and connect to the XIAO.
* Flash with the Firmware in the 'Firmware' folder.
  * ..or a later firmware from the main MicroPython site
  * the version in this repo is the Firmware I have tested with
* After sucessfully flashing you should be sitting at the REPL console of the device in your environement; eg:
```python
  MicroPython v1.24.0 on 2024-10-25; Raspberry Pi Pico with RP2040
  Type "help()" for more information.
  >>> 
```
# Installing:
Upload the whole of this folder ('micropython') onto the root of your device; and ('micropython/fonts') as a folder on the device.
* The 'Firmware' folder should not be copied; the README does not need copying euther.

## Initial Configuration:
Copy `config-default.py` to 'config.py` on the device.
* if you are using alternate hardware pins etc. you will need to adjust the hardware config definitions here
* See the [config](#Config) section below for more.

# Test Hardware:
*Note: The hardware test script reads its configuration from the config file above.*
* Run `hwTest.py` omn the device:
```python
Testing printXIAO comms, screen, pixel and button
UART initialised
Button present on: GPIO2
sent: M122
recieved: b'{"seq":28720,"resp":"=== Diagnostics ===\\n"}\n{"seq":28721,"resp":"RepRapFirmware for Duet 2 WiFi/Ethernet version 3.5.4 (2024-11-24 10:43:42) running on Duet WiFi 1.02 or later\\n"}\n{"seq":28722,"resp":"Board ID: 08DGM-9568A-F23SJ-6JTD0-3S46L-KVVVF\\n"}\n{"seq":28723,"resp":"Used output buffers: 3 of 26 (16 max)\\n"}\n'
button: Pressed
sent: M122
recieved: b'{"seq":28810,"resp":"=== Diagnostics ===\\n"}\n{"seq":28811,"resp":"RepRapFirmware for Duet 2 WiFi/Ethernet version 3.5.4 (2024-11-24 10:43:42) running on Duet WiFi 1.02 or later\\n"}\n{"seq":28812,"resp":"Board ID: 08DGM-9568A-F23SJ-6JTD0-3S46L-KVVVF\\n"}\n{"seq":28813,"resp":"Used output buffers: 3 of 26 (16 max)\\n"}\n'
sent: M122
..etc..
```
* You should see the OLED displays outlined and showing 'left' and 'right' as appropriate; the NeoPixel shuld be cycling R->G->B, if you press the button you should see a message on REPL console.
* The script sends [`M115`](https://docs.duet3d.com/User_manual/Reference/Gcodes#m115-get-firmware-version-and-capabilities) every second to the connected RRF machine; and then returns the (JSON encoded) output to the REPL console:

If you do not see any serial output the first thing to do is test (swap) the polarity of the RX and TX lines by reversing the connector on the PrintPY.
* The second thing to test is that both the PrintPy and RRF controller have the baud rate configured properly.

# Commissioning:
Once the test script is running correctly you can try running 'printXIAO.py' directly from the IDE. You should now see everything running, with a brief splash-screen and then the current printer status displayed. On the console you should see:
```
printXIAO is starting
UART initialised
starting output
connected to ObjectModel
button present on: GPIO2
PrintPY::printXIAO is running
[519ms, 112000b] Up: 3d:12h:52:47 | Off | ip: 10.0.0.30
[504ms, 112000b] Up: 3d:12h:52:48 | Off | ip: 10.0.0.30
[505ms, 112000b] Up: 3d:12h:52:49 | Off | ip: 10.0.0.30
etc..
```
The (default configured) status lines show:
* [Fetch cycle time, free memory after fetching and collect()ing]
* Uptime reported by the Controller firmware
* Main status | Wifi Status | Job Progress (if any) | System messages (if any)

The Neopixel will be flashing with the printer 'mood', the heartbeat LED should be cycling as requests are sent.

## Dealing with multi-thread reset errors on the RP2040!
This is annoying; the RP2040 micropython port does not handle multi-cpu systems properly when they have threads running on the second CPU. 

*Important:* Once the main printXIAO code is running you can interrupt the main loop by pressing **ctrl-c** in the REPL console, but this fails to fully 'soft reset' the board. 
1) Crtl-c' in the repl console should be followed immediately by running 'micropython.reset()' to fully reset the hardware.
3) Press the reset button on the XIAO board (it's tiny and hard to access, especially once the wiring is done, use a small non-conductive plastic rod to do this)
4) Force the reset by unplugging it completely from the printer and usb-c.

*If you do not do this there is a high chance the board will quickly stop responding to REPL commands; it gets into some sort of bad USB state. This plagued me during the last stages of development.*

# AutoStart at boot
Once configured; enable running at boot time by editing the last four lines of the config as described in the comments. Then mount on your machine, close the case, and enjoy seeing your printers status at-a-glance.

Once Autostart is enabled the multi-thread errors discussed above are more serious since the code is starting automatically after you reset it. The solution is pressing **ctrl-c** quickly after the reset/reboot, before the main code loop starts. This is why there is a startup countdown, to give console users a chance to interrupt the code *before* the second CPU thread starts.

# Architecture
`printXIAO.py` is the main program; it runs a continual loop that queries the RRF controller to fetch the current objectModel (machine state). It then calls two output class modules to display data from the objectModel:
- `lumenXIAO.py` : Shows the controller status using the onboard NeoPixel on the Xiao RP2040 board.
- `heartbeatXIAO.py` : Shows a communication 'heartbeat' using the auxillary RGB led on the board.
- `outputI2Cx2.py` : Displays the machine state on a twin OLED display, showing the overall status; current temperatures and heater statuses; job status (when active), messages and network status.
  - The display is built entirely out of fonts (using symbol fonts where necesscary) and uses my own microPython fonts, font writer and marquee.
  - Single or Twin extruders are supported, as are systems with enclosures.
![Alpha demo](../Docs/3-heaters-alpha3.jpg)

# Requirements:
There are no external dependencies or requirements needed, this folder contains the `printXIAO` code itself and all the libraries it uses.

### SerialOM
Development of the communications code happens in the `serialOM` repo:
https://github.com/easytarget/serialOM

### EZfont Libraries and fonts are in the `fonts` folder
Development of the Font display system (Font Writer, Marquee and the Fonts themselves) happens in the `microPyEZfonts` repo:
https://github.com/easytarget/microPyEZfonts

## Config
As noted above, you need to copy `config-default.py` to `config.py` in the root folder of your device.

Then make any changes you might want.
* See the comments in the config file.
* There are not many 'user options' to play with, and the defaults are set up sensibly for the XIAO 2040 board used here.
* You can set the list of states where the Display should turn off:
  * OLED displays can [burn in](https://forum.makerforums.info/t/oled-display-burn-in-the-evidence/90223) if left on all the time, making the output look reaaly ugly!
  * Turning the displays off when the Printer is `off` is a very good idea.
  * If your printer is permanently on it may be a good idea to add `[idle]` as well as `[off]` to the list of screen off states.
* Another important option here is the Baud rate for the serial port; you must match the speed with the speed configured on your controller. The default baud rate for PrintXIAO is 230400 baud, no parity.
* Only mess with the Hardware settings if you are using alternate wiring or boards etc..
* Do not try to 'speed up' the main (once per second by default) fetch/update cycle too much, the cpu needs at least 500ms to do each fetch cycle, plus 150ms to render the updates to the display panels.
* NeoPixel and display brightnesses can be set, you may want to reduce these in a dark workshop. You can set a different brightness for 'off states'.
* THe default network interface can be defined (for controllers with more than one) as can the default commands sent to enable/disable the network.
