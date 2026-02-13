import json
import os
import time
from PySide6.QtCore import QObject, Signal

class ConfigManager(QObject):
    settings_changed = Signal(dict)
    
    def __init__(self, config_dir="config"):
        super().__init__()
        self.config_dir = config_dir
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            
        self.settings_ref = os.path.join(self.config_dir, "settings.json")
        self.history_ref = os.path.join(self.config_dir, "history.json")
        
        self.settings = self._load_settings()
        self.history = self._load_history()
        
        # Performance Tracking
        self.baseline_stats = {
            "avg_temp": 0.0,
            "peak_temp": 0.0,
            "stability_score": 0.0, # Simple variance measure
            "data_points": 0
        }
        self.session_history = [] # Rolling 100 points for current session

    def update_performance_metrics(self, current_avg_temp, current_max_temp):
        # Baseline collection (first 60 points / 1 min typical)
        if self.baseline_stats["data_points"] < 60:
            n = self.baseline_stats["data_points"]
            self.baseline_stats["avg_temp"] = (self.baseline_stats["avg_temp"] * n + current_avg_temp) / (n + 1)
            self.baseline_stats["peak_temp"] = max(self.baseline_stats["peak_temp"], current_max_temp)
            self.baseline_stats["data_points"] += 1
            
        # Session history for stability tracking
        self.session_history.append(current_avg_temp)
        if len(self.session_history) > 100:
            self.session_history.pop(0)

    def get_performance_snapshot(self):
        if not self.session_history:
            return None
            
        curr_avg = sum(self.session_history) / len(self.session_history)
        curr_peak = max(self.session_history)
        
        # Improvement deltas
        temp_reduction = self.baseline_stats["avg_temp"] - curr_avg
        peak_reduction = self.baseline_stats["peak_temp"] - curr_peak
        
        return {
            "baseline_avg": self.baseline_stats["avg_temp"],
            "current_avg": curr_avg,
            "temp_reduction": max(0, temp_reduction),
            "peak_reduction": max(0, peak_reduction),
            "improvement_pct": (temp_reduction / self.baseline_stats["avg_temp"] * 100) if self.baseline_stats["avg_temp"] > 0 else 0
        }
    def _load_settings(self):
        default_settings = {
            "thresholds": {
                "safe": 70.0,
                "warm": 80.0,
                "hot": 90.0
            },
            "refresh_rate": 1000,
            "show_numeric": True,
            "show_predictions": True,
            "enable_notifications": True,
            "enable_logging": True,
            "export_path": os.getcwdb().decode()
        }
        
        if os.path.exists(self.settings_ref):
            try:
                with open(self.settings_ref, 'r') as f:
                    return {**default_settings, **json.load(f)}
            except Exception:
                return default_settings
        return default_settings

    def _load_history(self):
        if os.path.exists(self.history_ref):
            try:
                with open(self.history_ref, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_settings(self, new_settings):
        self.settings = {**self.settings, **new_settings}
        with open(self.settings_ref, 'w') as f:
            json.dump(self.settings, f, indent=4)
        self.settings_changed.emit(self.settings)

    def add_history_entry(self, decision):
        if not self.settings.get("enable_logging", True):
            return
            
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": decision.get("reason", "Unknown decision"),
            "action": decision.get("action", "NO_ACTION"),
            "pid": decision.get("pid"),
            "process_name": decision.get("process_name", "Unknown"),
            "from_core": decision.get("from_core"),
            "to_core": decision.get("to_core")
        }
        
        self.history.insert(0, entry)
        self.history = self.history[:15] # Keep last 15
        
        with open(self.history_ref, 'w') as f:
            json.dump(self.history, f, indent=4)

    def get_settings(self):
        return self.settings

    def get_history(self):
        return self.history
