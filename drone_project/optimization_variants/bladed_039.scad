/*
 * COMPLETE MOTOR + IMPELLER ASSEMBLY
 * For CFD fluid testing and visualization
 * 
 * This model includes:
 *   - Brushless motor (2204-2206 size)
 *   - Motor shaft (5mm)
 *   - Impeller hub
 *   - 3 impeller variants (bladeless, AI-blades, hybrid)
 *   - Mounting plate
 * 
 * Usage:
 *   - Render full assembly: F6
 *   - Export for CFD: Set EXPORT_MODE = "impeller_only"
 *   - Change design: Set IMPELLER_TYPE = "bladeless" | "bladed" | "hybrid"
 */

// ============================================================================
// CONFIGURATION PARAMETERS (AI-Optimizable)
// ============================================================================

// General Settings
$fn = 60;  // Resolution for CFD export (increase to 100 for final)

// Export Mode
EXPORT_MODE = "impeller_only";  // Options: "full_assembly", "impeller_only", "motor_only"

// Impeller Type
IMPELLER_TYPE = "bladed";  // Options: "bladeless", "bladed", "hybrid"

// Motor Specifications (2204-2206 brushless)
MOTOR_DIAMETER = 28;         // mm
MOTOR_HEIGHT = 25;           // mm
MOTOR_SHAFT_DIAMETER = 5;    // mm (standard)
MOTOR_SHAFT_LENGTH = 15;     // mm (extends above motor)
MOTOR_MOUNT_PATTERN = 16;    // mm (16x16 or 19x19 common)
MOTOR_SCREW_DIAMETER = 3;    // M3 screws

// Impeller Parameters - BLADELESS
BLADELESS_OUTER_DIAMETER = 90;    // mm
BLADELESS_AIR_GAP = 0.8;          // mm (optimize: 0.6-1.2)
BLADELESS_THROAT_RATIO = 0.72;    // (optimize: 0.65-0.80)
BLADELESS_EXPANSION_ANGLE = 18;   // degrees (optimize: 12-25)
BLADELESS_RING_THICKNESS = 3;     // mm (optimize: 2-4)
BLADELESS_HEIGHT = 24;            // mm

// Impeller Parameters - BLADED
BLADED_DIAMETER = 85;
BLADED_HUB_DIAMETER = 15;         // mm (optimize: 12-20)
BLADED_BLADE_COUNT = 3;
BLADED_ROOT_CHORD = 35;
BLADED_TIP_CHORD_RATIO = 0.7;    // (optimize: 0.6-0.8)
BLADED_BLADE_THICKNESS = 2;       // mm (optimize: 1.5-3)
BLADED_BLADE_TWIST = -25;
BLADED_ATTACK_ANGLE = -8;
BLADED_BLADE_HEIGHT = 12;         // mm (optimize: 10-15)

// Hub Parameters
HUB_DIAMETER = 15;
HUB_HEIGHT = 10;
HUB_SET_SCREW_DIAMETER = 3;  // M3 set screw

// Mounting Plate
PLATE_SIZE = 50;
PLATE_THICKNESS = 3;

// ============================================================================
// MOTOR MODEL
// ============================================================================

module brushless_motor_2204() {
    color("DarkSlateGray") {
        // Motor can (bell)
        difference() {
            cylinder(h=MOTOR_HEIGHT, d=MOTOR_DIAMETER);
            
            // Hollow inside (weight reduction visualization)
            translate([0, 0, -0.5])
                cylinder(h=MOTOR_HEIGHT - 5, d=MOTOR_DIAMETER - 4);
            
            // Mounting holes
            for(i = [0:3]) {
                rotate([0, 0, i * 90])
                    translate([MOTOR_MOUNT_PATTERN/2, 0, MOTOR_HEIGHT/2])
                        rotate([90, 0, 0])
                            cylinder(h=MOTOR_DIAMETER, d=MOTOR_SCREW_DIAMETER, center=true);
            }
        }
        
        // Motor base
        translate([0, 0, -3])
            cylinder(h=3, d=MOTOR_DIAMETER - 2);
    }
    
    // Motor shaft
    color("Silver")
        translate([0, 0, MOTOR_HEIGHT])
            cylinder(h=MOTOR_SHAFT_LENGTH, d=MOTOR_SHAFT_DIAMETER);
    
    // Shaft tip (for hub attachment)
    color("Silver")
        translate([0, 0, MOTOR_HEIGHT + MOTOR_SHAFT_LENGTH])
            cylinder(h=2, d=MOTOR_SHAFT_DIAMETER - 0.5);
}

