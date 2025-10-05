"""
MJPEG stream parsing utilities.

This module provides utilities for parsing and handling MJPEG streams
from ESP32-CAM devices.
"""

import cv2
import numpy as np
import requests
import logging
from typing import Iterator, Optional, Tuple

logger = logging.getLogger(__name__)


class MJPEGParser:
    """Parser for MJPEG streams."""
    
    def __init__(self, stream_url: str, timeout: int = 5):
        """
        Initialize MJPEG parser.
        
        Args:
            stream_url: URL of the MJPEG stream
            timeout: Connection timeout in seconds
        """
        self.stream_url = stream_url
        self.timeout = timeout
        self._session: Optional[requests.Session] = None
        self._stream: Optional[requests.Response] = None
    
    def connect(self) -> bool:
        """
        Connect to the MJPEG stream.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._session = requests.Session()
            self._stream = self._session.get(
                self.stream_url,
                timeout=self.timeout,
                stream=True
            )
            
            if self._stream.status_code == 200:
                logger.info(f"Connected to MJPEG stream: {self.stream_url}")
                return True
            else:
                logger.error(f"Failed to connect: HTTP {self._stream.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to stream: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the stream."""
        if self._stream:
            self._stream.close()
            self._stream = None
        if self._session:
            self._session.close()
            self._session = None
        logger.info("Disconnected from MJPEG stream")
    
    def parse_frames(self, max_frames: Optional[int] = None) -> Iterator[np.ndarray]:
        """
        Parse frames from the MJPEG stream.
        
        Args:
            max_frames: Maximum number of frames to parse (None for unlimited)
            
        Yields:
            Numpy arrays representing frames
        """
        if not self._stream:
            logger.error("Not connected to stream")
            return
        
        frame_count = 0
        byte_buffer = b''
        
        try:
            for chunk in self._stream.iter_content(chunk_size=1024):
                byte_buffer += chunk
                
                # Look for JPEG markers
                start = byte_buffer.find(b'\xff\xd8')  # JPEG start
                end = byte_buffer.find(b'\xff\xd9')    # JPEG end
                
                if start != -1 and end != -1 and end > start:
                    # Extract JPEG image
                    jpg = byte_buffer[start:end + 2]
                    byte_buffer = byte_buffer[end + 2:]
                    
                    # Decode JPEG
                    frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        frame_count += 1
                        yield frame
                        
                        if max_frames and frame_count >= max_frames:
                            break
                
                # Prevent buffer from growing too large
                if len(byte_buffer) > 100000:
                    byte_buffer = byte_buffer[-10000:]
                    
        except Exception as e:
            logger.error(f"Error parsing frames: {e}")
        finally:
            logger.info(f"Parsed {frame_count} frames")
    
    def get_single_frame(self) -> Optional[np.ndarray]:
        """
        Get a single frame from the stream.
        
        Returns:
            Numpy array representing the frame, or None if failed
        """
        if not self._stream:
            if not self.connect():
                return None
        
        try:
            for frame in self.parse_frames(max_frames=1):
                return frame
        except Exception as e:
            logger.error(f"Error getting single frame: {e}")
        
        return None
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def extract_frame_from_stream(stream_url: str, timeout: int = 5) -> Optional[np.ndarray]:
    """
    Extract a single frame from an MJPEG stream.
    
    Args:
        stream_url: URL of the MJPEG stream
        timeout: Connection timeout
        
    Returns:
        Numpy array representing the frame, or None if failed
    """
    with MJPEGParser(stream_url, timeout) as parser:
        return parser.get_single_frame()


def test_mjpeg_stream(stream_url: str, duration: int = 5) -> Tuple[bool, dict]:
    """
    Test an MJPEG stream and collect statistics.
    
    Args:
        stream_url: URL of the MJPEG stream
        duration: Test duration in seconds
        
    Returns:
        Tuple of (success, stats_dict)
    """
    stats = {
        'frames_received': 0,
        'avg_frame_size': 0,
        'errors': 0
    }
    
    try:
        import time
        parser = MJPEGParser(stream_url)
        
        if not parser.connect():
            return False, stats
        
        start_time = time.time()
        frame_sizes = []
        
        for frame in parser.parse_frames():
            if frame is not None:
                stats['frames_received'] += 1
                frame_sizes.append(frame.size)
            else:
                stats['errors'] += 1
            
            if (time.time() - start_time) >= duration:
                break
        
        parser.disconnect()
        
        if frame_sizes:
            stats['avg_frame_size'] = sum(frame_sizes) // len(frame_sizes)
        
        return True, stats
        
    except Exception as e:
        logger.error(f"Error testing stream: {e}")
        return False, stats
