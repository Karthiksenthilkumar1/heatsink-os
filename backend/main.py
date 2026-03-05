import time
import logging
import threading
import psutil
from sensors.thermal_reader import ThermalSensor
# Relative imports might be tricky depending on how it's run, using absolute-ish paths
from process.process_monitor import ProcessMonitor
from core.thermal_trend import ThermalTrend
from core.decision_engine import DecisionEngine
from core.predictor import Predictor
from core.migration_mode import MigrationModeFilter
from process.migrator import Migrator
from api.server import state, app
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("HeatSink-OS")

class HeatSinkOrchestrator:
    def __init__(self):
        self.sensor = ThermalSensor()
        self.monitor = ProcessMonitor()
        self.trend = ThermalTrend()
        self.decision_engine = DecisionEngine()
        self.predictor = Predictor()
        self.mode_filter = MigrationModeFilter(mode="smart")  # Default to Smart mode
        self.migrator = Migrator()
        self.balancer_enabled = True # Default ON
        self.running = True

    def start_api_thread(self):
        api_thread = threading.Thread(target=lambda: uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error"), daemon=True)
        api_thread.start()
        logger.info("API server started in background thread on http://127.0.0.1:8000")

    def run_loop(self):
        logger.info("Starting HeatSink-OS main control loop...")
        state["status"] = "Running"
        
        # Initialize psutil counters
        psutil.cpu_percent(interval=None, percpu=True)
        
        while self.running:
            try:
                # 1. Read sensors
                thermal_data = self.sensor.get_thermal_data()
                
                # 2. Monitor load
                load_report = self.monitor.get_load_report()
                
                # 3. Analyze trends
                trend_report = self.trend.update(thermal_data)
                
                # 4. Predict
                predictions = self.predictor.predict(trend_report)
                
                # Update Eligibility State
                if state.get("toggle_request"):
                    pid = state.pop("toggle_request")
                    self.monitor.toggle_lock(pid)
                    
                state["app_report"] = self.monitor.get_eligibility_report()
                
                # Handle mode change requests
                if state.get("mode_change_request"):
                    new_mode = state.pop("mode_change_request")
                    self.mode_filter.set_mode(new_mode)
                
                # 5. Decide (Pass locked_names)
                decision = self.decision_engine.decide(
                    thermal_data, 
                    load_report, 
                    trend_report, 
                    predictions,
                    locked_names=self.monitor.locked_names
                )
                
                # Apply migration mode filter (non-invasive refinement layer)
                decision = self.mode_filter.apply(decision, 
                                                 core_scores=getattr(self.decision_engine, 'core_scores', None),
                                                 thermal_data=thermal_data)
                
                # Toggle Core Balancer State
                # Use pop(key, None) for thread safety (atomic-ish)
                req = state.pop("balancer_toggle_request", None)
                if req:
                    self.balancer_enabled = (req == "on")
                    logger.info(f"Core Balancer {'enabled' if self.balancer_enabled else 'disabled'} by user")
                
                # Update global state for API
                state["thermal_data"] = thermal_data
                state["load_report"] = load_report
                state["trend_report"] = trend_report
                state["predictions"] = predictions
                state["decision"] = decision
                state["migration_mode"] = self.mode_filter.get_mode()
                state["balancer_enabled"] = self.balancer_enabled
                
                # Expose core fatigue for UI
                state["core_fatigue"] = self.decision_engine.core_fatigue
                
                # 6. Apply migration if needed (HARD GATED)
                if decision["action"] == "MIGRATE":
                    if self.balancer_enabled:
                        self.migrator.migrate(decision["pid"], decision["to_core"])
                    else:
                        logger.info("Migration skipped: Core Balancer OFF")

            except Exception as e:
                import traceback
                logger.error(f"Error in control loop: {e}\n{traceback.format_exc()}")
                state["status"] = f"Error: {e}"
            
            time.sleep(0.5)

    def stop(self):
        self.running = False
        state["status"] = "Stopped"

if __name__ == "__main__":
    orchestrator = HeatSinkOrchestrator()
    orchestrator.start_api_thread()
    try:
        orchestrator.run_loop()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        orchestrator.stop()