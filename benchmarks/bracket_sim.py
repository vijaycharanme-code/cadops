"""
Mounting Bracket Structural Analysis (Baseline vs Revised).
"""
import sys, os, tempfile
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend-sim")))

from mesh_generator import MeshGenerator
from deck_generator import CalculixDeckGenerator
from solver import CalculixSolver

def run_bracket(thickness: float = 6.0):
    mg = MeshGenerator()
    dg = CalculixDeckGenerator()
    solver = CalculixSolver()
    with tempfile.TemporaryDirectory() as td:
        geo = os.path.join(td, "brk.geo")
        msh = os.path.join(td, "brk.msh")
        mg.generate_bracket_geometry_geo(60, 30, 50, thickness, 4.0, 4.0, geo)
        mg.mesh_geo_to_msh(geo, msh, 1)
        mesh = mg.parse_msh2(msh)
        fixed = [n for n, (x,y,z) in mesh["nodes"].items() if x <= 0.1]
        loaded = [n for n, (x,y,z) in mesh["nodes"].items() if x >= 60*0.65 and z >= thickness - 0.5]
        mat = {"youngs_modulus": 70000.0, "poissons_ratio": 0.33, "yield_strength": 276.0}
        deck = dg.generate_structural_deck(mesh["nodes"], mesh["elements"], mat, fixed, loaded, (0, 0, -100.0), 1)
        res = solver.run_simulation(deck, "brk")
        dat = res["dat_results"]
        max_vm = dat["max_stress"]
        disps = dat["displacements"]
        min_uz = min((d[2] for d in disps.values()), default=0.0)
        return abs(min_uz), max_vm

if __name__ == "__main__":
    d0, s0 = run_bracket(6.0)
    d1, s1 = run_bracket(8.5)
    print(f"Base: defl={d0:.4f}mm, vm={s0:.2f}MPa | Rev: defl={d1:.4f}mm, vm={s1:.2f}MPa")
