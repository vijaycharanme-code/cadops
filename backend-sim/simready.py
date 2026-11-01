"""
NVIDIA SimReady Asset Client.
"""
import os, json, shutil, urllib.request, urllib.parse
from typing import List, Dict, Any, Optional

HF_API_BASE = "https://huggingface.co/api/datasets/nvidia/simready-assets"
HF_RAW_BASE = "https://huggingface.co/datasets/nvidia/simready-assets/raw/main"

class SimReadyClient:
    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir is None:
            cache_dir = os.path.join(os.path.dirname(__file__), "cache", "simready")
        self.cache_dir = os.path.abspath(cache_dir)
        os.makedirs(self.cache_dir, exist_ok=True)
        self.index_file = os.path.join(self.cache_dir, "cached_index.json")

    def search_online(self, query: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        try:
            req = urllib.request.Request(f"{HF_API_BASE}/tree/main", headers={"User-Agent": "CADMind/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            results = []
            cached_ids = set(self.list_cached().keys())
            q = query.strip().lower()
            for item in data:
                path = item.get("path", "")
                if "/" in path: continue
                if q and q not in path.lower(): continue
                cat = "General"
                if any(k in path.lower() for k in ["pole", "medical", "xray", "ct_"]): cat = "Medical"
                elif any(k in path.lower() for k in ["robot", "arm"]): cat = "Robotics"
                results.append({
                    "id": path, "name": path.replace("_", " "),
                    "category": cat, "path": path, "is_cached": path in cached_ids
                })
                if len(results) >= limit: break
            return results
        except Exception:
            return list(self.list_cached().values())

    def get_asset_package_details(self, asset_id: str) -> Dict[str, Any]:
        local_p = os.path.join(self.cache_dir, asset_id, "com.nvidia.simready.packaging.json")
        if os.path.exists(local_p):
            with open(local_p, "r") as f: return {"id": asset_id, "is_cached": True, "metadata": json.load(f)}
        try:
            url = f"{HF_RAW_BASE}/{urllib.parse.quote(asset_id)}/com.nvidia.simready.packaging.json"
            req = urllib.request.Request(url, headers={"User-Agent": "CADMind/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                return {"id": asset_id, "is_cached": False, "metadata": json.loads(resp.read().decode())}
        except Exception as e:
            return {"id": asset_id, "is_cached": False, "error": str(e)}

    def download_asset(self, asset_id: str) -> Dict[str, Any]:
        target = os.path.join(self.cache_dir, asset_id)
        os.makedirs(target, exist_ok=True)
        dest = os.path.join(target, "com.nvidia.simready.packaging.json")
        try:
            url = f"{HF_RAW_BASE}/{urllib.parse.quote(asset_id)}/com.nvidia.simready.packaging.json"
            req = urllib.request.Request(url, headers={"User-Agent": "CADMind/1.0"})
            with urllib.request.urlopen(req, timeout=20) as resp, open(dest, "wb") as f:
                f.write(resp.read())
            with open(dest, "r") as f: meta = json.load(f)
            cached = self.list_cached()
            cached[asset_id] = {"id": asset_id, "name": asset_id.replace("_", " "), "metadata": meta}
            with open(self.index_file, "w") as f: json.dump(cached, f, indent=2)
            return {"status": "success", "asset_id": asset_id, "local_path": target}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def list_cached(self) -> Dict[str, Any]:
        if not os.path.exists(self.index_file): return {}
        try:
            with open(self.index_file, "r") as f: return json.load(f)
        except Exception: return {}

    def remove_from_cache(self, asset_id: str) -> bool:
        shutil.rmtree(os.path.join(self.cache_dir, asset_id), ignore_errors=True)
        cached = self.list_cached()
        if asset_id in cached:
            del cached[asset_id]
            with open(self.index_file, "w") as f: json.dump(cached, f, indent=2)
        return True
