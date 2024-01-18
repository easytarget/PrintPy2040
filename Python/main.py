from ws2812 import WS2812
import utime
import machine

power = machine.Pin(11,machine.Pin.OUT)
power.value(1)

led = WS2812(12,1)#WS2812(pin_num,led_count)
 
brights = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1]

while True:
    for bright in brights:
        led.brightness = bright
        print("rainbow : " + str(bright*100) + "%")
        led.rainbow_cycle(0.01)
