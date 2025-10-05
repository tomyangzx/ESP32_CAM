"""
Frame capture and saving utilities.

This module provides tools for capturing and saving frames from cameras
with various formats and naming conventions.
"""

import cv2
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class FrameCapture:
    """Utility class for capturing and saving frames."""
    
    def __init__(self, output_dir: str = "captures"):
        """
        Initialize frame capture utility.
        
        Args:
            output_dir: Directory to save captured frames
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Frame capture initialized with output dir: {self.output_dir}")
    
    def save_frame(self, frame: np.ndarray, camera_name: str = "camera", 
                   prefix: str = "", suffix: str = "") -> Optional[str]:
        """
        Save a single frame to disk.
        
        Args:
            frame: Frame to save (numpy array)
            camera_name: Name of the camera
            prefix: Optional prefix for filename
            suffix: Optional suffix for filename
            
        Returns:
            Path to saved file or None if failed
        """
        if frame is None:
            logger.error("Cannot save None frame")
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"{prefix}{camera_name}_{timestamp}{suffix}.jpg"
            filepath = self.output_dir / filename
            
            cv2.imwrite(str(filepath), frame)
            logger.info(f"Saved frame to {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error saving frame: {e}")
            return None
    
    def save_frame_pair(self, frame1: np.ndarray, frame2: np.ndarray,
                       name1: str = "cam1", name2: str = "cam2") -> tuple:
        """
        Save a pair of frames with synchronized timestamps.
        
        Args:
            frame1: First frame
            frame2: Second frame
            name1: Name for first camera
            name2: Name for second camera
            
        Returns:
            Tuple of (path1, path2)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        
        path1 = None
        path2 = None
        
        try:
            if frame1 is not None:
                filename1 = f"{name1}_{timestamp}.jpg"
                filepath1 = self.output_dir / filename1
                cv2.imwrite(str(filepath1), frame1)
                path1 = str(filepath1)
            
            if frame2 is not None:
                filename2 = f"{name2}_{timestamp}.jpg"
                filepath2 = self.output_dir / filename2
                cv2.imwrite(str(filepath2), frame2)
                path2 = str(filepath2)
            
            logger.info(f"Saved frame pair: {path1}, {path2}")
            
        except Exception as e:
            logger.error(f"Error saving frame pair: {e}")
        
        return path1, path2
    
    def save_annotated_frame(self, frame: np.ndarray, camera_name: str,
                            text: Optional[str] = None) -> Optional[str]:
        """
        Save frame with text annotation.
        
        Args:
            frame: Frame to save
            camera_name: Camera name
            text: Optional text to overlay on frame
            
        Returns:
            Path to saved file or None if failed
        """
        if frame is None:
            return None
        
        # Create a copy to avoid modifying original
        annotated_frame = frame.copy()
        
        # Add timestamp
        timestamp_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(annotated_frame, timestamp_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add camera name
        cv2.putText(annotated_frame, camera_name, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add custom text if provided
        if text:
            cv2.putText(annotated_frame, text, (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return self.save_frame(annotated_frame, camera_name, prefix="annotated_")
    
    def create_video_writer(self, filename: str, fps: int = 20,
                           frame_size: tuple = (640, 480)) -> cv2.VideoWriter:
        """
        Create a video writer for recording streams.
        
        Args:
            filename: Output video filename
            fps: Frames per second
            frame_size: Frame size (width, height)
            
        Returns:
            VideoWriter instance
        """
        filepath = self.output_dir / filename
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        writer = cv2.VideoWriter(str(filepath), fourcc, fps, frame_size)
        
        logger.info(f"Created video writer: {filepath} ({fps} FPS, {frame_size})")
        return writer
