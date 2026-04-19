# 🛡️ Advanced Smart Surveillance System (v2.0)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV">
  <img src="https://img.shields.io/badge/YOLOv8-00FFFF?style=for-the-badge&logo=ultralytics&logoColor=black" alt="YOLOv8">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
</p>

## 📌 Project Overview

**SmartEye AI v2.0** is an enterprise-grade AI surveillance dashboard. This version upgrades from a single-camera setup to a **Multi-Camera Command Center**, featuring real-time object detection, night movement alerts, and automated PDF reporting.

---

## ✨ New Advanced Features (v2.0)

- 🎥 **Multi-Camera Support**: Simultaneous monitoring of Gate, Room, and Parking via `config/cameras.json`.
- 🌙 **Night Movement Detection**: Automated alerts and logging for suspicious activity between **10 PM and 6 AM**.
- 📊 **Automated PDF Reports**: Daily generation of activity summaries including charts and statistics at **23:59**.
- 💎 **Premium Glassmorphism UI**: High-end white theme with animated cards, live status indicators, and a responsive grid layout.
- 📡 **Camera Health Monitoring**: Real-time detection of camera online/offline statuses with visual warnings.
- 🕒 **Activity Timeline**: Scrollable live feed of all system events and detections.
- 🆔 **License Plate Recognition (ALPR)**: Extraction and logging of number plates with cropped evidence storage.

---

## 🏗️ System Architecture

```mermaid
graph TD
    A[Multiple RTSP Streams] --> B[Multi-Camera Manager]
    B --> C[Independent YOLOv8 Pipelines]
    C --> D[Object Tracker & Counter]
    D --> E{Event Handler}
    E -->|Normal| F[Detection Log]
    E -->|Night Time| G[Night Alert System]
    F --> H[(SQLite Database)]
    G --> H
    H --> I[Automated PDF Generator]
    H --> J[Premium Flask Dashboard]
    J --> K[Real-time UI Updates]
```

---

## 📂 Project Structure

```text
smart-surveillance/
├── config/              # Camera & System configurations
├── database/            # SQLite storage (surveillance.db)
├── detection/           # CV Logic (Detector, Tracker, Counter)
├── reports/             # Generated Daily PDF Reports
├── logs/                # System & Detection logs
├── images/              # Evidence snapshots (organized by camera/type)
├── static/              # Premium CSS, JS & Assets
├── templates/           # Flask HTML templates
├── main.py              # Application Entry Point
├── multi_camera_manager.py
├── report_generator.py
└── night_detector.py
```

---

## ⚙️ Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Cameras**:
   Edit `config/cameras.json` to add your RTSP links:
   ```json
   {
     "Gate": "rtsp://...",
     "Parking": "rtsp://..."
   }
   ```

3. **Run**:
   ```bash
   python main.py
   ```

---

## 👨‍💻 Author
**P. Vishnu Vardhan**  
*Internship Project — ITC Limited (PSPD)*
