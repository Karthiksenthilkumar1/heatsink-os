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
        "active_decision": state["decision"].get("action")
    }

def start_api():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    start_api()
