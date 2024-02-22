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

class handleOM:
    '''
        Object Model communications tools class provides
        specific functions used to fetch and process OM keys via
        a serial/stream interface
    '''

    def __init__(self, rrf, config, rawLog=None):
        self.rrf = rrf
        self.config = config
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
            self._commsFail("Failed to query length of input buffer")
        if waiting > 0:
            try:
                junk = self.rrf.read().decode('ascii')
            except:
                self._commsFail("Failed to flush input buffer")
            if self.rawLog:
                self.rawLog.write(junk)
        # Now send our command (+ checksum)
        try:
            self.rrf.write(bytearray(code + "*" + str(chksum) + "\r\n",'utf-8'))
        except:
            self._commsFail('Gcode serial write failed')
        try:
            self.rrf.flush()
        except:
            self._commsFail('Gcode serial write buffer flush failed')
        # log what we sent
        if self.rawLog:
            self.rawLog.write("\n> " + code + "*" + str(chksum) + "\n")

    def firmwareRequest(self):
        # Use M115 to (re-establish comms and verify firmware
        # Send the M115 info request and look for a sensible reply
        print('> M115\n>> ',end='')
        try:
            self.rrf.write(b'\n')
        except:
            self._commsFail('M115 initial serial write failed')
        self.sendGcode('M115')
        try:
            response = self.rrf.read_until(b"ok").decode('ascii')
        except:
            self._commsFail("Failed to read M115 response")
        print(response.replace('\n','\n>> '))
        if self.rawLog:
            self.rawLog.write(response + '\n')
        if not 'RepRapFirmware' in response:
            return False
        return True

    # Handle serial or comms errors
    def _commsFail(self,why):
        print('Communications error: ' + why +'\nRestarting in ',end='')
        # Pause for a few seconds, then restart
        for c in range(self.config.rebootDelay,0,-1):
            print(c,end=' ',flush=True)
            sleep_ms(1000)
        print()
        execv(executable, ['python'] + argv)   #  CPython
        #reset() # Micropython; reboot module

    # Handle a request cycle to the OM
    def _request(self, out, OMkey, OMflags):
        '''
            This is the main request send/recieve function, it sends a OM key request to the
            controller and returns True when a valid response was recieved, False otherwise.
        '''
        response = self._query(OMkey, OMflags)
        if len(response) == 0:
            return False
        else:
            return self._updateOM(out,response)

    # send query and await response
    def _query(self, OMkey, OMflags):
        '''
            Sends a query and waits for response data,
            returns a list of response lines, or None
        '''
        # Construct the M409 command
        cmd = 'M409 F"' + OMflags + '" K"' + OMkey + '"'
        # Send the command to RRF
        self.sendGcode(cmd)
        # And wait for a response
        requestTime = ticks_ms()
        response = []
        nest = 0;
        maybeJSON = ''
        notJSON = ''
        # only look for responses within the requestTimeout period
        while (ticks_diff(ticks_ms(),requestTime) < self.config.requestTimeout):
            # Read a character, tolerate and ignore decoder errors
            try:
                char = self.rrf.read(1).decode('ascii')
            except UnicodeDecodeError:
                char = None
            except:
                self._commsFail('Serial/UART failed: Cannot read from controller')
            if self.rawLog and char:
                self.rawLog.write(char)
            # for each char classify as either 'possibly in json block' or not.
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
                        # if we see 'ok' outside of a JSON block break immediately from wait loop
                        if (notJSON[-2:] == 'ok'):
                            break
        return response

    def _updateOM(self,out,response):
        # Merge or replace the local OM copy with results from the query

        # A Local function for recursive/iterative merge of dict/list structures.
        # https://stackoverflow.com/questions/19378143/python-merging-two-arbitrary-data-structures#1
        def merge(a, b):
            if isinstance(a, dict) and isinstance(b, dict):
                d = dict(a)
                d.update({k: merge(a.get(k, None), b[k]) for k in b})
                return d
            if isinstance(a, list) and isinstance(b, list):
                return [merge(x, y) for x, y in zip_longest(a, b)]
            return a if b is None else b

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
                # M409 may legitimately return an empty key, only process keys with contents
                if payload['result'] != None:
                    # We have a result, store it
                    if 'f' in payload['flags']:
                        # Frequent updates just refresh the existing key
                        out.localOM[payload['key']] = merge(out.localOM[payload['key']],payload['result'])
                    else:
                        # Verbose output replaces the existing key
                        out.localOM[payload['key']] = payload['result']
            else:
                # Valid JSON but no 'result' data in it
                return False
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
                self._commsFail('failed to accqire initial "' + key + '" data')
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
                self._commsFail('failed to accqire initial "' + key + '" data')
        return self.machineMode

    def update(self, out):
        nofail = True  # track (soft) failures
        if self.seqs == None:
            # SBC mode; do a verbose update of all keys
            for key in ['state'] + out.omKeys[self.machineMode]:
                #print('#',end='')  # debug
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
