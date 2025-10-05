# ESP32-CAM OpenCV Application

A comprehensive, professional framework for managing and processing video streams from ESP32-CAM devices using OpenCV and Python.

## 🌟 Features

- **📹 Multiple Viewer Options**: GUI-based dual/single camera viewers and web-based interface
- **🔧 Robust Connection Management**: Automatic retry logic and error recovery
- **⚙️ Flexible Configuration**: Environment variables, YAML files, and programmatic configuration
- **🔍 Diagnostic Tools**: Network scanning, connectivity testing, and performance monitoring
- **💾 Frame Capture**: Save individual frames or synchronized pairs
- **🧪 Comprehensive Testing**: Unit tests, integration tests, and mocking support
- **🎯 CLI Interface**: Command-line tools for all operations

## 📁 Directory Structure

```
OpenCV_APP/
├── core/                      # Core functionality
│   ├── config.py             # Configuration management
│   ├── camera_base.py        # Camera base classes
│   ├── connection_manager.py # Connection handling
│   └── diagnostics.py        # Diagnostic utilities
├── viewers/                   # Viewer applications
│   ├── dual_viewer.py        # Dual camera GUI viewer
│   ├── single_viewer.py      # Single camera GUI viewer
│   └── web_viewer.py         # Web-based viewer
├── utils/                     # Utility modules
│   ├── frame_capture.py      # Frame saving utilities
│   ├── network_utils.py      # Network utilities
│   └── mjpeg_parser.py       # MJPEG parsing
├── cli/                       # Command-line interface
│   ├── main_cli.py           # Main CLI entry point
│   └── diagnostic_cli.py     # Diagnostic commands
├── config/                    # Configuration files
│   ├── camera_config.yaml    # Camera configuration
│   └── settings.json         # Application settings
├── tests/                     # Test suite
│   ├── test_cameras.py       # Camera tests
│   ├── test_network.py       # Network tests
│   └── test_integration.py   # Integration tests
└── requirements.txt           # Python dependencies
```

## 🚀 Quick Start

### Installation

1. **Navigate to the OpenCV_APP directory:**
   ```bash
   cd OpenCV_APP
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Configure your ESP32-CAM devices using environment variables or YAML configuration:

**Option 1: Environment Variables**
```bash
export ESP32_CAM_1_IP=192.168.2.88
export ESP32_CAM_2_IP=192.168.2.133
```

**Option 2: YAML Configuration**
Edit `config/camera_config.yaml`:
```yaml
cameras:
  - name: ESP32_CAM_1
    ip: 192.168.2.88
    port: 80
  - name: ESP32_CAM_2
    ip: 192.168.2.133
    port: 80
```

### Usage

#### Dual Camera Viewer (GUI)
```bash
python -m cli.main_cli view
```

Controls:
- `q` - Quit
- `s` - Save synchronized frame pair
- `a` - Save annotated frames

#### Single Camera Viewer (GUI)
```bash
python -m cli.main_cli view-single --camera ESP32_CAM_1
```

#### Web-Based Viewer
```bash
python -m cli.main_cli web --host 0.0.0.0 --port 5000
```
Then open http://localhost:5000 in your browser.

#### Diagnostic Tools
```bash
# Test all cameras
python -m cli.main_cli diagnose

# Test specific camera
python -m cli.diagnostic_cli test-camera --camera ESP32_CAM_1

# Scan network for devices
python -m cli.diagnostic_cli scan-network --subnet 192.168.2

# Generate diagnostic report
python -m cli.diagnostic_cli full-report --output report.json
```

#### Configuration Management
```bash
# Show current configuration
python -m cli.main_cli config-info

# List all cameras
python -m cli.main_cli list-cameras

# Add a new camera
python -m cli.main_cli add-camera --name ESP32_CAM_3 --ip 192.168.2.150
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_cameras.py

# Run with coverage
python -m pytest --cov=. tests/

# Run verbose
python -m pytest -v tests/
```

## 📖 API Usage

### Programmatic Usage

```python
from core import get_config, ConnectionManager, ESP32Camera
from utils import FrameCapture

# Get configuration
config = get_config()

# Create connection manager
manager = ConnectionManager(retry_attempts=3, retry_delay=2)

# Add cameras from configuration
for cam_name in ["ESP32_CAM_1", "ESP32_CAM_2"]:
    cam_config = config.get_camera(cam_name)
    manager.add_camera_from_config(cam_config)

# Connect to all cameras
results = manager.connect_all()

# Read frames
cam1 = manager.get_camera("ESP32_CAM_1")
ret, frame = cam1.read()

# Save frames
fc = FrameCapture()
fc.save_frame(frame, "ESP32_CAM_1")

# Cleanup
manager.disconnect_all()
```

### Mock Camera for Testing

```python
from core import MockCamera

# Create mock camera
mock_cam = MockCamera("TestCam", width=640, height=480)
mock_cam.connect()

# Read frames (generates synthetic frames)
ret, frame = mock_cam.read()
```

## 🔧 Advanced Configuration

### Custom Configuration File

```python
from core import get_config

config = get_config(config_file="/path/to/custom_config.yaml")
```

### Programmatic Configuration

```python
from core import get_config

config = get_config()
config.add_camera("ESP32_CAM_3", "192.168.2.150", 80)
```

## 🛠️ Development

### Code Style

The project uses:
- `black` for code formatting
- `pylint` for linting
- `mypy` for type checking

```bash
# Format code
black OpenCV_APP/

# Run linter
pylint OpenCV_APP/

# Type checking
mypy OpenCV_APP/
```

### Contributing

1. Write tests for new features
2. Ensure all tests pass
3. Follow existing code style
4. Update documentation

## 📝 Architecture

### Core Components

- **CameraBase**: Abstract base class for camera implementations
- **ESP32Camera**: OpenCV-based ESP32-CAM implementation
- **MockCamera**: Test implementation for unit testing
- **ConnectionManager**: Manages multiple camera connections with retry logic
- **AppConfig**: Centralized configuration management

### Utilities

- **FrameCapture**: Frame saving and annotation
- **MJPEGParser**: MJPEG stream parsing
- **NetworkUtils**: Network diagnostics and testing
- **CameraDiagnostics**: Camera-specific diagnostics

### Viewers

- **DualCameraViewer**: OpenCV GUI for two cameras
- **SingleCameraViewer**: OpenCV GUI for single camera
- **WebViewer**: Flask-based web interface

## 🐛 Troubleshooting

### Camera Not Connecting

1. Check camera is powered and on network
2. Verify IP address is correct
3. Test with ping: `ping 192.168.2.88`
4. Run diagnostics: `python -m cli.diagnostic_cli test-camera --camera ESP32_CAM_1`

### Network Issues

1. Ensure devices are on same subnet
2. Check firewall settings
3. Scan network: `python -m cli.diagnostic_cli scan-network --subnet 192.168.2`

### Dependencies

If installation fails:
```bash
# Install OpenCV separately
pip install opencv-python

# Or use conda
conda install -c conda-forge opencv
```

## 📚 Related Documentation

- [ESP32-CAM Main README](../README.md) - Hardware setup and firmware
- [ESP32-CAM Datasheet](https://github.com/espressif/esp32-camera)
- [OpenCV Documentation](https://docs.opencv.org/)

## 📄 License

This project is part of the ESP32_CAM repository. See main repository for license information.

## 🙏 Acknowledgments

Built for the ESP32-CAM dual camera setup project. Designed for easy integration with OpenCV computer vision workflows.
