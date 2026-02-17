// 50mm Bladeless Impeller Housing
// Ducted design for efficiency
// Servo-actuated tilt mount

$fn = 100;

// Parameters
impeller_diameter = 50;
duct_outer_diameter = 58;
duct_height = 35;
wall_thickness = 2.5;
inlet_taper_angle = 15; // Degrees
outlet_expansion_angle = 10;
motor_mount_diameter = 28;
servo_mount_width = 23;
servo_mount_length = 12.5;
tilt_axis_diameter = 4; // Bearing or pivot rod

// Main ducted housing
module impeller_housing() {
    difference() {
        union() {
            // Main duct body
            cylinder(h = duct_height, d = duct_outer_diameter);
            
            // Inlet bell (top)
            translate([0, 0, duct_height])
            cylinder(h = 8, d1 = duct_outer_diameter, d2 = duct_outer_diameter + 12);
            
            // Outlet diffuser (bottom)
            translate([0, 0, -6])
            cylinder(h = 6, d1 = duct_outer_diameter + 8, d2 = duct_outer_diameter);
            
            // Mounting tabs for servo connection (2x sides)
            for (i = [0:1]) {
                rotate([0, 0, i * 180])
                translate([duct_outer_diameter/2, 0, duct_height/2])
                cube([8, servo_mount_width + 4, 16], center = true);
            }
            
            // Aerodynamic stator vanes (4x for flow straightening)
            for (i = [0:3]) {
                rotate([0, 0, i * 90])
                translate([impeller_diameter/2 - 2, 0, duct_height - 15])
                linear_extrude(height = 10, twist = -15)
                square([wall_thickness, 3], center = true);
            }
        }
        
        // Inner duct bore
        translate([0, 0, -7])
        cylinder(h = duct_height + 16, d = impeller_diameter + 1);
        
        // Motor mounting recess
        translate([0, 0, duct_height/2 - 5])
        cylinder(h = 12, d = motor_mount_diameter);
        
        // Motor mounting holes (4x M2 or M2.5)
        for (i = [0:3]) {
            rotate([0, 0, i * 90 + 45])
            translate([10, 0, duct_height/2 - 5])
            cylinder(h = 12, d = 2.5);
        }
        
        // Tilt axis pivot holes (through mounting tabs)
        for (i = [0:1]) {
            rotate([0, 0, i * 180])
            translate([duct_outer_diameter/2 + 4, 0, duct_height/2])
            rotate([90, 0, 0])
            cylinder(h = 40, d = tilt_axis_diameter, center = true);
        }
        
        // Wire routing channel
        translate([0, duct_outer_diameter/2 - 2, duct_height/2])
        cube([5, 10, duct_height + 10], center = true);
        
        // Weight reduction slots (8x radial)
        for (i = [0:7]) {
            rotate([0, 0, i * 45])
            translate([duct_outer_diameter/2 - 4, 0, 5])
            cube([wall_thickness + 1, 4, duct_height - 10], center = true);
        }
    }
}

// Servo linkage bracket
module servo_bracket() {
    difference() {
        union() {
            // Main bracket body
            cube([servo_mount_length, servo_mount_width, 6], center = true);
            
            // Pivot boss
            translate([servo_mount_length/2 + 3, 0, 0])
            rotate([90, 0, 0])
            cylinder(h = servo_mount_width, d = 8, center = true);
        }
        
        // Servo arm connection slot
        translate([-servo_mount_length/2, 0, 0])
        cube([6, 3, 8], center = true);
        
        // Pivot hole
        translate([servo_mount_length/2 + 3, 0, 0])
        rotate([90, 0, 0])
        cylinder(h = servo_mount_width + 2, d = tilt_axis_diameter, center = true);
        
        // M2 mounting screws
        for (i = [-1:2:1]) {
            translate([-2, i * 8, 0])
            cylinder(h = 10, d = 2.2, center = true);
        }
    }
}

// Generate parts
impeller_housing();
translate([0, 80, 3]) rotate([0, 0, 90]) servo_bracket();
