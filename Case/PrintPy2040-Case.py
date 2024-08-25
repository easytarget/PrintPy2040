# PrintPy2040 Case

from openscad import *
from seeed_xiao import rp2040
from fasteners import hex3mm
from dupont import dupont_socket
from buttons import pcb_button_std
from displays_oled import JMD0_96A_2

# This is a very small model, 60 is fine here:
fn=60
# I override in a lot of places for speed and because
# the effects are simply not visible on mm-sized bits.

# OLED screen modules
# CRITICAL: Valuse must matc hones defined for the screen
# in displays_oled.JMD0_96A_2()
sx = 27.4              # Board width
sy = 28                # Board height
vx = 21.7              # viewport width
vy = 10.8              # viewport height
vo = -1.75             # viewport y offset
holeOff = 23.5/2       # Holes are 23.5mm apart
pinOff = (sy/2)-1.5    # Pins on PCB are 1.5mm from edge
screenOff = (sx/2)+0.1 # X offset for each screen + gap

# Case size (x,y based on screen dimensions)
inX = (2*sx)+1         # basic interior space based on screens
inY = sy+1
#inZ = 13              # how deep (depends on cpu board etc..)
inZ = 10              # SLIM CASE
#inZ = 16              # LARGE CASE
wallRad=1.5           # round off (case thickness)
#insetB=8              # inset for button and socket (8 is max..)
insetB=6              # SLIM CASE

printing = False  # <-- Set True to generate print plate

def printplate():
    parts = []
    parts.append(foot([70,-6,3],[0,0,0]))
    parts.append(mount([70,15,9],[90,0,180]))
    parts.append(casebody([0,40,0],[0,0,180]))
    parts.append(casebody([70,40,0],[0,0,180],usb=False))
    parts.append(caseback())
    output(parts)
    
def view():
    footangle = 0
    e = 0    # 'Explode' factor
    parts = [
        # fittings
        rp2040([0,-12.2,4]).translate([0,0,e*0.8]),
        hex3mm(12,[23.1,-19.5,3],[0,-90,0]).translate([e*2,-e,-e]),
        hex3mm(12,[-23.1,-19.5,3],[0,90,0]).translate([-e*2,-e,-e]),
        dupont_socket(1,5,[-24.48,-7.5,insetB],[180,0,0]).translate([0,0,-e*2]),
        pcb_button_std([-19.5,2,insetB],[0,180,0]).translate([0,0,-e*1.5]),
        screens([0,0,inZ+0.8],[0,0,0]).translate([0,0,e]),
        # case bits
        foot([0,-19.5,3],[footangle,0,0]).translate([0,-e,-e]),
        #mount([0,-19.5,3],[footangle,0,0]).translate([0,-e,-e]),
        casebody([0,0,inZ+5.1],[180,0,0]).translate([0,0,e*3]),
        caseback(),
    ]
    output(parts)

def casebody(pos=[0,0,0],rot=[0,0,0],usb=True):
    def body():
        c = cube([inX,inY,inZ],center=True)
        c = c.translate([0,0,inZ/2+wallRad])
        s = minkowski([c,sphere(wallRad)])
        return s.color("WhiteSmoke")
    def viewport():
        # Screen Opening, 0.5mm margin)
        x=(2*(screenOff+(vx/2)))+1
        y=vy+1
        c1 = cube([x+2,y+1,0.1],center=True)
        c1 = c1.translate([0,vo,0])
        c2 = cube([x,y,0.1],center=True)
        c2 = c2.translate([0,vo,1])
        return hull ([c1,c2])
    def inner1():
        # Section with fat pins to support oleds
        s = square([inX,inY],center=True)
        c = circle(2.6)
        p = []
        for o in [-screenOff,screenOff]:
            for x in [o-holeOff-1,o+holeOff+1]:
                for y in [-holeOff-1,holeOff+1]:
                    p.append(c.translate([x,y]))
        r = difference(s,p)
        r = linear_extrude(r,height=1.8,convexity=10)
        return r.translate([0,0,1])
    def inner2():
        # The rest of the body to the back.
        s = square([inX,inY],center=True)
        s = linear_extrude(s,height=2*inZ,convexity=10)
        return s.translate([0,0,2.7])
            
    def usbport():
        c1 = cylinder(r=4, h=30, center=True)
        c1 = c1.translate([3,0,0])
        c2 = cylinder(r=4, h=30, center=True)
        c2 = c2.translate([-3,0,0])
        c3 = cube([14,10,30],center=True)
        c3 = c3.translate([0,5,0])
        u = hull([c1,c2,c3])
        return u.rotate([90,0,0]).translate([0,10,inZ-1.5])
             
    r = [viewport(),inner1(),inner2()]
    if usb:
        r.append(usbport())
    #return union(r).rotate(rot).translate(pos)
    return difference(body(),r).rotate(rot).translate(pos)


