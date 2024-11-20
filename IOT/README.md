# Spy Camera Localization Project

This project is designed to detect and locate hidden spy cameras using a Raspberry Pi. It leverages WiFi packet sniffing, RSSI (Received Signal Strength Indicator) analysis, and IMU (Inertial Measurement Unit) data to estimate the camera's location. Below is a description of each file included in the project.

## File Descriptions

### `CombineScript.py`
This script combines RSSI and IMU data into a unified dataset. It performs interpolation and timestamp matching to create a trajectory map that visualizes RSSI values against movement data, enabling accurate localization of hidden cameras.

### `IMUCollect.py`
This script collects raw IMU data, such as accelerometer, gyroscope, and orientation readings, while moving the Raspberry Pi. The data is used to track movement and contribute to trajectory estimation.

### `IMUStepDetect.py`
This script processes the IMU data to detect steps and estimate movement direction. It refines the trajectory map by calculating positional changes based on step detection.

### `collect_rssi.py`
This script captures WiFi packets using the Raspberry Pi’s WiFi dongle in monitor mode. It filters packets based on the MAC address of the target camera and records RSSI values over time, providing the raw data required for camera localization.

### `guide.py`
It uses real-time RSSI data and trajectory information to guide the user toward the hidden camera. It provides directional feedback, such as displaying an arrow on the SenseHAT, to indicate the camera's location based on the strongest RSSI readings.

## How It Works
1. **WiFi Packet Capture**: Use `collect_rssi.py` to capture and log RSSI values from WiFi packets emitted by the hidden camera.
2. **IMU Data Collection**: Use `IMUCollect.py` to record movement data while walking around the room.
3. **Trajectory Mapping**: Use `IMUStepDetect.py` and `CombineScript.py` to merge and analyze RSSI and IMU data, creating a trajectory map that visualizes signal strength and movement.
4. **Real-Time Guidance**: Use `guide.py` to get real-time directional feedback, helping locate the hidden camera efficiently.

## Use Case
This project is especially useful for detecting hidden cameras in sensitive environments, such as hotel rooms or Airbnbs, enhancing personal privacy and security.
