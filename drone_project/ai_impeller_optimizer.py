#!/usr/bin/env python3
"""
AI-Driven Impeller Optimization Script
Generates parametric design variants for CFD testing

This script:
1. Generates design variants by modifying OpenSCAD parameters
2. Exports STL files for each variant
3. Creates a test matrix for CFD simulation
4. Tracks results and suggests optimal parameters

Usage:
    python ai_impeller_optimizer.py --mode grid_search
    python ai_impeller_optimizer.py --mode gradient_descent --best_variant 15
"""

import subprocess
import json
import os
from pathlib import Path
from itertools import product
import argparse

# ============================================================================
# CONFIGURATION
# ============================================================================

OPENSCAD_PATH = r"C:\Program Files\OpenSCAD\openscad.exe"
PROJECT_DIR = Path(__file__).parent
OUTPUT_DIR = PROJECT_DIR / "optimization_variants"
RESULTS_FILE = PROJECT_DIR / "optimization_results.json"

# Base template file
TEMPLATE_FILE = PROJECT_DIR / "motor_impeller_assembly.scad"

# ============================================================================
# OPTIMIZATION PARAMETERS
# ============================================================================

# Parameter ranges for BLADED impeller
BLADED_PARAMS = {
    "BLADED_DIAMETER": [85, 90, 95],           # mm
    "BLADED_BLADE_COUNT": [2, 3, 4],           # number
    "BLADED_ROOT_CHORD": [30, 35, 40],         # mm
    "BLADED_BLADE_TWIST": [-30, -25, -20],     # degrees
    "BLADED_ATTACK_ANGLE": [-8, -5, -2],       # degrees
}

# Parameter ranges for BLADELESS impeller  
BLADELESS_PARAMS = {
    "BLADELESS_AIR_GAP": [0.6, 0.8, 1.0],              # mm
    "BLADELESS_THROAT_RATIO": [0.68, 0.72, 0.76],      # ratio
    "BLADELESS_EXPANSION_ANGLE": [14, 18, 22],         # degrees
    "BLADELESS_RING_THICKNESS": [2.5, 3.0, 3.5],       # mm
}

# ============================================================================
# DESIGN VARIANT GENERATOR
# ============================================================================

class DesignVariant:
    """Represents a single impeller design with specific parameters"""
    
    def __init__(self, variant_id, impeller_type, params):
        self.id = variant_id
        self.type = impeller_type
        self.params = params
        self.results = None
        
    def __repr__(self):
        return f"Variant {self.id} ({self.type}): {self.params}"
    
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "params": self.params,
            "results": self.results
        }


def generate_grid_search_variants(impeller_type="bladed"):
    """Generate all combinations of parameters (grid search)"""
    
    params_dict = BLADED_PARAMS if impeller_type == "bladed" else BLADELESS_PARAMS
    
    # Get all parameter names and value lists
    param_names = list(params_dict.keys())
    param_values = list(params_dict.values())
    
    # Generate all combinations
    combinations = list(product(*param_values))
    
    variants = []
    for i, combo in enumerate(combinations):
        params = dict(zip(param_names, combo))
        variant = DesignVariant(f"{impeller_type}_{i:03d}", impeller_type, params)
        variants.append(variant)
    
    print(f"✓ Generated {len(variants)} design variants ({impeller_type})")
    return variants


def generate_gradient_variants(base_variant, step_size=0.1):
    """Generate variants around a base design using gradient descent"""
    
    variants = []
    variant_id = 0
    
    for param_name, base_value in base_variant.params.items():
        # Positive step
        params_plus = base_variant.params.copy()
        params_plus[param_name] = base_value * (1 + step_size)
        variants.append(DesignVariant(
            f"{base_variant.type}_grad_{variant_id:03d}",
            base_variant.type,
            params_plus
        ))
        variant_id += 1
        
        # Negative step
        params_minus = base_variant.params.copy()
        params_minus[param_name] = base_value * (1 - step_size)
        variants.append(DesignVariant(
            f"{base_variant.type}_grad_{variant_id:03d}",
            base_variant.type,
            params_minus
        ))
        variant_id += 1
    
    print(f"✓ Generated {len(variants)} gradient variants around base design")
    return variants


# ============================================================================
# OPENSCAD MODEL GENERATOR
# ============================================================================

