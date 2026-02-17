// Gimbal Ring for 90mm Main Impeller
// External gear teeth for servo actuation
// ±30° tilt capability

$fn = 120; // High resolution for smooth curves

// Parameters
main_impeller_diameter = 90;
ring_outer_diameter = 110;
ring_inner_diameter = 95;
ring_height = 25;
gear_tooth_count = 60;
gear_tooth_height = 3;
gear_tooth_width = 4;
bearing_seat_diameter = 92;
bearing_seat_depth = 3;
mounting_hole_diameter = 3.2; // M3 clearance
servo_arm_engagement_radius = 55;

// Main ring body
module gimbal_ring() {
    difference() {
        union() {
            // Main ring structure
            cylinder(h = ring_height, d = ring_outer_diameter);
            
            // External gear teeth
            for (i = [0:gear_tooth_count-1]) {
                rotate([0, 0, i * (360/gear_tooth_count)])
                translate([ring_outer_diameter/2, 0, ring_height/2])
                cube([gear_tooth_height, gear_tooth_width, ring_height], center = true);
            }
            
            // Reinforcement ribs (4x at cardinal points)
            for (i = [0:3]) {
                rotate([0, 0, i * 90])
                translate([ring_outer_diameter/2 - 5, 0, ring_height/2])
                cube([10, 6, ring_height], center = true);
            }
        }
        
        // Inner bore for impeller motor
        translate([0, 0, -1])
        cylinder(h = ring_height + 2, d = ring_inner_diameter);
        
        // Bearing seat (upper surface)
        translate([0, 0, ring_height - bearing_seat_depth])
        cylinder(h = bearing_seat_depth + 1, d = bearing_seat_diameter);
        
        // 4x mounting holes for gimbal pivot points
        for (i = [0:3]) {
            rotate([0, 0, i * 90])
            translate([servo_arm_engagement_radius, 0, -1])
            cylinder(h = ring_height + 2, d = mounting_hole_diameter);
        }
        
        // Weight reduction cutouts (8x)
        for (i = [0:7]) {
            rotate([0, 0, i * 45 + 22.5])
            translate([ring_outer_diameter/2 - 8, 0, ring_height/2])
            cube([12, 8, ring_height + 2], center = true);
        }
    }
}

// Motor mount platform (sits inside ring)
module motor_mount() {
    difference() {
        union() {
            // Mounting plate
            cylinder(h = 4, d = 85);
            
            // Motor boss
            translate([0, 0, 4])
            cylinder(h = 8, d = 28); // Standard brushless motor mount
        }
        
        // Center hole for motor shaft
        translate([0, 0, -1])
        cylinder(h = 20, d = 10);
        
        // 4x M3 motor mounting holes (16mm bolt circle)
        for (i = [0:3]) {
            rotate([0, 0, i * 90])
            translate([8, 8, -1])
            cylinder(h = 20, d = 3.2);
        }
        
        // Wire routing channels
        for (i = [0:1]) {
            rotate([0, 0, i * 180])
            translate([30, 0, 2])
            cube([30, 5, 10], center = true);
        }
    }
}

// Generate parts
translate([0, 0, 0]) gimbal_ring();
translate([0, 0, 35]) motor_mount();

// Text labels for orientation
translate([0, ring_outer_diameter/2 + 10, 1])
linear_extrude(height = 1)
text("FRONT", size = 6, halign = "center", font = "Liberation Sans:style=Bold");
