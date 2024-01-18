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
inZ = 10;       // how deep (depends on cpu board etc..)
wallRad=1.5;    // round off (case thickness)

printing = true;
assemble = !true;

if(printing) {
  casebody([0,20,0]);
  // lightchannel([0,60,0]);
  caseback([0,-20,0]);
  mcuplate([50,-20,0]);
  foot([0,-50,3]);
  mount([50,-50,9],[90,0,180]);
} else if (assemble) rotate([90,0,0]) {
  footangle = 0;
  // printable bits
  color("LightCyan")
  *casebody([0,0,inZ+5.1],[180,0,0]);
  // color("WhiteSmoke")
  // lightchannel([0,0,inZ+0.60],[180,180,180]);
  color("MediumPurple")
  *caseback();
  color("MediumPurple")
  mcuplate();
  color("MediumPurple",1)
  //foot([0,-19.5,3],[footangle,0,0]);
  *mount([0,-19.5,3],[footangle,0,0]);
  // components
  screens([0,0,inZ+0.8],[0,0,0]);
  rp2040([20,-1,4]);
  //socket([-18.8,-7.5,6],[180,0,0]);
  //button([-19.5,2,8],[0,180,0]);
  //3x12hexhead([23.1,-19.5,3],[0,-90,0]);
  //3x12hexhead([-23.1,-19.5,3],[0,90,0]);
} else {
  // work area
  *casebody([0,0,inZ+5.1],[180,0,0]);
  // *lightchannel([0,0,inZ+0.60],[180,180,180]);
  *caseback();
  mcuplate();
  *rp2040([20,-1,4]);
  *screens([0,0,inZ+0.8],[0,0,0]);
}

module casebody(pos=[0,0,0],rot=[0,0,0])
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
    linear_extrude(height=5,convexity=8) {
      difference() {
        square([inX,inY],center=true);
        for(o=[-screenOff,screenOff])
          for(x=[o-holeOff-1,o+holeOff+1],
              y=[-holeOff-1,holeOff+1])
        translate([x,y]) circle(2.6);
      }
    }
    // Now the bit with the pin tops
    translate([0,0,2.7])
    linear_extrude(height=2,convexity=8) {
      difference() {
        square([inX,inY],center=true);
        for(o=[-screenOff,screenOff])
          for(x=[o-holeOff,o+holeOff],
              y=[-holeOff,holeOff])
            translate([x,y]) circle(d=1);
      }
    }
    // Now the rest of the body to the back.
    translate([0,0,3.6])
    linear_extrude(height=2*inZ,convexity=8) {
      square([inX,inY],center=true);
    }
  }
}

/*

Currently unused, did not really work..

module lightchannel(pos=[0,0,0],rot=[180,0,0])
translate(pos) rotate(rot) {
  thick = inZ - 7.5;
  translate([0,0,-thick])
  linear_extrude(height=thick) {
    difference() {
      // Basic shape
      #minkowski() {
        translate([0,0,2])
        square([inX-1.3,inY-1.3],center=true);
        circle(r=0.5,$fn=24);
      }
      // pins and screenbacks
      for (x=[-screenOff,screenOff]) {
        translate([x,pinOff])
        square([12,4],center=true);
        translate([x,0])
        square([sx-2,sy-2],center=true);
      }
      // central clearance (ie: C3 on R/H screen)
      translate([0,-1])
      square([6,10],center=true);
    }
  }
  // Light collector
  translate([0,-1,-thick-1])
  linear_extrude(height=thick+1,scale=[0.21,5]) {
    square([3.5,5],center=t ue);
  }
}
*/

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
      translate([-19.5,2]) square([12.5,13.2],center=true);
      // mcu cutout
      hull() {
        for(x=[-10,24],y=[-9,7]) {
          translate([x,y]) circle(d=2);
        }
      }
      // vent
      hull() {
        translate([-22,11]) circle(d=2);
        translate([22,11]) circle(d=2);
      }
      // Socket
      translate([-18.8,-7.5])
      square([13.4,3],center=true);
    }
  }
  // foot mount
  translate([0,-19.5,3])
  rotate([0,90,0])
  difference() {
    union() {
      cylinder(d=6,h=30,center=true);
      translate([1,0,-14.5])
      cube([2,6,29]);
    }
    cylinder(d=3.2,h=33,center=true,$fn=6);
  }
  // Tabs to grip onto case
  linear_extrude(height=8,convexity=8) {
    difference() {
      union() {
        square([inX-0.3,24],center=true);
        square([50,inY-0.3],center=true);
      }
      square([inX-4.5,inY-4.5],center=true);
      translate([-screenOff,pinOff])
        square([11,4],center=true);
      translate([screenOff,pinOff])
        square([11,4],center=true);
    }
  }
  // Lip on tabs to grip case
  translate([0,0,7])
  linear_extrude(height=0.5,convexity=8) {
    difference() {
      union() {
        square([inX-0.1,24],center=true);
        square([50,inY-0.1],center=true);
      }
      square([inX-3,inY-3],center=true);
      translate([-screenOff,pinOff])
        square([11,4],center=true);
      translate([screenOff,pinOff])
        square([11,4],center=true);
    }
  }
  // Button recess
  translate([-19.5,2,2])
  linear_extrude(height=6,convexity=20) {
    difference() {
      square([14.5,15.2],center=true);
      square([12.5,13.2],center=true);
    }
  }
  // Button support
  translate([-19.5,2,8])
  linear_extrude(height=1,convexity=20,scale=[0.85,0.9]) {
    square([14.5,9],center=true);
  }
  // socket support
  translate([-18.8,-7.5])
  linear_extrude(height=6,convexity=20) {
    difference() {
      square([15.2,5],center=true);
      square([13.4,2.8],center=true);
    }
  }
  // mcu plate clips
  difference() {
    for (x=[-6,20],y=-[-9,11.12]) {
      translate([x,y,1])
      linear_extrude(height=6,convexity=20,scale=[0.4,1.2]) {
        square([12,2],center=true);
      }
    }
    // indents
    for(x=[-6,20],y=-[-7,9]) {
      translate([x,y,3.5])
      sphere(r=1.5,$fn=24);
    }

  }
}

