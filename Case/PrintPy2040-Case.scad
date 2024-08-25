// PrintPy2040 Case

// This is a very small model, 60 is fine here:
$fn=60;
// I override in a lot of places for speed and because
// the effects are simply not visible on mm-sized bits.

// OLED screen modules
sx = 27.4;              // Board width
sy = 28;                // Board height
vx = 21.7;              // viewport width
vy = 10.8;              // viewport height
vo = -1.75;             // viewport y offset
holeOff = 23.5/2;       // Holes are 23.5mm apart
pinOff = (sy/2)-1.5;    // Pins on PCB are 1.5mm from edge
screenOff = (sx/2)+0.1; // X offset for each screen + gap

// Case size (x,y based on screen dimensions)
inX = (2*sx)+1; // basic interior space based on screens
inY = sy+1;
inZ = 12.5;       // how deep (depends on cpu board etc..)
//inZ = 10;  // SLIM CASE
wallRad=1.5;    // round off (case thickness)
insetB=8;       // inset for button and socket (8 is max..)
//insetB=6;  // SLIM CASE

printing = true;
assemble = true;

if(printing) {
  casebody([0,20,0],[0,0,180]);
  casebody([66,20,0],[0,0,180],usb=false);
  caseback([0,-20,0]);
  foot([66,-25,3]);
  mount([66,-8,9],[90,0,180]);
} else if (assemble) rotate([90,0,0]) {
  footangle = -90;
  // printable bits
  color("WhiteSmoke")
  casebody([0,0,inZ+5.1],[180,0,0]);
  color("MediumPurple")
  caseback();
  color("MediumPurple")
  foot([0,-19.5,3],[footangle,0,0]);
  //mount([0,-19.5,3],[footangle,0,0]);
  // components
  screens([0,0,inZ+0.8],[0,0,0]);
  rp2040([0,-12.2,4]);
  socket([-19.4,-7.5,insetB],[180,0,0]);
  button([-19.5,2,insetB],[0,180,0]);
  3x12hexhead([23.1,-19.5,3],[0,-90,0]);
  3x12hexhead([-23.1,-19.5,3],[0,90,0]);
} else {
  // work area
  difference() {
    union() {
      *casebody([0,0,inZ+5.1],[180,0,0]);
      caseback();
      rp2040([0,-12.2,4]);
      *screens([0,0,inZ+0.8],[0,0,0]);
    }
    // Intersector.. for layout checking
    translate([10,-50,-10])
    *cube([100,100,100]);
  }
}

module casebody(pos=[0,0,0],rot=[0,0,0],usb=true)
translate(pos) rotate(rot) {
  difference() {
    // Basic shape
    minkowski() {
      translate([0,0,inZ/2+wallRad])
      cube([inX,inY,inZ],center=true);
      sphere(wallRad);
    }
    // Screen Opening, 0.5mm margin)
    hull() {
      x=(2*(screenOff+(vx/2)))+1;
      y=vy+1;
      translate([0,vo,0])
      cube([x+2,y+1,0.1],center=true);
      translate([0,vo,1])
      cube([x,y,0.1],center=true);
    }
    // Display mounts
    // Section with fat pins to support oleds
    translate([0,0,1])
    linear_extrude(height=1.8,convexity=8) {
      difference() {
        square([inX,inY],center=true);
        for(o=[-screenOff,screenOff])
          for(x=[o-holeOff-1,o+holeOff+1],
              y=[-holeOff-1,holeOff+1])
        translate([x,y]) circle(2.6);
      }
    }
    // Now the rest of the body to the back.
    translate([0,0,2.7])
    linear_extrude(height=2*inZ,convexity=8) {
      square([inX,inY],center=true);
    }
    if (usb) {
      translate([0,10,inZ-1.5])
      rotate([90,0,0])
      hull() {
        translate([3,0,0])
        cylinder(r=4, h=30, center=true);
        translate([-3,0,0])
        cylinder(r=4, h=30, center=true);
        translate([0,5,0])
        cube([14,10,30],center=true);
      }
    }
  }
}

