"""
Unit tests for camera functionality.

Tests camera connection, frame capture, and error handling.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import ESP32Camera, MockCamera, CameraConfig
from core.connection_manager import ConnectionManager


class TestMockCamera(unittest.TestCase):
    """Test cases for MockCamera."""
    
    def test_mock_camera_creation(self):
        """Test creating a mock camera."""
        camera = MockCamera("TestCam", width=640, height=480)
        self.assertEqual(camera.name, "TestCam")
        self.assertEqual(camera.width, 640)
        self.assertEqual(camera.height, 480)
        self.assertFalse(camera.is_connected)
    
    def test_mock_camera_connect(self):
        """Test connecting to mock camera."""
        camera = MockCamera("TestCam")
        result = camera.connect()
        self.assertTrue(result)
        self.assertTrue(camera.is_connected)
    
    def test_mock_camera_read(self):
        """Test reading frames from mock camera."""
        camera = MockCamera("TestCam", width=320, height=240)
        camera.connect()
        
        ret, frame = camera.read()
        self.assertTrue(ret)
        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape, (240, 320, 3))
    
    def test_mock_camera_disconnect(self):
        """Test disconnecting mock camera."""
        camera = MockCamera("TestCam")
        camera.connect()
        self.assertTrue(camera.is_connected)
        
        camera.disconnect()
        self.assertFalse(camera.is_connected)


class TestESP32Camera(unittest.TestCase):
    """Test cases for ESP32Camera."""
    
    def test_camera_creation(self):
        """Test creating an ESP32 camera."""
        camera = ESP32Camera("TestCam", "http://192.168.1.100/stream")
        self.assertEqual(camera.name, "TestCam")
        self.assertEqual(camera.stream_url, "http://192.168.1.100/stream")
        self.assertFalse(camera.is_connected)
    
    @patch('requests.get')
    @patch('cv2.VideoCapture')
    def test_camera_connect_success(self, mock_video_capture, mock_requests_get):
        """Test successful camera connection."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response
        
        # Mock VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_video_capture.return_value = mock_cap
        
        camera = ESP32Camera("TestCam", "http://192.168.1.100/stream")
        result = camera.connect()
        
        self.assertTrue(result)
        self.assertTrue(camera.is_connected)
    
    @patch('requests.get')
    def test_camera_connect_failure(self, mock_requests_get):
        """Test failed camera connection."""
        # Mock failed HTTP response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response
        
        camera = ESP32Camera("TestCam", "http://192.168.1.100/stream")
        result = camera.connect()
        
        self.assertFalse(result)
        self.assertFalse(camera.is_connected)
    
    def test_camera_read_not_connected(self):
        """Test reading from disconnected camera."""
        camera = ESP32Camera("TestCam", "http://192.168.1.100/stream")
        ret, frame = camera.read()
        
        self.assertFalse(ret)
        self.assertIsNone(frame)


class TestConnectionManager(unittest.TestCase):
    """Test cases for ConnectionManager."""
    
    def test_connection_manager_creation(self):
        """Test creating a connection manager."""
        manager = ConnectionManager(retry_attempts=3, retry_delay=1)
        self.assertEqual(manager.retry_attempts, 3)
        self.assertEqual(manager.retry_delay, 1)
        self.assertEqual(len(manager.cameras), 0)
    
    def test_add_camera(self):
        """Test adding a camera to the manager."""
        manager = ConnectionManager()
        camera = MockCamera("TestCam")
        
        manager.add_camera(camera)
        self.assertEqual(len(manager.cameras), 1)
        self.assertIn("TestCam", manager.cameras)
    
    def test_add_camera_from_config(self):
        """Test adding a camera from configuration."""
        manager = ConnectionManager()
        config = CameraConfig("TestCam", "192.168.1.100", 80)
        
        manager.add_camera_from_config(config)
        self.assertEqual(len(manager.cameras), 1)
        self.assertIn("TestCam", manager.cameras)
    
    def test_connect_camera_success(self):
        """Test successful camera connection through manager."""
        manager = ConnectionManager()
        camera = MockCamera("TestCam")
        manager.add_camera(camera)
        
        result = manager.connect_camera("TestCam")
        self.assertTrue(result)
        self.assertTrue(camera.is_connected)
    
    def test_get_connected_cameras(self):
        """Test getting list of connected cameras."""
        manager = ConnectionManager()
        
        cam1 = MockCamera("Cam1")
        cam2 = MockCamera("Cam2")
        
        manager.add_camera(cam1)
        manager.add_camera(cam2)
        
        manager.connect_camera("Cam1")
        
        connected = manager.get_connected_cameras()
        self.assertEqual(len(connected), 1)
        self.assertIn("Cam1", connected)
        self.assertNotIn("Cam2", connected)
    
    def test_disconnect_all(self):
        """Test disconnecting all cameras."""
        manager = ConnectionManager()
        
        cam1 = MockCamera("Cam1")
        cam2 = MockCamera("Cam2")
        
        manager.add_camera(cam1)
        manager.add_camera(cam2)
        
        manager.connect_camera("Cam1")
        manager.connect_camera("Cam2")
        
        manager.disconnect_all()
        
        self.assertEqual(len(manager.get_connected_cameras()), 0)


if __name__ == '__main__':
    unittest.main()
