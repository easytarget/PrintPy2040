# Various dupont sockets, plugs, jumpers.
# Simply rendered.
from openscad import *
fn=12

# PinSocket, defaults to 2.54mm pitch, centered on pin 1
def dupont_socket(rows=1, columns=1, 
                  pos=[0,0,0], rot=[0,0,0],
                  pitch=2.54, height=8):
    def sock(x,y):
        b = cube([pitch,pitch,height],center=True)
        s = cube([1,1,height],center=True).translate([0,0,0.5])
        return difference(b,s).translate([x*pitch,y*pitch,height/2])
    def pin(x,y):
        l = height*0.5   
        p = cube([0.5,0.5,l],center=True)
        r = sphere(0.1)
        return minkowski([p,r]).translate([x*pitch,y*pitch,-l+(l/2)+1])
    ret = []
    for c in range(columns):
        for r in range(rows):
            ret.append(sock(c,r).color('grey'))
            ret.append(pin(c,r).color('gold'))
    return union(ret).rotate(rot).translate(pos)

# Plug(s), defaults to 2.54mm pitch, centered on pin 1
def dupont_plug(rows=1, columns=1, 
                  pos=[0,0,0], rot=[0,0,0],
                  pitch=2.54, height=8):
    l = height*0.8
    def sock(x,y):
        b = cube([pitch-0.25,pitch-0.25,height],center=True)
        r = sphere(0.1)
        o = minkowski([b,r])
        s = cylinder(d=1.2,h=height,center=True).translate([0,0,0.5])
        return difference(o,s).translate([x*pitch,y*pitch,l+height/2])
    def pin(x,y):
        l = height*0.75   
        p = cube([0.5,0.5,l+1],center=True)
        r = sphere(0.1)
        return minkowski([p,r]).translate([x*pitch,y*pitch,l/2+0.6])
    ret = []
    for c in range(columns):
        for r in range(rows):
            ret.append(sock(c,r).color('grey'))
            ret.append(pin(c,r).color('gold'))
    return union(ret).rotate(rot).translate(pos)

# PCB Pinstrip, defaults to 2.54mm pitch, centered on pin 1
def dupont_pins(rows=1, columns=1, 
                pos=[0,0,0], rot=[0,0,0],
                pitch=2.54, height=8):
    def base(x,y):
        b = cube([pitch-0.25,pitch-0.25,1.4],center=True)
        r = sphere(0.1)
        o = minkowski([b,r])
        return o.translate([x*pitch,y*pitch,0.7])
    def pin(x,y):
        # relative length of pin to height
        l = height+4
        o = height*0.8
        p = cube([0.5,0.5,height+2],center=True)
        r = sphere(0.1)
        return minkowski([p,r]).translate([x*pitch,y*pitch,(l/2)-4])
    ret = []
    for c in range(columns):
        for r in range(rows):
            ret.append(base(c,r).color('grey'))
            ret.append(pin(c,r).color('gold'))
    return union(ret).rotate(rot).translate(pos)
    
def dupont_jumper(rows=1, columns=2, 
                  pos=[0,0,0], rot=[0,0,0],
                  pitch=2.54, height=6):
    def sock(x,y):
        b = cube([pitch,pitch,height],center=True)
        s = cube([1,1,height+1],center=True).translate([0,0,0])
        return difference(b,s).translate([x*pitch,y*pitch,height/2])
    def pin(x,y):
        p = cube([0.5,0.5,2],center=True)
        r = sphere(0.1)
        return minkowski([p,r]).translate([x*pitch,y*pitch,height-1])
    ret = []
    jump = []
    for c in range(columns):
        for r in range(rows):
            ret.append(sock(c,r).color('grey'))
            jump.append(pin(c,r))
    ret.append(hull(jump).color('gold'))
    return union(ret).rotate(rot).translate(pos)

def main():
    '''
        Example use / layout
    '''
    out = [dupont_socket(4,2),
           dupont_plug(1,pos=[10,0,0]),
           dupont_plug(3,pos=[10,(2*2.54),0]),
           dupont_pins(6,2,pos=[-10,0,0]),
           dupont_jumper(pos=[0,(5*2.54),0])
          ]
    output(out)

if __name__ == "__main__":
    main()