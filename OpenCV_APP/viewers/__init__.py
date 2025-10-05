"""
Viewer applications for ESP32-CAM devices.

This package contains different viewer implementations:
- DualCameraViewer: View two cameras simultaneously
- SingleCameraViewer: View a single camera
- WebViewer: Browser-based interface
"""

from .dual_viewer import DualCameraViewer
from .single_viewer import SingleCameraViewer

__all__ = [
    'DualCameraViewer',
    'SingleCameraViewer',
]