module caseback(pos=[0,0,0],rot=[0,0,0])
translate(pos) rotate(rot) {
  //Baseplate
  linear_extrude(height=2,convexity=20) {
    difference() {
      minkowski() {
        square([inX-wallRad,inY-wallRad],center=true);
        circle(wallRad);
      }
      // button opening
      translate([-19.4,2]) square([12.5,13.2],center=true);
      // vents
      hull() {
        translate([-22,11]) circle(d=2);
        translate([22,11]) circle(d=2);
      }
      hull() {
        translate([-22,-11]) circle(d=2);
        translate([22,-11]) circle(d=2);
      }
      // logo
      translate([8,0])
      mirror([1,0])
      scale([1,1.2])
      text("XIAO",halign="center",valign="center",size=10,$fn=24);
      // Socket
      translate([-19.4,-7.5])
      square([13.8,2.8],center=true);
    }
  }
  // support the logo
  translate([7,0.25,1])
  linear_extrude(height=1,convexity=10,scale=[0.9,0.6]) {
    square([34,1.5],center=true);
  }
  // foot mount
  translate([0,-19.5,3])
  rotate([0,90,0])
  difference() {
    union() {
      cylinder(d=6,h=30,center=true);
      translate([1,0,-14.5])
      cube([2,6,8]);
      translate([1,0,6.5])
      cube([2,6,8]);
    }
    cylinder(d=3.2,h=33,center=true,$fn=6);
    translate([0,0,0])
    cube([8,10,14],center=true);
  }
  // Walls to grip onto case
  difference() {
    linear_extrude(height=inZ-1+0.7,convexity=8) {
      difference() {
        square([51,inY-0.3],center=true);
        square([inX-4.5,inY-4.5],center=true);
      }
    }
    // The USB-C socket hole
    translate([0,-10,6.8])
    rotate([90,0,0])
    hull() {
      for (x=[-1,1]) {
        translate([x*3,0,0])
        cylinder(d=3.25,h=10,$fn=24);
      }
    }
    // Then cut wall to make the USB-C clip
    translate([0,-13,6])
    linear_extrude(height=inZ,convexity=10) {
      square([8,4],center=true);
    }
    translate([0,-13,0])
    linear_extrude(height=6,convexity=10,scale=[1.5,1]) {
      square([4,4],center=true);
    }
    // gaps in upper wall
    for (x=[-1,1]) {
      translate([15*x,13,2])
      linear_extrude(height=inZ-1,convexity=10,scale=[2,1]) {
        square([9.8,4],center=true);
      }
    }
  }
  // Lip on walls to grip case
  translate([0,0,8.5])
  linear_extrude(height=1,convexity=8) {
    difference() {
      square([46,inY-0.1],center=true);
      square([inX-3,inY-3],center=true);
      translate([0,-12])
      square([8,8],center=true);
      for (x=[-1,1]) {
        translate([16*x,12])
        square([22,8],center=true);
      }
    }
  }
  // clip posts at other end of MCU
  difference() {
    for (x=[-1,1]) {
      translate([x*6.3,7.8,2])
      linear_extrude(height=4.6, convexity=10, scale=[0.66,0.9]) {
        translate([2*x,3])
        square([4,7],center=true);
      }
    }
    translate([0,0,4])
    linear_extrude(height=1.2, convexity=10) {
      projection() {
        scale([1.02,1.02])
         rp2040([0,-12.2,4]);
      }
    }
    translate([0,7.8,5.5])
    rotate([45,0,0])
    cube([20,1.7,2.55],center=true);
  }
  // brace clip walls
  for (x=[-1,1]) {
    translate([11.6*x,-14.2,2])
    linear_extrude(height=7,convexity=10,scale=[1,0.3]) {
      translate([0,3])
      square([1.6,6],center=true);
    }
  }
  // screen support pins
  for (x=[-1,1],y=[-1,1]) {
    translate([(x*screenOff)+(x*holeOff),y*holeOff,inZ+0.7])
    sphere(0.6);
  }
  // screen support posts
  linear_extrude(height=inZ+0.7,convexity=10) {
  for (x=[-1,1],y=[-1,1])
    translate([(x*screenOff)+(x*holeOff),y*holeOff])
    circle(2);
  }
  // support screens in center
  translate([0,0,inZ-1])
  linear_extrude(height=1.7,convexity=8) {
    difference() {
      square([12,inY-0.3],center=true);
      square([inX-4.5,inY-4.5],center=true);
      translate([0,-13,6])
      square([8,4],center=true);
    }
  }
  // Button recess
  translate([-19.4,2,2])
  linear_extrude(height=insetB-2,convexity=20) {
    difference() {
      square([14.5,15.2],center=true);
      square([12.5,13.2],center=true);
    }
    // Fillet to connect to the nearby screen post
    translate([-7.25,7.5])
    square([2,1]);
  }
  // Button support
  translate([-19.4,2,insetB])
  linear_extrude(height=1,convexity=20, scale=[0.85,1]) {
    for (y=[-3,0,3]) {
      translate([0,y])
      square([14.5,1.4],center=true);
    }
  }
  // socket support
  translate([-19.4,-7.5,2])
  linear_extrude(height=insetB-2,convexity=20) {
    difference() {
      square([15.6,5],center=true);
      square([13.8,2.8],center=true);
    }
  }
  translate([-19.4,-9,insetB+0.5])
  cube([15.6,2,1],center=true);
  // Thin wall around base
  difference() {
    linear_extrude(height=3,convexity=8) {
      difference() {
        union() {
          square([inX-0.3,inY-6],center=true);
          square([inX-6,inY-0.3],center=true);
        }
        square([inX-2,inY-2],center=true);
        translate([0,-14])
        square([10,6],center=true);
      }
    }
  }
}

