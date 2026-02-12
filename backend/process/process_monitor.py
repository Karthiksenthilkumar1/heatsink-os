import psutil
import logging

logger = logging.getLogger(__name__)

class ProcessMonitor:
    """
    Identifies top CPU-consuming processes and maps them to core load.
    """
    def __init__(self, top_n=5):
        self.top_n = top_n

    def get_core_load(self):
        """
        Returns CPU load per core.
        """
        return psutil.cpu_percent(interval=None, percpu=True)

    def get_top_processes(self):
        """
        Identifies the top N CPU-consuming processes.
        """
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                # Filter out system-critical processes and Idle process (PID 0)
                if proc.info['pid'] <= 4:
                    continue
                if proc.info['cpu_percent'] is None:
                    continue
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Sort by cpu_percent
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return processes[:self.top_n]

    def get_load_report(self):
        """
        Provides structured load data per core and top processes.
        """
        core_loads = self.get_core_load()
        top_procs = self.get_top_processes()
        
        report = {}
        # Format top processes as a list of dicts with name and pid
        process_metadata = [{"pid": p['pid'], "name": p['name']} for p in top_procs]
        
        for i, load in enumerate(core_loads):
            report[i] = {
                "load_percent": load,
                "top_processes": process_metadata # Showing global heavies with names
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
