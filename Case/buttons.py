# Various pushbuttons.
# Simply rendered.
from openscad import *
fn=60

# A VERY common button design used in lots of kits etc.
def pcb_button_std(pos=[0,0,0],rot=[0,0,0]):
    def inner():
        b = square([11,11],center=True)
        r = linear_extrude(b,3.3,convexity=10)
        return r.color("Silver")
        
    def body():
        o = square([12,12],center=True)
        i = square([11,11],center=True)
        c = linear_extrude(difference(o,i),3.3,convexity=10)
        r = [circle(3.4)]
        for x in [-1,1]:
            for y in [-1,1]:
                r.append(circle(0.5).translate([3.75*x,3.75*y]))
        d = linear_extrude(r,4.1,convexity=10)
        m = square([3,3],center=True)
        e = linear_extrude(m,7.2,convexity=10) 
        t = square([4,4],center=True)
        f = linear_extrude(t,2.3,convexity=10).translate([0,0,5.7])
        return union([c,d,e,f]).color("DimGray")
            
    def pins():
        r = []
        for x in [-1,1]:
            for y in [-1,1]:
                r.append(circle(0.5).translate([2.5*x,6*y]))
        p = linear_extrude(r,3,convexity=10).translate([0,0,-2])
        return p.color("Gold")
    
    ret = []
    ret.append(inner())
    ret.append(body())
    ret.append(pins())

    return union(ret).rotate(rot).translate(pos)

def main():
    '''
        Example use / layout
    '''
    out = [pcb_button_std()]
    output(out)

if __name__ == "__main__":
    main()