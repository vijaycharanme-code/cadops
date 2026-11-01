"""
Cantilever Beam FEA vs Analytical Euler-Bernoulli Verification.
Geometry: 100 mm x 20 mm x 10 mm
Load: 100 N tip load in -Z direction
Material: Aluminum E = 70,000 MPa, nu = 0.33
Euler-Bernoulli Analytical: w_tip = (F * L^3) / (3 * E * I) = -0.2857 mm
"""
import sys, os, tempfile
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend-sim")))

from mesh_generator import MeshGenerator
from deck_generator import CalculixDeckGenerator
from solver import CalculixSolver

def run_cantilever_benchmark(mesh_size: float = 3.0, order: int = 1):
    L, W, H = 100.0, 20.0, 10.0
    F = 100.0
    E = 70000.0
    nu = 0.33
    I = (W * (H**3)) / 12.0
    w_analytical = -(F * (L**3)) / (3.0 * E * I)

    mg = MeshGenerator()
    dg = CalculixDeckGenerator()
    solver = CalculixSolver()

    with tempfile.TemporaryDirectory() as td:
        geo_p = os.path.join(td, "beam.geo")
        msh_p = os.path.join(td, "beam.msh")
        mg.generate_beam_geometry_geo(L, W, H, mesh_size, geo_p)
        mg.mesh_geo_to_msh(geo_p, msh_p, order=order)
        mesh = mg.parse_msh2(msh_p)

        fixed = [nid for nid, (x, y, z) in mesh["nodes"].items() if x <= 0.05]
        tip_nodes = [nid for nid, (x, y, z) in mesh["nodes"].items() if x >= L - 0.1]
        mat = {"youngs_modulus": E, "poissons_ratio": nu}
        deck = dg.generate_structural_deck(mesh["nodes"], mesh["elements"], mat, fixed, tip_nodes, (0, 0, -F), order=order)
        res = solver.run_simulation(deck, job_name="cantilever")
        disps = res["dat_results"]["displacements"]
        tip_uz = [disps[nid][2] for nid in tip_nodes if nid in disps]
        mean_uz = sum(tip_uz) / len(tip_uz)

        print(f"Nodes: {mesh['num_nodes']}, Elements: {mesh['num_elements']}")
        print(f"Mean tip Uz: {mean_uz:.4f} mm, Analytical: {w_analytical:.4f} mm")
        return mean_uz

if __name__ == "__main__":
    run_cantilever_benchmark()
