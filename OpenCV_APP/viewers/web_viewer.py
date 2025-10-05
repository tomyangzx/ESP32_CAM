"""
Web-based viewer for ESP32-CAM devices.

This module provides a Flask-based web interface for viewing camera streams
and controlling cameras through a web browser.
"""

from flask import Flask, render_template_string, Response, jsonify
import cv2
import logging
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import get_config, ConnectionManager

logger = logging.getLogger(__name__)

app = Flask(__name__)
connection_manager: Optional[ConnectionManager] = None
config = None


# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ESP32-CAM Web Viewer</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f0f0f0;
        }
        h1 {
            color: #333;
        }
        .camera-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }
        .camera-box {
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .camera-box h2 {
            margin-top: 0;
            color: #555;
        }
        img {
            border: 2px solid #ddd;
            border-radius: 4px;
            max-width: 640px;
        }
        .controls {
            margin-top: 10px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 5px;
        }
        button:hover {
            background-color: #45a049;
        }
        .info {
            margin-top: 10px;
            padding: 10px;
            background-color: #e7f3fe;
            border-left: 4px solid #2196F3;
        }
    </style>
</head>
<body>
    <h1>🎥 ESP32-CAM Web Viewer</h1>
    
    <div class="info">
        <strong>Controls:</strong> Use the buttons below each camera to control the stream.
        Streams update automatically.
    </div>
    
    <div class="camera-container">
        <div class="camera-box">
            <h2>ESP32_CAM_1</h2>
            <img src="{{ url_for('video_feed', camera_name='ESP32_CAM_1') }}" 
                 alt="Camera 1 Stream" onerror="this.src='/static/no-signal.png'">
            <div class="controls">
                <button onclick="refreshStream('ESP32_CAM_1')">🔄 Refresh</button>
                <button onclick="captureFrame('ESP32_CAM_1')">📸 Capture</button>
            </div>
        </div>
        
        <div class="camera-box">
            <h2>ESP32_CAM_2</h2>
            <img src="{{ url_for('video_feed', camera_name='ESP32_CAM_2') }}" 
                 alt="Camera 2 Stream" onerror="this.src='/static/no-signal.png'">
            <div class="controls">
                <button onclick="refreshStream('ESP32_CAM_2')">🔄 Refresh</button>
                <button onclick="captureFrame('ESP32_CAM_2')">📸 Capture</button>
            </div>
        </div>
    </div>
    
    <script>
        function refreshStream(cameraName) {
            const imgs = document.querySelectorAll('img[alt*="' + cameraName + '"]');
            imgs.forEach(img => {
                img.src = img.src.split('?')[0] + '?t=' + new Date().getTime();
            });
        }
        
        function captureFrame(cameraName) {
            fetch('/capture/' + cameraName, {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message || 'Frame captured!');
                })
                .catch(error => {
                    alert('Error capturing frame: ' + error);
                });
        }
    </script>
</body>
</html>
"""


def generate_frames(camera_name: str):
    """
    Generate frames for streaming.
    
    Args:
        camera_name: Name of the camera
        
    Yields:
        JPEG frames in multipart format
    """
    global connection_manager
    
    if not connection_manager:
        return
    
    camera = connection_manager.get_camera(camera_name)
    if not camera:
        logger.error(f"Camera {camera_name} not found")
        return
    
    while True:
        ret, frame = camera.read()
        if not ret or frame is None:
            continue
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        
        frame_bytes = buffer.tobytes()
        
        # Yield frame in multipart format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/')
def index():
    """Render the main page."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/video_feed/<camera_name>')
def video_feed(camera_name: str):
    """
    Video streaming route.
    
    Args:
        camera_name: Name of the camera to stream
    """
    return Response(
        generate_frames(camera_name),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/capture/<camera_name>', methods=['POST'])
def capture_frame(camera_name: str):
    """
    Capture a frame from a camera.
    
    Args:
        camera_name: Name of the camera
    """
    global connection_manager
    
    if not connection_manager:
        return jsonify({'error': 'Connection manager not initialized'}), 500
    
    camera = connection_manager.get_camera(camera_name)
    if not camera:
        return jsonify({'error': f'Camera {camera_name} not found'}), 404
    
    ret, frame = camera.read()
    if ret and frame is not None:
        from utils import FrameCapture
        fc = FrameCapture()
        path = fc.save_frame(frame, camera_name)
        return jsonify({
            'message': f'Frame captured successfully',
            'path': path
        })
    else:
        return jsonify({'error': 'Failed to capture frame'}), 500


@app.route('/status')
def status():
    """Get status of all cameras."""
    global connection_manager
    
    if not connection_manager:
        return jsonify({'error': 'Connection manager not initialized'}), 500
    
    connected = connection_manager.get_connected_cameras()
    health = connection_manager.health_check()
    
    return jsonify({
        'connected_cameras': connected,
        'health_status': health
    })


def initialize_cameras():
    """Initialize camera connections."""
    global connection_manager, config
    
    config = get_config()
    connection_manager = ConnectionManager(retry_attempts=3, retry_delay=2)
    
    # Add cameras
    for cam_name in ["ESP32_CAM_1", "ESP32_CAM_2"]:
        cam_config = config.get_camera(cam_name)
        if cam_config:
            connection_manager.add_camera_from_config(cam_config)
    
    # Connect to cameras
    results = connection_manager.connect_all()
    logger.info(f"Camera connection results: {results}")


def main(host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """
    Run the web viewer.
    
    Args:
        host: Host to bind to
        port: Port to listen on
        debug: Enable debug mode
    """
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Initializing ESP32-CAM Web Viewer")
    initialize_cameras()
    
    logger.info(f"Starting web server on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == "__main__":
    main()