def caseback(pos=[0,0,0],rot=[0,0,0]):
    def plate():
        def vent(y):
            c1 = circle(1).translate([-22,y])
            c2 = circle(1).translate([22,y])
            return hull([c1,c2])
        def logo():
            t = text("XIAO",halign="center",valign="center",
                      size=10,fn=24)
            t = t.scale([1,1.2]).mirror([1,0,0])    # <-- THIS!
            #t = t.scale([1,1.2]).mirror([1,0])
            return t.translate([8,0])
        # baseplate
        s = square([inX-wallRad,inY-wallRad],center=True)
        b = minkowski([s,circle(wallRad)])
        # button and socket openings
        o1 = square([12.5,13.2],center=True)
        o1 = o1.translate([-19.4,2])
        o2 = square([13,2.8],center=True)
        o2 = o2.translate([-19.4,-7.5])
        r = [vent(11),vent(-11),logo(),o1,o2]
        p = difference(b,r)
        return linear_extrude(p,height=2,convexity=20)

    def footmount():
        b = [cylinder(d=6,h=30,center=True)]
        b.append(cube([2,6,8]).translate([1,0,-14.5]))
        b.append(cube([2,6,8]).translate([1,0,6.5]))
        c = [cylinder(d=3.2,h=33,center=True,fn=6)]
        c.append(cube([8,10,14],center=True))
        r = difference(union(b),c)
        return r.rotate([0,90,0]).translate([0,-19.5,3])

    def supports():
        # Logo support
        ls = square([34,1.5],center=True)
        ls = linear_extrude(ls,height=1,convexity=10,scale=[0.9,0.6])
        r =  [ls.translate([7,0.25,1.5])]
        # Support button and socket
        for y in [-6,-2,2,6]:
            s = square([15.6,2],center=True)
            e = linear_extrude(s,height=1,convexity=20,scale=[0.85,1])
            r.append(e.translate([-19.4,y,insetB]))
        return union(r)

    def screenpins():
        r = []
        c = cylinder(r1=2.2,r2=1.6,h=inZ-1.3)
        s = sphere(0.6).translate([0,0,inZ-1.3])
        p = union([c,s])
        # Screen support posts + balls
        for x in [-1,1]:
            for y in [-1,1]:
                r.append(p.translate([(x*screenOff)+(x*holeOff),y*holeOff,2]))
        return union(r)
    
    def lip():
        # Thin wall around base to stop dust and light bleed
        s1 = square([inX-0.3,inY-5],center=True)
        s2 = square([inX-5,inY-0.3],center=True)
        s3 = square([inX-2,inY-2],center=True)
        w1 = difference(union([s1,s2]),s3)
        return linear_extrude(w1,height=3,convexity=8)
    
    def housings():
        # Button and socket housings
        s1 = square([15.6,5],center=True)
        s2 = square([13,2.8],center=True)
        s3 = square([15.6,16],center=True)
        s4 = square([12.5,13.2],center=True)
        w = [difference(s1,s2).translate([-19.4,-7.5]),
             difference(s3,s4).translate([-19.4,2])]
        # matching support for pins on other edge
        s5 = square([1.4,2*holeOff],center=True)
        w.append(s5.translate([screenOff+holeOff,0]))
        return linear_extrude(union(w),height=insetB,convexity=20)
        
    def mcuclip():
        def walls():
            # main walls to support screens in center
            s1 = square([26,inY-0.3],center=True)
            s2 = square([28,inY-4.5],center=True)
            w = difference(s1,s2)
            return linear_extrude(w,height=inZ+0.7,convexity=10,scale=[0.3,1])
        def grip():
            # Outdent to grip casebody
            l1 = square([8,inY-0.1],center=True)
            l2 = square([16,inY-2],center=True)
            w = difference(l1,l2)
            w = linear_extrude(w,height=2,convexity=10)
            return w.translate([0,0,inZ-1.3])
        def rear():
            # brackets for end of board
            s = square([24,0.5],center=True).translate([0,8.75])
            c = circle(r=1)
            m = minkowski([s,c])
            return linear_extrude(m,height=6.2,convexity=10)
        def outline():
            p = projection(rp2040([0,-12.2,4]))
            return linear_extrude(p,height=7,convexity=10)
        def usboval():
            c = cylinder(d=3.2, h=40, center=True)
            c1 = c.rotate([90,0,0]).translate([-2.9,0,6.8])
            c2 = c.rotate([90,0,0]).translate([2.9,0,6.8])
            s = square([0.2,inY],center=True)
            g = linear_extrude(s,height=inZ-1.8,convexity=10,scale=[1,1])
            return hull([c1,c2,g.translate([0,0,2])])
        def rpshort(p=[0,0,0]):
            c = cube([20,30,20]).translate([-10,0,0])
            m = rp2040()
            return intersection(c,m).translate(p)

        w = union(walls(),grip(),rear())
        g = [outline().translate([0,0,4]),
             usboval(),
             rp2040([0,-12.1,4]).scale([1.03,1.02,1.03]),
             rpshort([0,-12.2,5.2])]
        return difference(w,g)
        #return rpshort().color('red')

    r = [plate(),
         footmount(),
         housings(),
         supports(),
         screenpins(),
         lip(),
         mcuclip()]
    return union(r).rotate(rot).translate(pos).color("SlateBlue")


