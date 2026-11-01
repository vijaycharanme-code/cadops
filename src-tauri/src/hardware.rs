use serde::Serialize;
use sysinfo::System;

#[derive(Debug, Serialize, Clone)]
pub struct HardwareInfo {
    pub os: String,
    pub cpu_brand: String,
    pub cpu_cores: usize,
    pub total_memory_gb: f64,
    pub used_memory_gb: f64,
    pub gpu_detected: bool,
    pub gpu_name: String,
    pub vram_mb: Option<u64>,
    pub rtx_3050_compatible: bool,
    pub installed_tools: InstalledTools,
}

#[derive(Debug, Serialize, Clone)]
pub struct InstalledTools {
    pub openscad: bool,
    pub gmsh: bool,
    pub calculix_ccx: bool,
    pub python: bool,
}

pub fn detect_hardware() -> HardwareInfo {
    let mut sys = System::new_all();
    sys.refresh_all();

    let total_ram = sys.total_memory() as f64 / (1024.0 * 1024.0 * 1024.0);
    let used_ram = sys.used_memory() as f64 / (1024.0 * 1024.0 * 1024.0);
    let cpus = sys.cpus();
    let cpu_brand = if !cpus.is_empty() {
        cpus[0].brand().to_string()
    } else {
        "Unknown CPU".to_string()
    };
    let cpu_cores = cpus.len();

    let (gpu_detected, gpu_name, vram_mb) = detect_nvidia_gpu();
    let rtx_3050_compatible = gpu_name.to_lowercase().contains("rtx") || gpu_name.to_lowercase().contains("nvidia");

    let tools = InstalledTools {
        openscad: which::which("openscad").is_ok(),
        gmsh: which::which("gmsh").is_ok(),
        calculix_ccx: which::which("ccx").is_ok(),
        python: which::which("python3").is_ok() || which::which("python").is_ok(),
    };

    HardwareInfo {
        os: std::env::consts::OS.to_string(),
        cpu_brand,
        cpu_cores,
        total_memory_gb: (total_ram * 10.0).round() / 10.0,
        used_memory_gb: (used_ram * 10.0).round() / 10.0,
        gpu_detected,
        gpu_name,
        vram_mb,
        rtx_3050_compatible,
        installed_tools: tools,
    }
}

fn detect_nvidia_gpu() -> (bool, String, Option<u64>) {
    if which::which("nvidia-smi").is_ok() {
        if let Ok(output) = std::process::Command::new("nvidia-smi")
            .arg("--query-gpu=gpu_name,memory.total")
            .arg("--format=csv,noheader,nounits")
            .output()
        {
            if output.status.success() {
                let text = String::from_utf8_lossy(&output.stdout);
                let line = text.lines().next().unwrap_or("").trim();
                let parts: Vec<&str> = line.split(',').collect();
                if !parts.is_empty() {
                    let name = parts[0].trim().to_string();
                    let vram = if parts.len() > 1 {
                        parts[1].trim().parse::<u64>().ok()
                    } else {
                        None
                    };
                    return (true, name, vram);
                }
            }
        }
    }
    (false, "Generic / CPU fallback".to_string(), None)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_detect_hardware() {
        let hw = detect_hardware();
        assert!(hw.cpu_cores > 0);
        assert!(hw.total_memory_gb > 0.0);
    }
}
