"""
ESP32-CAM OpenCV Application

A professional framework for ESP32-CAM camera management and processing.

This package provides:
- Camera connection management with retry logic
- Multiple viewer options (GUI and web-based)
- Diagnostic utilities
- Configuration management
- Frame capture and recording
"""

__version__ = "1.0.0"
__author__ = "ESP32-CAM Project"

from . import core
from . import viewers
from . import utils
from . import cli

__all__ = ['core', 'viewers', 'utils', 'cli']