// ============================================================================
// IMPELLER HUB
// ============================================================================

module impeller_hub() {
    color("Gray")
    difference() {
        // Hub body
        cylinder(h=HUB_HEIGHT, d=HUB_DIAMETER);
        
        // Shaft hole (5mm + 0.2mm clearance)
        translate([0, 0, -0.5])
            cylinder(h=HUB_HEIGHT + 1, d=MOTOR_SHAFT_DIAMETER + 0.2);
        
        // Set screw holes (2x for balance)
        for(i = [0:1]) {
            rotate([0, 0, i * 180])
                translate([HUB_DIAMETER/2 - 1, 0, HUB_HEIGHT/2])
                    rotate([0, 90, 0])
                        cylinder(h=5, d=HUB_SET_SCREW_DIAMETER);
        }
    }
}

// ============================================================================
// BLADELESS IMPELLER (Dyson-style)
// ============================================================================

module bladeless_impeller() {
    outer_r = BLADELESS_OUTER_DIAMETER / 2;
    throat_r = outer_r * BLADELESS_THROAT_RATIO;
    gap = BLADELESS_AIR_GAP;
    
    color("SkyBlue", 0.7)
    difference() {
        // Outer ring
        rotate_extrude()
            translate([outer_r - BLADELESS_RING_THICKNESS/2, BLADELESS_HEIGHT/2, 0])
                circle(d=BLADELESS_RING_THICKNESS + BLADELESS_HEIGHT);
        
        // Inner air gap (critical for Coanda effect)
        rotate_extrude()
            translate([outer_r - gap - BLADELESS_RING_THICKNESS/2, BLADELESS_HEIGHT/2, 0])
                circle(d=BLADELESS_RING_THICKNESS + BLADELESS_HEIGHT - 2*gap);
    }
    
    // Base plate (connects to hub)
    color("SkyBlue", 0.7)
    translate([0, 0, -2])
        difference() {
            cylinder(h=2, d=outer_r * 2);
            translate([0, 0, -0.5])
                cylinder(h=3, d=HUB_DIAMETER + 1);
        }
    
    // Air inlet (bell-shaped for smooth flow)
    color("SkyBlue", 0.7)
    translate([0, 0, -2]) {
        difference() {
            cylinder(h=15, d1=throat_r * 2, d2=outer_r * 1.8);
            translate([0, 0, -0.5])
                cylinder(h=16, d1=throat_r * 2 - 3, d2=outer_r * 1.8 - 3);
        }
    }
}

// ============================================================================
// AI-OPTIMIZED BLADED IMPELLER (NACA 2412 profile)
// ============================================================================

module naca_2412_blade(chord, height, twist_angle, attack_angle) {
    // Simplified NACA 2412 airfoil profile
    // Using parametric approximation for 3D printing
    
    color("LightSteelBlue", 0.8)
    linear_extrude(height=height, twist=twist_angle, scale=BLADED_TIP_CHORD_RATIO) {
        rotate([0, 0, attack_angle])
        polygon([
            // Upper surface (cambered)
            [0, 0],
            [chord * 0.05, chord * 0.03],
            [chord * 0.1, chord * 0.045],
            [chord * 0.2, chord * 0.055],
            [chord * 0.3, chord * 0.058],
            [chord * 0.4, chord * 0.056],
            [chord * 0.5, chord * 0.052],
            [chord * 0.6, chord * 0.046],
            [chord * 0.7, chord * 0.038],
            [chord * 0.8, chord * 0.028],
            [chord * 0.9, chord * 0.016],
            [chord * 1.0, chord * 0.002],
            // Lower surface (less cambered)
            [chord * 0.9, -chord * 0.010],
            [chord * 0.8, -chord * 0.016],
            [chord * 0.7, -chord * 0.020],
            [chord * 0.6, -chord * 0.022],
            [chord * 0.5, -chord * 0.023],
            [chord * 0.4, -chord * 0.022],
            [chord * 0.3, -chord * 0.020],
            [chord * 0.2, -chord * 0.016],
            [chord * 0.1, -chord * 0.010],
            [chord * 0.05, -chord * 0.005],
        ]);
    }
}

module bladed_impeller() {
    // Blades
    for(i = [0 : BLADED_BLADE_COUNT - 1]) {
        rotate([0, 0, i * (360 / BLADED_BLADE_COUNT)])
            translate([BLADED_HUB_DIAMETER/2, 0, 0])
                rotate([90, 0, 0])
                    naca_2412_blade(
                        BLADED_ROOT_CHORD, 
                        (BLADED_DIAMETER - BLADED_HUB_DIAMETER) / 2,
                        BLADED_BLADE_TWIST,
                        BLADED_ATTACK_ANGLE
                    );
    }
    