module foot(pos=[0,0,0],rot=[0,0,0])
translate(pos) rotate(rot) {
  rotate([0,90,0])
  difference() {
    hull() {
      cylinder(d=6,h=46,center=true);
      translate([1.5,-16,0])
      cylinder(d=3,h=36,center=true);
    }
    hull() {
      cylinder(d=6.4,h=30.3,center=true);
      translate([6,-6,0])
      cylinder(d=6.4,h=30.3,center=true);
    }
    cylinder(d=3.4,h=41,center=true);
    for (z=[-22,22]) {
      translate([0,0,z])
      cylinder(d=6.6,h=4,center=true);
    }
    rotate([0,90,0])
    translate([0,-14,1.8])
    linear_extrude(height=2,convexity=10) {
      text("EasyTarget",size=5,halign="center",$fn=24);
    }
  }
}

module mount(pos=[0,0,0],rot=[0,0,0])
translate(pos) rotate(rot) {
  rotate([90,-90,90])
  difference() {
    union() {
      hull() {
        cylinder(d=6,h=40,center=true);
        translate([0,6,0])
        cylinder(d=6,h=26,center=true);
      }
      hull() {
        translate([0,6,0])
        cylinder(d=6,h=26,center=true);
        translate([-15,7,0])
        cylinder(d=4,h=20,center=true);
      }
    }
    cylinder(d=3.4,h=41,center=true);
    hull() {
      cylinder(d=6.4,h=30.3,center=true);
      translate([-6,0,0])
      cylinder(d=6.4,h=30.3,center=true);
    }
    for (z=[-22,22]) {
      translate([0,0,z])
      cylinder(d=6.6,h=4,center=true);
    }
    rotate([0,90,90])
    translate([0,10,8])
    linear_extrude(height=1.1,convexity=10) {
      text("Easy",size=5,halign="center");
    }
    rotate([0,90,90])
    translate([0,0.5,8])
    linear_extrude(height=1.1,convexity=10) {
      text("Target",size=5,halign="center",$fn=24);
    }
    rotate([0,90,90])
    translate([0,7,3])
    linear_extrude(height=10,convexity=10) {
      circle(d=3.5);
    }
    rotate([0,90,90])
    translate([0,7,3])
    linear_extrude(height=4,convexity=10) {
      circle(d=6);
    }
  }
}

// Modules and parts

// Two screens with correct spacing.
module screens(pos=[0,0,0],rot=[0,0,0])
translate(pos) rotate(rot) {
  // left
  oled([-screenOff,0,0]);
  // right
  oled([screenOff,0,0]);
  // tape that seals the join..
  color("black")
  cube([2,sx-6,0.02],center=true);
}

// OLED is based on a generic JMD0.96A-2 module
module oled(pos=[0,0,0],rot=[0,0,0],pins=false)
translate(pos) rotate(rot) {
  color("blue")
  linear_extrude(height=1.2,convexity=5)
  difference() {
    square([sx,sy],center=true);
    for(x=[-1,1],y=[-1,1])
      translate([x*holeOff,y*holeOff]) circle(d=2.3);
  }
  color("grey",0.7) {
    translate([0,-0.25,1.3])
    linear_extrude(height=1.4,convexity=5)
    square([sx,19.2],center=true);
    translate([0,-10,1.3])
    linear_extrude(height=0.8,convexity=5)
    square([12.5,7.8],center=true);
    translate([0,1.5,1.3])
    linear_extrude(height=1.8,convexity=5)
    square([sx,14.5],center=true);
  }
  for(x=[-3.81,-1.27,1.27,3.81]) {
    if (pins) {
      color("gold")
      translate([x,pinOff,-8.3])
      linear_extrude(height=11.3,convexity=5)
      square([0.6,0.6],center=true);
      color("grey")
      translate([x,pinOff,-2.5])
      linear_extrude(height=2.5,convexity=5)
      square([2,2.6],center=true);
    } else {
      color("gold")
      translate([x,pinOff,-1])
      linear_extrude(height=3,convexity=5)
      circle(d=1, $fn=24);
    }
  }
}

