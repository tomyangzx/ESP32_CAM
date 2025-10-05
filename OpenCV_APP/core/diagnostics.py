"""
Diagnostic utilities for ESP32-CAM connections.

This module provides tools for testing camera connectivity,
network diagnostics, and performance monitoring.
"""

import requests
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime
import socket

logger = logging.getLogger(__name__)


class CameraDiagnostics:
    """Diagnostic tools for ESP32-CAM cameras."""
    
    @staticmethod
    def ping_camera(ip: str, port: int = 80, timeout: int = 3) -> bool:
        """
        Check if camera is reachable via TCP.
        
        Args:
            ip: Camera IP address
            port: Camera port
            timeout: Timeout in seconds
            
        Returns:
            True if camera is reachable, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.error(f"Error ping {ip}:{port} - {e}")
            return False
    
    @staticmethod
    def check_http_status(url: str, timeout: int = 5) -> Dict[str, any]:
        """
        Check HTTP status of camera endpoint.
        
        Args:
            url: Camera URL
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with status information
        """
        result = {
            'url': url,
            'reachable': False,
            'status_code': None,
            'response_time': None,
            'error': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout)
            end_time = time.time()
            
            result['reachable'] = True
            result['status_code'] = response.status_code
            result['response_time'] = round((end_time - start_time) * 1000, 2)  # ms
            
            logger.info(f"HTTP check for {url}: {response.status_code} ({result['response_time']}ms)")
            
        except requests.exceptions.Timeout:
            result['error'] = 'Timeout'
            logger.error(f"Timeout checking {url}")
        except requests.exceptions.ConnectionError:
            result['error'] = 'Connection Error'
            logger.error(f"Connection error for {url}")
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error checking {url}: {e}")
        
        return result
    
    @staticmethod
    def test_stream_quality(stream_url: str, duration: int = 10) -> Dict[str, any]:
        """
        Test stream quality by measuring frame rate and stability.
        
        Args:
            stream_url: MJPEG stream URL
            duration: Test duration in seconds
            
        Returns:
            Dictionary with quality metrics
        """
        import cv2
        
        result = {
            'stream_url': stream_url,
            'frames_received': 0,
            'frames_failed': 0,
            'avg_fps': 0,
            'duration': duration,
            'stable': False,
            'error': None
        }
        
        try:
            cap = cv2.VideoCapture(stream_url)
            if not cap.isOpened():
                result['error'] = 'Failed to open stream'
                return result
            
            start_time = time.time()
            frame_count = 0
            failed_count = 0
            
            while (time.time() - start_time) < duration:
                ret, frame = cap.read()
                if ret and frame is not None:
                    frame_count += 1
                else:
                    failed_count += 1
                
                # Brief delay to not hammer the stream
                time.sleep(0.01)
            
            end_time = time.time()
            actual_duration = end_time - start_time
            
            cap.release()
            
            result['frames_received'] = frame_count
            result['frames_failed'] = failed_count
            result['avg_fps'] = round(frame_count / actual_duration, 2)
            result['stable'] = failed_count < (frame_count * 0.1)  # Less than 10% failure
            
            logger.info(f"Stream quality test: {frame_count} frames, {result['avg_fps']} FPS")
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error testing stream quality: {e}")
        
        return result
    
    @staticmethod
    def get_camera_info(status_url: str, timeout: int = 5) -> Dict[str, any]:
        """
        Get camera information from status page.
        
        Args:
            status_url: Camera status page URL
            timeout: Request timeout
            
        Returns:
            Dictionary with camera information
        """
        result = {
            'url': status_url,
            'available': False,
            'info': None,
            'error': None
        }
        
        try:
            response = requests.get(status_url, timeout=timeout)
            if response.status_code == 200:
                result['available'] = True
                # Try to parse HTML for device info
                # This is a simple implementation - could be enhanced
                result['info'] = {
                    'content_length': len(response.text),
                    'headers': dict(response.headers)
                }
                logger.info(f"Retrieved camera info from {status_url}")
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error getting camera info: {e}")
        
        return result
    
    @staticmethod
    def run_full_diagnostics(ip: str, port: int = 80) -> Dict[str, any]:
        """
        Run comprehensive diagnostics on a camera.
        
        Args:
            ip: Camera IP address
            port: Camera port
            
        Returns:
            Dictionary with all diagnostic results
        """
        stream_url = f"http://{ip}:{port}/stream"
        status_url = f"http://{ip}:{port}/"
        
        logger.info(f"Running full diagnostics on {ip}:{port}")
        
        diagnostics = {
            'camera_ip': ip,
            'camera_port': port,
            'timestamp': datetime.now().isoformat(),
            'ping_test': CameraDiagnostics.ping_camera(ip, port),
            'http_status': CameraDiagnostics.check_http_status(status_url),
            'stream_status': CameraDiagnostics.check_http_status(stream_url),
            'camera_info': CameraDiagnostics.get_camera_info(status_url)
        }
        
        # Only test stream quality if basic checks pass
        if diagnostics['ping_test'] and diagnostics['stream_status']['reachable']:
            diagnostics['stream_quality'] = CameraDiagnostics.test_stream_quality(stream_url, duration=5)
        else:
            diagnostics['stream_quality'] = {'error': 'Skipped - camera not reachable'}
        
        return diagnostics


class NetworkDiagnostics:
    """Network diagnostic utilities."""
    
    @staticmethod
    def get_local_ip() -> str:
        """Get local machine IP address."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    @staticmethod
    def scan_subnet(subnet: str, port: int = 80, timeout: float = 0.5) -> List[str]:
        """
        Scan subnet for ESP32-CAM devices.
        
        Args:
            subnet: Subnet to scan (e.g., "192.168.2")
            port: Port to check
            timeout: Timeout per host
            
        Returns:
            List of reachable IP addresses
        """
        reachable_hosts = []
        
        logger.info(f"Scanning subnet {subnet}.0/24 on port {port}")
        
        for i in range(1, 255):
            ip = f"{subnet}.{i}"
            if CameraDiagnostics.ping_camera(ip, port, timeout):
                reachable_hosts.append(ip)
                logger.info(f"Found device at {ip}")
        
        return reachable_hosts
