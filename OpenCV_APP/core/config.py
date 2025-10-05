"""
Centralized configuration management for ESP32-CAM OpenCV application.

This module handles configuration from multiple sources:
- Environment variables
- YAML configuration files
- Default values
"""

import os
import yaml
from typing import Dict, Optional
from pathlib import Path


class CameraConfig:
    """Configuration for a single camera."""
    
    def __init__(self, name: str, ip: str, port: int = 80):
        self.name = name
        self.ip = ip
        self.port = port
        self.stream_url = f"http://{ip}:{port}/stream"
        self.status_url = f"http://{ip}:{port}/"
    
    def __repr__(self):
        return f"CameraConfig(name='{self.name}', ip='{self.ip}', port={self.port})"


class AppConfig:
    """Main application configuration manager."""
    
    # Default camera IPs from the repository configuration
    DEFAULT_CAM_1_IP = "192.168.2.88"
    DEFAULT_CAM_2_IP = "192.168.2.133"
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Optional path to YAML configuration file
        """
        self.cameras: Dict[str, CameraConfig] = {}
        self._load_config(config_file)
    
    def _load_config(self, config_file: Optional[str] = None):
        """Load configuration from file and environment variables."""
        # First, try to load from YAML file
        if config_file and Path(config_file).exists():
            self._load_from_yaml(config_file)
        else:
            # Try default config location
            default_config = Path(__file__).parent.parent / "config" / "camera_config.yaml"
            if default_config.exists():
                self._load_from_yaml(str(default_config))
        
        # Override with environment variables (higher priority)
        self._load_from_env()
        
        # Ensure we have at least the default cameras
        if "ESP32_CAM_1" not in self.cameras:
            cam1_ip = os.getenv("ESP32_CAM_1_IP", self.DEFAULT_CAM_1_IP)
            self.cameras["ESP32_CAM_1"] = CameraConfig("ESP32_CAM_1", cam1_ip)
        
        if "ESP32_CAM_2" not in self.cameras:
            cam2_ip = os.getenv("ESP32_CAM_2_IP", self.DEFAULT_CAM_2_IP)
            self.cameras["ESP32_CAM_2"] = CameraConfig("ESP32_CAM_2", cam2_ip)
    
    def _load_from_yaml(self, config_file: str):
        """Load configuration from YAML file."""
        try:
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
                
            if config_data and 'cameras' in config_data:
                for cam_data in config_data['cameras']:
                    name = cam_data.get('name')
                    ip = cam_data.get('ip')
                    port = cam_data.get('port', 80)
                    
                    if name and ip:
                        self.cameras[name] = CameraConfig(name, ip, port)
        except Exception as e:
            print(f"Warning: Failed to load config from {config_file}: {e}")
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Check for ESP32_CAM_1_IP and ESP32_CAM_2_IP
        cam1_ip = os.getenv("ESP32_CAM_1_IP")
        if cam1_ip:
            self.cameras["ESP32_CAM_1"] = CameraConfig("ESP32_CAM_1", cam1_ip)
        
        cam2_ip = os.getenv("ESP32_CAM_2_IP")
        if cam2_ip:
            self.cameras["ESP32_CAM_2"] = CameraConfig("ESP32_CAM_2", cam2_ip)
    
    def get_camera(self, name: str) -> Optional[CameraConfig]:
        """Get camera configuration by name."""
        return self.cameras.get(name)
    
    def get_all_cameras(self) -> Dict[str, CameraConfig]:
        """Get all camera configurations."""
        return self.cameras
    
    def add_camera(self, name: str, ip: str, port: int = 80):
        """Add a new camera configuration."""
        self.cameras[name] = CameraConfig(name, ip, port)
    
    def __repr__(self):
        return f"AppConfig(cameras={list(self.cameras.keys())})"


# Global configuration instance
_config_instance: Optional[AppConfig] = None


def get_config(config_file: Optional[str] = None) -> AppConfig:
    """
    Get the global configuration instance.
    
    Args:
        config_file: Optional path to configuration file
        
    Returns:
        AppConfig instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = AppConfig(config_file)
    return _config_instance


def reset_config():
    """Reset the global configuration instance."""
    global _config_instance
    _config_instance = None
