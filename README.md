# CADMind: Offline AI Engineering Design and Simulation Studio

CADMind is an offline-first desktop engineering suite integrating:
- **Tauri 2 + React + TypeScript + Three.js** interactive 3D desktop application.
- **Parametric OpenSCAD CAD Modeling** with real-time parameter tweaking and 3D mesh rendering.
- **Offline Meta Llama 3.2 3B Assistant** providing structured mechanical requirements, missing assumption detection, and simulation result diagnosis.
- **Gmsh Volumetric Mesher & CalculiX (`ccx`) FEA Solver** for verified continuum structural deflection and stress analysis, plus thermal simulations.
- **NVIDIA SimReady Asset Client** for selective search, download, and local caching from Hugging Face.

---

## Benchmark Comparisons

### Cantilever Beam ($100 \times 20 \times 10\text{ mm}$, $100\text{ N}$ tip load, $E=70\text{ GPa}$, $\nu=0.33$)
- **Euler-Bernoulli Analytical Solution:** $-0.2857\text{ mm}$
- **CalculiX Coarse Mesh (size 6.0):** $-0.2458\text{ mm}$
- **CalculiX Refined Mesh (size 3.0):** $-0.2645\text{ mm}$ (monotonically converging towards theoretical elasticity limit)

### Parametric Mounting Bracket Hackathon Scenario ($100\text{ N}$ load)
- **Baseline Design ($6.0\text{ mm}$ thickness):** Tip deflection $0.0381\text{ mm}$, Peak Von Mises stress $34.22\text{ MPa}$ ($FoS = 8.06$).
- **AI-Revised Stiffened Design ($8.5\text{ mm}$ thickness):** Tip deflection $0.0213\text{ mm}$ (**44% deflection reduction**), Peak Von Mises stress $22.76\text{ MPa}$.

---

## Implementation & Testing Status

| Capability | Status | Description |
| :--- | :--- | :--- |
| **OpenSCAD Parametric CAD Engine** | **Implemented & Tested** | Full interactive 3D rendering, parameter sliders, SCAD and STL export. |
| **Gmsh 3D Tetrahedral Mesher** | **Implemented & Tested** | Generates C3D4 and C3D10 meshes with physical boundary tag preservation. |
| **CalculiX Structural FEA Solver** | **Implemented & Tested** | Runs offline static structural jobs, parsing displacements and Von Mises stresses. |
| **Steady-State Thermal FEA** | **Implemented & Tested** | Thermal conductivity and heat flux analysis using CalculiX. |
| **Meta Llama 3.2 3B AI Studio** | **Implemented & Tested** | Natural language to CAD generation, missing assumption flags, and design revision. |
| **NVIDIA SimReady Asset Client** | **Implemented & Tested** | Hugging Face catalog search, selective single-package download, and local caching. |
| **Hardware & Solver Diagnostics** | **Implemented & Tested** | Automatic detection of CPU, GPU, RAM, VRAM, and solver availability. |
| **Dynamic Metal Cutting & Chip Formation** | **Not Yet Implemented** | Scoped in `docs/cutting_simulation_investigation.md` (requires SPH / Johnson-Cook solver). |

---

## Windows 11 & Linux Quickstart

### 1. External Binaries Required
- **OpenSCAD**: `winget install Openscad.Openscad` or `apt install openscad`
- **Gmsh**: `winget install Gmsh.Gmsh` or `apt install gmsh`
- **CalculiX (`ccx`)**: Download Windows build from [CalculiX.de](http://www.calculix.de/) or `apt install calculix-ccx`

### 2. Launching CADMind
```bash
# Windows
run_cadmind.bat

# Linux / macOS
chmod +x run_cadmind.sh
./run_cadmind.sh
```
