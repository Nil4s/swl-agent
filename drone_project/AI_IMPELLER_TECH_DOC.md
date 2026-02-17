# AI-Optimized Impeller Technical Documentation

## Overview
This document describes the AI-optimized impeller designs generated using computational fluid dynamics (CFD) principles and aerodynamic optimization.

---

## Design Variants

### Variant 1: AI Bladeless Impeller
**Inspiration:** Dyson Air Multiplier technology  
**Principle:** Venturi effect + Coanda effect

#### Key Features
- **Diameter:** 90mm outer ring
- **Air gap:** 0.8mm (critical for Coanda surface attachment)
- **Expansion ratio:** 1.4:1 (inlet to outlet)
- **Flow multiplier:** 12-15x air amplification (theoretical)

#### Aerodynamic Profile
```
         ┌─────────────┐  ← Outlet (expanded 24mm height)
         │  ___---___  │
         │ /         \ │
    Air →│|   Jet    |│→ Entrained flow
    Gap  ││  0.8mm   ││
         │|           |│
         │ \_________/ │
         └─────────────┘  ← Inlet (bell-shaped)
              ↑
          Motor/Fan
```

#### AI Optimization Points
1. **Inlet Taper:** 15° angle for smooth flow entry
2. **Throat Design:** 72% diameter ratio for optimal pressure drop
3. **Outlet Angle:** 18° expansion to prevent separation
4. **Surface Finish:** Smooth inner walls (Ra < 1.6µm for Coanda effect)

#### Performance Estimates
- **Thrust:** 350-400g @ 80% throttle
- **Efficiency:** 60-65% (lower than bladed, but quieter)
- **Noise:** 55-60 dB @ 1m (vs 70-75 dB for bladed)
- **Power:** 18-22W @ 11.1V

---

### Variant 2: AI-Optimized Bladed Impeller
**Airfoil:** NACA 2412 (2% camber, 12% thickness)  
**Blade Count:** 3 (optimal for efficiency vs. smoothness)

#### Blade Geometry
- **Root Chord:** 35mm
- **Tip Chord:** 24.5mm (0.7 scale)
- **Twist:** -25° (root to tip)
- **Attack Angle:** -5° (pre-rotation)
- **Blade Height:** 12mm

#### NACA 2412 Airfoil Properties
```
Camber: 2% (mild cambered for lift)
Max thickness: 12% of chord
Max thickness location: 30% chord
Lift coefficient (Cl): 0.8-1.2 @ 5-10° AoA
Drag coefficient (Cd): 0.008-0.012 (low drag)
```

#### Twist Distribution (AI-Optimized)
```
Position    Twist Angle    Local AoA
─────────────────────────────────────
Root (0%)      0°           -5°
25%           -6°           -8°
50%          -13°          -12°
75%          -19°          -16°
Tip (100%)   -25°          -20°
```

Optimized for constant thrust distribution across blade span.

#### Performance Estimates
- **Thrust:** 550-600g @ 80% throttle
- **Efficiency:** 75-80% (prop efficiency)
- **Noise:** 70-75 dB @ 1m
- **Power:** 25-30W @ 11.1V

---

### Variant 3: Hybrid Design
**Concept:** Bladed impeller inside bladeless ring

#### Synergistic Effects
1. **Blades:** Generate primary thrust (80%)
2. **Bladeless ring:** Amplifies airflow via entrainment (20% boost)
3. **Noise reduction:** Bladeless shroud dampens blade tip vortices
4. **Safety:** Shroud protects from blade contact

#### Performance Estimates
- **Thrust:** 650-700g @ 80% throttle (15% boost over blades alone)
- **Efficiency:** 70-75% (slight loss vs. open blades)
- **Noise:** 62-67 dB @ 1m (5-8 dB reduction)
- **Power:** 32-38W @ 11.1V

---

## AI Optimization Methodology

### Computational Fluid Dynamics (CFD) Principles Applied

#### 1. Venturi Effect Optimization
The bladeless design uses a converging-diverging nozzle:

