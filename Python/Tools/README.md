## Test tools:

### `telnetRRF.py`
Implement a ObjectModel based fetch/update/display cycle in Python, basically a prototype for the 'heart' of PrintPy
* notes:
  * CPython; but I am trying to keep all the logic and data handling simple and low-memory for running on microPython.
    * eg: using global variables rather than passing the status as an object to/from functions.
  * Run on my desktop machine to run M409 ObjectModel queries over a network connection.
    * `telnet` is convenient to use remotely since it closely resembles the serial port.
  * See comment in RRFconfig.py.example for configuring connection details
  * Will be used to prototype the logic for the main code; doing this on the desktop is very convenient..
