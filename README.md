# ESP32 CAM Project

A hobby project utilizing two ESP32 CAM modules for various camera-based applications.

## Table of Contents
- [Project Overview](#project-overview)
- [Hardware Setup](#hardware-setup)
- [Flashing Instructions](#flashing-instructions)
- [Device Configuration](#device-configuration)
- [Development Environment](#development-environment)
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
├── esp32_cam_firmware/    (submodule - ESP32 camera firmware)
│   ├── src/
│   │   └── main.cpp
│   └── platformio.ini
├── .gitmodules
├── README.md
├── image.png
└── ...
```

> **Note**: The ESP32 firmware code is managed as a git submodule for easier integration with OpenCV dual camera processing.

## Network Configuration

Both ESP32 CAM devices are configured to work within the local network (`192.168.2.x` subnet). Ensure your development machine is on the same network for direct communication.

## Collaboration Notes

- **Potential Collaboration**: Check possible interaction with Leo Chen
- **Development Focus**: Camera streaming and IoT applications

---

## Getting Started

1. Clone this repository
   ```bash
   git clone https://github.com/tomyangzx/ESP32_CAM.git
   cd ESP32_CAM
   ```

2. Initialize and update submodules
   ```bash
   git submodule init
   git submodule update
   ```

3. Install PlatformIO extension in VS Code
4. Navigate to the `esp32_cam_firmware` directory and flash the firmware following the [flashing instructions](#flashing-instructions)
5. Access the web interface using the device IP addresses listed above

