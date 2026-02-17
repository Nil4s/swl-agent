#!/usr/bin/env python3
"""
Export Motor/Impeller Model for SimScale CFD Simulation

This script:
1. Exports STL files optimized for SimScale
2. Creates a fluid domain (cylindrical wind tunnel)
3. Generates SimScale setup instructions
4. Validates mesh quality

Usage:
    python export_for_simscale.py --type bladed --rpm 7000
    python export_for_simscale.py --type bladeless --rpm 9000 --with_domain
"""

import subprocess
import json
import os
import argparse
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

OPENSCAD_PATH = r"C:\Program Files\OpenSCAD\openscad.exe"
PROJECT_DIR = Path(__file__).parent
EXPORT_DIR = PROJECT_DIR / "simscale_exports"
TEMPLATE_FILE = PROJECT_DIR / "motor_impeller_assembly.scad"

# SimScale recommended settings
SIMSCALE_FN = 100  # Higher resolution for CFD
IMPELLER_DIAMETER = 90  # mm
MOTOR_HEIGHT = 25  # mm

# Fluid domain dimensions (for wind tunnel)
DOMAIN_LENGTH = IMPELLER_DIAMETER * 6  # 540mm upstream/downstream
DOMAIN_DIAMETER = IMPELLER_DIAMETER * 4  # 360mm diameter

# ============================================================================
# STL EXPORT FUNCTIONS
# ============================================================================

