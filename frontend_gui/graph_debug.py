import logging
import os
from datetime import datetime

# Configure debug logger
logger = logging.getLogger('heatsink_graph_debug')

class GraphDebugLogger:
    """
    Optional debug validation layer for graph data flow.
    Can be completely removed without affecting functionality.
    
    Enable: set HEATSINK_DEBUG=1
    Disable: unset or set to 0
    """
    
    def __init__(self):
        self.enabled = os.getenv('HEATSINK_DEBUG', '0') == '1'
        
        if self.enabled:
            # Setup file handler for debug logs
            log_file = 'heatsink_graph_debug.log'
            handler = logging.FileHandler(log_file, mode='w')
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            ))
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
            
            logger.info("=" * 60)
            logger.info("HeatSink Graph Debug Logger Initialized")
            logger.info("=" * 60)
    
    def log_api_response(self, endpoint: str, data: dict):
        """Log API response data"""
        if not self.enabled:
            return
        
        logger.debug(f"API Response [{endpoint}]: {data}")
    
    def log_buffer_observation(self, raw_value, validated_value):
        """Log buffer data observation"""
        if not self.enabled:
            return
        
        if raw_value != validated_value:
            logger.warning(f"Buffer corrected: {raw_value} -> {validated_value}")
        else:
            logger.debug(f"Buffer received: {validated_value}°C")
    
    def log_graph_update(self, temperature: float, data_points: int):
        """Log graph update event"""
        if not self.enabled:
            return
        
        logger.debug(f"Graph updated: {temperature:.1f}°C (buffer size: {data_points})")
    
    def log_statistics(self, stats: dict):
        """Log buffer statistics"""
        if not self.enabled:
            return
        
        logger.info(
            f"Stats - Min: {stats.get('min', 'N/A'):.1f}°C, "
            f"Max: {stats.get('max', 'N/A'):.1f}°C, "
            f"Avg: {stats.get('avg', 'N/A'):.1f}°C, "
            f"Count: {stats.get('count', 0)}"
        )
    
    def log_error(self, message: str):
        """Log error message"""
        if not self.enabled:
            return
        
        logger.error(message)

# Global debug logger instance
debug_logger = GraphDebugLogger()