# The Foot adapter for freestanding units
def foot(pos=[0,0,0],rot=[0,0,0]):
    def body(): 
        c1 = cylinder(d=6,h=46,center=True)
        c2 = cylinder(d=3,h=36,center=True)
        c2 = c2.translate([1.5,-16,0])
        h1 = hull([c1,c2]).rotate([0,90,0])
        return h1.color("SlateBlue")
    def cut():
        c1 = cylinder(d=6.4,h=30.3,center=True)
        c2 = cylinder(d=6.4,h=30.3,center=True)
        c2 = c2.translate([6,-6,0])
        return hull([c1,c2])
    def holes():
        c = cylinder(d=6.6,h=4,center=True)
        r = [cylinder(d=3.4,h=41,center=True)]
        for z in [-22,22]:
            r.append(c.translate([0,0,z]))
        return union(r)
    def logo():
        s = "EasyTarget"
        t = text(s,size=5,valign="center",halign="center",fn=24)
        t = linear_extrude(t,height=2,convexity=10)
        t = t.translate([0,-12,1.8]).rotate([0,90,0])
        return t
    r = union([cut(),holes(),logo()]).rotate([0,90,0])
    return difference(body(),r).rotate(rot).translate(pos)

# The mount adapter (foot with a bend and a through-hole)
def mount(pos=[0,0,0],rot=[0,0,0]):
    def body():
        c1 = cylinder(d=6,h=40,center=True)
        c2 = cylinder(d=6,h=26,center=True).translate([0,6,0])
        b1 = hull([c1,c2])
        c3 = cylinder(d=6,h=26,center=True).translate([0,6,0])
        c4 = cylinder(d=4,h=20,center=True).translate([-15,7,0])
        b2 = hull([c3,c4])
        h1 = union([b1,b2]).rotate([90,-90,90])
        return h1.color("SlateBlue")
    def cut():
        c1 = cylinder(d=6.4,h=30.3,center=True)
        c2 = cylinder(d=6.4,h=30.3,center=True)
        c2 = c2.translate([6,0,0])
        return hull([c1,c2])
    def holes():
        c = cylinder(d=6.6,h=4,center=True)
        r = [cylinder(d=3.4,h=41,center=True)]
        for z in [-22,22]:
            r.append(c.translate([0,0,z]))
        return union(r)
    def logo():
        s1 = "Easy"
        s2 = "Target"
        t1 = text(s1,size=5,valign="center",halign="center",fn=24)
        t1 = t1.translate([0,10])
        t2 = text(s2,size=5,valign="center",halign="center",fn=24)
        t2 = t2.translate([0,0.5])
        t = union([t1,t2])
        t = linear_extrude(t,height=2,convexity=10)
        t = t.translate([0,-12,8.8]).rotate([90,-90,0])
        return t
    def bolt():
        c1 = circle(d=3.5)
        c1 = linear_extrude(c1,height=10,convexity=10)
        c2 = circle(d=7)
        c2 = linear_extrude(c2,height=4,convexity=10)
        b = union([c1,c2])
        return  b.translate([0,7,3]).rotate([0,90,-90])
    r = union([cut(),holes(),logo(),bolt()]).rotate([0,90,0])
    return difference(body(),r).rotate(rot).translate(pos)

# Two screens with correct spacing.
def screens(pos=[0,0,0],rot=[0,0,0]):
    # left
    l = JMD0_96A_2([-screenOff,0,0],message='PrintPY',pins=False)
    # right
    r = JMD0_96A_2([screenOff,0,0],message='RP2040',pins=False)
    # tape that seals the join..
    t = cube([2,sx-6,0.02],center=True).color("black")
    return union([l,r,t]).rotate(rot).translate(pos)

if printing:
    printplate()
else:
    view()
