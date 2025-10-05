@echo off
REM ESP32-CAM Project Setup Script for Windows
REM This script helps set up the WiFi configuration

echo ESP32-CAM Project Setup
echo ======================

REM Check if wifi_config.h already exists
if exist "src\wifi_config.h" (
    echo ✓ WiFi configuration file already exists: src\wifi_config.h
    echo   If you need to update WiFi credentials, edit this file directly.
) else (
    echo Creating WiFi configuration file...
    
    REM Copy template to actual config file
    if exist "src\wifi_config.h.template" (
        copy "src\wifi_config.h.template" "src\wifi_config.h" >nul
        echo ✓ Created src\wifi_config.h from template
        echo ⚠️  IMPORTANT: Edit src\wifi_config.h and update your WiFi credentials!
        echo    This file will be ignored by git for security.
    ) else (
        echo ❌ Template file not found: src\wifi_config.h.template
        pause
        exit /b 1
    )
)

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Edit src\wifi_config.h with your WiFi credentials
echo 2. Update device_name in main_enhanced.cpp if needed
echo 3. Flash the firmware to your ESP32-CAM
echo.
echo Files to configure:
echo - src\wifi_config.h (your WiFi settings)
echo - src\main_enhanced.cpp (device name and other settings)
echo.
pause