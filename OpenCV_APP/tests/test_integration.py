"""
Integration tests for ESP32-CAM application.

Tests end-to-end functionality with mock components.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
import tempfile
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import get_config, reset_config, ConnectionManager, MockCamera
from utils import FrameCapture
import numpy as np


class TestConfigurationIntegration(unittest.TestCase):
    """Integration tests for configuration system."""
    
    def setUp(self):
        """Reset configuration before each test."""
        reset_config()
    
    def tearDown(self):
        """Clean up after each test."""
        reset_config()
    
    def test_default_configuration(self):
        """Test loading default configuration."""
        config = get_config()
        
        # Should have default cameras
        cam1 = config.get_camera("ESP32_CAM_1")
        cam2 = config.get_camera("ESP32_CAM_2")
        
        self.assertIsNotNone(cam1)
        self.assertIsNotNone(cam2)
        self.assertEqual(cam1.ip, "192.168.2.88")
        self.assertEqual(cam2.ip, "192.168.2.133")
    
    def test_environment_variable_override(self):
        """Test configuration override with environment variables."""
        os.environ['ESP32_CAM_1_IP'] = "10.0.0.1"
        os.environ['ESP32_CAM_2_IP'] = "10.0.0.2"
        
        reset_config()
        config = get_config()
        
        cam1 = config.get_camera("ESP32_CAM_1")
        cam2 = config.get_camera("ESP32_CAM_2")
        
        self.assertEqual(cam1.ip, "10.0.0.1")
        self.assertEqual(cam2.ip, "10.0.0.2")
        
        # Cleanup
        del os.environ['ESP32_CAM_1_IP']
        del os.environ['ESP32_CAM_2_IP']


class TestConnectionManagerIntegration(unittest.TestCase):
    """Integration tests for connection manager with cameras."""
    
    def setUp(self):
        """Setup for each test."""
        reset_config()
        self.manager = ConnectionManager(retry_attempts=2, retry_delay=0)
    
    def tearDown(self):
        """Cleanup after each test."""
        self.manager.disconnect_all()
    
    def test_manage_multiple_cameras(self):
        """Test managing multiple cameras."""
        cam1 = MockCamera("Cam1")
        cam2 = MockCamera("Cam2")
        
        self.manager.add_camera(cam1)
        self.manager.add_camera(cam2)
        
        # Connect all
        results = self.manager.connect_all()
        
        self.assertTrue(results["Cam1"])
        self.assertTrue(results["Cam2"])
        
        # Check connected cameras
        connected = self.manager.get_connected_cameras()
        self.assertEqual(len(connected), 2)
    
    def test_health_check(self):
        """Test health check functionality."""
        cam1 = MockCamera("Cam1")
        cam2 = MockCamera("Cam2")
        
        self.manager.add_camera(cam1)
        self.manager.add_camera(cam2)
        
        self.manager.connect_camera("Cam1")
        self.manager.connect_camera("Cam2")
        
        # Run health check
        health = self.manager.health_check()
        
        self.assertTrue(health["Cam1"])
        self.assertTrue(health["Cam2"])
    
    def test_reconnect_camera(self):
        """Test reconnecting a camera."""
        cam = MockCamera("TestCam")
        self.manager.add_camera(cam)
        
        # Initial connection
        self.assertTrue(self.manager.connect_camera("TestCam"))
        
        # Disconnect
        cam.disconnect()
        self.assertFalse(cam.is_connected)
        
        # Reconnect
        self.assertTrue(self.manager.reconnect_camera("TestCam"))
        self.assertTrue(cam.is_connected)


class TestFrameCaptureIntegration(unittest.TestCase):
    """Integration tests for frame capture functionality."""
    
    def setUp(self):
        """Setup temporary directory for captures."""
        self.temp_dir = tempfile.mkdtemp()
        self.frame_capture = FrameCapture(output_dir=self.temp_dir)
    
    def tearDown(self):
        """Cleanup temporary directory."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_save_frame(self):
        """Test saving a single frame."""
        # Create a test frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:, :] = [255, 0, 0]  # Blue frame
        
        # Save frame
        path = self.frame_capture.save_frame(frame, "TestCam")
        
        self.assertIsNotNone(path)
        self.assertTrue(os.path.exists(path))
    
    def test_save_frame_pair(self):
        """Test saving a pair of frames."""
        frame1 = np.zeros((480, 640, 3), dtype=np.uint8)
        frame1[:, :] = [255, 0, 0]
        
        frame2 = np.zeros((480, 640, 3), dtype=np.uint8)
        frame2[:, :] = [0, 255, 0]
        
        path1, path2 = self.frame_capture.save_frame_pair(frame1, frame2, "Cam1", "Cam2")
        
        self.assertIsNotNone(path1)
        self.assertIsNotNone(path2)
        self.assertTrue(os.path.exists(path1))
        self.assertTrue(os.path.exists(path2))
    
    def test_save_annotated_frame(self):
        """Test saving an annotated frame."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        path = self.frame_capture.save_annotated_frame(frame, "TestCam", "Test Annotation")
        
        self.assertIsNotNone(path)
        self.assertTrue(os.path.exists(path))


class TestEndToEndWorkflow(unittest.TestCase):
    """End-to-end integration tests."""
    
    def setUp(self):
        """Setup for each test."""
        reset_config()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Cleanup after each test."""
        reset_config()
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_complete_workflow(self):
        """Test complete workflow: config -> connect -> capture."""
        # Get configuration
        config = get_config()
        
        # Create connection manager
        manager = ConnectionManager()
        
        # Add mock cameras
        cam1 = MockCamera("TestCam1")
        cam2 = MockCamera("TestCam2")
        manager.add_camera(cam1)
        manager.add_camera(cam2)
        
        # Connect cameras
        results = manager.connect_all()
        self.assertTrue(all(results.values()))
        
        # Read frames
        ret1, frame1 = cam1.read()
        ret2, frame2 = cam2.read()
        
        self.assertTrue(ret1)
        self.assertTrue(ret2)
        self.assertIsNotNone(frame1)
        self.assertIsNotNone(frame2)
        
        # Save frames
        fc = FrameCapture(output_dir=self.temp_dir)
        path1, path2 = fc.save_frame_pair(frame1, frame2, "TestCam1", "TestCam2")
        
        self.assertIsNotNone(path1)
        self.assertIsNotNone(path2)
        
        # Verify files exist
        self.assertTrue(os.path.exists(path1))
        self.assertTrue(os.path.exists(path2))
        
        # Cleanup
        manager.disconnect_all()


if __name__ == '__main__':
    unittest.main()
