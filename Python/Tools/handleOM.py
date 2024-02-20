# Common classes between CPython and microPython
from json import loads

#from time import ticks_ms,ticks_diff  # microPython
from timeStubs import sleep_ms,ticks_ms,ticks_diff  # CPython

# CPython standard libs that need to be provided locally for microPython
from itertools import zip_longest
from functools import reduce

class handleOM:
    '''
        Object Model communications tools class
        specific functions used to fetch and process OM keys via
        a serial/bitstream interface
    '''

    def __init__(self, rrf, rawLog=None, nonJsonLog=None):
        self.rrf = rrf
        self.rawLog = rawLog
        self.nonJsonLog = nonJsonLog
        # string of valid ascii chars for JSON response body
        self.jsonChars = bytearray(range(0x20,0x7F)).decode('ascii')
        print('OMhandler is starting')

    # send a gcode+chksum then block until it is sent, or error
    def sendGcode(self, code):
        chksum = reduce(lambda x, y: x ^ y, map(ord, code))
        # absorb whatever is in our buffer
        if self.rrf.in_waiting > 0:
            junk = self.rrf.read().decode('ascii')
            self.rawLog.write(junk)
            self.nonJsonLog.write(junk)
        # Now send our command (+ checksum)
        try:
            self.rrf.write(bytearray(code + "*" + str(chksum) + "\r\n",'utf-8'))
        except:
            print('Write Failed')
            return False
        # wait for it to be sent
        try:
            self.rrf.flush()
        except:
            print('Flush Failed')
            return False
        # log what we sent
        if self.rawLog:
            self.rawLog.write("\n> " + code + "*" + str(chksum) + "\n")
        if self.nonJsonLog:
            self.nonJsonLog.write("\n> " + code + "*" + str(chksum) + "\n")
        return True

    def firmwareRequest(self):
        # Use M115 to (re)establish comms and verify firmware
        # Send the M115 info request and look for a sensible reply
        self.rrf.write(b'\n')
        if not self.sendGcode('M115'):
            return False
        response = self.rrf.read_until(b"ok").decode('ascii')
        if not 'RepRapFirmware' in response:
            return False
        print(response)
        return True

    # Handle a request to the OM
    def request(self, out, OMkey, OMflags, timeout=250):
        # Recursive/iterative merge of dict/list structures.
        # https://stackoverflow.com/questions/19378143/python-merging-two-arbitrary-data-structures#1
        def merge(a, b):
            if isinstance(a, dict) and isinstance(b, dict):
                d = dict(a)
                d.update({k: merge(a.get(k, None), b[k]) for k in b})
                return d
            if isinstance(a, list) and isinstance(b, list):
                return [merge(x, y) for x, y in zip_longest(a, b)]
            return a if b is None else b

        # Construct the command (no newline)
        cmd = 'M409 F"' + OMflags + '" K"' + OMkey + '"'
        # Send the M409 command to RRF
        if not self.sendGcode(cmd):
            commsFail('Serial/UART failed: Cannot write to controller')
            return False
        requestTime = ticks_ms()
        # And wait for a response
        response = []
        nest = 0;
        maybeJSON = ''
        notJSON = ''
        while (ticks_diff(ticks_ms(),requestTime) < timeout):
            try:
                char = self.rrf.read(1).decode('ascii')
            except UnicodeDecodeError:
                char = None
            except:
                commsFail('Serial/UART failed: Cannot read from controller')
            if self.rawLog and (char != None):
                self.rawLog.write(char)
            if char:
                if char in self.jsonChars:
                    if char == '{':
                        nest += 1
                    if nest > 0:
                        maybeJSON = maybeJSON + char
                    else:
                        notJSON = notJSON + char
                    if char == '}':
                        nest -= 1
                    if nest == 0:
                        if maybeJSON:
                            notJSON = '{...}' + notJSON  # helps debug
                            response.append(maybeJSON)
                            maybeJSON = ""
                        if (notJSON[-2:] == 'ok'):
                            break
        if self.nonJsonLog:
            self.nonJsonLog.write(notJSON + '\n')
        if len(response) == 0:
            #print('No sensible response from "',cmd,'" :: ',notJSON)
            return False
        # Process Json candidate lines
        for line in response:
            # Load as a json data structure
            try:
                payload = loads(line)
            except:
                # invalid JSON, print and skip to next line
                print('Invalid JSON:',line)
                continue
            # Update localOM data
            if 'result' in payload.keys():
                if payload['result'] == None:
                    # if reult is None the key doesnt exist
                    return False
                else:
                    # We have a valid result, store it
                    if 'v' in OMflags:
                        # Verbose output replaces the existing key
                        out.localOM[payload['key']] = payload['result']
                    else:
                        # Frequent updates just refresh the existing key
                        out.localOM[payload['key']] = merge(out.localOM[payload['key']],payload['result'])
            else:
                # Valid JSON but no 'result' data in it
                return False
        # If we got here; we had a successful cycle
        return True

    def seqRequest(self, out, OMseqcounter, machineMode):
        # Send a 'seqs' request to the OM, updates localOM and returns
        # a list of keys where the sequence number has changed
        changed=[]
        if self.request(out,'seqs','fnd99'):
            for key in out.verboseKeys[machineMode]:
                if OMseqcounter[key] != out.localOM['seqs'][key]:
                    changed.append(key)
                    OMseqcounter[key] = out.localOM['seqs'][key]
        else:
            print('Sequence key request failed')
        return changed
