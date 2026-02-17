// COMPLETE DRONE ASSEMBLY - 3D VISUALIZATION
// Exploded view showing all components
// Toggle between assembled and exploded views

$fn = 60; // Performance balance for preview

// ASSEMBLY MODE
exploded = true;  // Set to false for assembled view
explode_distance = 60; // mm separation in exploded view

// Import simplified shapes (actual parts would use include)
// Using basic geometry for fast visualization

// ============================================================================
// MAIN IMPELLER ASSEMBLY
// ============================================================================
module main_impeller_complete(explode = 0) {
    // Gimbal ring
    translate([0, 0, explode * 2])
    color("SteelBlue", 0.8)
    difference() {
        cylinder(h = 25, d = 110);
        translate([0, 0, -1])
        cylinder(h = 27, d = 95);
        
        // Gear teeth (simplified)
        for (i = [0:11]) {
            rotate([0, 0, i * 30])
            translate([55, 0, 12.5])
            cube([6, 4, 26], center = true);
        }
    }
    
    // Motor mount platform
    translate([0, 0, 8 - explode * 0.5])
    color("DarkSlateGray")
    difference() {
        cylinder(h = 4, d = 85);
        translate([0, 0, -1])
        cylinder(h = 6, d = 28);
    }
    
    // Main motor (visual representation)
    translate([0, 0, 12 - explode])
    color("Gold", 0.7)
    cylinder(h = 20, d = 28);
    
    // AI Bladeless ring (option 1)
    if (!exploded || explode > 0.5) {
        translate([0, 0, 32 + explode])
        color("LightSkyBlue", 0.6)
        difference() {
            // Outer shroud
            rotate_extrude()
            translate([45, 0, 0])
            polygon([
                [0, -12], [5, -10], [6, -6], [7, 0],
                [7, 8], [6, 14], [5, 18], [3, 22], [0, 24]
            ]);
            
            // Inner duct
            rotate_extrude()
            translate([40, 0, 0])
            polygon([
                [0, -8], [3, -7], [4, -3], [4, 2],
                [4, 12], [3, 16], [2, 19], [0, 20]
            ]);
        }
    }
    
    // AI-Optimized blades (option 2 - inside bladeless)
    if (exploded && explode > 0.5) {
        translate([0, 0, 37 + explode * 1.5])
        color("Cyan", 0.5)
        for (i = [0:2]) {
            rotate([0, 0, i * 120])
            translate([14, 0, 0])
            linear_extrude(height = 12, twist = -25, scale = 0.7)
            polygon([
                [0, 0], [26, 0], [24, 2], [22, 2.5],
                [20, 2.5], [18, 2.3], [16, 2], [14, 1.5],
                [12, 1], [10, 0.5], [8, 0.3], [6, 0.2],
                [4, 0.1], [2, 0]
            ]);
        }
    }
}

// ============================================================================
// PERIPHERAL IMPELLER (50mm)
// ============================================================================
module peripheral_impeller(explode = 0) {
    // Housing
    color("RoyalBlue", 0.7)
    difference() {
        union() {
            cylinder(h = 35, d = 58);
            // Inlet bell
            translate([0, 0, 35])
            cylinder(h = 8, d1 = 58, d2 = 70);
            // Outlet diffuser
            translate([0, 0, -6])
            cylinder(h = 6, d1 = 66, d2 = 58);
        }
        
        translate([0, 0, -7])
        cylinder(h = 51, d = 50);
    }
    
    // Mounting tabs
    color("DarkBlue")
    for (i = [0:1]) {
        rotate([0, 0, i * 180])
        translate([29, 0, 17.5])
        cube([8, 27, 16], center = true);
    }
    
    // Motor (simplified)
    translate([0, 0, 17.5 - explode * 0.3])
    color("Orange", 0.6)
    cylinder(h = 15, d = 16);
}

// ============================================================================
// SERVO (SG90/MG90S)
// ============================================================================
module servo_sg90() {
    color("DarkSlateGray", 0.8)
    difference() {
        // Body
        cube([23, 12.5, 29], center = true);
        
        // Horn cutout
        translate([0, 0, 14.5])
        cylinder(h = 3, d = 6);
    }
    
    // Mounting ears
    color("Black")
    translate([0, 0, -14.5 + 17])
    cube([32.5, 12.5, 2.5], center = true);
    
    // Servo horn
    translate([0, 0, 16])
    color("White")
    cylinder(h = 4, d = 8);
}

// ============================================================================
// ARDUINO NANO + HOUSING
// ============================================================================
module arduino_nano_housing() {
    color("DarkGreen", 0.7)
    difference() {
        // Housing
        cube([51, 26, 15], center = true);
        
        // Cavity
        translate([0, 0, 1])
        cube([47, 22, 16], center = true);
    }
    
    // Arduino board (simplified)
    translate([0, 0, -3])
    color("DarkCyan", 0.9)
    cube([43, 18, 2], center = true);
    
