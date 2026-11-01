"""
CADMind CalculiX Result Parser.
"""
import os, math
from typing import Dict, Tuple, Any

class CalculixParser:
    def parse_dat_file(self, dat_path: str) -> Dict[str, Any]:
        if not os.path.exists(dat_path):
            return {"error": f"File not found: {dat_path}"}
        displacements: Dict[int, Tuple[float, float, float, float]] = {}
        stresses: Dict[int, float] = {}
        curr = None
        with open(dat_path, "r", errors="ignore") as f:
            for line in f:
                sline = line.strip()
                if not sline: continue
                if "displacements" in sline.lower(): curr = "DISP"; continue
                elif "stresses" in sline.lower() and "elem" in sline.lower(): curr = "STRESS"; continue
                if curr == "DISP":
                    parts = sline.split()
                    if len(parts) >= 4:
                        try:
                            nid = int(parts[0])
                            ux, uy, uz = float(parts[1]), float(parts[2]), float(parts[3])
                            displacements[nid] = (ux, uy, uz, math.sqrt(ux*ux + uy*uy + uz*uz))
                        except ValueError: pass
                elif curr == "STRESS":
                    parts = sline.split()
                    if len(parts) >= 8:
                        try:
                            eid = int(parts[0])
                            sxx, syy, szz = float(parts[2]), float(parts[3]), float(parts[4])
                            sxy, syz, szx = float(parts[5]), float(parts[6]), float(parts[7])
                            vm = math.sqrt(0.5 * ((sxx - syy)**2 + (syy - szz)**2 + (szz - sxx)**2 + 6.0 * (sxy**2 + syz**2 + szx**2)))
                            if eid not in stresses or vm > stresses[eid]: stresses[eid] = vm
                        except ValueError: pass
        max_d = max((d[3] for d in displacements.values()), default=0.0)
        max_s = max(stresses.values(), default=0.0)
        return {
            "displacements": displacements, "stresses": stresses,
            "max_displacement": max_d, "max_stress": max_s,
            "num_disp_nodes": len(displacements)
        }

    def parse_frd_file(self, frd_path: str) -> Dict[str, Any]:
        if not os.path.exists(frd_path): return {"error": "FRD not found"}
        disps: Dict[int, Tuple[float, float, float, float]] = {}
        temps: Dict[int, float] = {}
        with open(frd_path, "r", errors="ignore") as f:
            lines = f.readlines()
        i = 0
        n = len(lines)
        while i < n:
            line = lines[i]
            if line.startswith(" -4  DISP"):
                i += 1
                while i < n and not lines[i].startswith(" -3"):
                    dl = lines[i]
                    if dl.startswith(" -1") or dl.startswith(" -2"):
                        p = dl.split()
                        if len(p) >= 5:
                            try:
                                nid = int(p[1])
                                ux, uy, uz = float(p[2]), float(p[3]), float(p[4])
                                disps[nid] = (ux, uy, uz, math.sqrt(ux*ux + uy*uy + uz*uz))
                            except ValueError: pass
                    i += 1
            elif line.startswith(" -4  NDTEMP") or line.startswith(" -4  TEMP"):
                i += 1
                while i < n and not lines[i].startswith(" -3"):
                    tl = lines[i]
                    if tl.startswith(" -1") or tl.startswith(" -2"):
                        p = tl.split()
                        if len(p) >= 3:
                            try:
                                nid = int(p[1])
                                temps[nid] = float(p[2])
                            except ValueError: pass
                    i += 1
            i += 1
        return {"displacements": disps, "temperatures": temps}