def create_scad_file(variant, output_path):
    """Create OpenSCAD file with variant's parameters"""
    
    # Read template
    with open(TEMPLATE_FILE, 'r') as f:
        template = f.read()
    
    # Modify parameters
    modified = template
    
    # Set impeller type
    impeller_type_map = {
        "bladed": "bladed",
        "bladeless": "bladeless", 
        "hybrid": "hybrid"
    }
    modified = modified.replace(
        'IMPELLER_TYPE = "bladed"',
        f'IMPELLER_TYPE = "{impeller_type_map[variant.type]}"'
    )
    
    # Set export mode to impeller only (for CFD)
    modified = modified.replace(
        'EXPORT_MODE = "full_assembly"',
        'EXPORT_MODE = "impeller_only"'
    )
    
    # Replace each parameter
    for param_name, param_value in variant.params.items():
        # Find the line with this parameter
        search_str = f"{param_name} = "
        lines = modified.split('\n')
        
        for i, line in enumerate(lines):
            if search_str in line and not line.strip().startswith('//'):
                # Replace the value
                if isinstance(param_value, int):
                    lines[i] = f"{param_name} = {param_value};"
                else:
                    lines[i] = f"{param_name} = {param_value:.2f};"
                break
        
        modified = '\n'.join(lines)
    
    # Write modified file
    with open(output_path, 'w') as f:
        f.write(modified)
    
    return True


