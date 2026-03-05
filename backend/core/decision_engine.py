import logging

logger = logging.getLogger(__name__)

class DecisionEngine:
    """
    Combines thermal trends, current temperature, and CPU load to make migration decisions.
    """
    def __init__(self, critical_temp=90.0, warm_temp=75.0):
        self.critical_temp = critical_temp
        self.warm_temp = warm_temp
        self.last_migration_time = 0
        self.migration_cooldown = 3.0 # Increased for stability
        
        # Stability & Guard State
        self.core_fatigue = {} # core_id -> fatigue_score (time spent hot)
        self.process_affinity = {} # pid -> last_core (to penalize thrashing)
        self.last_tick_time = 0

    def calculate_core_composite_score(self, core_id, core_info, load_metric, trend, package_temp, cooling_eff):
        """
        Calculates a 'risk score' for a core. Higher = more urgent to migrate AWAY.
        """
        temp = core_info["temperature"]
        load = load_metric["load_percent"]
        trend_rate = trend.get("rate", 0.0)
        is_throttled = load_metric.get("is_throttled", False)
        
        # 1. Thermal Risk (Primary)
        # Base score from temperature relative to 90C
        thermal_score = (temp / self.critical_temp) * 50
        
        # 2. Proactive Load Risk (Leading indicator)
        # High load + rising trend amplifies score
        load_risk = (load / 100.0) * 20
        if trend_rate > 0.3:
            load_risk *= 1.5
            
        # 3. Efficiency Risk
        efficiency_penalty = 15 if is_throttled else 0
        
        # 4. Global Pressure
        # If package is hot, every core is at higher risk
        global_factor = (package_temp / 85.0) * 10
        
        # 5. Core Fatigue (Thermal Load history)
        fatigue = self.core_fatigue.get(core_id, 0) * 5
        
        return thermal_score + load_risk + efficiency_penalty + global_factor + fatigue

    def decide(self, thermal_data, load_report, trend_report, predictions=None, locked_names=None):
        """
        Makes a unified migration decision based on a composite multi-metric score.
        """
        import time
        import random
        now = time.time()
        locked_names = locked_names or set()
        dt = now - self.last_tick_time if self.last_tick_time > 0 else 0
        self.last_tick_time = now
        
        if now - self.last_migration_time < self.migration_cooldown:
            return {"action": "NO_ACTION", "reason": "System stabilizing..."}

        cores = thermal_data.get("cores", {})
        package_temp = thermal_data.get("CPU_Package", {}).get("temperature", 50.0)
        cooling_eff = thermal_data.get("cooling_efficiency", 1.0)
        
        if not cores:
            return {"action": "NO_ACTION", "reason": "No sensor data"}

        # Update Fatigue Tracking
        for cid, info in cores.items():
            if info["temperature"] > self.warm_temp:
                self.core_fatigue[cid] = min(10, self.core_fatigue.get(cid, 0) + dt)
            else:
                self.core_fatigue[cid] = max(0, self.core_fatigue.get(cid, 0) - dt)

        # 1. Score all cores for risk
        core_scores = {}
        for cid, info in cores.items():
            load_metric = load_report.get(cid, {"load_percent": 0.0})
            trend = trend_report.get(cid, {})
            core_scores[cid] = self.calculate_core_composite_score(cid, info, load_metric, trend, package_temp, cooling_eff)

        # 2. Identify migration candidates (Source Cores with high risk)
        # Proactive threshold: 65. Reactive/Critical: 85.
        source_candidates = [cid for cid, score in core_scores.items() if score > 60]
        
        if not source_candidates:
            return {"action": "NO_ACTION", "reason": "Thermal conditions optimal"}

        # Pick one source randomly from top risky cores
        source_candidates.sort(key=lambda x: core_scores[x], reverse=True)
        from_core = source_candidates[0] # Pick the riskiest
        
        top_procs = load_report.get(from_core, {}).get("top_processes", [])
        if not top_procs:
            return {"action": "NO_ACTION", "reason": "No migratable threads on high-risk core"}
        
        # Filter target process (Avoid background if CPU-bound exists)
        # NEW: Filter out locked processes by name
        target_proc = None
        for p in top_procs:
            if p.get("name") in locked_names:
                continue
            
            if not target_proc or p.get("type") == "CPU-BOUND":
                target_proc = p
                if p.get("type") == "CPU-BOUND": break

        if not target_proc:
            return {"action": "NO_ACTION", "reason": f"Core {from_core} is hot, but all heavy processes are LOCKED by user."}

        # Stability Guard: Affinity Penalty (Minimum time on core before re-migration)
        # Avoid "hovering" migrations
        last_move_time = self.process_affinity.get(target_proc["pid"], {}).get("timestamp", 0)
        if now - last_move_time < 10.0: # 10 second process-level cooldown
            return {"action": "NO_ACTION", "reason": f"Stability Guard: {target_proc['name']} recently moved"}

        # 3. Find optimal destination (Lowest risk)
        dest_candidates = []
        for cid, score in core_scores.items():
            if cid == from_core: continue
            # Only consider cores with significantly lower risk
            if score < (core_scores[from_core] - 20):
                dest_candidates.append((cid, score))
        
        if not dest_candidates:
            return {"action": "NO_ACTION", "reason": "Global thermal saturation (No cooler core available)"}
            
        dest_candidates.sort(key=lambda x: x[1]) # Lowest score first
        to_core = dest_candidates[0][0]

        # Final Decision
        self.last_migration_time = now
        self.process_affinity[target_proc["pid"]] = {"core": to_core, "timestamp": now}
        
        reason_type = "Proactive" if core_scores[from_core] < 80 else "Reactive (Hot)"
        selection_reason = f"{reason_type} Balancing: Score {core_scores[from_core]:.1f} -> {core_scores[to_core]:.1f}"
        
        return {
            "action": "MIGRATE",
            "from_core": from_core,
            "to_core": to_core,
            "pid": target_proc["pid"],
            "process_name": target_proc["name"],
            "selection_reason": selection_reason,
            "reason": f"{reason_type} migration of {target_proc['name']} to Core {to_core} to prevent hotspot development."
        }

if __name__ == "__main__":
    de = DecisionEngine()
    thermal = {"cores": {0: {"temperature": 90}, 1: {"temperature": 60}}}
    load = {0: {"load_percent": 80, "top_processes": [1234]}, 1: {"load_percent": 10, "top_processes": []}}
    trends = {0: {"status": "HEATING_FAST"}, 1: {"status": "STABLE"}}
    print(de.decide(thermal, load, trends))
