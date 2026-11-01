# Cutting, Chip Formation, and Dynamic Plasticity Investigation

## Status: Not Yet Implemented (Continuum FEA Operational, SPH Cutting Scoped)

### Physics & Numerical Complexity
Dynamic metal cutting involves:
1. Finite elastoplastic deformation and high strain rates ($10^3 - 10^6 \text{ s}^{-1}$).
2. Johnson-Cook constitutive law.
3. Adiabatic shear banding and chip separation.
4. Tool-workpiece contact and friction heat generation.

CalculiX static structural solver does not support mesh separation or SPH hydrodynamic simulation. We recommend SPHinXsys or explicit dynamic solvers for this capability.
