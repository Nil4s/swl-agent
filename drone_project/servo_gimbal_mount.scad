// Servo Mount for Gimbal Ring Control
// For MG90S 9g servo (12.5 x 23 x 29mm)
// Mounts to base plate, actuates gimbal ring

$fn = 80;

// MG90S Servo dimensions
servo_body_length = 23;
servo_body_width = 12.5;
servo_body_height = 29;
servo_ear_height = 17; // From bottom to mounting ear
servo_ear_thickness = 2.5;
servo_ear_length = 32.5;
mounting_hole_spacing = 28; // Center to center
mounting_hole_diameter = 2.2; // M2 clearance

// Mount parameters
base_plate_thickness = 3;
mount_height = 35; // Elevation for gear engagement
pivot_arm_length = 25;
gear_engagement_radius = 55;

// Main servo mounting bracket
module servo_mount() {
    difference() {
        union() {
            // Vertical support column
            translate([0, 0, mount_height/2])
            cube([18, servo_body_length + 6, mount_height], center = true);
            
            // Base mounting plate
            translate([0, 0, -2])
            cube([25, servo_body_length + 10, 4], center = true);
            
            // Servo cradle
            translate([-servo_body_width/2 - 2, 0, mount_height - servo_body_height/2 - 5])
            cube([servo_body_width + 4, servo_body_length + 4, servo_body_height], center = true);
            
            // Reinforcement gussets
            for (i = [-1:2:1]) {
                translate([0, i * (servo_body_length/2 + 2), mount_height/2])
                rotate([0, 0, 0])
                linear_extrude(height = mount_height, scale = [0.3, 1])
                square([15, 4], center = true);
            }
        }
        
        // Servo body cavity
        translate([-servo_body_width/2 - 1, 0, mount_height - servo_body_height/2 - 5])
        cube([servo_body_width + 0.5, servo_body_length + 0.5, servo_body_height + 1], center = true);
        
        // Servo mounting ear slots
        translate([0, 0, mount_height - servo_body_height + servo_ear_height - 5])
        cube([20, servo_body_length + 8, servo_ear_thickness + 0.3], center = true);
        
        // Mounting screw holes (M2 for servo ears)
        for (i = [-1:2:1]) {
            translate([0, i * mounting_hole_spacing/2, mount_height - servo_body_height + servo_ear_height - 5])
            rotate([0, 90, 0])
            cylinder(h = 30, d = mounting_hole_diameter, center = true);
        }
        
        // Base plate mounting holes (M3 to frame)
        for (x = [-1:2:1]) {
            for (y = [-1:2:1]) {
                translate([x * 8, y * (servo_body_length/2 + 2), -3])
                cylinder(h = 8, d = 3.2);
            }
        }
        
        // Wire routing channel
        translate([0, servo_body_length/2 + 2, mount_height/2])
        cube([6, 12, mount_height + 2], center = true);
    }
}

// Servo arm to gimbal ring linkage
module linkage_arm() {
    difference() {
        union() {
            // Main arm body
            hull() {
                // Servo horn connection
                cylinder(h = 4, d = 8);
                
                // Gimbal ring connection
                translate([pivot_arm_length, 0, 0])
                cylinder(h = 4, d = 8);
            }
            
            // Reinforcement rib
            translate([pivot_arm_length/2, 0, 2])
            cube([pivot_arm_length, 4, 3], center = true);
        }
        
        // Servo horn mounting hole (M2.5 or servo spline)
        translate([0, 0, -1])
        cylinder(h = 8, d = 3);
        
        // Gimbal ring connection hole (M3)
        translate([pivot_arm_length, 0, -1])
        cylinder(h = 8, d = 3.2);
        
        // Weight reduction
        translate([pivot_arm_length/2, 0, -1])
        cylinder(h = 8, d = 6);
    }
}

// Gimbal ring connection bearing housing
module bearing_mount() {
    difference() {
        cylinder(h = 8, d = 12);
        
        // Bearing bore (608 or similar small bearing)
        translate([0, 0, 2])
        cylinder(h = 7, d = 8.2);
        
        // Through hole
        translate([0, 0, -1])
        cylinder(h = 12, d = 4.2);
    }
}

// Generate parts layout
servo_mount();
translate([60, 0, 2]) rotate([0, 0, 90]) linkage_arm();
translate([60, 25, 0]) bearing_mount();

// Assembly note
translate([-15, -25, 1])
linear_extrude(height = 0.5)
text("3x per gimbal axis", size = 3, font = "Liberation Sans:style=Bold");
