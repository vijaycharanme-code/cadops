"""
CADMind CalculiX Solver Execution Service.
"""
import os, subprocess, tempfile, time
from typing import Dict, Any
from parser import CalculixParser

class CalculixSolver:
    def __init__(self, ccx_bin: str = "ccx"):
        self.ccx_bin = ccx_bin
        self.parser = CalculixParser()

    def run_simulation(self, input_deck: str, job_name: str = "job", timeout_seconds: int = 180) -> Dict[str, Any]:
        start = time.time()
        work_dir = tempfile.mkdtemp(prefix="cadmind_sim_")
        deck_path = os.path.join(work_dir, f"{job_name}.inp")
        with open(deck_path, "w") as f:
            f.write(input_deck)
        try:
            res = subprocess.run([self.ccx_bin, job_name], cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout_seconds)
            elapsed = time.time() - start
            dat_p = os.path.join(work_dir, f"{job_name}.dat")
            frd_p = os.path.join(work_dir, f"{job_name}.frd")
            return {
                "status": "success" if res.returncode == 0 else "failed",
                "returncode": res.returncode,
                "elapsed_seconds": elapsed,
                "stdout": res.stdout.decode("utf-8", errors="ignore"),
                "dat_results": self.parser.parse_dat_file(dat_p) if os.path.exists(dat_p) else {},
                "frd_results": self.parser.parse_frd_file(frd_p) if os.path.exists(frd_p) else {},
                "work_dir": work_dir
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "work_dir": work_dir}
