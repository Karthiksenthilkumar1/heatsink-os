import time
from collections import deque

class ThermalTrend:
    """
    Maintains a rolling temperature history per core and computes trends.
    """
    def __init__(self, history_size=10):
        self.history_size = history_size
        self.history = {} # core_id -> deque of (timestamp, temp)

    def update(self, thermal_data):
        """
        Updates history with new thermal data and returns a trend report.
        """
        now = time.time()
        # Handle CPU_Package
        if "CPU_Package" not in self.history:
            self.history["CPU_Package"] = deque(maxlen=self.history_size)
        self.history["CPU_Package"].append((now, thermal_data["CPU_Package"]["temperature"]))

        # Handle Cores
        for core_id, core_info in thermal_data.get("cores", {}).items():
            if core_id not in self.history:
                self.history[core_id] = deque(maxlen=self.history_size)
            self.history[core_id].append((now, core_info["temperature"]))

        return self.analyze_all_trends()

    def analyze_trend(self, history):
        """
        Analyzes trend for a single core/package history.
        """
        if len(history) < 2:
            return {"delta": 0.0, "rate": 0.0, "status": "STABLE"}

        t1, temp1 = history[0]
        t2, temp2 = history[-1]
        
        delta = temp2 - temp1
        duration = t2 - t1
        rate = delta / duration if duration > 0 else 0.0
        
        status = "STABLE"
        if rate > 0.5: # More than 0.5 degrees per second
            status = "HEATING_FAST"
        elif rate > 0.1:
            status = "WARMING"
        elif rate < -0.1:
            status = "COOLING"

        return {
            "delta": delta,
            "rate": rate,
            "status": status
        }

    def analyze_all_trends(self):
        """
        Computes trends for all tracked elements.
        """
        report = {}
        for key, history in self.history.items():
            report[key] = self.analyze_trend(history)
        return report

if __name__ == "__main__":
    tt = ThermalTrend()
    # Mock data
    for i in range(5):
        data = {
            "CPU_Package": {"temperature": 50 + i*2},
            "cores": {0: {"temperature": 45 + i*3}, 1: {"temperature": 48 + i}}
        }
        print(tt.update(data))
        time.sleep(1)
