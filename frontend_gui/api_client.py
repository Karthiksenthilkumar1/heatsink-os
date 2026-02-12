import requests
import logging

logger = logging.getLogger(__name__)

class HeatSinkAPIClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url

    def _get(self, endpoint):
        try:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=2)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API Error ({endpoint}): {e}")
            return None

    def get_status(self):
        return self._get("/status")

    def get_temps(self):
        return self._get("/temps")

    def get_load(self):
        return self._get("/load")

    def get_trend(self):
        return self._get("/trend")

    def get_decision(self):
        return self._get("/decision")
