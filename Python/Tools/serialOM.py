# Common classes between CPython and microPython
from json import loads

#from time import sleep_ms,ticks_ms,ticks_diff  # microPython
from timeStubs import sleep_ms,ticks_ms,ticks_diff  # CPython

#from machine import reset             # microPython
from sys import executable,argv,exit   # CPython
from os import execv                   # CPython

# CPython standard libs that need to be provided locally for microPython
from itertools import zip_longest
from functools import reduce

class serialOM:
    '''
        Object Model communications tools class provides
        specific functions used to fetch and process OM keys via
        a serial/stream interface
    '''

    def __init__(self, rrf, config, rawLog=None, restartOnFail=False):
        self.rrf = rrf
        self.config = config
        self.rawLog = rawLog
        self.restartOnFail = restartOnFail
        self.seqs = None
        self.machineMode = 'unavailable'
        # string of valid ascii chars for JSON response body
        self.jsonChars = bytearray(range(0x20,0x7F)).decode('ascii')
        print('jsonChars : ',self.jsonChars)
        print('serialOM is starting')


    # Handle serial or comms errors
    def _commsFail(self,why,error):
        print('Communications error: ' + why)
        print('>>> ' + str(error).replace('\n','\n>>> '))
        if self.restartOnFail:
            print('Restarting in ',end='')
            # Pause for a few seconds
            for c in range(self.config.rebootDelay,0,-1):
                print(c,end=' ',flush=True)
                sleep_ms(1000)
            print()
            # CPython; restart with original arguments
            execv(executable, ['python'] + argv)
            # Micropython; reboot module
            #reset()
        else:
            # TODO; raise an exception.. (and define one first!)
            print('Exiting')
            exit(1)

    # Handle a request cycle to the OM
    def _request(self, out, OMkey, OMflags):
        '''
            This is the main request send/recieve function, it sends a OM key request to the
            controller and returns True when a valid response was recieved, False otherwise.
        '''
        # Construct the M409 command
        cmd = 'M409 F"' + OMflags + '" K"' + OMkey + '"'
        queryResponse = self.getResponse(cmd)
        jsonResponse = self._onlyJson(queryResponse)
        if len(jsonResponse) == 0:
            return False
        else:
            return self._updateOM(out,jsonResponse,OMkey)

    def _onlyJson(self,queryResponse):
        # return JSON candidates from the query response
        if len(queryResponse) == 0:
            return []
        jsonResponse = []
        nest = 0
        for line in queryResponse:
            json = ''
            for char in line or '':
                if char == '{':
                    nest += 1
                if nest > 0 :
                    json += char
                if char == '}':
                    nest -= 1
                    if nest <0:
                        break
                    elif nest == 0:
                        jsonResponse.append(json)
                        json = ''
        #print('\nJSON Response: ',jsonResponse)
        return jsonResponse

    def _updateOM(self,out,response,OMkey):
        # Merge or replace the local OM copy with results from the query

        def merge(a, b):
            # A Local function for recursive/iterative merge of dict/list structures.
            # https://stackoverflow.com/questions/19378143/python-merging-two-arbitrary-data-structures#1
            if isinstance(a, dict) and isinstance(b, dict):
                d = dict(a)
                d.update({k: merge(a.get(k, None), b[k]) for k in b})
                return d
            if isinstance(a, list) and isinstance(b, list):
                return [merge(x, y) for x, y in zip_longest(a, b)]
            return a if b is None else b

        # Process Json candidate lines
        success = False
        for line in response:
            # Load as a json data structure
            try:
                payload = loads(line)
            except:
                # invalid JSON, print and skip to next line
                print('Invalid JSON:',line)
                continue
            # Update localOM data
            if 'key' not in payload.keys():
                # Valid JSON but no 'key' data in it
                continue
            elif payload['key'] != OMkey:
                # Valid JSON but not for the key we requested
                continue
            elif 'result' not in payload.keys():
                # Valid JSON but no 'result' data in it
                continue
            # We have a result, store it
            if 'f' in payload['flags']:
                # Frequent updates just refresh the existing key as needed
                if payload['result'] != None:
                    out.localOM[payload['key']] = merge(out.localOM[payload['key']],payload['result'])
                # M409 may legitimately return an empty key when getting frequent data
                success = True
            else:
                # Verbose output replaces the existing key if a result is supplied
                if payload['result'] != None:
                    out.localOM[payload['key']] = payload['result']
                    success = True
        return success

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

    def sendGcode(self, code):
        # send a gcode+chksum then block until it is sent, or error
        chksum = reduce(lambda x, y: x ^ y, map(ord, code))
        # absorb whatever is in our buffer
        try:
            waiting = self.rrf.in_waiting     # CPython, micropython use 'any()'
        except Exception as error:
            self._commsFail("Failed to query length of input buffer",error)
        if waiting > 0:
            try:
                junk = self.rrf.read().decode('ascii')
            except Exception as error:
                self._commsFail("Failed to flush input buffer",error)
            if self.rawLog:
                self.rawLog.write(junk)
        # send command (+ checksum)
        try:
            self.rrf.write(bytearray(code + "*" + str(chksum) + "\r\n",'utf-8'))
        except Exception as error:
            self._commsFail('Gcode serial write failed',error)
        try:
            self.rrf.flush()
        except Exception as error:
            self._commsFail('Gcode serial write buffer flush failed',error)
        # log what we sent
        if self.rawLog:
            self.rawLog.write("\n> " + code + "*" + str(chksum) + "\n")

    def firmwareRequest(self):

        # TODO: re-write this to use 'getResponse' !!!!!

        # Use M115 to (re-establish comms and verify firmware
        # Send the M115 info request and look for a sensible reply
        print('> M115\n>> ',end='')
        try:
            self.rrf.write(b'\n')
        except Exception as error:
            self._commsFail('M115 initial serial write failed',error)
        self.sendGcode('M115')
        # wait looking for a response
        response = ''
        sent = ticks_ms()
        while ticks_diff(ticks_ms(),sent) < self.config.fwCheckTimeout:
            try:
                response += self.rrf.read().decode('ascii')
            except Exception as error:
                self._commsFail("Failed to read M115 response",error)
        print(response.replace('\n','\n>> '))
        if self.rawLog:
            self.rawLog.write(response + '\n')
        # A basic test to see if we have an RRF firmware
        # - Ideally expand to add more checks, eg version.
        if 'RepRapFirmware' in response:
            return True
        return False

    def firstRequest(self,out):
        # request the initial seqs and state keys
        for key in ['seqs','state']:
            if not self._request(out,key,'vnd99'):
                print('failed to acqire initial "' + key + '" data')
                return None
        # Machine Mode
        self.machineMode = out.localOM['state']['machineMode']
        if self.machineMode not in out.omKeys.keys():
            print('We do not know how to process machine mode: ' + str(self.machineMode))
            return None
        # Determine SBC mode
        if (out.localOM['seqs'] == None) or (len(out.localOM['seqs']) == 0):
            print('no sequence data available')
            return None
        else:
            self.seqs = out.localOM['seqs']
        # Get initial data set
        for key in out.omKeys[self.machineMode]:
            if not self._request(out,key,'vnd99'):
                print('failed to acqire initial "' + key + '" data')
                return None
        return self.machineMode

    def update(self, out):
        # Do an update cycle; get new data and update localOM
        success = True  # track (soft) failures
        verboseList = self._seqRequest(out)
        for key in ['state'] + out.omKeys[self.machineMode]:
            if key in verboseList:
                #print('*',end='')  # debug
                if not self._request(out,key,'vnd99'):
                    success = False;
            else:
                #print('.',end='')  # debug
                if not self._request(out,key,'fnd99'):
                    success = False;
        return success

    def getResponse(self, cmd):
        '''
            Sends a query and waits for response data,
            returns a list of response lines, or None
        '''
        # Send the command to RRF
        self.sendGcode(cmd)
        # And wait for a response
        requestTime = ticks_ms()
        queryResponse = []
        line = ''
        # only look for responses within the requestTimeout period
        while (ticks_diff(ticks_ms(),requestTime) < self.config.requestTimeout):
            # Read a character, tolerate and ignore decoder errors
            try:
                char = self.rrf.read(1).decode('ascii')
            except UnicodeDecodeError:
                char = None
            except Exception as error:
                self._commsFail('Serial/UART failed: Cannot read from controller',error)
            if self.rawLog and char:
                self.rawLog.write(char)
            # store valid characters
            if char in self.jsonChars:
                line += char
            elif char == '\n':
                queryResponse.append(line)
                # if we see 'ok' at the line end break immediately from wait loop
                if (line[-2:] == 'ok'):
                    break
                line = ''
        return queryResponse