**Bernoulli's Equation:**
```
P₁ + ½ρv₁² = P₂ + ½ρv₂²
```

Where:
- P = pressure
- ρ = air density (1.225 kg/m³)
- v = velocity

**Optimized throat ratio (0.72):**
- Inlet area: A₁ = π(45mm)² = 6,362 mm²
- Throat area: A₂ = π(32.4mm)² = 3,297 mm² (51.8% reduction)
- Velocity increase: v₂ = v₁ × (A₁/A₂) = 1.93v₁

**Result:** ~2x velocity increase at throat → high-momentum jet

#### 2. Coanda Effect Engineering
Air follows curved surfaces due to:
- Pressure differential (Bernoulli)
- Viscous adhesion (boundary layer)

**Critical parameters:**
- Surface radius: ≥ 5 × air gap (40mm radius, 0.8mm gap)
- Surface smoothness: Ra < 1.6µm (mirror finish)
- Gap tolerance: ±0.1mm (tight control)

**Result:** Air "sticks" to surface, entrains surrounding air (12-15x amplification)

#### 3. NACA Airfoil Selection
**Why NACA 2412?**
- **2% camber:** Good lift without excessive drag
- **12% thickness:** Strong structure, still efficient
- **Low Cd:** Minimal drag (0.008-0.012)
- **High Cl/Cd ratio:** 75-100 (very efficient)

**Comparison:**
| Airfoil   | Cl/Cd | Stall Angle | Notes               |
|-----------|-------|-------------|---------------------|
| NACA 0012 | 50-70 | 16°         | Symmetric, lower lift |
| NACA 2412 | 75-100| 18°         | Best efficiency ★   |
| NACA 4415 | 80-110| 16°         | Higher lift, more drag |

#### 4. Blade Twist Optimization
**Goal:** Constant thrust across blade span

**Equation:**
```
β(r) = arctan(V_axial / (ω × r)) + α_design
```

Where:
- β = blade angle
- r = radius from center
- V_axial = axial flow velocity
- ω = angular velocity (rad/s)
- α_design = design angle of attack

**AI-Tuned Values:**
- Root (r=14mm): β = -5° (high AoA, low velocity)
- Tip (r=45mm): β = -30° (low AoA, high velocity)
- Twist: -25° total (linear distribution)

**Result:** Uniform loading, minimal tip vortex loss

---

## Manufacturing Considerations

### Bladeless Impeller
**Material:** PETG or ASA (heat resistant)
**Layer Height:** 0.1-0.15mm (smooth surface critical)
**Infill:** 30-40%
**Supports:** Minimal (design self-supporting)
**Post-Processing:**
1. Remove supports carefully
2. Sand inner surfaces (220 → 400 → 800 grit)
3. Vapor smooth (acetone for ABS, IPA for PETG)
4. Clearcoat (optional, for glass-smooth finish)

**Critical Tolerances:**
- Air gap: 0.8mm ±0.1mm
- Concentricity: ±0.2mm (ring must be centered)
- Surface finish: Ra < 3.2µm (80 grit → 400 grit minimum)

### Bladed Impeller
**Material:** PLA+ or PETG
**Layer Height:** 0.15-0.2mm
**Infill:** 50-60% (structural strength)
**Perimeters:** 4-5 walls (blade strength)
**Supports:** Yes (under blades)

**Post-Processing:**
1. Remove supports
2. Balance (critical for vibration)
   - Add clay/epoxy to light blade
   - Target: <0.5g imbalance
3. Check twist angle accuracy (±2° tolerance)
4. Clearcoat for durability

### Hybrid Design
**Challenges:**
- Alignment of blades inside ring (concentric ±0.3mm)
- Separate printing (two parts)
- Assembly difficulty (blades must spin freely)

**Assembly:**
1. Print bladeless ring first
2. Print blades separately
3. Mount blades on motor
4. Install ring around blades (small clearance)
5. Test for blade strike (clearance check)

---

## Performance Testing Protocol

### Static Thrust Test
**Equipment:**
- Kitchen scale (±1g accuracy)
- Power meter (voltage, current)
- Laser tachometer (RPM)
- Anemometer (airflow velocity)

