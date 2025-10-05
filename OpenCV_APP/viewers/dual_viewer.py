"""
Dual camera viewer for ESP32-CAM devices.

This module provides a GUI application for viewing streams from two
ESP32-CAM devices simultaneously.
"""

import cv2
import numpy as np
import logging
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import get_config, ConnectionManager
from utils import FrameCapture

logger = logging.getLogger(__name__)


class DualCameraViewer:
    """Viewer application for dual ESP32-CAM setup."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize dual camera viewer.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config = get_config(config_file)
        self.connection_manager = ConnectionManager(retry_attempts=3, retry_delay=2)
        self.frame_capture = FrameCapture()
        self.running = False
        
        # Get camera configurations
        self.cam1_config = self.config.get_camera("ESP32_CAM_1")
        self.cam2_config = self.config.get_camera("ESP32_CAM_2")
        
        if not self.cam1_config or not self.cam2_config:
            raise ValueError("Camera configurations not found")
        
        logger.info("Dual camera viewer initialized")
    
    def setup_cameras(self) -> bool:
        """
        Setup and connect to cameras.
        
        Returns:
            True if setup successful, False otherwise
        """
        logger.info("Setting up cameras...")
        
        # Add cameras to connection manager
        self.connection_manager.add_camera_from_config(self.cam1_config)
        self.connection_manager.add_camera_from_config(self.cam2_config)
        
        # Connect to cameras
        results = self.connection_manager.connect_all()
        
        if all(results.values()):
            logger.info("All cameras connected successfully")
            return True
        else:
            logger.error(f"Camera connection results: {results}")
            return False
    
    def run(self):
        """Run the dual camera viewer."""
        if not self.setup_cameras():
            logger.error("Failed to setup cameras")
            return
        
        self.running = True
        
        # Create windows
        cv2.namedWindow("ESP32_CAM_1", cv2.WINDOW_NORMAL)
        cv2.namedWindow("ESP32_CAM_2", cv2.WINDOW_NORMAL)
        
        # Get camera instances
        cam1 = self.connection_manager.get_camera("ESP32_CAM_1")
        cam2 = self.connection_manager.get_camera("ESP32_CAM_2")
        
        logger.info("Starting viewer loop. Press 'q' to quit, 's' to save frames")
        
        while self.running:
            # Read frames
            ret1, frame1 = cam1.read() if cam1 else (False, None)
            ret2, frame2 = cam2.read() if cam2 else (False, None)
            
            # Display frames
            if ret1 and frame1 is not None:
                cv2.imshow("ESP32_CAM_1", frame1)
            
            if ret2 and frame2 is not None:
                cv2.imshow("ESP32_CAM_2", frame2)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                logger.info("Quit requested")
                self.running = False
            elif key == ord('s'):
                logger.info("Saving frame pair")
                if ret1 and ret2:
                    self.frame_capture.save_frame_pair(
                        frame1, frame2,
                        "ESP32_CAM_1", "ESP32_CAM_2"
                    )
                else:
                    logger.warning("Cannot save - one or both frames unavailable")
            elif key == ord('a'):
                logger.info("Saving annotated frames")
                if ret1:
                    self.frame_capture.save_annotated_frame(frame1, "ESP32_CAM_1")
                if ret2:
                    self.frame_capture.save_annotated_frame(frame2, "ESP32_CAM_2")
        
        # Cleanup
        cv2.destroyAllWindows()
        self.connection_manager.disconnect_all()
        logger.info("Viewer stopped")


def main():
    """Main entry point for dual camera viewer."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        viewer = DualCameraViewer()
        viewer.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