// A VERY common button design used in lots of kits etc.
module button(pos=[0,0,0],rot=[0,0,0])
translate(pos) rotate(rot) {
  color("Silver")
  linear_extrude(3.3,convexity=10) {
    square([11,11],center=true);
  }
  color("DimGray") {
    linear_extrude(3.3,convexity=10) {
      difference() {
        square([12,12],center=true);
        square([11,11],center=true);
      }
    }
    linear_extrude(4.1,convexity=10) {
      circle(3.4);
      for(x=[-1,1],y=[-1,1]) {
        translate([3.75*x,3.75*y]) circle(0.5);
      }
    }
    linear_extrude(7.2,convexity=10) {
      square([3,3],center=true);
    }
    translate([0,0,5.7])
    linear_extrude(2.3,convexity=10) {
      square([4,4],center=true);
    }
  }
  color("Gold")
  translate([0,0,-2])
  linear_extrude(3,convexity=10) {
    for(x=[-1,1],y=[-1,1]) {
      translate([2.5*x,6*y]) circle(0.5);
    }
  }
}

// Any XIAO module will fit, this model is the RP2040
module rp2040(pos=[0,0,0],rot=[0,0,90])
translate(pos) rotate(rot) {
  color("green")  // PCB
  linear_extrude(height=1.2, convexity=10) {
    difference() {
      minkowski() {
        translate([10.625,0])
        square([19.25,15.5],center=true);
        circle(r=1,$fn=24);
      }
      for (x=[3:2.54:19],y=[-9,-7.7,7.7,9]) {
        translate([x,y])
        circle(d=0.8, $fn=24);
      }
    }
  }
  color("silver")  // USB-C
  translate([-1.2,0,2.8])
  rotate([0,90,0])
  hull() {
    for (y=[-1,1]) {
      translate([0,y*2.9,0])
      cylinder(d=3.2,h=7.25,$fn=24);
    }
  }
  color("slategrey")  // mcu
  translate([12.75,0,1.2])
  linear_extrude(height=1,convexity=10) {
    square([10.6,12.4], center=true);
  }
  color("azure")  // NeoPixel
  translate([19.9,0,1.2])
  linear_extrude(height=1,convexity=10) {
    square([2.4,2.6], center=true);
  }
  color("darkslategrey")  // discreet components
  translate([0,0,1.2])
  linear_extrude(height=0.5,convexity=10) {
    for (y=[-1,1]) {
      translate([3.8,y*5.3])
      square([5,1.5], center=true);
    }
  }
  for (y=[-1,1]) {
    translate([19.9,y*4,1.2]) {
      color("silver")  // switches
      linear_extrude(height=1,convexity=10) {
        square([2.4,4], center=true);
      }
      color("darkslategrey") // buttons
      cylinder(d=1.4,h=1.25,$fn=24);
    }
  }
  // solderpoints
  color("gold")
  translate([0,0,-0.4])
  linear_extrude(height=2,convexity=10)
    for (x=[3:2.54:19],y=[-7.7,7.7]) {
    translate([x,y])
    circle(d=1, $fn=24);
  }
}

// A 3mm X 12mm hex head bolt
module 3x12hexhead(pos=[0,0,0],rot=[0,0,0])
translate(pos) rotate(rot)
color("silver") {
  difference() {
    cylinder(d=5.2,h=3);
    translate([0,0,-0.1])
    cylinder(d=3,h=3);
  }
  translate([0,0,3])
  cylinder(d=3,h=12);
}

// 5pin PinSocket, defaults to 2.54mm pitch
module socket(pos=[0,0,0],rot=[0,0,0],pitch=2.54)
translate(pos) rotate(rot) {
  color("grey")
  linear_extrude(height=8,convexity=10) {
    difference() {
      square([pitch*5,pitch],center=true);
      for (x=[-2:1:2]) {
        translate([x*pitch,0])
        square([1,1],center=true);
      }
    }
  }
  color("grey")
  linear_extrude(height=1,convexity=10) {
    square([pitch*5,pitch],center=true);
  }
  color("gold")
  translate([0,0,-1.6])
  for (x=[-2:1:2]) {
    linear_extrude(height=1.6) {
      translate([x*pitch,0])
      square([0.6,0.6],center=true);
    }
  }
}