    // Hub disk (connects blades)
    color("LightSteelBlue", 0.8)
    cylinder(h=2, d=BLADED_HUB_DIAMETER + 4);
}

// ============================================================================
// HYBRID IMPELLER (Blades inside bladeless ring)
// ============================================================================

module hybrid_impeller() {
    // Outer bladeless ring
    bladeless_impeller();
    
    // Inner bladed impeller (scaled down to fit)
    scale([0.85, 0.85, 1])
        bladed_impeller();
}

// ============================================================================
// MOUNTING PLATE
// ============================================================================

module mounting_plate() {
    color("DimGray")
    difference() {
        // Base plate
        translate([-PLATE_SIZE/2, -PLATE_SIZE/2, 0])
            cube([PLATE_SIZE, PLATE_SIZE, PLATE_THICKNESS]);
        
        // Center hole for motor shaft
        translate([0, 0, -0.5])
            cylinder(h=PLATE_THICKNESS + 1, d=MOTOR_DIAMETER + 2);
        
        // Motor mounting holes
        for(i = [0:3]) {
            rotate([0, 0, i * 90])
                translate([MOTOR_MOUNT_PATTERN/2, 0, -0.5])
                    cylinder(h=PLATE_THICKNESS + 1, d=MOTOR_SCREW_DIAMETER);
        }
    }
}

// ============================================================================
// COMPLETE ASSEMBLY
// ============================================================================

module complete_assembly() {
    // Mounting plate (bottom)
    translate([0, 0, -PLATE_THICKNESS])
        mounting_plate();
    
    // Motor
    translate([0, 0, 0])
        brushless_motor_2204();
    
    // Hub (on shaft)
    translate([0, 0, MOTOR_HEIGHT + MOTOR_SHAFT_LENGTH - 2])
        impeller_hub();
    
    // Impeller (on hub)
    translate([0, 0, MOTOR_HEIGHT + MOTOR_SHAFT_LENGTH + HUB_HEIGHT]) {
        if (IMPELLER_TYPE == "bladeless") {
            bladeless_impeller();
        } else if (IMPELLER_TYPE == "bladed") {
            bladed_impeller();
        } else if (IMPELLER_TYPE == "hybrid") {
            hybrid_impeller();
        }
    }
}

// ============================================================================
// RENDER BASED ON EXPORT MODE
// ============================================================================

if (EXPORT_MODE == "full_assembly") {
    complete_assembly();
} 
else if (EXPORT_MODE == "impeller_only") {
    // For CFD testing - impeller + hub only
    impeller_hub();
    translate([0, 0, HUB_HEIGHT]) {
        if (IMPELLER_TYPE == "bladeless") {
            bladeless_impeller();
        } else if (IMPELLER_TYPE == "bladed") {
            bladed_impeller();
        } else if (IMPELLER_TYPE == "hybrid") {
            hybrid_impeller();
        }
    }
}
else if (EXPORT_MODE == "motor_only") {
    brushless_motor_2204();
}

// ============================================================================
// ANNOTATIONS FOR VISUALIZATION
// ============================================================================

// Uncomment to show dimensions
/*
color("Red", 0.3)
translate([BLADED_DIAMETER/2 + 10, 0, 20])
    text(str("Ø", BLADED_DIAMETER, "mm"), size=5, halign="left");

color("Green", 0.3)
translate([0, BLADED_DIAMETER/2 + 10, 20])
    text(str(BLADED_BLADE_COUNT, " blades"), size=5, halign="center");
*/

// ============================================================================
// EXPORT NOTES
// ============================================================================

/*
 * TO EXPORT FOR CFD TESTING:
 * 
 * 1. Set EXPORT_MODE = "impeller_only"
 * 2. Set IMPELLER_TYPE = "bladeless" (or "bladed" or "hybrid")
 * 3. Press F6 to render
 * 4. File → Export → Export as STL
 * 5. Use filename: impeller_bladeless_fn60.stl
 * 
 * FOR OPTIMIZATION:
 * - Modify parameters at top (marked with "optimize:")
 * - Re-render and export
 * - Upload to SimScale for CFD
 * - Compare results
 * 
 * RECOMMENDED CFD SETTINGS:
 * - Solver: k-omega SST
 * - RPM: 5000, 7000, 9000
 * - Mesh: 3-5M cells
 * - Boundary: Rotating zone on impeller
 */
