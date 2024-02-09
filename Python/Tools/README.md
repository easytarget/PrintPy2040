## Test tools:

### `serialRRF.py`
Implement a ObjectModel based fetch/update/display cycle in Python, basically a prototype for the 'heart' of PrintPy
* Uses `M409` commands to query the ObjectModel, parses the responses to a Dictionary structure
* Requires `pyserial` when run in CPython
* notes:
  * CPython; but I am trying to keep all the logic and data handling simple and low-memory for running on microPython.
    * eg: using global variables rather than passing the status as an object to/from functions.
  * Runs on a PaspberryPI connected to the RRF USB/serial port
  * See comment in RRFconfig.py.example for configuring connection details
  * Will be used to prototype the logic for the main code; doing this on the desktop is very convenient..
