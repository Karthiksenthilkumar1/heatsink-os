import psutil
import logging
import json
import os

logger = logging.getLogger(__name__)

class ProcessMonitor:
    """
    Identifies top CPU-consuming processes and maps them to core load.
    """
    def __init__(self, top_n=5):
        self.top_n = top_n
        self.locked_file = os.path.join(os.path.dirname(__file__), "locked_apps.json")
        self.locked_names = set() # Process names the user has locked
        self._load_locked_apps()

    def _load_locked_apps(self):
        try:
            if os.path.exists(self.locked_file):
                with open(self.locked_file, 'r') as f:
                    data = json.load(f)
                    # We now store and load process names instead of PIDs
                    self.locked_names = set(data.get("locked_names", []))
                logger.info(f"Loaded {len(self.locked_names)} locked applications from disk.")
        except Exception as e:
            logger.error(f"Failed to load locked_apps.json: {e}")

    def _save_locked_apps(self):
        try:
            with open(self.locked_file, 'w') as f:
                json.dump({"locked_names": list(self.locked_names)}, f)
        except Exception as e:
            logger.error(f"Failed to save locked_apps.json: {e}")

    def toggle_lock(self, pid):
        """
        Toggles migration lock for a specific PID (resolves to name for persistence).
        """
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            
            if name in self.locked_names:
                self.locked_names.remove(name)
                locked = False
            else:
                self.locked_names.add(name)
                locked = True
            
            self._save_locked_apps()
            return locked
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            logger.warning(f"Could not toggle lock for PID {pid}: Process not found or access denied")
            return False

    def get_eligibility_report(self):
        """
        Returns a list of all migratable processes with their lock status.
        Expanded to show all system apps.
        """
        apps = []
        # We look at more processes now for the comprehensive list
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                pid = proc.info['pid']
                if pid <= 4: continue # Skip System Idle and System
                
                name = proc.info['name']
                if not name: continue
                
                # Filter out obvious system noise if needed, but keep it broad
                if name.lower() in ["conhost.exe", "svchost.exe", "runtimebroker.exe"]:
                    continue

                apps.append({
                    "pid": pid,
                    "name": name,
                    "is_locked": name in self.locked_names,
                    "cpu": proc.info['cpu_percent'] or 0.0,
                    "status": "Running"
                })
            except (psutil.NoSuchProcess, psutil.ZombieProcess):
                pass
            except psutil.AccessDenied:
                # Still show the app if we have the name, mark as Restricted
                if proc.info.get('name'):
                    apps.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "is_locked": proc.info['name'] in self.locked_names,
                        "cpu": 0.0,
                        "status": "Restricted"
                    })
        
        # Sort: Locked first, then by CPU, then by Name
        apps.sort(key=lambda x: (x['is_locked'], x['cpu'], x['name']), reverse=True)
        return apps[:100] # Expanded to show more apps

    def get_core_metrics(self):
        """
        Returns per-core load, frequency, and throttling state.
        """
        loads = psutil.cpu_percent(interval=None, percpu=True)
        freqs = psutil.cpu_freq(percpu=True)
        
        metrics = []
        for i, load in enumerate(loads):
            current_f = freqs[i].current if len(freqs) > i else 0
            max_f = freqs[i].max if len(freqs) > i else 1
            
            # Detect throttling
            is_throttled = current_f < (max_f * 0.9) and load > 80.0
            
            # Simple Power Estimation: Load * Freq coefficient
            # Higher freq + higher load = higher heat dissipation
            power_est = (load / 100.0) * (current_f / max_f) * 15.0 # Watts approx per core
            
            metrics.append({
                "load": load,
                "frequency": current_f,
                "is_throttled": is_throttled,
                "power_estimate": power_est
            })
        return metrics

    def get_top_processes(self):
        """
        Identifies the top N CPU-consuming processes with classification.
        """
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'num_threads']):
            try:
                if proc.info['pid'] <= 4: continue
                if proc.info['cpu_percent'] is None: continue
                
                # Classification logic
                p_type = "BACKGROUND"
                if proc.info['cpu_percent'] > 40:
                    p_type = "CPU-BOUND"
                elif proc.info['cpu_percent'] > 10:
                    p_type = "INTERACTIVE"
                
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "cpu_percent": proc.info['cpu_percent'],
                    "type": p_type
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return processes[:self.top_n]

    def get_load_report(self):
        """
        Provides structured load data per core and top processes.
        """
        core_metrics = self.get_core_metrics()
        top_procs = self.get_top_processes()
        
        report = {}
        for i, metric in enumerate(core_metrics):
            report[i] = {
                "load_percent": metric["load"],
                "frequency": metric["frequency"],
                "is_throttled": metric["is_throttled"],
                "power_watts": metric["power_estimate"],
                "top_processes": top_procs # Still global for target selection
            }
        
        return report

if __name__ == "__main__":
    monitor = ProcessMonitor()
    import time
    # Initialize psutil counters
    psutil.cpu_percent(interval=0.1, percpu=True)
    while True:
        print(monitor.get_load_report())
        time.sleep(1)
