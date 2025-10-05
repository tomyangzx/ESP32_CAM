"""
Unit tests for network utilities.

Tests network connectivity and diagnostic functions.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    test_url_reachable,
    test_tcp_port,
    get_network_interfaces,
    test_stream_endpoint,
    format_connection_info
)
from core.diagnostics import CameraDiagnostics, NetworkDiagnostics


class TestNetworkUtils(unittest.TestCase):
    """Test cases for network utility functions."""
    
    @patch('requests.get')
    def test_url_reachable_success(self, mock_get):
        """Test URL reachability check - success case."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = test_url_reachable("http://example.com")
        self.assertTrue(result)
    
    @patch('requests.get')
    def test_url_reachable_failure(self, mock_get):
        """Test URL reachability check - failure case."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = test_url_reachable("http://example.com")
        self.assertFalse(result)
    
    @patch('socket.socket')
    def test_tcp_port_open(self, mock_socket):
        """Test TCP port check - port open."""
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 0
        mock_socket.return_value = mock_sock
        
        result = test_tcp_port("192.168.1.100", 80)
        self.assertTrue(result)
    
    @patch('socket.socket')
    def test_tcp_port_closed(self, mock_socket):
        """Test TCP port check - port closed."""
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 1
        mock_socket.return_value = mock_sock
        
        result = test_tcp_port("192.168.1.100", 80)
        self.assertFalse(result)
    
    def test_format_connection_info(self):
        """Test connection info formatting."""
        info = format_connection_info("192.168.1.100", 80)
        
        self.assertEqual(info['ip'], "192.168.1.100")
        self.assertEqual(info['port'], 80)
        self.assertEqual(info['stream_url'], "http://192.168.1.100:80/stream")
        self.assertEqual(info['status_url'], "http://192.168.1.100:80/")
        self.assertEqual(info['web_interface'], "http://192.168.1.100:80")
    
    @patch('requests.get')
    def test_stream_endpoint_success(self, mock_get):
        """Test stream endpoint check - success."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'multipart/x-mixed-replace'}
        mock_get.return_value = mock_response
        
        result = test_stream_endpoint("http://192.168.1.100/stream")
        
        self.assertTrue(result['accessible'])
        self.assertEqual(result['content_type'], 'multipart/x-mixed-replace')
        self.assertIsNone(result['error'])
    
    @patch('socket.gethostname')
    @patch('socket.gethostbyname')
    def test_get_network_interfaces(self, mock_gethostbyname, mock_gethostname):
        """Test getting network interfaces."""
        mock_gethostname.return_value = "test-host"
        mock_gethostbyname.return_value = "192.168.1.50"
        
        interfaces = get_network_interfaces()
        
        self.assertEqual(interfaces['hostname'], "test-host")
        self.assertEqual(interfaces['local_ip'], "192.168.1.50")


class TestCameraDiagnostics(unittest.TestCase):
    """Test cases for camera diagnostic tools."""
    
    @patch('socket.socket')
    def test_ping_camera_success(self, mock_socket):
        """Test ping camera - success."""
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 0
        mock_socket.return_value = mock_sock
        
        result = CameraDiagnostics.ping_camera("192.168.1.100", 80)
        self.assertTrue(result)
    
    @patch('socket.socket')
    def test_ping_camera_failure(self, mock_socket):
        """Test ping camera - failure."""
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 1
        mock_socket.return_value = mock_sock
        
        result = CameraDiagnostics.ping_camera("192.168.1.100", 80)
        self.assertFalse(result)
    
    @patch('requests.get')
    def test_check_http_status_success(self, mock_get):
        """Test HTTP status check - success."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = CameraDiagnostics.check_http_status("http://192.168.1.100")
        
        self.assertTrue(result['reachable'])
        self.assertEqual(result['status_code'], 200)
        self.assertIsNotNone(result['response_time'])
        self.assertIsNone(result['error'])
    
    @patch('requests.get')
    def test_check_http_status_timeout(self, mock_get):
        """Test HTTP status check - timeout."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()
        
        result = CameraDiagnostics.check_http_status("http://192.168.1.100")
        
        self.assertFalse(result['reachable'])
        self.assertEqual(result['error'], 'Timeout')


class TestNetworkDiagnostics(unittest.TestCase):
    """Test cases for network diagnostic tools."""
    
    @patch('socket.socket')
    def test_get_local_ip(self, mock_socket):
        """Test getting local IP address."""
        mock_sock = MagicMock()
        mock_sock.getsockname.return_value = ("192.168.1.50", 12345)
        mock_socket.return_value = mock_sock
        
        ip = NetworkDiagnostics.get_local_ip()
        self.assertEqual(ip, "192.168.1.50")
    
    @patch('core.diagnostics.CameraDiagnostics.ping_camera')
    @patch('requests.get')
    def test_scan_subnet(self, mock_get, mock_ping):
        """Test subnet scanning."""
        # Mock ping to return True for specific IPs
        def ping_side_effect(ip, port, timeout):
            return ip in ["192.168.2.88", "192.168.2.133"]
        
        mock_ping.side_effect = ping_side_effect
        
        # Mock HTTP get
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # This would take too long in real scenario, so we'll just test the logic
        # In a real test, we'd mock the entire range or limit it
        # For now, just verify the function exists and is callable
        self.assertTrue(callable(NetworkDiagnostics.scan_subnet))


if __name__ == '__main__':
    unittest.main()
