# Various fastners.
# Simply rendered. no threading incorporated
# In the real world Head dimensions canvary..
from openscad import *
fn=60

# A 3mm X 10mm (default) hex head bolt
def hex3mm(length=10, pos=[0,0,0], rot=[0,0,0]):
    o = cylinder(d=5.2, h=3)
    s = cylinder(d=3, h=3, fn=6)
    h = difference(o,s.translate([0,0,-0.1]))
    b = cylinder(d=3,h=length).translate([0,0,3])
    r = union([h,b]).rotate(rot).translate(pos)
    return r.color('silver')

def main():
    '''
        Example use / layout
    '''
    out = [hex3mm(12)]
    output(out)

if __name__ == "__main__":
    main()