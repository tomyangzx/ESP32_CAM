"""
Base camera classes and interfaces for ESP32-CAM integration.

This module provides abstract base classes and concrete implementations
for camera connection and frame capture.
"""

import cv2
import numpy as np
import requests
from abc import ABC, abstractmethod
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class CameraBase(ABC):
    """Abstract base class for camera interfaces."""
    
    def __init__(self, name: str, stream_url: str):
        """
        Initialize camera.
        
        Args:
            name: Camera identifier
            stream_url: URL for the camera stream
        """
        self.name = name
        self.stream_url = stream_url
        self._is_connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the camera.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame from the camera.
        
        Returns:
            Tuple of (success, frame) where success is bool and frame is numpy array
        """
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnect from the camera."""
        pass
    
    @property
    def is_connected(self) -> bool:
        """Check if camera is connected."""
        return self._is_connected


class ESP32Camera(CameraBase):
    """ESP32-CAM implementation using OpenCV VideoCapture."""
    
    def __init__(self, name: str, stream_url: str, timeout: int = 5):
        """
        Initialize ESP32 camera.
        
        Args:
            name: Camera identifier
            stream_url: URL for the camera MJPEG stream
            timeout: Connection timeout in seconds
        """
        super().__init__(name, stream_url)
        self.timeout = timeout
        self._capture: Optional[cv2.VideoCapture] = None
        self._last_frame: Optional[np.ndarray] = None
        self._frame_count = 0
    
    def connect(self) -> bool:
        """
        Connect to the ESP32-CAM stream.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to {self.name} at {self.stream_url}")
            
            # Test if URL is accessible
            response = requests.get(self.stream_url, timeout=self.timeout, stream=True)
            response.close()
            
            if response.status_code != 200:
                logger.error(f"Failed to connect to {self.name}: HTTP {response.status_code}")
                return False
            
            # Create VideoCapture
            self._capture = cv2.VideoCapture(self.stream_url)
            
            if not self._capture.isOpened():
                logger.error(f"Failed to open video capture for {self.name}")
                return False
            
            # Try to read one frame to verify
            ret, frame = self._capture.read()
            if ret and frame is not None:
                self._is_connected = True
                self._last_frame = frame
                logger.info(f"Successfully connected to {self.name}")
                return True
            else:
                logger.error(f"Failed to read initial frame from {self.name}")
                self._capture.release()
                self._capture = None
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Connection error for {self.name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to {self.name}: {e}")
            return False
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame from the camera.
        
        Returns:
            Tuple of (success, frame)
        """
        if not self._is_connected or self._capture is None:
            return False, None
        
        try:
            ret, frame = self._capture.read()
            if ret and frame is not None:
                self._last_frame = frame
                self._frame_count += 1
                return True, frame
            else:
                logger.warning(f"Failed to read frame from {self.name}")
                return False, self._last_frame  # Return last known good frame
        except Exception as e:
            logger.error(f"Error reading frame from {self.name}: {e}")
            return False, None
    
    def disconnect(self):
        """Disconnect from the camera."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None
        self._is_connected = False
        logger.info(f"Disconnected from {self.name}")
    
    def get_frame_count(self) -> int:
        """Get the number of frames read."""
        return self._frame_count
    
    def __del__(self):
        """Cleanup on destruction."""
        self.disconnect()


class MockCamera(CameraBase):
    """Mock camera for testing purposes."""
    
    def __init__(self, name: str, width: int = 640, height: int = 480):
        """
        Initialize mock camera.
        
        Args:
            name: Camera identifier
            width: Frame width
            height: Frame height
        """
        super().__init__(name, "mock://camera")
        self.width = width
        self.height = height
        self._frame_count = 0
    
    def connect(self) -> bool:
        """Connect to mock camera (always succeeds)."""
        self._is_connected = True
        logger.info(f"Mock camera {self.name} connected")
        return True
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Generate a mock frame.
        
        Returns:
            Tuple of (success, frame)
        """
        if not self._is_connected:
            return False, None
        
        # Generate a frame with changing color based on frame count
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        color_value = (self._frame_count % 255)
        frame[:, :] = [color_value, 128, 255 - color_value]
        
        # Add text overlay
        cv2.putText(frame, f"{self.name} - Frame {self._frame_count}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        self._frame_count += 1
        return True, frame
    
    def disconnect(self):
        """Disconnect mock camera."""
        self._is_connected = False
        logger.info(f"Mock camera {self.name} disconnected")
