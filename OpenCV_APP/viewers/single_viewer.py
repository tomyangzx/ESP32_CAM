"""
Single camera viewer for ESP32-CAM devices.

This module provides a simple GUI application for viewing a stream
from a single ESP32-CAM device.
"""

import cv2
import logging
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import get_config, ESP32Camera
from utils import FrameCapture

logger = logging.getLogger(__name__)


class SingleCameraViewer:
    """Viewer application for single ESP32-CAM."""
    
    def __init__(self, camera_name: str = "ESP32_CAM_1", config_file: Optional[str] = None):
        """
        Initialize single camera viewer.
        
        Args:
            camera_name: Name of the camera to view
            config_file: Optional path to configuration file
        """
        self.config = get_config(config_file)
        self.camera_name = camera_name
        self.frame_capture = FrameCapture()
        self.camera: Optional[ESP32Camera] = None
        self.running = False
        
        # Get camera configuration
        cam_config = self.config.get_camera(camera_name)
        if not cam_config:
            raise ValueError(f"Camera {camera_name} not found in configuration")
        
        self.camera = ESP32Camera(cam_config.name, cam_config.stream_url)
        logger.info(f"Single camera viewer initialized for {camera_name}")
    
    def connect(self) -> bool:
        """
        Connect to the camera.
        
        Returns:
            True if connection successful, False otherwise
        """
        logger.info(f"Connecting to {self.camera_name}...")
        return self.camera.connect()
    
    def run(self):
        """Run the single camera viewer."""
        if not self.connect():
            logger.error("Failed to connect to camera")
            return
        
        self.running = True
        
        # Create window
        window_name = f"{self.camera_name} - Press 'q' to quit, 's' to save"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        logger.info("Starting viewer loop")
        frame_count = 0
        
        while self.running:
            # Read frame
            ret, frame = self.camera.read()
            
            if ret and frame is not None:
                frame_count += 1
                
                # Add frame counter overlay
                cv2.putText(frame, f"Frame: {frame_count}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Display frame
                cv2.imshow(window_name, frame)
            else:
                logger.warning("Failed to read frame")
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                logger.info("Quit requested")
                self.running = False
            elif key == ord('s'):
                if ret and frame is not None:
                    logger.info("Saving frame")
                    self.frame_capture.save_frame(frame, self.camera_name)
                else:
                    logger.warning("Cannot save - frame unavailable")
            elif key == ord('a'):
                if ret and frame is not None:
                    logger.info("Saving annotated frame")
                    self.frame_capture.save_annotated_frame(frame, self.camera_name)
        
        # Cleanup
        cv2.destroyAllWindows()
        self.camera.disconnect()
        logger.info(f"Viewer stopped. Total frames: {frame_count}")


def main(camera_name: str = "ESP32_CAM_1"):
    """
    Main entry point for single camera viewer.
    
    Args:
        camera_name: Name of the camera to view
    """
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        viewer = SingleCameraViewer(camera_name)
        viewer.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


if __name__ == "__main__":
    import sys
    camera = sys.argv[1] if len(sys.argv) > 1 else "ESP32_CAM_1"
    main(camera)
