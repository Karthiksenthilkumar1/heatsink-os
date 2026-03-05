from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="HeatSink-OS API")

# These will be populated by the main orchestrator
state = {
    "thermal_data": {},
    "load_report": {},
    "trend_report": {},
    "predictions": {},
    "decision": {},
    "status": "Initializing"
}

@app.get("/temps")
def get_temps():
    return state["thermal_data"]

@app.get("/load")
def get_load():
    return state["load_report"]

@app.get("/trend")
def get_trend():
    return state["trend_report"]

@app.get("/decision")
def get_decision():
    return state["decision"]

@app.get("/status")
def get_status():
    return {
        "status": state["status"],
        "package_temp": state["thermal_data"].get("CPU_Package", {}).get("temperature"),
        "cooling_eff": state.get("thermal_data", {}).get("cooling_efficiency", 1.0),
        "core_fatigue": state.get("core_fatigue", {}),
        "active_decision": state["decision"].get("action"),
        "migration_mode": state.get("migration_mode", "smart")
    }

@app.get("/applications")
def get_applications():
    """Returns list of running apps with lock status."""
    return state.get("app_report", [])

@app.post("/applications/toggle/{pid}")
def toggle_app_lock(pid: int):
    """Toggles lock for a PID. Orchestrator will pick this up."""
    # We use a signal-like state change
    state["toggle_request"] = pid
    return {"status": "requested", "pid": pid}

@app.get("/mode")
def get_migration_mode():
    """Returns the current migration mode."""
    return {
        "mode": state.get("migration_mode", "smart"),
        "balancer_enabled": state.get("balancer_enabled", True),
        "available_modes": ["smart", "thermal_first", "performance_first", "conservative"]
    }

@app.post("/balancer/{status}")
def set_balancer_status(status: str):
    """Enable or disable the core balancer."""
    if status.lower() in ["on", "off"]:
        state["balancer_toggle_request"] = status.lower()
        return {"status": "requested", "target": status}
    return {"error": "Invalid status. Use 'on' or 'off'"}

@app.post("/mode/{mode}")
def set_migration_mode(mode: str):
    """Sets the migration mode. Orchestrator will apply it."""
    valid_modes = ["smart", "thermal_first", "performance_first", "conservative"]
    if mode not in valid_modes:
        return {"status": "error", "message": f"Invalid mode. Must be one of: {valid_modes}"}
    
    state["mode_change_request"] = mode
    return {"status": "requested", "mode": mode}

def start_api():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    start_api()
