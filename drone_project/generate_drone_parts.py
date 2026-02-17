#!/usr/bin/env python3
"""
Drone Part Generator - Parametric CAD to STL Conversion
Generates STL files from OpenSCAD designs with custom parameters
"""

import subprocess
import os
from pathlib import Path

# Parameters for customization
PARAMS = {
    'main_impeller_diameter': 90,      # Main impeller size (mm)
    'peripheral_diameter': 50,          # Peripheral impeller size (mm)
    'arm_length': 200,                  # Center to motor distance (mm)
    'gimbal_tilt_range': 30,            # Max tilt angle (degrees)
    'ring_outer_diameter': 110,         # Gimbal ring outer (mm)
    'gear_tooth_count': 60,             # Number of gear teeth
    'servo_model': 'MG90S',             # Servo type
    'frame_thickness': 3,               # Base plate thickness (mm)
    'duct_height': 35,                  # Peripheral impeller duct height (mm)
}

# File paths
BASE_DIR = Path(__file__).parent
SCAD_FILES = {
    'gimbal_ring': BASE_DIR / 'gimbal_ring.scad',
    'peripheral_housing': BASE_DIR / 'peripheral_impeller_housing.scad',
    'servo_mount': BASE_DIR / 'servo_gimbal_mount.scad',
}