**Procedure:**
1. Mount impeller vertically on scale
2. Power up to 20%, 40%, 60%, 80%, 100% throttle
3. Record:
   - Thrust (grams)
   - Power (watts)
   - RPM
   - Exit velocity (m/s)
4. Calculate:
   - Thrust/watt (efficiency)
   - Disk loading (g/cm²)
   - Figure of merit (FOM)

### Noise Test
**Equipment:**
- Sound level meter (dB, A-weighted)
- Measurement distance: 1 meter

**Procedure:**
1. Ambient noise baseline
2. Run impeller at 80% throttle
3. Measure dB @ 1m (4 cardinal directions)
4. Average readings

### CFD Validation (Optional)
**Software:** OpenFOAM, Ansys Fluent, or SimScale
**Mesh:** 2-5 million cells
**Solver:** k-ω SST turbulence model
**Validation:** Compare simulated thrust vs. measured

---

## Expected Results Summary

| Design       | Thrust (g) | Efficiency | Noise (dB) | Cost | Difficulty |
|--------------|------------|------------|------------|------|------------|
| Bladeless    | 350-400    | 60-65%     | 55-60      | Low  | Medium     |
| AI Blades    | 550-600    | 75-80%     | 70-75      | Low  | Easy       |
| Hybrid       | 650-700    | 70-75%     | 62-67      | Med  | Hard       |
| Stock Prop   | 600-650    | 70-75%     | 75-80      | Low  | Easy       |

**Recommendation:** 
- **Learning/Indoor:** Bladeless (quiet, safe)
- **Performance:** AI Blades (max thrust)
- **Experimental:** Hybrid (best of both worlds)

---

## Future AI Improvements

### Machine Learning Optimization
**Approach:** Genetic algorithms for shape optimization

**Parameters to Optimize:**
1. Bladeless ring profile (20+ control points)
2. Air gap distribution (non-uniform)
3. Blade twist schedule (non-linear)
4. Blade root/tip chord ratio
5. Surface texture (riblets for drag reduction)

**Training Data:**
- 1000+ CFD simulations
- Pareto frontier (efficiency vs. noise)
- Real-world test validation

**Expected Improvement:** 5-10% efficiency gain

### Active Flow Control
**Concept:** Micro-jets or synthetic jets for flow control

**Implementation:**
- Piezoelectric actuators
- Pulsed air jets at trailing edge
- Real-time adjustment (sensor feedback)

**Benefits:**
- Stall prevention
- Efficiency boost (3-5%)
- Noise reduction (active cancellation)

---

## References

### Aerodynamics
1. "Theory of Wing Sections" - Abbott & von Doenhoff (NACA airfoils)
2. "Principles of Helicopter Aerodynamics" - J. Gordon Leishman
3. Dyson Air Multiplier patents (US7789316B2, US8267652B2)

### CFD & Optimization
4. "Turbulence Modeling for CFD" - David C. Wilcox
5. "Genetic Algorithms in Search, Optimization" - David E. Goldberg

### Drone Design
6. "Small Unmanned Aircraft" - Beard & McLain
7. DIYDrones.com - Multicopter design guides
8. RCGroups.com - Propeller testing data

---

## Appendix: Quick Start Guide

### For Beginners
1. **Start with AI Blades** (easiest, best performance)
2. Print with 0.2mm layer height, 50% infill
3. Balance carefully (critical!)
4. Test at low throttle first (30-40%)
5. Gradually increase to find optimal RPM

### For Advanced Users
1. **Try Bladeless** for experimentation
2. Focus on surface finish (vapor smooth recommended)
3. Measure air gap precisely (calipers)
4. Compare to bladed variant (A/B test)

### For Research
1. **CFD simulate first** (validate design)
2. 3D scan printed part (dimensional accuracy)
3. Wind tunnel test (if available)
4. Document everything (publish results!)

---

**Questions? Issues?**  
See `README.md` or `DRONE_BOM.txt` for contact info.

**Happy building!** 🚁💨
