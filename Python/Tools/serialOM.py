# Common classes between CPython and microPython
from json import loads

#from time import sleep_ms,ticks_ms,ticks_diff  # microPython
from timeStubs import sleep_ms,ticks_ms,ticks_diff  # CPython

# SoftFail stuff; depreciated
#from machine import reset             # microPython
from sys import executable,argv,exit   # CPython
from os import execv                   # CPython

# CPython standard libs that need to be provided locally for microPython
from itertools import zip_longest
from functools import reduce

class serialOM:
    '''
        Object Model communications tools class provides a class with
        specific functions used to fetch and process the RRF Object Model
        via a serial/stream interface.

        We make two different types of request on a 'per key' basis:
          Verbose status requests to read the full key
          Frequent requests that just return the frequently changing key values
        Verbose requests are more 'expensive' in terms of processor and data use,
        so we only make these when we need to.

        There is a special key returned by M409; `seqs`, which returns an
        incremental count of changes to the values /not/ returned with the
        frequent update requests. We use this key to trigger verbose updates
        when necessary for all the keys we monitor.

        If either the machine mode changes, or the uptime rolls-back we clean
        and rebuild our local object model copy

        See:
        https://docs.duet3d.com/User_manual/Reference/Gcodes#m409-query-object-model
        https://github.com/Duet3D/RepRapFirmware/wiki/Object-Model-Documentation


        arguments:
            rrf :           Serial stream or similar
            requestTimeout: Timeout for response after sending a request (ms)
            rawLog:         File object for the raw log, or None
            quiet:          Print messages on startup and when soft errors are encountered

        provides:
            sendGcode(code):    Sends a Gcode to controller with checksum
            getResponse(code):  Sends a Gcode and returns the response as a list of lines
            update():           Updates local model from the controller

    '''

    def __init__(self, rrf, omKeys, requestTimeout=500, rawLog=None, quiet=False):
        self.rrf = rrf
        self.omKeys = omKeys
        self.requestTimeout = requestTimeout
        self.rawLog = rawLog
        self.loud = not quiet
        self.defaultModel = {'state':{'status':'unknown'},'seqs':None}
        self.model = self.defaultModel
        self.seqs = {}
        self.machineMode = 'unavailable'
        self.upTime = -1
        # string of valid ascii chars for JSON response body
        self.jsonChars = bytearray(range(0x20,0x7F)).decode('ascii')
        self.seqKeys = ['state']  # we always check 'state'
        for mode in omKeys.keys():
            self.seqKeys = list(set(self.seqKeys) | set(omKeys[mode]))

        # Main Init

        if self.loud:
            print('serialOM is starting')
        # check for a valid response to a firmware version query
        if self.loud:
            print('checking for connected RRF controller')
        retries = 10
        while not self._firmwareRequest():
            retries -= 1
            if retries == 0:
                if self.loud:
                    print('failed to get a sensible response from controller')
                return None
            if self.loud:
                print('failed..retrying')
            sleep_ms(self.requestTimeout)
        print('controller is connected')
        sleep_ms(self.requestTimeout)  # helps the controller 'settle' after reboots etc.
        if self.loud:
            print('making initial data set request')
        if self.update():
            if self.loud:
                print('connected to ObjectModel')
        if self.machineMode == 'unavailable':
            if self.loud:
                print('could not obtain initial machine state')
            return None

    # Handle serial or comms errors
    # depreciated
    # TODO; remove this and raise an exception.. (and define one first!)
    def _commsFail(self,why,error):
        print('communications error: ' + why)
        print('>>> ' + str(error).replace('\n','\n>>> '))
        print('restarting in ',end='')
        # Pause for a few seconds
        for c in range(8,0,-1):
            print(c,end=' ',flush=True)
            sleep_ms(1000)
        print()
        # CPython; restart with original arguments
        execv(executable, ['python'] + argv)
        # Micropython; reboot module
        #reset()

    # Handle a request cycle to the OM
    def _omRequest(self, OMkey, OMflags):
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
            return self._updateOM(jsonResponse,OMkey)

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
        return jsonResponse

    def _updateOM(self,response,OMkey):
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
                if self.loud:
                    print('invalid JSON:',line)
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
                    self.model[payload['key']] = merge(self.model[payload['key']],payload['result'])
                # M409 may legitimately return an empty key when getting frequent data
                success = True
            else:
                # Verbose output replaces the existing key if a result is supplied
                if payload['result'] != None:
                    self.model[payload['key']] = payload['result']
                    success = True
        return success

    def _keyRequest(self,key,verboseList):
        # Do an individual key request using the correct verbosity
        if key in verboseList:
            #print('*',end='')  # debug
            if not self._omRequest(key,'vnd99'):
                return False;
        else:
            #print('.',end='')  # debug
            if not self._omRequest(key,'fnd99'):
                 return False;
        return True

    def _stateRequest(self,verboseSeqs):
        # sends a state request
        # handles machine mode and uptime changes

        def cleanstart():
            # clean and reset the local OM and seqs, returns full seqs list
            self.model = self.defaultModel
            self.seqs = {}
            return self.seqKeys

        if not self._keyRequest('state',verboseSeqs):
            if self.loud:
                print('"state" key request failed')
            return False
        verboseList = verboseSeqs
        if self.machineMode != self.model['state']['machineMode']:
            verboseList = cleanstart()
        elif self.upTime > self.model['state']['upTime']:
            verboseList = cleanstart()
        self.upTime = self.model['state']['upTime']
        self.machineMode = self.model['state']['machineMode']
        return verboseList

    def _seqRequest(self):
        # Send a 'seqs' request to the OM, updates localOM and returns
        # a list of keys where the sequence number has changed
        changed=[]
        if self.seqs == {}:
            # no previous data, start from scratch
            for key in self.seqKeys:
                self.seqs[key] = -1
        # get the seqs key, note and record all changes
        if self._omRequest('seqs','fnd99'):
            for key in self.seqKeys:
                if self.seqs[key] != self.model['seqs'][key]:
                    changed.append(key)
                    self.seqs[key] = self.model['seqs'][key]
        else:
            if self.loud:
                print('sequence key request failed')
        return changed

    def _firmwareRequest(self):
        # Use M115 to (re-establish comms and verify firmware
        # Send the M115 info request and look for a sensible reply
        if self.loud:
            print('> M115')
        response = self.getResponse('M115')
        haveRRF = False
        if len(response) > 0:
            for line in response:
                if self.loud:
                    print('>> ' + line)
                if self.rawLog:
                    self.rawLog.write(line + '\n')
                # A basic test to see if we have an RRF firmware
                # - Ideally expand to add more checks, eg version.
                if 'RepRapFirmware' in line:
                    haveRRF = True
        return haveRRF

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
        while (ticks_diff(ticks_ms(),requestTime) < self.requestTimeout):
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

    def update(self):
        # Do an update cycle; get new data and update localOM
        success = True  # track (soft) failures
        verboseSeqs = self._seqRequest()
        verboseList = self._stateRequest(verboseSeqs)
        for key in self.omKeys[self.machineMode]:
            if not self._keyRequest(key, verboseList):
                success = False
        return success
