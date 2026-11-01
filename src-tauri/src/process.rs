use std::process::{Child, Command};
use std::sync::Mutex;

pub struct ProcessSupervisor {
    child: Mutex<Option<Child>>,
}

impl ProcessSupervisor {
    pub fn new() -> Self {
        Self {
            child: Mutex::new(None),
        }
    }

    pub fn start_sim_service(&self) -> Result<String, String> {
        let mut lock = self.child.lock().unwrap();
        if lock.is_some() {
            return Ok("Service already running".to_string());
        }

        let py_bin = if which::which("python3").is_ok() {
            "python3"
        } else {
            "python"
        };

        match Command::new(py_bin)
            .arg("backend-sim/server.py")
            .arg("8000")
            .spawn()
        {
            Ok(child) => {
                *lock = Some(child);
                Ok("Simulation backend service started on port 8000".to_string())
            }
            Err(e) => Err(format!("Failed to start backend service: {}", e)),
        }
    }

    pub fn stop_sim_service(&self) {
        let mut lock = self.child.lock().unwrap();
        if let Some(mut child) = lock.take() {
            let _ = child.kill();
        }
    }
}

impl Drop for ProcessSupervisor {
    fn drop(&mut self) {
        self.stop_sim_service();
    }
}
