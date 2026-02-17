// Arduino Nano/Pro Mini Flight Controller Housing
// Budget-friendly alternative to F4/F7 FC
// Integrated MPU6050 IMU + ESC connections

$fn = 80;

// Arduino Nano dimensions
nano_length = 43.2;
nano_width = 18.0;
nano_height = 10; // With USB connector
nano_usb_width = 8;
nano_usb_height = 4;

// Housing parameters
wall_thickness = 2;
clearance = 1; // Air gap around board
mounting_hole_diameter = 2.5; // M2.5 standoffs
housing_base_height = 15;
housing_lid_height = 12;

// Arduino Nano housing - main compartment
module arduino_housing_base() {
    difference() {
        union() {
            // Main body
            cube([
                nano_length + 2*wall_thickness + 2*clearance,
                nano_width + 2*wall_thickness + 2*clearance,
                housing_base_height
            ]);
            
            // Side cable ports (reinforced)
            for (i = [0:1]) {
                translate([
                    i * (nano_length + 2*wall_thickness + 2*clearance),
                    (nano_width + 2*wall_thickness + 2*clearance)/2,
                    housing_base_height/2
                ])
                rotate([0, 90, 0])
                cylinder(h = 4, d = 15, center = true);
            }
            
            // Mounting tabs (4x corners for M3 to frame)
            for (x = [0, 1]) {
                for (y = [0, 1]) {
                    translate([
                        x * (nano_length + 2*wall_thickness + 2*clearance + 8) - 4,
                        y * (nano_width + 2*wall_thickness + 2*clearance + 8) - 4,
                        0
                    ])
                    cylinder(h = 3, d = 8);
                }
            }
        }
        
        // Inner cavity for Arduino
        translate([wall_thickness, wall_thickness, 2])
        cube([
            nano_length + 2*clearance,
            nano_width + 2*clearance,
            housing_base_height
        ]);
        
        // USB port cutout (front)
        translate([
            wall_thickness + clearance + (nano_length - nano_usb_width)/2,
            -1,
            housing_base_height - nano_usb_height - 2
        ])
        cube([nano_usb_width, wall_thickness + 2, nano_usb_height + 5]);
        
        // Pin header access holes (both sides)
        for (i = [0:1]) {
            translate([
                wall_thickness + clearance + 2.5,
                i * (nano_width + 2*clearance + wall_thickness - 2),
                2
            ])
            cube([nano_length - 5, 4, housing_base_height]);
        }
        
        // Cable routing holes (sides)
        for (i = [0:1]) {
            translate([
                i * (nano_length + 2*wall_thickness + 2*clearance),
                (nano_width + 2*wall_thickness + 2*clearance)/2,
                housing_base_height/2
            ])
            rotate([0, 90, 0])
            cylinder(h = 8, d = 10, center = true);
        }
        
        // Ventilation slots (bottom)
        for (i = [0:4]) {
            translate([
                wall_thickness + clearance + 5 + i * 8,
                (nano_width + 2*wall_thickness + 2*clearance)/2,
                -1
            ])
            cube([4, nano_width - 4, 3]);
        }
        
        // Frame mounting holes (4x corners)
        for (x = [0, 1]) {
            for (y = [0, 1]) {
                translate([
                    x * (nano_length + 2*wall_thickness + 2*clearance + 8) - 4,
                    y * (nano_width + 2*wall_thickness + 2*clearance + 8) - 4,
                    -1
                ])
                cylinder(h = 5, d = 3.2); // M3 clearance
            }
        }
        
        // Lid snap-fit slots (4x sides)
        for (i = [0:3]) {
            rotate([0, 0, i * 90])
            translate([
                (nano_length + 2*wall_thickness + 2*clearance)/2 - 8,
                (nano_width + 2*wall_thickness + 2*clearance)/2 + wall_thickness/2,
                housing_base_height - 4
            ])
            cube([16, wall_thickness + 1, 5]);
        }
    }
    
    // Internal standoffs for Arduino (4x mounting holes)
    standoff_positions = [
        [3, 2.5],
        [nano_length - 3, 2.5],
        [3, nano_width - 2.5],
        [nano_length - 3, nano_width - 2.5]
    ];
    
    for (pos = standoff_positions) {
        translate([
            wall_thickness + clearance + pos[0],
            wall_thickness + clearance + pos[1],
            2
        ])
        difference() {
            cylinder(h = 5, d = 5);
            translate([0, 0, 2])
            cylinder(h = 4, d = 2.2); // M2 screw hole
        }
    }
}

// Snap-fit lid
module arduino_housing_lid() {
    difference() {
        union() {
            // Main lid plate
            cube([
                nano_length + 2*wall_thickness + 2*clearance,
                nano_width + 2*wall_thickness + 2*clearance,
                wall_thickness
            ]);
            
            // Snap-fit tabs (4x sides)
            for (i = [0:3]) {
                rotate([0, 0, i * 90])
                translate([
                    (nano_length + 2*wall_thickness + 2*clearance)/2 - 8,
                    (nano_width + 2*wall_thickness + 2*clearance)/2 + wall_thickness - 0.5,
                    -3
                ])
                cube([16, 1.5, 3]);
            }
            
            // Internal rim (sits inside housing)
            translate([wall_thickness - 0.5, wall_thickness - 0.5, -housing_lid_height])
            difference() {
                cube([
                    nano_length + 2*clearance + 1,
                    nano_width + 2*clearance + 1,
                    housing_lid_height
                ]);
                translate([wall_thickness, wall_thickness, -1])
                cube([
                    nano_length + 2*clearance - 2*wall_thickness + 1,
                    nano_width + 2*clearance - 2*wall_thickness + 1,
                    housing_lid_height + 2
                ]);
            }
        }
        
        // Status LED window
        translate([
            (nano_length + 2*wall_thickness + 2*clearance)/2,
            (nano_width + 2*wall_thickness + 2*clearance)/2,
            -1
        ])
        cylinder(h = wall_thickness + 2, d = 8);
        
        // Ventilation slots (top)
        for (i = [0:3]) {
            translate([
                wall_thickness + clearance + 8 + i * 8,
                wall_thickness + clearance + 2,
                -1
            ])
            cube([4, nano_width - 4, wall_thickness + 2]);
        }
    }
}

