"""
Network utility functions for ESP32-CAM applications.

This module provides network testing and discovery utilities.
"""

import socket
import requests
import logging
from typing import List, Dict, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def test_url_reachable(url: str, timeout: int = 5) -> bool:
    """
    Test if a URL is reachable.
    
    Args:
        url: URL to test
        timeout: Request timeout in seconds
        
    Returns:
        True if URL is reachable, False otherwise
    """
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"URL {url} not reachable: {e}")
        return False


def get_host_ip(url: str) -> Optional[str]:
    """
    Extract IP address from URL.
    
    Args:
        url: URL to parse
        
    Returns:
        IP address or hostname, or None if parsing fails
    """
    try:
        parsed = urlparse(url)
        return parsed.hostname
    except Exception as e:
        logger.error(f"Error parsing URL {url}: {e}")
        return None


def test_tcp_port(host: str, port: int, timeout: float = 3.0) -> bool:
    """
    Test if a TCP port is open on a host.
    
    Args:
        host: Hostname or IP address
        port: Port number
        timeout: Connection timeout in seconds
        
    Returns:
        True if port is open, False otherwise
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        logger.error(f"Error testing port {host}:{port} - {e}")
        return False


def discover_cameras_in_subnet(subnet: str, port: int = 80, 
                               timeout: float = 0.5) -> List[str]:
    """
    Discover ESP32-CAM devices in a subnet.
    
    Args:
        subnet: Subnet prefix (e.g., "192.168.2")
        port: Port to scan (default: 80)
        timeout: Timeout per host check
        
    Returns:
        List of discovered camera IP addresses
    """
    discovered = []
    
    logger.info(f"Scanning subnet {subnet}.0/24 on port {port}")
    
    for i in range(1, 255):
        ip = f"{subnet}.{i}"
        if test_tcp_port(ip, port, timeout):
            # Additional check: try to access the root page
            try:
                url = f"http://{ip}:{port}/"
                response = requests.get(url, timeout=1)
                if response.status_code == 200:
                    discovered.append(ip)
                    logger.info(f"Discovered camera at {ip}")
            except:
                pass
    
    return discovered


def get_network_interfaces() -> Dict[str, str]:
    """
    Get network interface information.
    
    Returns:
        Dictionary mapping interface names to IP addresses
    """
    interfaces = {}
    
    try:
        hostname = socket.gethostname()
        interfaces['hostname'] = hostname
        interfaces['local_ip'] = socket.gethostbyname(hostname)
    except Exception as e:
        logger.error(f"Error getting network interfaces: {e}")
    
    return interfaces


def test_stream_endpoint(stream_url: str, timeout: int = 5) -> Dict[str, any]:
    """
    Test if a stream endpoint is working.
    
    Args:
        stream_url: MJPEG stream URL
        timeout: Request timeout
        
    Returns:
        Dictionary with test results
    """
    result = {
        'url': stream_url,
        'accessible': False,
        'content_type': None,
        'error': None
    }
    
    try:
        response = requests.get(stream_url, timeout=timeout, stream=True)
        result['accessible'] = response.status_code == 200
        result['content_type'] = response.headers.get('Content-Type')
        response.close()
        
        logger.info(f"Stream endpoint test: {stream_url} - {result['accessible']}")
        
    except requests.exceptions.Timeout:
        result['error'] = 'Timeout'
    except requests.exceptions.ConnectionError:
        result['error'] = 'Connection Error'
    except Exception as e:
        result['error'] = str(e)
    
    return result


def format_connection_info(ip: str, port: int = 80) -> Dict[str, str]:
    """
    Format connection information for a camera.
    
    Args:
        ip: Camera IP address
        port: Camera port
        
    Returns:
        Dictionary with formatted URLs and connection info
    """
    return {
        'ip': ip,
        'port': port,
        'stream_url': f"http://{ip}:{port}/stream",
        'status_url': f"http://{ip}:{port}/",
        'web_interface': f"http://{ip}:{port}"
    }
