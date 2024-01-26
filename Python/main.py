import machine
import time
import ssd1306
import select
from neopixel import NeoPixel
import json
from functools import reduce

print("PrintPy: Starting")
# Hardware

# 2x displays on 2x I2C
I2C0_SDA_PIN = 28
I2C0_SCL_PIN = 29
I2C1_SDA_PIN = 6
I2C1_SCL_PIN = 7
i2c0=machine.I2C(0,sda=machine.Pin(I2C0_SDA_PIN), scl=machine.Pin(I2C0_SCL_PIN))
i2c1=machine.I2C(1,sda=machine.Pin(I2C1_SDA_PIN), scl=machine.Pin(I2C1_SCL_PIN))
display0 = ssd1306.SSD1306_I2C(128, 64, i2c0, addr=0x3c)
display1 = ssd1306.SSD1306_I2C(128, 64, i2c1, addr=0x3c)

def buttonpress(p):  # Needs debounce!
    global light
    print("button")
    light = (light[1],light[2],light[0])  # at present, cycle light colors..
    time.sleep(0.1)  # 100ms of debounce before we return control.

# hardware button
button1 = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
button1.irq(trigger=button1.IRQ_FALLING, handler=buttonpress)

# Neopixel
pixelpower = machine.Pin(11,machine.Pin.OUT)  # Power pin
pixelpower.value(1)                           # turn on immediately
pixel = NeoPixel(machine.Pin(12),1)           # data on pin 12

# RGB Led, default off
rgbR = machine.Pin(17,machine.Pin.OUT)
rgbG = machine.Pin(16,machine.Pin.OUT)
rgbB = machine.Pin(25,machine.Pin.OUT)

def setRGB(state=(False,False,False)):
    rgbR.value(not state[0])   # pins are inverted
    rgbG.value(not state[1])
    rgbB.value(not state[2])
    
setRGB()

# Serial
rrf = machine.UART(0)
rrf.init(baudrate=57600,timeout=50,timeout_char=25)
rrfsending = select.poll()
rrfsending.register(rrf, select.POLLIN)

def sendGcode(code=""):
    chksum = reduce(lambda x, y: x ^ y, map(ord, code))
    rrf.write(code + "*" + str(chksum) + "\r\n")

# Init

display0.rect(0, 0, 127, 16, 1)
display0.rect(10, 20, 107, 43, 1)
display0.text('Hello', 44, 5, 1)
display1.rect(0, 0, 127, 16, 1)
display1.rect(10, 20, 107, 43, 1)
display1.text('World', 44, 5, 1)
display0.show()
display1.show()

pixel[0]=(0,0,0)
pixel.write

# Vars

begin = time.ticks_ms()  # DEMO

printerstate = {}        # This....

speed = 50;              # Loop polling speed (ms)
start = time.ticks_ms()  # Set when we send packets
light = (1,0,0)          # Current NeoPixel value
intensity = 55           # Scale the NeoPixel power (dimming)
flashing = False         # Is the NeoPixel active?
rgbstate = (True,False,False)

# Main Loop

while True:

    # The timeout value for the poll commad sets the base loop speed
    if (rrfsending.poll(speed)):
        # Process any incoming packets here
        packet = rrf.readline()
        try:
            printerstate = json.loads(packet)
            setRGB(rgbstate)
            rgbstate = (rgbstate[2],rgbstate[0],rgbstate[1])
        except:
            print("\r\nInvalid data recieved: " + str(packet))
            setRGB((True,True,True))  # white = packet error
        print()
        print("Latest state: " + str(printerstate))
        if "status" in printerstate:
            print("Status: " + printerstate["status"])
                
    waiting = int(time.ticks_diff(time.ticks_ms(), start))  #how long since we sent the last request?
    
    if (flashing and (waiting >= speed)):
        print("-", end="")
        pixel[0]=(0,0,0)
        pixel.write()
        flashing = False

    if (waiting >= 1000):
        print(".", end="")
        start = time.ticks_ms()  # reset the timer
        sendGcode("M408 S0")     # Send a new packet request
        flashing = True          # flash the pixel
        pixel[0] = (int(light[0]*intensity),int(light[1]*intensity),int(light[2]*intensity))
        pixel.write()
        
    # display runtime in mins and secs for demo
    now = int(time.ticks_diff(time.ticks_ms(), begin))
    secs = int((now / 1000) % 60)
    mins = int((now / 60000) % 60)
    display0.fill_rect(11, 21, 105, 41, 0)
    display1.fill_rect(11, 21, 105, 41, 0)
    display0.text(str(mins), 58, 35, 1)
    display1.text(str(secs), 58, 35, 1)
    if "status" in printerstate:
        display0.rect(1, 1, 125, 14, 0, True)
        display0.text("State: " + printerstate["status"], 10, 5, 1)
    display0.show()
    display1.show()