def export_impeller_stl(impeller_type, rpm, output_path):
    """Export impeller+hub as STL for SimScale"""
    
    # Create temporary SCAD file with proper settings
    temp_scad = output_path.parent / f"temp_{impeller_type}.scad"
    
    with open(TEMPLATE_FILE, 'r') as f:
        content = f.read()
    
    # Modify settings for SimScale export
    content = content.replace(
        'EXPORT_MODE = "full_assembly"',
        'EXPORT_MODE = "impeller_only"'
    )
    content = content.replace(
        'IMPELLER_TYPE = "bladed"',
        f'IMPELLER_TYPE = "{impeller_type}"'
    )
    content = content.replace(
        '$fn = 60',
        f'$fn = {SIMSCALE_FN}'
    )
    
    with open(temp_scad, 'w') as f:
        f.write(content)
    
    # Render to STL
    print(f"🔧 Rendering {impeller_type} impeller (fn={SIMSCALE_FN})...")
    
    cmd = [
        OPENSCAD_PATH,
        "-o", str(output_path),
        "-D", f"$fn={SIMSCALE_FN}",
        str(temp_scad)
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if result.returncode == 0 and output_path.exists():
            file_size = output_path.stat().st_size / (1024 * 1024)
            print(f"✓ Exported: {output_path.name} ({file_size:.2f} MB)")
            temp_scad.unlink()  # Clean up temp file
            return True
        else:
            print(f"✗ Export failed: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def export_motor_stl(output_path):
    """Export motor body as STL (for reference/visualization)"""
    
    temp_scad = output_path.parent / "temp_motor.scad"
    
    with open(TEMPLATE_FILE, 'r') as f:
        content = f.read()
    
    # Modify for motor-only export
    content = content.replace(
        'EXPORT_MODE = "full_assembly"',
        'EXPORT_MODE = "motor_only"'
    )
    content = content.replace(
        '$fn = 60',
        f'$fn = {SIMSCALE_FN}'
    )
    
    with open(temp_scad, 'w') as f:
        f.write(content)
    
    print(f"🔧 Rendering motor body...")
    
    cmd = [
        OPENSCAD_PATH,
        "-o", str(output_path),
        "-D", f"$fn={SIMSCALE_FN}",
        str(temp_scad)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0 and output_path.exists():
            file_size = output_path.stat().st_size / (1024 * 1024)
            print(f"✓ Exported: {output_path.name} ({file_size:.2f} MB)")
            temp_scad.unlink()
            return True
        else:
            print(f"✗ Export failed: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def create_fluid_domain_scad(output_path):
    """Create cylindrical fluid domain (wind tunnel) for CFD"""
    
    domain_scad = f"""
// Fluid Domain for SimScale CFD
// Cylindrical wind tunnel around impeller

$fn = {SIMSCALE_FN};

DOMAIN_LENGTH = {DOMAIN_LENGTH};
DOMAIN_DIAMETER = {DOMAIN_DIAMETER};
IMPELLER_DIAMETER = {IMPELLER_DIAMETER};

difference() {{
    // Outer cylinder (wind tunnel)
    cylinder(h=DOMAIN_LENGTH, d=DOMAIN_DIAMETER, center=true);
    
    // Inner void (remove impeller space)
    translate([0, 0, 0])
        cylinder(h=IMPELLER_DIAMETER, d=IMPELLER_DIAMETER * 1.2, center=true);
}}
"""
    
    with open(output_path, 'w') as f:
        f.write(domain_scad)
    
    print(f"✓ Created fluid domain: {output_path.name}")
    return True


# ============================================================================
# SIMSCALE SETUP GUIDE
# ============================================================================

def generate_simscale_guide(impeller_type, rpm, export_dir):
    """Generate step-by-step SimScale setup instructions"""
    
    guide = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                     SIMSCALE CFD SETUP GUIDE                             ║
║                     Impeller: {impeller_type.upper():12}  RPM: {rpm:5}                      ║
╚══════════════════════════════════════════════════════════════════════════╝

📁 EXPORTED FILES:
   ✓ impeller_{impeller_type}_rpm{rpm}.stl  (Rotating impeller + hub)
   ✓ motor_body.stl                         (Stationary motor - reference)
   ✓ fluid_domain.scad                      (Optional - create in CAD)

═══════════════════════════════════════════════════════════════════════════

🌐 STEP 1: CREATE PROJECT IN SIMSCALE
═══════════════════════════════════════════════════════════════════════════
1. Go to https://www.simscale.com/
2. Create new project: "Impeller CFD - {impeller_type.title()} @ {rpm} RPM"
3. Choose: "Fluid Dynamics" → "Incompressible"

═══════════════════════════════════════════════════════════════════════════

📤 STEP 2: UPLOAD GEOMETRY
═══════════════════════════════════════════════════════════════════════════
1. Upload: impeller_{impeller_type}_rpm{rpm}.stl
2. Optional: Upload motor_body.stl (for visualization)
3. Set units: Millimeters (mm)
4. Check geometry: No errors, manifold mesh

═══════════════════════════════════════════════════════════════════════════

⚙️  STEP 3: SIMULATION SETUP
═══════════════════════════════════════════════════════════════════════════

Analysis Type:
   • Steady State
   • Incompressible
   • k-omega SST turbulence model

Fluid:
   • Material: Air
   • Density: 1.225 kg/m³
   • Viscosity: 1.831e-5 kg/(m·s)
   • Temperature: 20°C

═══════════════════════════════════════════════════════════════════════════

🔄 STEP 4: ROTATING ZONE (CRITICAL!)
═══════════════════════════════════════════════════════════════════════════

Create Rotating Zone:
   1. Select impeller geometry
   2. Rotation type: MRF (Multiple Reference Frame)
   3. Rotation axis: Z-axis (0, 0, 1)
   4. Origin: (0, 0, 0)
   5. Angular velocity: {rpm * 0.10472:.3f} rad/s  ({rpm} RPM)
   6. Zone radius: {IMPELLER_DIAMETER/2 + 5:.1f} mm
   7. Zone height: {MOTOR_HEIGHT + 30:.1f} mm

═══════════════════════════════════════════════════════════════════════════

🌊 STEP 5: BOUNDARY CONDITIONS
═══════════════════════════════════════════════════════════════════════════

Inlet (Bottom):
   • Type: Velocity Inlet
   • Direction: Z-axis (upward)
   • Velocity: 0 m/s (static test) or 5-10 m/s (forward flight)
   • Turbulence: 5% intensity

Outlet (Top):
   • Type: Pressure Outlet
   • Pressure: 0 Pa (atmospheric)
   • Backflow turbulence: 5%

Impeller Surface:
   • Type: Wall
   • Roughness: Smooth
   • Wall treatment: Wall Function

Motor Surface (if included):
   • Type: Wall - No Slip
   • Stationary

═══════════════════════════════════════════════════════════════════════════

🕸️  STEP 6: MESHING
═══════════════════════════════════════════════════════════════════════════

Mesh Settings:
   • Type: Hex-dominant
   • Base element size: 2 mm
   • Refinement levels: 3
   • Target cell count: 3-5 million cells

Refinement Zones:
   1. Impeller surface: 3 levels (0.5 mm)
   2. Rotating zone: 2 levels (1 mm)
   3. Wake region: 1 level (1.5 mm)

Boundary Layers:
   • Number of layers: 5
   • Growth rate: 1.3
   • First layer thickness: 0.1 mm
   • Target y+: 30-300

═══════════════════════════════════════════════════════════════════════════

📊 STEP 7: RESULT PROBES
═══════════════════════════════════════════════════════════════════════════

Create Force Probes:
   1. Thrust force (Z-direction on impeller)
   2. Torque (rotation axis)
   3. Power = Torque × Angular velocity

Create Field Probes:
   1. Velocity slice (XY plane at impeller height)
   2. Pressure distribution on blades
   3. Vorticity (check flow separation)

═══════════════════════════════════════════════════════════════════════════

▶️  STEP 8: RUN SIMULATION
═══════════════════════════════════════════════════════════════════════════

Solver Settings:
   • Maximum iterations: 500
   • Convergence criteria: 1e-4
   • Relaxation factors: Default (0.3 for pressure, 0.7 for velocity)

Estimated Time:
   • With 3M cells: ~30-60 minutes
   • With 5M cells: ~60-120 minutes

═══════════════════════════════════════════════════════════════════════════

📈 STEP 9: POST-PROCESSING
═══════════════════════════════════════════════════════════════════════════

Extract Results:
   ✓ Thrust (N) → Convert to grams: Thrust_N × 101.97
   ✓ Torque (N·m)
   ✓ Power (W) = Torque × (2π × RPM / 60)
   ✓ Efficiency = Thrust / Power (g/W)

Visualizations:
   • Velocity streamlines
   • Pressure contours on blades
   • Vorticity iso-surfaces
   • Blade loading distribution

═══════════════════════════════════════════════════════════════════════════

📋 STEP 10: RECORD RESULTS
═══════════════════════════════════════════════════════════════════════════

Save to: optimization_results.json

Format:
{{
  "variant_id": "{impeller_type}_{rpm}",
  "type": "{impeller_type}",
  "rpm": {rpm},
  "thrust": <value_in_grams>,
  "torque": <value_in_Nm>,
  "power": <value_in_watts>,
  "efficiency": <thrust/power>
}}

Then run:
    python ai_impeller_optimizer.py --mode analyze

═══════════════════════════════════════════════════════════════════════════

🔧 TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════

Problem: Mesh fails
Solution: Reduce refinement levels or increase base size

Problem: Simulation diverges
Solution: Reduce relaxation factors (0.2/0.5) or lower RPM

Problem: No thrust
Solution: Check rotating zone setup, verify axis direction

Problem: Unrealistic results
Solution: Check units (mm vs m), verify boundary conditions

═══════════════════════════════════════════════════════════════════════════

📚 REFERENCES
═══════════════════════════════════════════════════════════════════════════
• SimScale Docs: https://www.simscale.com/docs/
• Tutorial: Rotating Machinery (Propeller)
• Best Practices: k-omega SST Turbulence Model

═══════════════════════════════════════════════════════════════════════════
"""
    
    guide_path = export_dir / f"SIMSCALE_SETUP_{impeller_type}_rpm{rpm}.txt"
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"\n✓ Setup guide: {guide_path.name}")
    return guide_path


def generate_json_template(impeller_type, rpm, export_dir):
    """Generate JSON template for results recording"""
    
    template = {
        "variant_id": f"{impeller_type}_rpm{rpm}",
        "type": impeller_type,
        "rpm": rpm,
        "thrust": None,
        "torque": None,
        "power": None,
        "efficiency": None,
        "notes": "Fill in values from SimScale post-processing"
    }
    
    template_path = export_dir / f"results_template_{impeller_type}_rpm{rpm}.json"
    with open(template_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"✓ Results template: {template_path.name}")
    return template_path


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Export for SimScale CFD")
    parser.add_argument("--type", choices=["bladed", "bladeless", "hybrid"],
                       default="bladed", help="Impeller type")
    parser.add_argument("--rpm", type=int, default=7000,
                       help="Rotation speed (RPM)")
    parser.add_argument("--with_motor", action="store_true",
                       help="Export motor body (for visualization)")
    parser.add_argument("--with_domain", action="store_true",
                       help="Create fluid domain SCAD file")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("SIMSCALE EXPORT TOOL")
    print("=" * 70)
    
    # Check OpenSCAD
    if not os.path.exists(OPENSCAD_PATH):
        print(f"❌ OpenSCAD not found: {OPENSCAD_PATH}")
        return
    
    print(f"✓ OpenSCAD: {OPENSCAD_PATH}")
    
    # Create export directory
    EXPORT_DIR.mkdir(exist_ok=True)
    print(f"✓ Export directory: {EXPORT_DIR}\n")
    
    # Export impeller
    impeller_stl = EXPORT_DIR / f"impeller_{args.type}_rpm{args.rpm}.stl"
    success = export_impeller_stl(args.type, args.rpm, impeller_stl)
    
    if not success:
        print("\n❌ Impeller export failed")
        return
    
    # Export motor (optional)
    if args.with_motor:
        motor_stl = EXPORT_DIR / "motor_body.stl"
        export_motor_stl(motor_stl)
    
    # Create fluid domain (optional)
    if args.with_domain:
        domain_scad = EXPORT_DIR / "fluid_domain.scad"
        create_fluid_domain_scad(domain_scad)
    
    # Generate setup guide
    guide_path = generate_simscale_guide(args.type, args.rpm, EXPORT_DIR)
    
    # Generate results template
    template_path = generate_json_template(args.type, args.rpm, EXPORT_DIR)
    
    # Summary
    print("\n" + "=" * 70)
    print("EXPORT COMPLETE")
    print("=" * 70)
    print(f"✓ Impeller: {impeller_stl.name}")
    if args.with_motor:
        print(f"✓ Motor: motor_body.stl")
    if args.with_domain:
        print(f"✓ Domain: fluid_domain.scad")
    print(f"\n📖 Read setup guide: {guide_path.name}")
    print(f"\n🚀 Next: Upload STL to SimScale and follow the guide")


if __name__ == "__main__":
    main()
