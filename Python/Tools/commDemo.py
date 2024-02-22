import serial
rrf = serial.Serial('/dev/ttyACM0',57600,timeout=0.2)
while True:
    string = ''
    char = b''
    while char not in ['\n','\r']:
        try:
            char = rrf.read(1).decode('ascii')
        except UnicodeDecodeError:
            char = b'?'
        if char:
            if char in bytearray(range(0x20,0x7F)).decode('ascii'):
                string += str(char)
            else:
                break
    print('> ' + string)
