import logging

logger = logging.getLogger(__name__)

class Predictor:
    """
    Predicts future temperatures based on current trends.
    """
    def __init__(self, horizon_seconds=10):
        self.horizon_seconds = horizon_seconds

    def predict(self, trend_report):
        """
        Extrapolates current trends to predict temperatures after horizon_seconds.
        """
        predictions = {}
        for core_id, trend in trend_report.items():
            if core_id == "CPU_Package":
                # Package trend analysis might be different, but using same logic for now
                continue
                
            rate = trend.get("rate", 0.0)
            # Find the latest temperature from some state or pass it in
            # For simplicity, let's assume we return a 'delta_to_critical' or just the predicted increase
            predicted_increase = rate * self.horizon_seconds
            
            predictions[core_id] = {
                "predicted_increase": predicted_increase,
                "will_throttle": False # To be determined by decision engine comparing with current temp
            }
            
        return predictions

if __name__ == "__main__":
    predictor = Predictor()
    trends = {0: {"rate": 0.6}, 1: {"rate": 0.1}}
    print(predictor.predict(trends))