module mcuplate(pos=[0,0,0],rot=[0,0,0])
translate(pos) rotate(rot) {
  linear_extrude(height=1.2,convexity=10) {
    difference() {
      // baseplate
      hull() {
        for(x=[-10,24],y=[-9,7]) {
          translate([x,y]) circle(d=1,$fn=24);
        }
      }
      // logo
      translate([7,-1])
      mirror([1,0])
      scale([0.9,1])
      //offset(r=0.1,$fn=24)
      text("XIAO",halign="center",valign="center",size=10,$fn=24);
      // removal slot
      translate([24.0,-1])
      square([1,9],center=true);
    }
  }
  // support the board and logo, stiffen length-wise
  translate([7.5,-0.8,1])
  linear_extrude(height=2.9,convexity=10,scale=[0.9,0.2]) {
    square([27,2.4],center=true);
  }
  // clip mechanism and mcu support
  difference() {
    union() {
      // USB-C clip + bracket
      translate([20.45,-1,1])
      linear_extrude(height=9,convexity=10) {
        square([5,17],center=true);
      }
      // reinforce USB-C clip plates 
      for (y=[-6.9,4.9]) {
        translate([19,y,1])
        linear_extrude(height=4,convexity=10,scale=[0.6,0.6]) {
          square([11,2.2],center=true);
        }
      }
      // 'button end' board positioners
      for(y=-[-5.75,7.75]) {
        translate([-4.5,y,1])
        linear_extrude(height=6,convexity=10,scale=[0.4,1]) {
          square([10,3.5],center=true);
        }
      }
      // board clips
      for(y=-[-6.5,8.5]) {
        translate([1.5,y,1])
        linear_extrude(height=9,convexity=10,scale=[0.6,1],) {
          translate([-6,0])
          square([10,2],center=true);
        }
      }
      // balls
      for(x=[-6,20],y=-[-7,9]) {
        translate([x,y,3.5])
        sphere(r=1.52,$fn=24);
      }
    }
    // remove cutout for xiao board
    translate([20,-1,4])
    linear_extrude(height=1.4,convexity=10) {
      xiaoOutline(r=0.2);
    }
    // this creates a insert clearance to clip xiao into
    translate([20,-1,5.3])
    linear_extrude(height=5.5,convexity=10,scale=[0.75,1]) {
      xiaoOutline(r=0);
    }
    // The USB-C socket hole
    translate([15,-1,6.8])
    rotate([0,90,0])
    hull() {
      for (y=[-1,1]) {
        translate([0,y*3,0])
        cylinder(d=3.5,h=10,$fn=24);
      }
    }
    // Then cut USB bracket body to make a clip
    translate([20.9,-1,0])
    linear_extrude(height=11,convexity=10) {
      square([8,6.75],center=true);
    }
    translate([20.6,-1,0])
    linear_extrude(height=5,convexity=10,scale=[1,0.6]) {
      square([2.4,10.66],center=true);
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

// Any XIAO module will fit, this is model is the RP2040
module rp2040(pos=[0,0,0],rot=[0,0,180])
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

// Generate an outline of the XIAO.
module xiaoOutline(r=0) {
  offset(r=r,$fn=24)
  projection(cut = true,$fn=24)
  rp2040();
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
  linear_extrude(height=6,convexity=10) {
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
  translate([0,0,-0.6])
  for (x=[-2:1:2]) {
    linear_extrude(height=0.6) {
      translate([x*pitch,1.6])
      square([0.6,4],center=true);
    }
  }
}