OUTPUT_DIR = BASE_DIR / 'stl_output'
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_stl(scad_file: Path, output_file: Path, params: dict = None):
    """
    Generate STL from OpenSCAD file using openscad command line
    
    Args:
        scad_file: Path to .scad source file
        output_file: Path for output .stl file
        params: Optional parameter overrides
    """
    if not scad_file.exists():
        print(f"Error: {scad_file} not found")
        return False
    
    # Check if OpenSCAD is installed
    try:
        subprocess.run(['openscad', '--version'], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: OpenSCAD not found. Install from https://openscad.org/")
        print(f"You can manually open {scad_file} in OpenSCAD and export STL")
        return False
    
    # Build command
    cmd = ['openscad', '-o', str(output_file)]
    
    # Add parameter overrides
    if params:
        for key, value in params.items():
            cmd.extend(['-D', f'{key}={value}'])
    
    cmd.append(str(scad_file))
    
    print(f"Generating {output_file.name}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"  ✓ Success: {output_file}")
            return True
        else:
            print(f"  ✗ Failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  ✗ Timeout generating {output_file}")
        return False


def generate_all_parts():
    """Generate all drone parts with current parameters"""
    print("="*70)
    print("DRONE PART GENERATOR")
    print("="*70)
    print("\nCurrent Parameters:")
    for key, value in PARAMS.items():
        print(f"  {key:25} = {value}")
    print()
    
    success_count = 0
    total_count = 0
    
    # Generate gimbal ring
    total_count += 1
    if generate_stl(
        SCAD_FILES['gimbal_ring'],
        OUTPUT_DIR / 'gimbal_ring.stl',
        {
            'main_impeller_diameter': PARAMS['main_impeller_diameter'],
            'ring_outer_diameter': PARAMS['ring_outer_diameter'],
            'gear_tooth_count': PARAMS['gear_tooth_count'],
        }
    ):
        success_count += 1
    
    # Generate peripheral impeller housings (need 4x)
    total_count += 1
    if generate_stl(
        SCAD_FILES['peripheral_housing'],
        OUTPUT_DIR / 'peripheral_impeller_housing.stl',
        {
            'impeller_diameter': PARAMS['peripheral_diameter'],
            'duct_height': PARAMS['duct_height'],
        }
    ):
        success_count += 1
        print("  Note: Print 4x of this part")
    
    # Generate servo mounts (need 3x for gimbal control)
    total_count += 1
    if generate_stl(
        SCAD_FILES['servo_mount'],
        OUTPUT_DIR / 'servo_gimbal_mount.stl',
        {
            'gear_engagement_radius': PARAMS['ring_outer_diameter'] / 2,
        }
    ):
        success_count += 1
        print("  Note: Print 3x of this part for gimbal control")
    
    print()
    print("="*70)
    print(f"Generation complete: {success_count}/{total_count} parts successful")
    print(f"Output directory: {OUTPUT_DIR}")
    print("="*70)
    
    if success_count < total_count:
        print("\nIf OpenSCAD is not installed, you can:")
        print("1. Install OpenSCAD from https://openscad.org/downloads.html")
        print("2. Manually open .scad files and export to STL")
        print("3. Use online OpenSCAD viewers (e.g., OpenJSCAD)")


def print_instructions():
    """Print 3D printing instructions"""
    print("\n" + "="*70)
    print("3D PRINTING INSTRUCTIONS")
    print("="*70)
    print("""
PART: Gimbal Ring (gimbal_ring.stl)
  Material: PETG or PLA
  Layer Height: 0.2mm
  Infill: 30-40%
  Supports: No
  Quantity: 1x
  Print Time: ~2-3 hours
  Notes: Print with brim for bed adhesion. Critical dimensional accuracy.

PART: Peripheral Impeller Housing (peripheral_impeller_housing.stl)
  Material: PETG preferred (heat resistance)
  Layer Height: 0.15-0.2mm
  Infill: 25-30%
  Supports: Yes (for inlet bell)
  Quantity: 4x
  Print Time: ~1.5 hours each
  Notes: Ensure smooth inner duct surface for airflow efficiency.

PART: Servo Gimbal Mount (servo_gimbal_mount.stl)
  Material: PETG or PLA+
  Layer Height: 0.2mm
  Infill: 40-50% (structural component)
  Supports: Yes (for servo cavity)
  Quantity: 3x
  Print Time: ~1 hour each
  Notes: Strong layer adhesion critical. Print with reinforcement.

GENERAL SETTINGS:
  - Nozzle: 0.4mm
  - Temperature: PLA 200-210°C, PETG 230-240°C
  - Bed: PLA 60°C, PETG 70-80°C
  - Print Speed: 40-60mm/s for structural parts
  - Wall Lines: 3-4 for strength
  - Top/Bottom Layers: 4-5

POST-PROCESSING:
  - Remove any support material carefully
  - Test fit all parts before assembly
  - Ream out bearing holes if too tight (use drill bits)
  - Light sanding on mating surfaces for smooth operation
  - Apply thread locker to all metal fasteners during assembly
    """)


def estimate_material_usage():
    """Estimate filament usage for complete build"""
    parts = {
        'Gimbal ring': (35, 1),              # grams, quantity
        'Peripheral housings': (25, 4),
        'Servo mounts': (18, 3),
        'Motor mounts': (15, 5),
        'Brackets & misc': (40, 1),
    }
    
    total_weight = sum(weight * qty for weight, qty in parts.values())
    
    print("\n" + "="*70)
    print("MATERIAL USAGE ESTIMATE")
    print("="*70)
    for part, (weight, qty) in parts.items():
        print(f"{part:30} {weight}g x {qty} = {weight*qty}g")
    print("-"*70)
    print(f"{'TOTAL FILAMENT NEEDED':30} {total_weight}g")
    print(f"{'With 20% safety margin':30} {int(total_weight * 1.2)}g")
    print(f"{'Approximate cost (at $20/kg)':30} ${total_weight * 0.024:.2f}")
    print("="*70)


if __name__ == '__main__':
    generate_all_parts()
    print_instructions()
    estimate_material_usage()
    
    print("\nNext steps:")
    print("1. Review generated STL files in slicer software")
    print("2. Slice with recommended settings above")
    print("3. Print parts in recommended order: servo mounts → housings → gimbal ring")
    print("4. Refer to DRONE_BOM.txt for complete parts list")
    print("5. Test fit all components before final assembly")
