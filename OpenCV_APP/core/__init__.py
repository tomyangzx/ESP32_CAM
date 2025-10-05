"""
Core modules for ESP32-CAM OpenCV application.

This package contains the fundamental components for camera management,
configuration, connection handling, and diagnostics.
"""

from .config import AppConfig, CameraConfig, get_config, reset_config
from .camera_base import CameraBase, ESP32Camera, MockCamera
from .connection_manager import ConnectionManager
from .diagnostics import CameraDiagnostics, NetworkDiagnostics

__all__ = [
    'AppConfig',
    'CameraConfig',
    'get_config',
    'reset_config',
    'CameraBase',
    'ESP32Camera',
    'MockCamera',
    'ConnectionManager',
    'CameraDiagnostics',
    'NetworkDiagnostics',
]
