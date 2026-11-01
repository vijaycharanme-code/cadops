"""
CADMind Local Simulation & Engineering HTTP Service.
"""
import os, sys, json, shutil, tempfile
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from mesh_generator import MeshGenerator
from deck_generator import CalculixDeckGenerator
from solver import CalculixSolver
from simready import SimReadyClient

class SimulationRequestHandler(BaseHTTPRequestHandler):
    mg = MeshGenerator()
    dg = CalculixDeckGenerator()
    solver = CalculixSolver()
    simready = SimReadyClient()

    def _headers(self, code=200, ct="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ct)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self): self._headers(200)

    def do_GET(self):
        p = urlparse(self.path)
        path = p.path
        q = parse_qs(p.query)
        if path == "/api/health":
            self._headers(200)
            self.wfile.write(json.dumps({
                "status": "online",
                "service": "CADMind Engineering Backend",
                "binaries": {
                    "openscad": shutil.which("openscad") is not None,
                    "gmsh": shutil.which("gmsh") is not None,
                    "calculix_ccx": shutil.which("ccx") is not None
                }
            }).encode())
            return
        elif path == "/api/simready/search":
            query = q.get("q", [""])[0]
            limit = int(q.get("limit", ["30"])[0])
            self._headers(200)
            self.wfile.write(json.dumps(self.simready.search_online(query, limit)).encode())
            return
        elif path == "/api/simready/details":
            aid = q.get("id", [""])[0]
            self._headers(200)
            self.wfile.write(json.dumps(self.simready.get_asset_package_details(aid)).encode())
            return
        self._headers(404)
        self.wfile.write(b'{"error": "not found"}')

    def do_POST(self):
        p = urlparse(self.path)
        path = p.path
        len_h = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(len_h).decode() if len_h > 0 else "{}"
        try: data = json.loads(body)
        except Exception: data = {}

        if path == "/api/cad/render":
            scad = data.get("scad", "")
            with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
                stl_p = tmp.name
            try:
                self.mg.render_scad_to_stl(scad, stl_p)
                with open(stl_p, "rb") as f: content = f.read()
                self._headers(200, "application/octet-stream")
                self.wfile.write(content)
            finally:
                if os.path.exists(stl_p): os.remove(stl_p)
            return

        elif path == "/api/simulation/structural":
            l = float(data.get("length", 60.0))
            w = float(data.get("width", 30.0))
            h = float(data.get("height", 50.0))
            th = float(data.get("thickness", 6.0))
            hr = float(data.get("hole_radius", 4.0))
            ms = float(data.get("mesh_size", 4.0))
            load_z = float(data.get("load_z", -100.0))

            with tempfile.TemporaryDirectory() as td:
                geo_p = os.path.join(td, "part.geo")
                msh_p = os.path.join(td, "part.msh")
                self.mg.generate_bracket_geometry_geo(l, w, h, th, hr, ms, geo_p)
                self.mg.mesh_geo_to_msh(geo_p, msh_p, order=1)
                mesh = self.mg.parse_msh2(msh_p)

                nodes, elements = mesh["nodes"], mesh["elements"]
                fixed = [nid for nid, (x, y, z) in nodes.items() if x <= 0.1]
                loaded = [nid for nid, (x, y, z) in nodes.items() if x >= l * 0.65 and z >= th - 0.5]

                mat = {"youngs_modulus": 70000.0, "poissons_ratio": 0.33, "yield_strength": 276.0}
                deck = self.dg.generate_structural_deck(nodes, elements, mat, fixed, loaded, (0, 0, load_z), order=1)
                res = self.solver.run_simulation(deck, job_name="bracket")
                disps = res.get("dat_results", {}).get("displacements", {})
                stresses = res.get("dat_results", {}).get("stresses", {})

                max_disp_z = min((d[2] for d in disps.values()), default=0.0)
                max_vm = max(stresses.values(), default=0.0)
                fos = mat["yield_strength"] / max_vm if max_vm > 0 else 999.0

                self._headers(200)
                self.wfile.write(json.dumps({
                    "status": "success",
                    "results": {
                        "max_displacement_mm": max((d[3] for d in disps.values()), default=0.0),
                        "max_deflection_z_mm": abs(max_disp_z),
                        "max_von_mises_mpa": max_vm,
                        "yield_strength_mpa": mat["yield_strength"],
                        "factor_of_safety": round(fos, 2)
                    }
                }).encode())
            return

        elif path == "/api/simready/download":
            aid = data.get("asset_id", "")
            self._headers(200)
            self.wfile.write(json.dumps(self.simready.download_asset(aid)).encode())
            return
        elif path == "/api/simready/delete":
            aid = data.get("asset_id", "")
            self._headers(200)
            self.wfile.write(json.dumps({"status": "deleted" if self.simready.remove_from_cache(aid) else "error"}).encode())
            return

        self._headers(404)
        self.wfile.write(b'{"error": "not found"}')

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = HTTPServer(("127.0.0.1", port), SimulationRequestHandler)
    print(f"CADMind server on http://127.0.0.1:{port}")
    server.serve_forever()
