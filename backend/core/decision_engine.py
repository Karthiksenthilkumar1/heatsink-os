import logging

logger = logging.getLogger(__name__)

class DecisionEngine:
    """
    Combines thermal trends, current temperature, and CPU load to make migration decisions.
    """
    def __init__(self, critical_temp=85.0, safe_temp=70.0):
        self.critical_temp = critical_temp
        self.safe_temp = safe_temp
        self.last_migration_time = 0
        self.migration_cooldown = 2.0 # Wait 2 seconds between any migrations

    def decide(self, thermal_data, load_report, trend_report, predictions=None):
        """
        Decides if a migration is needed.
        """
        import time
        now = time.time()
        if now - self.last_migration_time < self.migration_cooldown:
            return {"action": "NO_ACTION", "reason": "Cooldown active"}

        cores = thermal_data.get("cores", {})
        if not cores:
            return {"action": "NO_ACTION", "reason": "No per-core thermal data"}

        hot_cores = []
        safe_cores = []

        for core_id, core_info in cores.items():
            temp = core_info["temperature"]
            trend = trend_report.get(core_id, {})
            load = load_report.get(core_id, {}).get("load_percent", 0.0)
            
            # Classification
            is_hot = temp >= self.critical_temp or trend.get("status") == "HEATING_FAST"
            is_safe = temp <= self.safe_temp and load < 30.0 # Safe core must have low load too

            if is_hot:
                hot_cores.append(core_id)
            if is_safe:
                safe_cores.append(core_id)

        if not hot_cores:
            return {"action": "NO_ACTION", "reason": "No hot cores detected"}

        if not safe_cores:
            return {"action": "NO_ACTION", "reason": "No safe cores available for migration"}

        # For simplicity, pick the first hot core and the first safe core
        from_core = hot_cores[0]
        to_core = safe_cores[0]
        
        # Get top process from hot core (using report which has global heavies)
        top_pids = load_report.get(from_core, {}).get("top_processes", [])
        if not top_pids:
            return {"action": "NO_ACTION", "reason": f"No heavy processes found on hot core {from_core}"}

        self.last_migration_time = now
        top_proc = top_pids[0]
        return {
            "action": "MIGRATE",
            "from_core": from_core,
            "to_core": to_core,
            "pid": top_proc["pid"],
            "process_name": top_proc["name"],
            "reason": f"Core {from_core} is hot ({cores[from_core]['temperature']}C), moving {top_proc['name']} to Core {to_core}"
        }

if __name__ == "__main__":
    de = DecisionEngine()
    thermal = {"cores": {0: {"temperature": 90}, 1: {"temperature": 60}}}
    load = {0: {"load_percent": 80, "top_processes": [1234]}, 1: {"load_percent": 10, "top_processes": []}}
    trends = {0: {"status": "HEATING_FAST"}, 1: {"status": "STABLE"}}
    print(de.decide(thermal, load, trends))
