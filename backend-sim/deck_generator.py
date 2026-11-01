"""
CADMind CalculiX Deck Generator.
"""
from typing import Dict, List, Tuple, Any

class CalculixDeckGenerator:
    def generate_structural_deck(
        self,
        nodes: Dict[int, Tuple[float, float, float]],
        elements: Dict[int, List[int]],
        material: Dict[str, Any],
        fixed_node_ids: List[int],
        loaded_nodes: List[int],
        total_force: Tuple[float, float, float],
        order: int = 1,
        title: str = "CADMind Structural FEA"
    ) -> str:
        elem_type = "C3D4" if order == 1 else "C3D10"
        youngs_modulus = material.get("youngs_modulus", 70000.0)
        poissons_ratio = material.get("poissons_ratio", 0.33)
        density = material.get("density", 2.7e-9)

        lines = [f"** {title}", "*HEADING", f" {title}", "*NODE, NSET=NALL"]
        for nid, (x, y, z) in nodes.items():
            lines.append(f"{nid}, {x:.6f}, {y:.6f}, {z:.6f}")

        lines.append(f"*ELEMENT, TYPE={elem_type}, ELSET=EALL")
        for eid, nids in elements.items():
            lines.append(f"{eid}, " + ", ".join(str(n) for n in nids))

        if fixed_node_ids:
            lines.append("*NSET, NSET=NFIX")
            for i in range(0, len(fixed_node_ids), 10):
                lines.append(", ".join(str(n) for n in fixed_node_ids[i:i+10]))

        if loaded_nodes:
            lines.append("*NSET, NSET=NLOAD")
            for i in range(0, len(loaded_nodes), 10):
                lines.append(", ".join(str(n) for n in loaded_nodes[i:i+10]))

        lines.append("*MATERIAL, NAME=ALUMINUM")
        lines.append("*ELASTIC")
        lines.append(f"{youngs_modulus:.1f}, {poissons_ratio:.4f}")
        lines.append("*DENSITY")
        lines.append(f"{density:.6e}")
        lines.append("*SOLID SECTION, ELSET=EALL, MATERIAL=ALUMINUM")
        lines.append("*STEP")
        lines.append("*STATIC")

        if fixed_node_ids:
            lines.append("*BOUNDARY")
            lines.append("NFIX, 1, 3, 0.0")

        if loaded_nodes and (total_force[0] != 0 or total_force[1] != 0 or total_force[2] != 0):
            num = len(loaded_nodes)
            fx, fy, fz = total_force[0] / num, total_force[1] / num, total_force[2] / num
            lines.append("*CLOAD")
            for nid in loaded_nodes:
                if fx != 0: lines.append(f"{nid}, 1, {fx:.6f}")
                if fy != 0: lines.append(f"{nid}, 2, {fy:.6f}")
                if fz != 0: lines.append(f"{nid}, 3, {fz:.6f}")

        lines.append("*NODE PRINT, NSET=NALL")
        lines.append("U")
        lines.append("*EL PRINT, ELSET=EALL")
        lines.append("S")
        lines.append("*NODE FILE")
        lines.append("U")
        lines.append("*EL FILE")
        lines.append("S")
        lines.append("*END STEP")
        return "\n".join(lines) + "\n"

    def generate_thermal_deck(
        self,
        nodes: Dict[int, Tuple[float, float, float]],
        elements: Dict[int, List[int]],
        conductivity: float,
        specific_heat: float,
        fixed_temp_nodes: List[int],
        fixed_temp_value: float,
        heat_flux_nodes: List[int],
        heat_flux_value: float,
        title: str = "CADMind Thermal FEA"
    ) -> str:
        lines = [f"** {title}", "*HEADING", f" {title}", "*NODE, NSET=NALL"]
        for nid, (x, y, z) in nodes.items():
            lines.append(f"{nid}, {x:.6f}, {y:.6f}, {z:.6f}")
        lines.append("*ELEMENT, TYPE=C3D4, ELSET=EALL")
        for eid, nids in elements.items():
            lines.append(f"{eid}, " + ", ".join(str(n) for n in nids))
        if fixed_temp_nodes:
            lines.append("*NSET, NSET=NTEMP1")
            for i in range(0, len(fixed_temp_nodes), 10):
                lines.append(", ".join(str(n) for n in fixed_temp_nodes[i:i+10]))
        lines.append("*MATERIAL, NAME=THERMAL_MAT")
        lines.append("*CONDUCTIVITY")
        lines.append(f"{conductivity:.6f}")
        lines.append("*SPECIFIC HEAT")
        lines.append(f"{specific_heat:.6f}")
        lines.append("*SOLID SECTION, ELSET=EALL, MATERIAL=THERMAL_MAT")
        lines.append("*STEP")
        lines.append("*HEAT TRANSFER, STEADY STATE")
        if fixed_temp_nodes:
            lines.append("*BOUNDARY")
            lines.append(f"NTEMP1, 11, 11, {fixed_temp_value:.2f}")
        lines.append("*NODE PRINT, NSET=NALL")
        lines.append("NT")
        lines.append("*NODE FILE")
        lines.append("NT")
        lines.append("*END STEP")
        return "\n".join(lines) + "\n"
