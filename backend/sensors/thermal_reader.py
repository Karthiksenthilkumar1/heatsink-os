try:
    import wmi
except ImportError:
    wmi = None
import time
import logging
import psutil
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ThermalSensor:
    """
    Acts as a pure data provider for CPU thermal information using WMI.
    """
    def __init__(self):
        try:
            self.w = wmi.WMI(namespace="root\\wmi")
        except Exception as e:
            logger.error(f"Failed to initialize WMI: {e}")
            self.w = None

    def get_thermal_data(self):
        """
        Reads per-core or package temperatures from WMI.
        Returns data in structured format.
        """
        data = {
            "CPU_Package": {
                "temperature": 0.0,
                "unit": "C",
                "source": "WMI",
                "timestamp": time.time()
            },
            "cores": {}
        }

        if not self.w:
            # Fallback to simulation immediately
            pass
        else:
            try:
                # MSAcpi_ThermalZoneTemperature is a common class for thermal data
                # Temperature is usually in decikelvins (T * 10 + 2732)
                thermal_zones = self.w.MSAcpi_ThermalZoneTemperature()
                if thermal_zones:
                    # Use the first zone as package temperature for now
                    temp_dk = thermal_zones[0].CurrentTemperature
                    temp_c = (temp_dk - 2732) / 10.0
                    data["CPU_Package"]["temperature"] = temp_c
                    
                    # Some systems expose multiple zones or instances for cores
                    for i, zone in enumerate(thermal_zones):
                        z_temp = (zone.CurrentTemperature - 2732) / 10.0
                        data["cores"][i] = {
                            "temperature": z_temp,
                            "unit": "C",
                            "timestamp": time.time()
                        }
                else:
                    raise Exception("No thermal zones found")
            except Exception as e:
                # Log error and fall through to simulation
                if not hasattr(self, '_wmi_error_logged'):
                   logger.warning(f"WMI Access Denied or No Zones. Detail: {e}")
                   self._wmi_error_logged = True
            
        # SIMULATION FALLBACK if data["cores"] is empty (meaning WMI failed or wasn't present)
        if not data["cores"]:
            import random
            data["CPU_Package"]["temperature"] = 65.0 + random.uniform(-1, 5)
            data["CPU_Package"]["source"] = "SIMULATED"
            for i in range(psutil.cpu_count()):
                data["cores"][i] = {
                    "temperature": 60.0 + random.uniform(-2, 10),
                    "unit": "C",
                    "timestamp": time.time()
                }
            
        return data

if __name__ == "__main__":
    sensor = ThermalSensor()
    while True:
        print(sensor.get_thermal_data())
        time.sleep(1)
