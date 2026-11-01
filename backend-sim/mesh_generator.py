"""
CADMind Mesh Generator.
Converts OpenSCAD geometry or STL into volumetric tetrahedral meshes using Gmsh.
"""
import os
import subprocess
import tempfile
from typing import Dict, List, Tuple, Any

class MeshGenerator:
    def __init__(self, gmsh_bin: str = "gmsh", openscad_bin: str = "openscad"):
        self.gmsh_bin = gmsh_bin
        self.openscad_bin = openscad_bin

    def render_scad_to_stl(self, scad_content: str, output_stl: str) -> bool:
        with tempfile.NamedTemporaryFile(suffix=".scad", delete=False, mode="w") as f:
            f.write(scad_content)
            scad_path = f.name
        try:
            cmd = [self.openscad_bin, "-o", output_stl, scad_path]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
            if res.returncode != 0:
                raise RuntimeError(f"OpenSCAD rendering failed: {res.stderr.decode('utf-8', errors='ignore')}")
            return os.path.exists(output_stl) and os.path.getsize(output_stl) > 0
        finally:
            if os.path.exists(scad_path):
                os.remove(scad_path)

    def generate_beam_geometry_geo(self, length: float, width: float, height: float, mesh_size: float, output_geo: str):
        geo_content = f"""
SetFactory("OpenCASCADE");
Box(1) = {{0, 0, 0, {length}, {width}, {height}}};
Mesh.CharacteristicLengthMin = {mesh_size};
Mesh.CharacteristicLengthMax = {mesh_size};
Mesh 3;
"""
        with open(output_geo, "w") as f:
            f.write(geo_content)

    def generate_bracket_geometry_geo(self, length: float, width: float, height: float, thickness: float, hole_radius: float, mesh_size: float, output_geo: str):
        h1_x = length * 0.7
        h1_y = width * 0.5
        h2_y = width * 0.5
        h2_z = height * 0.7
        th_pad = thickness + 4.0
        geo_content = f"""
SetFactory("OpenCASCADE");
Box(1) = {{0, 0, 0, {length}, {width}, {thickness}}};
Box(2) = {{0, 0, 0, {thickness}, {width}, {height}}};
b() = BooleanUnion{{ Volume{{1}}; Delete; }}{{ Volume{{2}}; Delete; }};
Cylinder(3) = {{{h1_x}, {h1_y}, -2, 0, 0, {th_pad}, {hole_radius}}};
Cylinder(4) = {{-2, {h2_y}, {h2_z}, {th_pad}, 0, 0, {hole_radius}}};
b2() = BooleanDifference{{ Volume{{b()}}; Delete; }}{{ Volume{{3}}; Delete; }};
final() = BooleanDifference{{ Volume{{b2()}}; Delete; }}{{ Volume{{4}}; Delete; }};
Mesh.CharacteristicLengthMin = {mesh_size};
Mesh.CharacteristicLengthMax = {mesh_size};
Mesh 3;
"""
        with open(output_geo, "w") as f:
            f.write(geo_content)

    def mesh_geo_to_msh(self, geo_file: str, output_msh: str, order: int = 1) -> bool:
        cmd = [self.gmsh_bin, "-3", "-order", str(order), "-format", "msh2", geo_file, "-o", output_msh]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        if res.returncode != 0:
            raise RuntimeError(f"Gmsh meshing failed: {res.stderr.decode('utf-8', errors='ignore')}")
        return os.path.exists(output_msh) and os.path.getsize(output_msh) > 0

    def parse_msh2(self, msh_file: str) -> Dict[str, Any]:
        nodes: Dict[int, Tuple[float, float, float]] = {}
        elements: Dict[int, List[int]] = {}
        surface_triangles: Dict[int, List[int]] = {}

        with open(msh_file, "r") as f:
            lines = f.readlines()

        i = 0
        n_lines = len(lines)
        while i < n_lines:
            line = lines[i].strip()
            if line == "$Nodes":
                i += 1
                num_nodes = int(lines[i].strip())
                i += 1
                for _ in range(num_nodes):
                    parts = lines[i].strip().split()
                    nid = int(parts[0])
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    nodes[nid] = (x, y, z)
                    i += 1
            elif line == "$Elements":
                i += 1
                num_elems = int(lines[i].strip())
                i += 1
                for _ in range(num_elems):
                    parts = lines[i].strip().split()
                    eid = int(parts[0])
                    elem_type = int(parts[1])
                    num_tags = int(parts[2])
                    node_indices = [int(p) for p in parts[3 + num_tags:]]
                    if elem_type in (4, 11):
                        elements[eid] = node_indices
                    elif elem_type in (2, 9):
                        surface_triangles[eid] = node_indices
                    i += 1
            i += 1

        return {
            "nodes": nodes,
            "elements": elements,
            "surface_triangles": surface_triangles,
            "num_nodes": len(nodes),
            "num_elements": len(elements)
        }
