# Common classes between CPython and microPython
from json import loads

#from time import sleep_ms,ticks_ms,ticks_diff  # microPython
from timeStubs import sleep_ms,ticks_ms,ticks_diff  # CPython

#from machine import reset             # microPython
from sys import executable,argv        # CPython
from os import execv                   # CPython

# CPython standard libs that need to be provided locally for microPython
from itertools import zip_longest
from functools import reduce

# Handle serial or comms errors
def commsFail(why):
    print('Communications error: ' + why +'\nRestarting in ',end='')
    # Pause for 8 seconds, then restart
    for c in range(8,0,-1):
        print(c,end=' ',flush=True)
        sleep_ms(1000)
    print()
    execv(executable, ['python'] + argv)   #  CPython
    #reset() # Micropython; reboot module

class handleOM:
    '''
        Object Model communications tools class
        specific functions used to fetch and process OM keys via
        a serial/bitstream interface
    '''

    def __init__(self, rrf, rawLog=None):
        self.rrf = rrf
        self.rawLog = rawLog
        self.seqs = None
        self.machineMode = 'unavailable'
        # string of valid ascii chars for JSON response body
        self.jsonChars = bytearray(range(0x20,0x7F)).decode('ascii')
        print('OMhandler is starting')

    # send a gcode+chksum then block until it is sent, or error
    def sendGcode(self, code):
        chksum = reduce(lambda x, y: x ^ y, map(ord, code))
        # absorb whatever is in our buffer
        try:
            waiting = self.rrf.in_waiting     # CPython, micropython use 'any()'
        except:
            commsFail("Failed to flush input buffer")
        if waiting > 0:
            junk = self.rrf.read().decode('ascii')
            if self.rawLog:
                self.rawLog.write(junk)
        # Now send our command (+ checksum)
        try:
            self.rrf.write(bytearray(code + "*" + str(chksum) + "\r\n",'utf-8'))
        except:
            print('Serial write failed')
            return False
        try:
            self.rrf.flush()
        except:
            print('Serial write buffer flush failed')
            return False
        # log what we sent
        if self.rawLog:
            self.rawLog.write("\n> " + code + "*" + str(chksum) + "\n")
        return True

    def firmwareRequest(self):
        # Use M115 to (re-establish comms and verify firmware
        # Send the M115 info request and look for a sensible reply
        print('> M115\n> ',end='')
        self.rrf.write(b'\n')
        if not self.sendGcode('M115'):
            return False
        response = self.rrf.read_until(b"ok").decode('ascii')
        print(response)
        if self.rawLog:
            self.rawLog.write(response + '\n')
        if not 'RepRapFirmware' in response:
            return False
        return True

    # Handle a request to the OM
    def _request(self, out, OMkey, OMflags, timeout=250):
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
                            #notJSON = '{...}' + notJSON  # helps debug
                            response.append(maybeJSON)
                            maybeJSON = ""
                        if (notJSON[-2:] == 'ok'):
                            break
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
                if payload['result'] != None:
                    # We have a result, store it
                    if 'v' in OMflags:
                        # Verbose output replaces the existing key
                        out.localOM[payload['key']] = payload['result']
                    else:
                        # Frequent updates just refresh the existing key
                        out.localOM[payload['key']] = merge(out.localOM[payload['key']],payload['result'])
                else:
                    # empty result, only fail if key is not in seqs, M409 may legitimately return an empty key.
                    if payload['key'] not in self.seqs:
                        return False
            else:
                # Valid JSON but no 'result' data in it
                return False
        # If we got here; we had a successful cycle
        return True

    def _seqRequest(self, out):
        # Send a 'seqs' request to the OM, updates localOM and returns
        # a list of keys where the sequence number has changed
        changed=[]
        if self._request(out,'seqs','fnd99'):
            for key in ['state'] + out.omKeys[self.machineMode]:
                if self.seqs[key] != out.localOM['seqs'][key]:
                    changed.append(key)
                    self.seqs[key] = out.localOM['seqs'][key]
        else:
            print('Sequence key request failed')
        return changed

    def firstRequest(self,out):
        # request the initial iseqs and state keys
        for key in ['seqs','state']:
            if not self._request(out,key,'vnd99'):
                commsFail('failed to accqire initial "' + key + '" data')
        # Machine Mode
        self.machineMode = out.localOM['state']['machineMode']
        # Determine SBC mode
        if (out.localOM['seqs'] == None) or (len(out.localOM['seqs']) == 0):
            print('RRF controller is in SBC mode')
            self.seqs = None
        else:
            print('RRF controller is standalone')
            self.seqs = out.localOM['seqs']
        # Get initial data set
        for key in out.omKeys[self.machineMode]:
            if not self._request(out,key,'vnd99'):
                commsFail('failed to accqire initial "' + key + '" data')
        return self.machineMode

    def update(self, out):
        nofail = True  # track (soft) failures
        if self.seqs == None:
            # SBC mode; do a verbose update of all keys
            for key in ['state'] + out.omKeys[self.machineMode]:
                if not self._request(out,key,'vnd99'):
                    nofail = False;
        else:
            # seqs mode; only update frequent data unless seqs have changed
            verboseList = self._seqRequest(out)
            for key in ['state'] + out.omKeys[self.machineMode]:
                if key in verboseList:
                    #print('*',end='')  # debug
                    if not self._request(out,key,'vnd99'):
                        nofail = False;
                else:
                    #print('.',end='')  # debug
                    if not self._request(out,key,'fnd99'):
                        nofail = False;
        return nofail