from openscad import *
fn=60

# Util: decimal range, aka: range() with floats
#  replicates openscad `for(var=[start, increment, stop])` function correctly.
import decimal
def drange(x, y, jump):
  while x < y:
    yield float(x)
    x += decimal.Decimal(jump)

# XIAO module, fit is generic, but this model is the RP2040
def rp2040(pos = [0, 0, 0], rot = [0, 0, 90]):
    def pcb():
        s = square([19.25, 15.5], center=True).translate([10.625, 0])
        c = circle(r = 1, fn = 24)
        b = minkowski([s, c])
        h = []
        for x in drange(3, 19, 2.54):
            for y in [-9, -7.7, 7.7, 9]:
                h.append(circle(d = 0.8, fn = 24).translate([x, y]))
        p = linear_extrude(difference(b,h), height = 1.2, convexity = 10)
        return p.color('green')
        
    def usbc():
        c = cylinder(d = 3.2, h = 7.25, fn = 24)
        h = []
        for y in [-1,1]:
            h.append(c.translate([0, y * 2.9, 0]))
        c = hull(h).rotate([0, 90, 0]).translate([-1.2, 0, 2.8])
        return c.color('silver')
        
    def mcu():
        c = square([10.6, 12.4], center = True)
        m = linear_extrude(c, height = 1, convexity=10)
        m = m.translate([12.75, 0, 1.2])
        return m.color('slategrey')
        
    def pixel():
        c = square([2.4, 2.6], center = True)
        p = linear_extrude(c, height = 1, convexity = 10)
        p = p.translate([19.9, 0, 1.2])
        return p.color('azure')
        
    def dis():  # discreet components
        c = square([5,1.5], center=True)
        p = []
        for y in [-1, 1]:
            p.append(c.translate([3.8, y*5.3]))
        d = linear_extrude(union(p), height = 0.5 ,convexity = 10)
        d = d.translate([0, 0, 1.2])
        return d.color('darkslategrey')
        
    def switches():
        b = cube([2.4,4,2], center=True)
        c = cylinder(d = 1.4, h = 1.25, fn=24)
        s = []
        for y in [-1, 1]:
            s.append(b.translate([19.9, y*4, 1.2]).color('silver'))
            s.append(c.translate([19.9, y*4, 1.2]).color('darkslategrey'))
        return union(s)
    
    def solderpoints():
        c = circle(d=1, fn=24)
        p = []
        for x in drange(3, 19, 2.54):
            for y in [-7.7, 7.7]:
                p.append(c.translate([x, y]))
        s = linear_extrude(union(p), height=2, convexity=10)
        s = s.translate([0,0,-0.4])
        return s.color('gold')
        
        
    ret = union([pcb(),usbc(),mcu(),
                pixel(),dis(),switches(), solderpoints()])
    return ret.rotate(rot).translate(pos)
def main():
    '''
        Example use / layout
    '''
    out = [rp2040()]
    output(out)

if __name__ == "__main__":
    main()