def render_variant_to_stl(variant, scad_path, stl_path):
    """Render OpenSCAD file to STL using CLI"""
    
    cmd = [
        OPENSCAD_PATH,
        "-o", str(stl_path),
        "-D", "$fn=60",
        str(scad_path)
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0 and stl_path.exists():
            file_size = stl_path.stat().st_size / (1024 * 1024)
            return True, file_size
        else:
            return False, result.stderr
    
    except Exception as e:
        return False, str(e)


# ============================================================================
# BATCH PROCESSING
# ============================================================================

def process_variants(variants, output_dir):
    """Generate STL files for all variants"""
    
    output_dir.mkdir(exist_ok=True)
    
    success_count = 0
    results = []
    
    for variant in variants:
        print(f"\n📐 Processing {variant.id}...")
        print(f"   Parameters: {variant.params}")
        
        # Create .scad file
        scad_path = output_dir / f"{variant.id}.scad"
        create_scad_file(variant, scad_path)
        print(f"   ✓ SCAD file: {scad_path.name}")
        
        # Render to STL
        stl_path = output_dir / f"{variant.id}.stl"
        print(f"   Rendering... ", end="", flush=True)
        
        success, info = render_variant_to_stl(variant, scad_path, stl_path)
        
        if success:
            print(f"✓ STL ({info:.2f} MB)")
            success_count += 1
            results.append(variant.to_dict())
        else:
            print(f"✗ Failed: {info}")
    
    return success_count, results


# ============================================================================
# CFD TEST MATRIX GENERATOR
# ============================================================================

def generate_cfd_test_matrix(variants, rpm_values=[5000, 7000, 9000]):
    """Generate test matrix for CFD simulations"""
    
    matrix = []
    
    for variant in variants:
        for rpm in rpm_values:
            test = {
                "variant_id": variant.id,
                "variant_type": variant.type,
                "params": variant.params,
                "rpm": rpm,
                "stl_file": f"{variant.id}.stl",
                "status": "pending",
                "thrust": None,
                "power": None,
                "efficiency": None
            }
            matrix.append(test)
    
    return matrix


def save_test_matrix(matrix, filename="cfd_test_matrix.json"):
    """Save test matrix to JSON file"""
    
    filepath = PROJECT_DIR / filename
    
    with open(filepath, 'w') as f:
        json.dump(matrix, f, indent=2)
    
    print(f"\n✓ Test matrix saved: {filepath}")
    print(f"  Total tests: {len(matrix)}")
    return filepath


# ============================================================================
# RESULT ANALYSIS
# ============================================================================

def analyze_results(results_file):
    """Analyze CFD results and find optimal design"""
    
    if not results_file.exists():
        print(f"❌ Results file not found: {results_file}")
        print(f"\n📋 How to populate results:")
        print(f"   1. First run: python ai_impeller_optimizer.py --mode grid_search")
        print(f"   2. This generates STL files and cfd_test_matrix.json")
        print(f"   3. Run CFD simulations (SimScale, OpenFOAM, etc.)")
        print(f"   4. Create {results_file.name} with this format:")
        print(f'      [{{"variant_id": "bladed_000", "params": {{...}}, "rpm": 7000,')
        print(f'        "thrust": 850.5, "power": 120.3, "efficiency": 7.07}}, ...]')
        print(f"   5. Then run analyze mode again")
        
        # Check if test matrix exists
        matrix_file = PROJECT_DIR / "cfd_test_matrix.json"
        if matrix_file.exists():
            print(f"\n✓ Found test matrix: {matrix_file}")
            print(f"   You can use this as a template to create {results_file.name}")
        
        return None
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Find best variants
    completed = [r for r in results if r.get("thrust") is not None]
    
    if not completed:
        print("No completed tests found.")
        return None
    
    # Sort by efficiency (thrust/power)
    best_efficiency = max(completed, key=lambda x: x.get("efficiency", 0))
    best_thrust = max(completed, key=lambda x: x.get("thrust", 0))
    
    print("\n" + "="*70)
    print("OPTIMIZATION RESULTS ANALYSIS")
    print("="*70)
    
    print(f"\n🏆 Best Efficiency: {best_efficiency['variant_id']}")
    print(f"   Efficiency: {best_efficiency['efficiency']:.2f} g/W")
    print(f"   Thrust: {best_efficiency['thrust']:.1f} g @ {best_efficiency['rpm']} RPM")
    print(f"   Parameters: {json.dumps(best_efficiency['params'], indent=6)}")
    
    print(f"\n🚀 Best Thrust: {best_thrust['variant_id']}")
    print(f"   Thrust: {best_thrust['thrust']:.1f} g @ {best_thrust['rpm']} RPM")
    print(f"   Efficiency: {best_thrust['efficiency']:.2f} g/W")
    print(f"   Parameters: {json.dumps(best_thrust['params'], indent=6)}")
    
    return {
        "best_efficiency": best_efficiency,
        "best_thrust": best_thrust
    }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="AI Impeller Optimization")
    parser.add_argument("--mode", choices=["grid_search", "gradient_descent", "analyze"],
                       default="grid_search", help="Optimization mode")
    parser.add_argument("--impeller_type", choices=["bladed", "bladeless", "both"],
                       default="bladed", help="Impeller type to optimize")
    parser.add_argument("--base_variant", type=str, help="Base variant for gradient descent")
    
    args = parser.parse_args()
    
    print("="*70)
    print("AI IMPELLER OPTIMIZER")
    print("="*70)
    
    # Check OpenSCAD
    if not os.path.exists(OPENSCAD_PATH):
        print(f"❌ OpenSCAD not found: {OPENSCAD_PATH}")
        print("   Please install OpenSCAD or update OPENSCAD_PATH")
        return
    
    print(f"✓ OpenSCAD: {OPENSCAD_PATH}")
    print(f"✓ Output directory: {OUTPUT_DIR}")
    
    # ========================================================================
    # MODE: GRID SEARCH
    # ========================================================================
    
    if args.mode == "grid_search":
        print(f"\n🔍 Mode: Grid Search")
        print(f"   Type: {args.impeller_type}")
        
        variants = []
        
        if args.impeller_type == "bladed" or args.impeller_type == "both":
            variants.extend(generate_grid_search_variants("bladed"))
        
        if args.impeller_type == "bladeless" or args.impeller_type == "both":
            variants.extend(generate_grid_search_variants("bladeless"))
        
        print(f"\n📊 Total variants: {len(variants)}")
        print(f"   Estimated render time: {len(variants) * 30 / 60:.1f} minutes")
        
        # Process variants
        success, results = process_variants(variants, OUTPUT_DIR)
        
        print(f"\n" + "="*70)
        print(f"BATCH PROCESSING COMPLETE")
        print("="*70)
        print(f"✓ Success: {success}/{len(variants)} variants")
        print(f"✓ STL files: {OUTPUT_DIR}")
        
        # Generate CFD test matrix
        matrix = generate_cfd_test_matrix(variants)
        matrix_file = save_test_matrix(matrix)
        
        print(f"\n📋 Next Steps:")
        print(f"   1. Upload STL files to SimScale")
        print(f"   2. Run CFD simulations (use test matrix as guide)")
        print(f"   3. Record results in: {RESULTS_FILE}")
        print(f"   4. Run: python ai_impeller_optimizer.py --mode analyze")
    
    # ========================================================================
    # MODE: GRADIENT DESCENT
    # ========================================================================
    
    elif args.mode == "gradient_descent":
        print(f"\n📈 Mode: Gradient Descent")
        
        if not args.base_variant:
            print("❌ Error: --base_variant required for gradient descent")
            print("   Example: --base_variant bladed_015")
            return
        
        # Load base variant from previous results
        # (Implementation depends on results file format)
        print(f"   Base: {args.base_variant}")
        print("   Step size: 10%")
        
        # TODO: Load base variant and generate gradient variants
        print("\n⚠️  Gradient descent mode not yet implemented")
        print("   Run grid search first to find good starting point")
    
    # ========================================================================
    # MODE: ANALYZE RESULTS
    # ========================================================================
    
    elif args.mode == "analyze":
        print(f"\n📊 Mode: Analyze Results")
        analyze_results(RESULTS_FILE)


if __name__ == "__main__":
    main()
