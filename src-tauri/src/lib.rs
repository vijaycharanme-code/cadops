pub mod ai_engine;
pub mod hardware;
pub mod process;

use ai_engine::{AIResponse, explain_simulation_results, process_natural_language_prompt};
use hardware::{detect_hardware, HardwareInfo};
use process::ProcessSupervisor;
use std::sync::Arc;

pub struct AppState {
    pub supervisor: Arc<ProcessSupervisor>,
}

#[tauri::command]
fn get_system_hardware() -> HardwareInfo {
    detect_hardware()
}

#[tauri::command]
fn prompt_llama(prompt: String) -> AIResponse {
    process_natural_language_prompt(&prompt)
}

#[tauri::command]
fn explain_fea_results(max_disp_mm: f64, max_stress_mpa: f64, yield_strength: f64) -> String {
    explain_simulation_results(max_disp_mm, max_stress_mpa, yield_strength)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let supervisor = Arc::new(ProcessSupervisor::new());
    let _ = supervisor.start_sim_service();

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .manage(AppState { supervisor })
        .invoke_handler(tauri::generate_handler![
            get_system_hardware,
            prompt_llama,
            explain_fea_results
        ])
        .run(tauri::generate_context!())
        .expect("error while running CADMind desktop application");
}
