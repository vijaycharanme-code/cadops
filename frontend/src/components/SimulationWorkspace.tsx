import React, { useState } from "react";
import { CADViewport } from "./CADViewport";

interface SimResult {
  max_displacement_mm: number;
  max_deflection_z_mm: number;
  max_von_mises_mpa: number;
  yield_strength_mpa: number;
  factor_of_safety: number;
}

export const SimulationWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"analysis" | "simready">("analysis");
  const [material, setMaterial] = useState("Aluminum 6061-T6");
  const [loadZ, setLoadZ] = useState(-100);
  const [thickness, setThickness] = useState(6.0);
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<SimResult | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [assets, setAssets] = useState<Array<{ id: string; name: string; category: string; is_cached: boolean }>>([
    { id: "IV_pole_a01", name: "IV pole a01", category: "Medical", is_cached: true },
    { id: "industrial_robot_arm", name: "Industrial Robot Arm", category: "Robotics", is_cached: false },
    { id: "xray_machine_cart", name: "XRay Machine Cart", category: "Medical", is_cached: false },
  ]);
  const [selectedAsset, setSelectedAsset] = useState<any | null>(assets[0]);

  const runSimulation = async () => {
    setIsRunning(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/simulation/structural", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          length: 60.0,
          width: 30.0,
          height: 50.0,
          thickness: thickness,
          hole_radius: 4.0,
          mesh_size: 4.0,
          load_z: loadZ,
        }),
      });
      const data = await res.json();
      if (data.results) {
        setResults(data.results);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsRunning(false);
    }
  };

  const downloadAsset = async (id: string) => {
    try {
      await fetch("http://127.0.0.1:8000/api/simready/download", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ asset_id: id }),
      });
      setAssets((prev) =>
        prev.map((a) => (a.id === id ? { ...a, is_cached: true } : a))
      );
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="flex h-full w-full bg-zinc-950 text-zinc-100">
      <div className="w-80 bg-zinc-900 border-r border-zinc-800 flex flex-col">
        <div className="flex border-b border-zinc-800">
          <button onClick={() => setActiveTab("analysis")} className={`flex-1 py-3 text-xs font-semibold uppercase tracking-wider ${activeTab === "analysis" ? "text-cyan-400 border-b-2 border-cyan-400 bg-zinc-900" : "text-zinc-400 bg-zinc-950"}`}>FEA Analysis</button>
          <button onClick={() => setActiveTab("simready")} className={`flex-1 py-3 text-xs font-semibold uppercase tracking-wider ${activeTab === "simready" ? "text-cyan-400 border-b-2 border-cyan-400 bg-zinc-900" : "text-zinc-400 bg-zinc-950"}`}>SimReady Explorer</button>
        </div>
        {activeTab === "analysis" ? (
          <div className="p-4 space-y-4 overflow-y-auto flex-1 text-xs">
            <div>
              <label className="text-zinc-400 block mb-1">Target CAD Part</label>
              <select className="w-full bg-zinc-950 border border-zinc-700 rounded p-2 text-zinc-200">
                <option>Parametric Mounting Bracket</option>
              </select>
            </div>
            <div>
              <label className="text-zinc-400 block mb-1">Material Specification</label>
              <select value={material} onChange={(e) => setMaterial(e.target.value)} className="w-full bg-zinc-950 border border-zinc-700 rounded p-2 text-zinc-200">
                <option>Aluminum 6061-T6 (E=70GPa, Sy=276MPa)</option>
                <option>Structural Steel (E=210GPa, Sy=250MPa)</option>
                <option>Titanium Ti-6Al-4V (E=114GPa, Sy=880MPa)</option>
              </select>
            </div>
            <div>
              <label className="text-zinc-400 block mb-1">Bracket Thickness (mm)</label>
              <input type="number" step="0.5" value={thickness} onChange={(e) => setThickness(Number(e.target.value))} className="w-full bg-zinc-950 border border-zinc-700 rounded p-2 text-zinc-200" />
            </div>
            <div>
              <label className="text-zinc-400 block mb-1">Applied Static Load (N)</label>
              <input type="number" value={loadZ} onChange={(e) => setLoadZ(Number(e.target.value))} className="w-full bg-zinc-950 border border-zinc-700 rounded p-2 text-zinc-200" />
            </div>
            <div>
              <label className="text-zinc-400 block mb-1">Boundary Conditions</label>
              <div className="bg-zinc-950 p-2.5 rounded border border-zinc-800 text-zinc-400 space-y-1">
                <div>• Support: Fixed base plane (Ux=Uy=Uz=0)</div>
                <div>• Load: Distributed Z-shear on upper flange</div>
                <div>• Mesh: Gmsh 3D Tetrahedral (C3D4)</div>
              </div>
            </div>
            <button onClick={runSimulation} disabled={isRunning} className="w-full py-2.5 bg-cyan-600 hover:bg-cyan-500 rounded font-semibold text-white shadow disabled:opacity-50">{isRunning ? "Solving with CalculiX..." : "Run Continuum FEA"}</button>
          </div>
        ) : (
          <div className="p-4 space-y-4 overflow-y-auto flex-1 text-xs">
            <div>
              <input type="text" placeholder="Search SimReady assets..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="w-full bg-zinc-950 border border-zinc-700 rounded p-2 text-zinc-200" />
            </div>
            <div className="space-y-2">
              {assets.map((asset) => (
                <div key={asset.id} onClick={() => setSelectedAsset(asset)} className={`p-2.5 rounded border cursor-pointer ${selectedAsset?.id === asset.id ? "bg-zinc-800 border-cyan-500" : "bg-zinc-950 border-zinc-800 hover:border-zinc-700"}`}>
                  <div className="font-semibold text-zinc-200">{asset.name}</div>
                  <div className="flex justify-between text-zinc-400 mt-1">
                    <span>{asset.category}</span>
                    <span className={asset.is_cached ? "text-emerald-400" : "text-zinc-500"}>{asset.is_cached ? "Cached" : "Online"}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      <div className="flex-1 flex flex-col">
        <div className="p-3 bg-zinc-900 border-b border-zinc-800 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-sm text-zinc-200">Simulation Viewport & Results</span>
            <span className="text-xs bg-zinc-800 px-2 py-0.5 rounded text-zinc-400">CalculiX ccx Offline Solver</span>
          </div>
        </div>
        <div className="flex-1 relative">
          <CADViewport />
          {results && (
            <div className="absolute top-4 right-4 bg-zinc-900/90 backdrop-blur border border-zinc-700 rounded-lg p-4 w-72 shadow-xl space-y-3 text-xs">
              <div className="font-bold text-zinc-100 border-b border-zinc-800 pb-2">CalculiX Real FEA Output</div>
              <div className="flex justify-between">
                <span className="text-zinc-400">Max Deflection (Z):</span>
                <span className="font-mono text-cyan-400 font-bold">{results.max_deflection_z_mm.toFixed(4)} mm</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-400">Peak Von Mises:</span>
                <span className="font-mono text-amber-400 font-bold">{results.max_von_mises_mpa.toFixed(2)} MPa</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-400">Yield Strength (Sy):</span>
                <span className="font-mono text-zinc-300">{results.yield_strength_mpa} MPa</span>
              </div>
              <div className="flex justify-between border-t border-zinc-800 pt-2">
                <span className="text-zinc-400">Factor of Safety (FoS):</span>
                <span className={`font-mono font-bold ${results.factor_of_safety >= 1.5 ? "text-emerald-400" : "text-rose-400"}`}>{results.factor_of_safety}</span>
              </div>
              <div className="text-zinc-500 text-[10px] italic">Verified Continuum Mechanics Solution (Offline Gmsh + ccx)</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
