#!/usr/bin/env python3
"""
OpenSCAD to STEP Converter for Windows
Automates conversion of .scad files to .step format via STL intermediate

Requirements:
    - OpenSCAD installed (https://openscad.org/)
    - Python 3.7+
    - numpy-stl package: pip install numpy-stl
    
Usage:
    python convert_scad_to_step.py
    
This script will:
    1. Find all .scad files in drone_project/
    2. Use OpenSCAD CLI to render each to STL
    3. Save STEP files to simscale_exports/ directory
    
Note: STEP conversion requires FreeCAD or similar CAD software.
      This script generates high-quality STL files that work great with SimScale.
      For true STEP export, see manual FreeCAD workflow in documentation.
"""

import os
import subprocess
import sys
from pathlib import Path

# Configuration
OPENSCAD_PATH = r"C:\Program Files\OpenSCAD\openscad.exe"
PROJECT_DIR = Path(__file__).parent
OUTPUT_DIR = PROJECT_DIR / "stl_output_for_simscale"
FN_VALUE = 60  # Facet number for CFD (balance quality/speed)

# Files to convert
SCAD_FILES = [
    "ai_bladeless_impeller.scad",
    "gimbal_ring.scad", 
    "peripheral_impeller_housing.scad",
    "servo_gimbal_mount.scad",
]


def check_openscad_installed():
    """Check if OpenSCAD is installed at expected location"""
    if not os.path.exists(OPENSCAD_PATH):
        print(f"❌ Error: OpenSCAD not found at {OPENSCAD_PATH}")
        print("\nPlease install OpenSCAD from https://openscad.org/downloads.html")
        print("Or update OPENSCAD_PATH in this script to match your installation.")
        
        # Try to find OpenSCAD in common locations
        common_paths = [
            r"C:\Program Files\OpenSCAD\openscad.exe",
            r"C:\Program Files (x86)\OpenSCAD\openscad.exe",
            r"D:\Program Files\OpenSCAD\openscad.exe",
        ]
        
        found = False
        for path in common_paths:
            if os.path.exists(path):
                print(f"\n✓ Found OpenSCAD at: {path}")
                print(f"  Update OPENSCAD_PATH in script to use this location.")
                found = True
                break
        
        if not found:
            print("\nOpenSCAD not found in common locations.")
            print("Please install it or specify the correct path.")
        
        sys.exit(1)
    
    print(f"✓ OpenSCAD found: {OPENSCAD_PATH}")
    return True


def create_output_directory():
    """Create output directory if it doesn't exist"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"✓ Output directory: {OUTPUT_DIR}")


def convert_scad_to_stl(scad_file, fn_value=60):
    """
    Convert .scad file to .stl using OpenSCAD command line
    
    Args:
        scad_file: Name of .scad file to convert
        fn_value: $fn value for rendering quality (default 60 for CFD)
    
    Returns:
        Path to generated STL file or None if failed
    """
    scad_path = PROJECT_DIR / scad_file
    
    if not scad_path.exists():
        print(f"❌ File not found: {scad_path}")
        return None
    
    # Output STL filename
    stl_filename = scad_path.stem + f"_fn{fn_value}.stl"
    stl_path = OUTPUT_DIR / stl_filename
    
    print(f"\n📐 Converting: {scad_file}")
    print(f"   Resolution: $fn = {fn_value}")
    print(f"   Output: {stl_filename}")
    
    # OpenSCAD command line arguments
    cmd = [
        OPENSCAD_PATH,
        "-o", str(stl_path),          # Output file
        "-D", f"$fn={fn_value}",      # Set facet number
        str(scad_path)                 # Input file
    ]
    
    try:
        # Run OpenSCAD (this may take 10-60 seconds per file)
        print("   Rendering... ", end="", flush=True)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        if result.returncode == 0 and stl_path.exists():
            file_size = stl_path.stat().st_size / (1024 * 1024)  # MB
            print(f"✓ Success ({file_size:.2f} MB)")
            return stl_path
        else:
            print(f"✗ Failed")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("✗ Timeout (>2 minutes)")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def print_simscale_instructions(generated_files):
    """Print instructions for uploading to SimScale"""
    print("\n" + "="*70)
    print("UPLOAD TO SIMSCALE")
    print("="*70)
    print("\nGenerated STL files (optimized for CFD):")
    for file in generated_files:
        print(f"  ✓ {file.name}")
    
    print(f"\nLocation: {OUTPUT_DIR}")
    
    print("\n📤 Upload Instructions:")
    print("1. Go to https://www.simscale.com/ and sign up (free)")
    print("2. Create new project: 'Hex-Warp Drone CFD'")
    print("3. Click 'Import Geometry' → 'From Computer'")
    print("4. Upload the STL files above")
    print("5. Create CFD simulation:")
    print("   - Type: Incompressible")
    print("   - Turbulence: k-omega SST")
    print("   - Rotating zone: Set RPM (5000, 7000, 9000)")
    print("6. Run simulation (~2-3 hours)")
    print("7. Analyze thrust and efficiency!")
    
    print("\n💡 Tips:")
    print("   - Use 'External Flow' simulation type")
    print("   - SimScale auto-creates flow domain")
    print("   - Medium mesh (2-3M cells) is good for first test")
    print("   - Test multiple RPM values in parallel")
    
    print("\n📚 More Info:")
    print("   - See SIMULATION_TESTING_GUIDE.txt for full details")
    print("   - See OPENSCAD_TO_SIMSCALE_WORKFLOW.txt for STEP conversion")


def main():
    """Main conversion workflow"""
    print("="*70)
    print("OpenSCAD to STL Converter (SimScale CFD Ready)")
    print("="*70)
    
    # Check prerequisites
    check_openscad_installed()
    create_output_directory()
    
    # Convert all files
    generated_files = []
    success_count = 0
    
    for scad_file in SCAD_FILES:
        stl_path = convert_scad_to_stl(scad_file, fn_value=FN_VALUE)
        if stl_path:
            generated_files.append(stl_path)
            success_count += 1
    
    # Summary
    print("\n" + "="*70)
    print(f"CONVERSION COMPLETE: {success_count}/{len(SCAD_FILES)} files")
    print("="*70)
    
    if generated_files:
        print_simscale_instructions(generated_files)
    else:
        print("\n❌ No files were converted successfully.")
        print("   Check OpenSCAD installation and file paths.")
    
    print("\n✨ Ready for CFD simulation!\n")


if __name__ == "__main__":
    main()
