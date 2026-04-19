# 🛡️ SmartEye AI: Advanced Multi-Camera Surveillance System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV">
  <img src="https://img.shields.io/badge/YOLOv8-00FFFF?style=for-the-badge&logo=ultralytics&logoColor=black" alt="YOLOv8">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
</p>

## 📌 Overview
**SmartEye AI** is a professional-grade surveillance solution that leverages State-of-the-Art (SOTA) Computer Vision to transform standard CCTV feeds into intelligent, actionable data streams. Designed for high-security environments, the system automates object detection, tracking, and reporting with a premium, user-centric dashboard.

## 🚀 Key Features (v2.0)

### 🌓 Night Movement Detection
*   **Intelligent Guarding**: Automatically activates high-sensitivity detection between **10 PM and 6 AM**.
*   **Instant Alerts**: Triggers visual/auditory alarms and saves photographic evidence when suspicious activity is detected during restricted hours.

### 📹 Multi-Camera Ecosystem
*   **Parallel Processing**: Concurrent monitoring of up to 4 cameras (Gate, Office, Parking, etc.).
*   **RTSP Support**: Industrial-standard support for IP cameras and local webcams.

### 📊 Professional Dashboard
*   **Smart Categorization**: Live tracking of **Humans**, **Two-Wheelers**, and **Vehicles** in dedicated sidebar sections.
*   **Hybrid Theme**: Premium dark-navigation aesthetic with a clean, high-productivity light workspace.
*   **Real-time Timeline**: Live activity logs and system status monitoring.

### 📝 Automated Reporting
*   **PDF Summaries**: Daily generation of comprehensive PDF reports including activity charts and event logs.
*   **Evidence Archive**: Permanent SQLite storage with easy-to-browse snapshot history.

## 🛠️ Tech Stack
*   **Core Engine**: Python 3.x, Ultralytics YOLOv8, DeepSORT Tracking.
*   **Vision Processing**: OpenCV, EasyOCR (Automatic License Plate Recognition).
*   **Web Interface**: Flask, Vanilla CSS (Glassmorphism), JavaScript.
*   **Reporting**: ReportLab, Matplotlib, Pandas.

## 📥 Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/VishnuVardhanCodes/Smart-Surveillance.git
   cd Smart-Surveillance
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Cameras**
   Edit `config/cameras.json` to add your RTSP links:
   ```json
   {
     "Gate": "rtsp://your_camera_link",
     "Room": "0" 
   }
   ```

4. **Run the Application**
   ```bash
   python main.py
   ```

## 📂 Project Structure
```
├── config/              # Camera configuration files
├── database/            # SQLite storage
├── static/              # CSS, JS, and UI Assets
│   ├── css/
│   └── images/          # Evidence snapshots
├── templates/           # HTML views (Dashboard, History, Reports)
├── detector.py          # Core YOLOv8 inference engine
├── report_generator.py  # PDF & Analytics logic
├── night_detector.py    # Time-based security rules
└── main.py              # Flask server and API entry point
```

## 🤝 Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request to enhance the vision capabilities or UI design.

---
**Developed by [Vishnu Vardhan](https://github.com/VishnuVardhanCodes) during ITC Internship.**
