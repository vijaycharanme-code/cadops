"""
Thermal FEA Benchmark.
"""
import sys, os, tempfile
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend-sim")))

from mesh_generator import MeshGenerator
from deck_generator import CalculixDeckGenerator
from solver import CalculixSolver

def run_thermal():
    mg = MeshGenerator()
    dg = CalculixDeckGenerator()
    solver = CalculixSolver()
    with tempfile.TemporaryDirectory() as td:
        geo = os.path.join(td, "t.geo")
        msh = os.path.join(td, "t.msh")
        mg.generate_beam_geometry_geo(50, 10, 10, 3.0, geo)
        mg.mesh_geo_to_msh(geo, msh, 1)
        mesh = mg.parse_msh2(msh)
        t_nodes = [n for n, (x,y,z) in mesh["nodes"].items() if x <= 0.05]
        deck = dg.generate_thermal_deck(mesh["nodes"], mesh["elements"], 160.0, 900.0, t_nodes, 100.0, [], 0.0)
        res = solver.run_simulation(deck, "therm")
        temps = res["frd_results"]["temperatures"]
        print(f"Thermal run successful. Nodes with temp: {len(temps)}")
        return len(temps) > 0

if __name__ == "__main__":
    run_thermal()