    // Components on board
    translate([0, 0, -1])
    color("Black")
    cube([10, 10, 3], center = true);
}

// ============================================================================
// MPU6050 IMU
// ============================================================================
module mpu6050_imu() {
    color("Purple", 0.8)
    cube([21, 16, 3], center = true);
    
    // Sensor chip
    translate([0, 0, 2])
    color("Silver")
    cube([4, 4, 1], center = true);
}

// ============================================================================
// LIPO BATTERY (2S pouch cell)
// ============================================================================
module lipo_battery() {
    color("Yellow", 0.7)
    cube([60, 30, 8], center = true);
    
    // Connector
    translate([0, 15, 0])
    color("Red")
    cube([10, 3, 6], center = true);
}

// ============================================================================
// FRAME BASE
// ============================================================================
module frame_base() {
    color("Gray", 0.5)
    difference() {
        union() {
            // Center hub
            cylinder(h = 3, d = 120);
            
            // Arms (4x)
            for (i = [0:3]) {
                rotate([0, 0, i * 90])
                translate([0, 60, 0])
                cube([30, 200, 3], center = true);
            }
        }
        
        // Center cutout
        translate([0, 0, -1])
        cylinder(h = 5, d = 100);
    }
}

// ============================================================================
// COMPLETE ASSEMBLY
// ============================================================================

// Set explosion factor
explosion = exploded ? explode_distance : 0;

// FRAME (bottom layer)
translate([0, 0, -20])
frame_base();

// MAIN IMPELLER (center)
translate([0, 0, 0])
main_impeller_complete(explosion / 60);

// PERIPHERAL IMPELLERS (4x on arms)
for (i = [0:3]) {
    rotate([0, 0, i * 90])
    translate([0, 260, 10 + (exploded ? explosion/2 : 0)])
    peripheral_impeller(explosion / 60);
}

// GIMBAL SERVOS (3x around center)
translate([50, -50, -5 - (exploded ? explosion/3 : 0)])
rotate([0, 0, 45])
servo_sg90();

translate([-45, 45, -5 - (exploded ? explosion/3 : 0)])
rotate([0, 0, 135])
servo_sg90();

translate([45, 45, -5 - (exploded ? explosion/3 : 0)])
rotate([0, 0, 225])
servo_sg90();

// ARDUINO NANO HOUSING (center, below gimbal)
translate([0, 0, -15 - (exploded ? explosion/2 : 0)])
arduino_nano_housing();

// MPU6050 IMU (center, on top of Arduino)
translate([0, 0, -7 - (exploded ? explosion/2.2 : 0)])
mpu6050_imu();

// BATTERIES (4x in arms)
for (i = [0:3]) {
    rotate([0, 0, i * 90])
    translate([0, 170, -10 - (exploded ? explosion/4 : 0)])
    rotate([0, 0, 90])
    lipo_battery();
}

// VISUALIZATION HELPERS
// Reference axes
if (exploded) {
    // X-axis (red)
    color("Red", 0.3)
    translate([0, 0, -25])
    rotate([0, 90, 0])
    cylinder(h = 300, d = 2, center = true);
    
    // Y-axis (green)
    color("Green", 0.3)
    translate([0, 0, -25])
    rotate([90, 0, 0])
    cylinder(h = 300, d = 2, center = true);
    
    // Z-axis (blue)
    color("Blue", 0.3)
    cylinder(h = 150, d = 2, center = true);
}

// Component labels (for documentation)
module label(text_str, height = 3) {
    linear_extrude(height = 0.5)
    text(text_str, size = height, font = "Liberation Sans:style=Bold", halign = "center");
}

if (exploded) {
    translate([0, 0, 80])
    color("Black")
    label("EXPLODED VIEW", 6);
    
    translate([0, 300, 20])
    color("Black")
    label("Peripheral Impeller (4x)", 4);
    
    translate([0, -120, -20])
    color("Black")
    label("Arduino FC + IMU", 4);
    
    translate([0, 0, 90])
    color("Black")
    label("Main Impeller", 4);
    
    translate([80, -80, -10])
    color("Black")
    label("Gimbal Servos (3x)", 3);
} else {
    translate([0, 0, 100])
    color("Black")
    label("ASSEMBLED VIEW", 6);
}

// Technical info overlay
translate([-280, -280, -25])
color("Black")
linear_extrude(height = 0.5) {
    text("Gimbal Impeller Drone", size = 5, font = "Liberation Sans:style=Bold");
}

translate([-280, -290, -25])
color("Black")
linear_extrude(height = 0.5) {
    text("520mm wingspan | 450g weight | AI-optimized", size = 3);
}

translate([-280, -297, -25])
color("Black")
linear_extrude(height = 0.5) {
    text("Arduino Nano FC | 4x 50mm + 1x 90mm impellers", size = 3);
}
