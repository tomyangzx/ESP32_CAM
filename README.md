# ESP32 CAM Project

A hobby project utilizing two ESP32 CAM modules for various camera-based applications.

## Table of Contents
- [Project Overview](#project-overview)
- [Hardware Setup](#hardware-setup)
- [Flashing Instructions](#flashing-instructions)
- [Device Configuration](#device-configuration)
- [Development Environment](#development-environment)
- [OpenCV Application](#opencv-application)
- [Network Configuration](#network-configuration)
- [Collaboration Notes](#collaboration-notes)

## Project Overview

This project involves working with ESP32 CAM modules to create camera-based IoT applications. The project is built using PlatformIO and supports web-based camera streaming.

## Hardware Setup

### Required Components
- 2x ESP32 CAM modules
- USB programmer/uploader board
- Connecting cables

### Board Layout
![ESP32 CAM Setup](image.png)

## Flashing Instructions

### Prerequisites
Download and install CH34x USB drivers:
- **Driver Download**: [CH34x Windows Driver v3.4](https://sparks.gogo.co.nz/assets/_site_/downloads/CH34x_Install_Windows_v3_4.zip)
- Compatible with both Arduino IDE and PlatformIO

### Flashing Procedure
1. **Press and hold** the IOD button on the uploader board
2. **Press** the Reset button on the ESP32 CAM board 
   > ⚠️ Note: Use the reset button on the ESP32 CAM, not the uploader board
3. **Release** the Reset button first, then release the IOD button
4. Begin upload process in your IDE

## Device Configuration

### Device #1
- **IP Address**: `192.168.2.88`
- **Hostname**: `esp32-9DBF24.sphairon.box`
- **MAC Address**: `ec:62:60:9d:bf:24`
- **Web Interface**: [http://192.168.2.88](http://192.168.2.88)

### Device #2
- **IP Address**: `192.168.2.133`
- **Hostname**: `esp32-9B2468.sphairon.box`
- **MAC Address**: `c8:f0:9e:9b:24:68`
- **Web Interface**: [http://192.168.2.133](http://192.168.2.133)

## Development Environment

### OpenCV Virtual Environment Setup

```powershell
# Navigate to project directory
cd C:\Users\tomya\my_project

# Activate virtual environment
venv\Scripts\activate

# Deactivate when done
deactivate
```

### Project Structure
```
ESP32_CAM/
├── OpenCV_APP/           # Python OpenCV application framework
│   ├── core/            # Core camera and config management
│   ├── viewers/         # GUI and web viewers
│   ├── utils/           # Utility functions
│   ├── cli/             # Command-line interface
│   ├── config/          # Configuration files
│   ├── tests/           # Test suite
│   └── README.md        # OpenCV_APP documentation
├── src/                 # ESP32 firmware source
│   └── main.cpp
├── platformio.ini
├── .gitmodules
├── README.md
├── image.png
└── ...
```

> **Note**: The ESP32 firmware provides the camera streaming functionality, while the OpenCV_APP directory contains a professional Python framework for processing and viewing the camera streams.

## OpenCV Application

The `OpenCV_APP` directory contains a comprehensive Python framework for working with ESP32-CAM streams.

### Features

- **🎥 Multiple Viewer Options**: GUI-based dual/single camera viewers and web interface
- **🔧 Robust Connection Management**: Automatic retry logic and error recovery
- **⚙️ Flexible Configuration**: Environment variables, YAML files, and programmatic setup
- **🔍 Diagnostic Tools**: Network scanning, connectivity testing, performance monitoring
- **💾 Frame Capture**: Save individual frames or synchronized pairs
- **🧪 Comprehensive Testing**: Full test suite with mocking support

### Quick Start

1. **Install Python dependencies:**
   ```bash
   cd OpenCV_APP
   pip install -r requirements.txt
   ```

2. **Configure cameras (optional):**
   ```bash
   export ESP32_CAM_1_IP=192.168.2.88
   export ESP32_CAM_2_IP=192.168.2.133
   ```

3. **Run dual camera viewer:**
   ```bash
   python -m cli.main_cli view
   ```

4. **Run web interface:**
   ```bash
   python -m cli.main_cli web
   # Access at http://localhost:5000
   ```

5. **Run diagnostics:**
   ```bash
   python -m cli.main_cli diagnose
   ```

For detailed documentation, see [OpenCV_APP/README.md](OpenCV_APP/README.md).

## Network Configuration

Both ESP32 CAM devices are configured to work within the local network (`192.168.2.x` subnet). Ensure your development machine is on the same network for direct communication.

## Collaboration Notes

- **Potential Collaboration**: Check possible interaction with Leo Chen
- **Development Focus**: Camera streaming and IoT applications

## Security Notes

- 🔒 **WiFi credentials** are stored in `src/wifi_config.h` which is **not committed to git**
- 🔒 Keep your `wifi_config.h` file local and secure
- 🔒 Never commit WiFi passwords to version control
- 🔒 Use the provided template system for secure credential management

---

## Getting Started

### 1. Clone and Setup
```bash
git clone https://github.com/tomyangzx/ESP32_CAM.git
cd ESP32_CAM
```

### 2. Configure WiFi Credentials
Run the setup script to create your local WiFi configuration:

**Windows:**
```cmd
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

**Manual Setup:**
```bash
cp src/wifi_config.h.template src/wifi_config.h
# Edit src/wifi_config.h with your WiFi credentials
```

### 3. Update WiFi Settings
Edit `src/wifi_config.h` and replace the placeholder values:
```cpp
const char* WIFI_SSID = "your_actual_wifi_name";
const char* WIFI_PASSWORD = "your_actual_password";
```

### 4. Configure Device Name (Optional)
For multiple devices, edit `src/main_enhanced.cpp`:
```cpp
const char* device_name = "ESP32_CAM_1";  // Change to "ESP32_CAM_2" for second device
```

### 5. Flash Firmware
1. Install PlatformIO extension in VS Code
2. Follow the [flashing instructions](#flashing-instructions)
3. Upload the firmware to your ESP32-CAM

### 6. Access Web Interface
After flashing, access your device at the IP addresses shown in serial output or use the [configured addresses](#device-configuration)

