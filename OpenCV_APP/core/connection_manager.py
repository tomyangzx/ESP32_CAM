"""
Connection management utilities for ESP32-CAM applications.

This module provides robust connection handling with retry logic,
error recovery, and connection pooling.
"""

import time
import logging
from typing import Dict, Optional, List
from .camera_base import CameraBase, ESP32Camera
from .config import CameraConfig

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages connections to multiple cameras with retry logic."""
    
    def __init__(self, retry_attempts: int = 3, retry_delay: int = 2):
        """
        Initialize connection manager.
        
        Args:
            retry_attempts: Number of connection retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.cameras: Dict[str, CameraBase] = {}
        self._connection_stats: Dict[str, dict] = {}
    
    def add_camera(self, camera: CameraBase):
        """
        Add a camera to the manager.
        
        Args:
            camera: Camera instance to manage
        """
        self.cameras[camera.name] = camera
        self._connection_stats[camera.name] = {
            'attempts': 0,
            'successes': 0,
            'failures': 0,
            'last_error': None
        }
        logger.info(f"Added camera {camera.name} to connection manager")
    
    def add_camera_from_config(self, config: CameraConfig):
        """
        Create and add a camera from configuration.
        
        Args:
            config: CameraConfig instance
        """
        camera = ESP32Camera(config.name, config.stream_url)
        self.add_camera(camera)
    
    def connect_camera(self, name: str) -> bool:
        """
        Connect to a specific camera with retry logic.
        
        Args:
            name: Camera name
            
        Returns:
            True if connection successful, False otherwise
        """
        if name not in self.cameras:
            logger.error(f"Camera {name} not found in manager")
            return False
        
        camera = self.cameras[name]
        stats = self._connection_stats[name]
        
        for attempt in range(1, self.retry_attempts + 1):
            stats['attempts'] += 1
            logger.info(f"Connecting to {name} (attempt {attempt}/{self.retry_attempts})")
            
            try:
                if camera.connect():
                    stats['successes'] += 1
                    logger.info(f"Successfully connected to {name}")
                    return True
                else:
                    stats['failures'] += 1
                    logger.warning(f"Failed to connect to {name} on attempt {attempt}")
            except Exception as e:
                stats['failures'] += 1
                stats['last_error'] = str(e)
                logger.error(f"Error connecting to {name}: {e}")
            
            if attempt < self.retry_attempts:
                logger.info(f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
        
        logger.error(f"Failed to connect to {name} after {self.retry_attempts} attempts")
        return False
    
    def connect_all(self) -> Dict[str, bool]:
        """
        Connect to all cameras.
        
        Returns:
            Dictionary mapping camera names to connection success status
        """
        results = {}
        for name in self.cameras.keys():
            results[name] = self.connect_camera(name)
        return results
    
    def disconnect_camera(self, name: str):
        """
        Disconnect a specific camera.
        
        Args:
            name: Camera name
        """
        if name in self.cameras:
            self.cameras[name].disconnect()
            logger.info(f"Disconnected camera {name}")
    
    def disconnect_all(self):
        """Disconnect all cameras."""
        for name in self.cameras.keys():
            self.disconnect_camera(name)
    
    def get_camera(self, name: str) -> Optional[CameraBase]:
        """
        Get a camera instance by name.
        
        Args:
            name: Camera name
            
        Returns:
            Camera instance or None if not found
        """
        return self.cameras.get(name)
    
    def get_connected_cameras(self) -> List[str]:
        """
        Get list of currently connected cameras.
        
        Returns:
            List of connected camera names
        """
        return [name for name, cam in self.cameras.items() if cam.is_connected]
    
    def get_connection_stats(self, name: str) -> Optional[dict]:
        """
        Get connection statistics for a camera.
        
        Args:
            name: Camera name
            
        Returns:
            Dictionary with connection statistics or None if not found
        """
        return self._connection_stats.get(name)
    
    def reconnect_camera(self, name: str) -> bool:
        """
        Reconnect a camera (disconnect and connect).
        
        Args:
            name: Camera name
            
        Returns:
            True if reconnection successful, False otherwise
        """
        if name not in self.cameras:
            return False
        
        logger.info(f"Reconnecting camera {name}")
        self.disconnect_camera(name)
        time.sleep(1)  # Brief pause before reconnecting
        return self.connect_camera(name)
    
    def health_check(self) -> Dict[str, bool]:
        """
        Check health of all cameras by attempting to read a frame.
        
        Returns:
            Dictionary mapping camera names to health status
        """
        health_status = {}
        for name, camera in self.cameras.items():
            if not camera.is_connected:
                health_status[name] = False
                continue
            
            # Try to read a frame
            ret, frame = camera.read()
            health_status[name] = ret and frame is not None
        
        return health_status
    
    def __del__(self):
        """Cleanup on destruction."""
        self.disconnect_all()
