# 🛡️ SmartEye AI: Advanced Multi-Camera Surveillance System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV">
  <img src="https://img.shields.io/badge/YOLOv8-00FFFF?style=for-the-badge&logo=ultralytics&logoColor=black" alt="YOLOv8">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white" alt="Vercel">
  <img src="https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white" alt="Render">
</p>

## 📌 Project Overview
**SmartEye AI** is a professional-grade, intelligent surveillance solution designed to transform standard security feeds into actionable data streams. By combining **SOTA Computer Vision (YOLOv8)** with robust multi-camera management, the system provides real-time monitoring, automated threat detection, and comprehensive analytics.

Whether for home security, office monitoring, or industrial surveillance, SmartEye AI offers a premium experience with a high-performance backend and a modern, glassmorphic web dashboard.

---

## 🚀 Visionary Features

### 🧠 Intelligent Object Detection & Tracking
*   **Real-time Recognition**: Precision detection of Humans, Motorbikes, Bicycles, Cars, and Trucks.
*   **DeepSORT Integration**: Advanced multi-target tracking that maintains object identity across frames, even through temporary occlusions.
*   **Directional Counting**: Automatically logs entries and exits by monitoring movement across virtual boundaries.

### 🌓 Professional Night Security
*   **Time-Aware Sensitivity**: Automatically escalates detection thresholds between **10:00 PM and 6:00 AM**.
*   **Active Deterrence**: Triggers high-priority visual/auditory alarms on the dashboard when movement is detected during sensitive hours.
*   **Evidence Collection**: High-resolution snapshots are automatically categorized and stored as evidence for every night alert.

### 🚗 Automatic License Plate Recognition (ALPR)
*   **OCR-Powered Extraction**: Integrates **EasyOCR** to automatically read and log vehicle license plates.
*   **Searchable Database**: Plate numbers are stored alongside timestamps and image evidence for rapid lookup in the history section.

### 📊 Command Center & Analytics
*   **Hybrid Dashboard**: A premium dark-sidebar interface paired with a clean, high-productivity workspace.
*   **Real-time Timeline**: A live-updating stream of system events and detections.
*   **Daily PDF Reports**: Automated generation of comprehensive PDF summaries featuring activity charts (**Matplotlib**) and data tables.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend Core** | Python 3.8+, YOLOv8 (Ultralytics), DeepSORT |
| **Computer Vision** | OpenCV, EasyOCR, NumPy |
| **Web Framework** | Flask, Flask-CORS, Python-Dotenv |
| **Frontend UI** | Vanilla JS, HTML5, CSS3 (Glassmorphism), FontAwesome |
| **Data & Storage** | SQLite3, Pandas |
| **Analytics & PDF** | Matplotlib, ReportLab |

---

## 📂 Project Architecture
The project is decoupled into a modular structure for easy scalability and independent deployment.

```bash
Smart-Surveillance/
├── backend/             # 🧠 AI Brain & Server
│   ├── config/          # Camera & system configurations
│   ├── database/        # SQLite persistent storage
│   ├── images/          # Secure evidence snapshots
│   ├── logs/            # Real-time system logs
│   ├── models/          # YOLOv8 Weights & ML Assets
│   ├── reports/         # Generated PDF Archives
│   ├── main.py          # API & Stream Handler
│   └── *.py             # Modular detection & logic engines
├── frontend/            # 🎨 Visual Interface
│   ├── static/          # CSS themes & JS modules
│   └── templates/       # Glassmorphic HTML views
├── .env                 # Environment secrets
├── requirements.txt     # Global dependencies
└── README.md            # Documentation
```

---

## 📥 Getting Started

### 1️⃣ Clone and Prepare
```bash
git clone https://github.com/VishnuVardhanCodes/Smart-Surveillance.git
cd Smart-Surveillance
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Feeds
Edit `backend/config/cameras.json` to manage your streams:
```json
{
  "Front Gate": "rtsp://your_ip_camera_url",
  "Parking": "0" 
}
```

### 4️⃣ Launch System
```bash
python backend/main.py
```
*Access the Command Center at: `http://localhost:5000`*

---

## 🌐 Hybrid Deployment Guide

### **Backend (Render)**
1. Connect your GitHub repository to Render.
2. Set the Root Directory to `backend/`.
3. Build Command: `pip install -r requirements.txt`.
4. Start Command: `python main.py`.

### **Frontend (Vercel)**
1. Connect to Vercel.
2. Select the `frontend/` folder.
3. Configure the backend API URL as an environment variable for real-time data fetching.

---

## 🛡️ Security & Privacy
*   **Local Storage**: All video data stays on your local machine; only event logs and snapshots are stored.
*   **Privacy Masks**: Configurable detection zones to respect surrounding privacy.

## 🤝 Contribution & Feedback
Contributions are what make the open-source community an amazing place to learn and create. 
1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---
**Developed with ❤️ by [VishnuVardhanCodes](https://github.com/VishnuVardhanCodes) | ITC Internship Project 2026**
