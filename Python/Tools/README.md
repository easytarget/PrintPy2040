## serialRRFom.py

## use:

### microDemo:
```[code=python]
from serialOM import serialOM
from serial import Serial

rrf = Serial('/dev/ttyACM0',57600)
OM=serialOM(rrf, {'FFF':[],'CNC':[],'Laser':[]}, quiet=True)
print('state: ' + OM.model['state']['status']
     + ', up: ' + str(OM.model['state']['upTime']) + 's')
```
### printPy demo:
--quick description here please--

### serialOM.py
Implements a RRF ObjectModel fetch/update cycle in Python, basically a prototype for the 'heart' of PrintPy
* Uses `M409` commands to query the ObjectModel, parses the responses to a Dictionary structure for output
  * Uses the `seqs` sequence numbers to limit load on the controller by only making verbose requests as needed.
  * Traps all serial errors and provides it's own `serialOMError` exception that can be trapped to handle communications issues seamlessly.
    * The `printPY.py` demo demonstrates this.
  * Returns a `serialOM.model` structure (dict) with all currently known data
  * After initial connection has been made `serialOM.update()` can be called to update and refresh the local ObjectModel
  * Can fetch different sets of top level ObjectModel keys depending on the master machine mode `FFF`,`CNC` or `Laser`.
  * Rebuilds the ObjectModel if it detects either a machine mode change, or a restart of the controller
* Requires `pyserial`
  * Install your distros pyserial package: eg: `sudo apt install python-serial`, or `pip install --user pyserial`, or use a virtualenv (advanced users).
  * On linux make sure your user is in the 'dialout' group to access the devices
  * There is no reason why this wont run on Windows, but I have not tried this. You will need a Python 3 install with pyserial, and change the device path to the windows equivalent.
* Notes:
  * CPython; but I am trying to keep all the logic and data handling simple and low-memory for running on microPython.
    * Non micropython standard libs are discouraged unless they have a easy micropython equivalent/local lib.
    * All times are in `ms` (micropython uses `int(ms)` for it's timing basics rather than `float(seconds)`)
  * Tested and developed on a RaspberryPI connected to my Duet2 wifi via USB/serial