// MPU6050 IMU sensor mount (separate module)
module mpu6050_mount() {
    mpu_length = 21;
    mpu_width = 16;
    mpu_height = 3;
    
    difference() {
        union() {
            // Base plate
            cube([mpu_length + 8, mpu_width + 8, 3]);
            
            // Standoffs (4x)
            for (x = [0, 1]) {
                for (y = [0, 1]) {
                    translate([
                        4 + x * mpu_length,
                        4 + y * mpu_width,
                        3
                    ])
                    cylinder(h = 5, d = 5);
                }
            }
            
            // Vibration dampening posts (TPU insert)
            for (x = [0, 1]) {
                for (y = [0, 1]) {
                    translate([
                        (x * (mpu_length + 8)) + (x == 0 ? 2 : -2),
                        (y * (mpu_width + 8)) + (y == 0 ? 2 : -2),
                        -8
                    ])
                    cylinder(h = 8, d = 6);
                }
            }
        }
        
        // MPU6050 mounting holes (4x M2)
        for (x = [0, 1]) {
            for (y = [0, 1]) {
                translate([
                    4 + x * mpu_length,
                    4 + y * mpu_width,
                    2
                ])
                cylinder(h = 8, d = 2.2);
            }
        }
        
        // Frame mounting holes (through posts)
        for (x = [0, 1]) {
            for (y = [0, 1]) {
                translate([
                    (x * (mpu_length + 8)) + (x == 0 ? 2 : -2),
                    (y * (mpu_width + 8)) + (y == 0 ? 2 : -2),
                    -9
                ])
                cylinder(h = 15, d = 3.2); // M3 clearance
            }
        }
    }
}

// ESC holder/organizer
module esc_holder() {
    esc_width = 25;
    esc_length = 30;
    
    difference() {
        union() {
            // Base plate
            cube([esc_length + 8, esc_width + 6, 2]);
            
            // Side clips (flexible)
            for (i = [0:1]) {
                translate([
                    4 + i * esc_length,
                    3,
                    2
                ])
                cube([2, esc_width, 8]);
            }
            
            // Wire routing channels
            translate([0, (esc_width + 6)/2, 0])
            cube([esc_length + 8, 3, 6]);
        }
        
        // Zip tie slots
        for (i = [0:2]) {
            translate([
                6 + i * 10,
                -1,
                4
            ])
            cube([3, esc_width + 8, 3]);
        }
        
        // Mounting holes (M3)
        for (i = [0:1]) {
            translate([
                4 + i * esc_length,
                (esc_width + 6)/2,
                -1
            ])
            cylinder(h = 5, d = 3.2);
        }
    }
}

// Power distribution board (simple)
module power_distribution() {
    pcb_size = 40;
    
    difference() {
        union() {
            // Main board
            cube([pcb_size, pcb_size, 1.6]);
            
            // XT30/XT60 connector mount
            translate([pcb_size/2 - 8, -5, 0])
            cube([16, 5, 8]);
            
            // Solder pad towers (6x outputs: 5 motors + 1 servo)
            for (i = [0:5]) {
                angle = i * 60;
                translate([
                    pcb_size/2 + cos(angle) * 12,
                    pcb_size/2 + sin(angle) * 12,
                    1.6
                ])
                cylinder(h = 6, d = 6);
            }
        }
        
        // Battery connector hole
        translate([pcb_size/2 - 6, -6, 2])
        cube([12, 8, 6]);
        
        // Wire routing holes in pads
        for (i = [0:5]) {
            angle = i * 60;
            translate([
                pcb_size/2 + cos(angle) * 12,
                pcb_size/2 + sin(angle) * 12,
                0
            ])
            cylinder(h = 10, d = 2.5);
        }
        
        // Center mounting hole
        translate([pcb_size/2, pcb_size/2, -1])
        cylinder(h = 5, d = 4);
        
        // Corner mounting holes (4x M3)
        for (x = [0, 1]) {
            for (y = [0, 1]) {
                translate([
                    5 + x * (pcb_size - 10),
                    5 + y * (pcb_size - 10),
                    -1
                ])
                cylinder(h = 5, d = 3.2);
            }
        }
    }
}

// Generate all parts
translate([0, 0, 0]) arduino_housing_base();
translate([70, 0, housing_lid_height]) rotate([180, 0, 0]) arduino_housing_lid();
translate([0, 40, 0]) mpu6050_mount();
translate([40, 40, 0]) esc_holder();
translate([80, 40, 0]) power_distribution();

// Assembly notes
translate([0, -10, 0])
linear_extrude(height = 0.5)
text("Arduino FC Housing", size = 4, font = "Liberation Sans:style=Bold");
