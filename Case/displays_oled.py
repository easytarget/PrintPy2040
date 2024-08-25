# Various OLED displays.
# Simply rendered.
from openscad import *
fn=24

# OLED is based on a generic JMD0.96A-2 module
def JMD0_96A_2(pos=[0,0,0],rot=[0,0,0],message=None,pins=True):
    sx = 27.4             # Board width
    sy = 28               # Board height
    vx = 21.7             # viewport width
    vy = 10.8             # viewport height
    vo = -1.75            # viewport y offset
    holeOff = 23.5/2      # Holes are 23.5mm apart
    pinOff = (sy/2)-1.5   # Pins on PCB are 1.5mm from edge

    def pcb():
        p = square([sx,sy],center=True)
        c = circle(d=2.3)
        h = []
        for x in [-1,1]:
            for y in [-1,1]:
                h.append(c.translate([x*holeOff,y*holeOff]))
        b = difference(p,h)
        b = linear_extrude(b,height=1.2,convexity=10)
        return b.color("DodgerBlue")

    def ribbon():
        s1 = square([12.5,8],center=True)
        s1 = s1.translate([0,-9.9])
        s2 = square([22,4],center=True)
        s2 = s2.translate([0,-8])
        h = hull([s1,s2])
        h = linear_extrude(h,height=1,convexity=10)
        return h.translate([0,0,-0.2]).color('Goldenrod')

    def components():
        s1 = square([24,3],center=True)
        s2 = square([22,4],center=True)
        s2 = s2.translate([-1,7])
        c = linear_extrude([s1,s2],height=1.25,convexity=10)
        return c.translate([0,0,-1]).color('Grey')

    def glass():
        b = square([sx,19.2],center=True)
        b = linear_extrude(b,height=1.4,convexity=5)
        b = b.translate([0,-0.25,1.3])
        w = square([12.5,7.8],center=True)
        w = linear_extrude(w,height=0.8,convexity=5)
        w = w.translate([0,-10,1.3])
        v = square([sx,14.5],center=True)
        v = linear_extrude(v,height=1.8,convexity=5)
        v = v.translate([0,1.5,1.3])
        return union([b,w,v]).color("Grey")

    def pin(x): 
        if (pins):
            c = square([0.6,0.6],center=True)
            c = linear_extrude(c,height=11.3,convexity=5)
            c = c.translate([x,pinOff,-8.3]).color("gold")
            b = square([2,2.6],center=True)
            b = linear_extrude(b,height=2.5,convexity=5)
            b = b.translate([x,pinOff,-2.5]).color("grey")
            return union([c,b])
        else:
            c = circle(d=1)
            c = linear_extrude(c,height=3,convexity=5)
            c = c.translate([x,pinOff,-1]).color("gold")
            return c

    def msg(m,c):
        print(m,c)
        t = text(m,size=2,valign='center',halign='center')
        t = linear_extrude(t,height=0.01,convexity=10)
        return t.translate([0,1.5,3.1]).color(c)

    ret = []
    ret.append(pcb())
    ret.append(ribbon())
    ret.append(glass())
    ret.append(components())
    for x in [-3.81,-1.27,1.27,3.81]:
        ret.append(pin(x))

    if message is not None:
        ret.append(msg(message,'White'))

    return union(ret).rotate(rot).translate(pos)

def main():
    '''
        Example use / layout
    '''
    out = [JMD0_96A_2(),
           JMD0_96A_2([30,0,0],message='OLED',pins=False)]

    output(out)

if __name__ == "__main__":
    main()
