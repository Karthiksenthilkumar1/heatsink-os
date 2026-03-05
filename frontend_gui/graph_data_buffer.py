import logging
import time
from collections import deque
from typing import Optional

logger = logging.getLogger(__name__)

class GraphDataBuffer:
    """
    Non-intrusive data observer layer for thermal graph.
    Validates, buffers, and normalizes temperature data without modifying existing logic.
    """
    
    def __init__(self, buffer_size: int = 60, valid_range: tuple = (0.0, 120.0)):
        """
        Initialize the graph data buffer.
        
        Args:
            buffer_size: Maximum number of data points to retain
            valid_range: (min, max) valid temperature range in Celsius
        """
        self.buffer = deque(maxlen=buffer_size)
        self.valid_range = valid_range
        self.last_valid_value: Optional[float] = None
        self.last_update_time: float = 0
        self._debug_enabled = False
        
        # Enable debug logging if environment variable is set
        import os
        if os.getenv('HEATSINK_DEBUG', '0') == '1':
            self._debug_enabled = True
            logger.setLevel(logging.DEBUG)
    
    def observe(self, temperature_value: Optional[float]) -> Optional[float]:
        """
        Observe and validate incoming temperature data.
        
        Args:
            temperature_value: Raw temperature value from API
            
        Returns:
            Validated temperature value or last known valid value
        """
        current_time = time.time()
        
        # Validate incoming data
        if temperature_value is None:
            if self._debug_enabled:
                logger.debug("Buffer received None value, using last valid")
            return self._get_fallback_value()
        
        # Check if value is in valid range
        if not (self.valid_range[0] <= temperature_value <= self.valid_range[1]):
            if self._debug_enabled:
                logger.warning(f"Temperature {temperature_value}°C out of valid range {self.valid_range}")
            return self._get_fallback_value()
        
        # Value is valid - store it
        self.buffer.append({
            'value': temperature_value,
            'timestamp': current_time
        })
        self.last_valid_value = temperature_value
        self.last_update_time = current_time
        
        if self._debug_enabled:
            logger.debug(f"Buffer received: {temperature_value:.1f}°C at {current_time:.2f}")
        
        return temperature_value
    
    def _get_fallback_value(self) -> Optional[float]:
        """
        Get fallback value when current data is invalid.
        
        Returns:
            Last known valid value or None if no valid data exists
        """
        if self.last_valid_value is not None:
            return self.last_valid_value
        
        # No valid data yet - return None (graph will handle gracefully)
        return None
    
    def get_latest_valid(self) -> Optional[float]:
        """
        Get the most recent valid temperature value.
        
        Returns:
            Latest valid temperature or None
        """
        return self.last_valid_value
    
    def get_buffer_snapshot(self) -> list:
        """
        Get a snapshot of the current buffer for analysis.
        
        Returns:
            List of temperature values in chronological order
        """
        return [entry['value'] for entry in self.buffer]
    
    def is_ready(self) -> bool:
        """
        Check if buffer has received at least one valid data point.
        
        Returns:
            True if buffer has valid data
        """
        return self.last_valid_value is not None
    
    def get_statistics(self) -> dict:
        """
        Get statistical information about buffered data.
        
        Returns:
            Dictionary with min, max, avg, and count
        """
        if not self.buffer:
            return {
                'min': None,
                'max': None,
                'avg': None,
                'count': 0
            }
        
        values = self.get_buffer_snapshot()
        return {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'count': len(values)
        }
