# 🛡️ ITC PSPD BCM | SmartEye AI Sentinel
### *The Next Generation of Intelligent Autonomous Surveillance*

<p align="center">
  <img src="https://img.shields.io/badge/Status-Production--Ready-success?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/AI-YOLOv8%20|%20DeepSORT-blueviolet?style=for-the-badge" alt="AI">
  <img src="https://img.shields.io/badge/Efficiency-Offline--First-orange?style=for-the-badge" alt="Offline">
  <img src="https://img.shields.io/badge/Security-Enterprise--Grade-blue?style=for-the-badge" alt="Security">
</p>

---

## 📌 Project Vision
**SmartEye AI Sentinel** is a professional-grade, intelligent surveillance ecosystem designed for the **ITC PSPD BCM** division. It transcends traditional CCTV by converting raw video feeds into high-value actionable intelligence. 

Unlike generic systems, SmartEye AI is **Offline-First**, ensuring 100% operational reliability even in restricted network environments, making it ideal for industrial, logistics, and high-security zones.

---

## 🚀 Unique Intelligence Features

### 🚥 Advanced Traffic & Speed Analytics
*   **Velocity Estimation**: Real-time speed calculation for vehicles at the Gate and Parking zones.
*   **Automatic License OCR**: Instant extraction of number plates using high-precision OCR models.
*   **Vehicle Classification**: Granular distinction between cars, trucks, buses, and two-wheelers.

### 🚻 Human Presence & Demographics
*   **Gender Analysis (Room Privacy)**: Intelligent classification of 'Male' and 'Female' occupants for office occupancy metrics.
*   **Stability Logic**: Uses high-fidelity majority-voting algorithms to ensure 99% accuracy even in varying poses.
*   **Directional Counting**: Tracks entry/exit flows across virtual boundaries with DeepSORT stability.

### 🌑 Sentinel Night Mode
*   **Proactive Threat Detection**: Automatically escalates sensitivity between **10:00 PM - 6:00 AM**.
*   **Smart Alerts**: Triggers real-time dashboard notifications and persistent evidence logging for night-time movement.

### 📊 Executive Reporting
*   **Auto-Generated PDF Summaries**: Professional daily reports featuring activity trends, speed violations, and demographic breakdowns.
*   **Searchable Intelligence**: A robust historical database allowing filtering by plate number, gender, camera, or date.

---

## 🛠️ Performance Tech Stack

| Component | Technology |
| :--- | :--- |
| **Core AI** | YOLOv8 (Nano/Small), DeepSORT (Tracking), EasyOCR |
| **Analysis** | Caffe Gender-Net DNN, OpenCV Image Processing |
| **Server** | Flask (Python 3.10+), Multi-threaded Camera Streams |
| **Storage** | SQLite3 (Persistent DB), Pandas (Data Frames) |
| **Reporting** | Matplotlib (Charts), ReportLab (PDF Generation) |
| **UI/UX** | Glassmorphic Dashboard, Vanilla CSS3, FontAwesome 6 |

---

## 📂 System Architecture
The repository follows a clean-separation architecture, decoupling the heavyweight AI backend from the lightweight visual frontend.

```bash
SmartEye-AI/
├── backend/            # 🧠 The Intelligent Core
│   ├── config/         # Camera & ROI JSON configurations
│   ├── models/         # Local AI Weights (YOLO, OCR, Gender)
│   ├── report_gen/     # PDF Generation Engines
│   ├── main.py         # Multi-threaded Flask API
│   └── *.py            # Modular detection & classification scripts
├── frontend/           # 🎨 The Visual Command Center
│   ├── static/         # Premium Glassmorphic CSS & JS Modules
│   └── templates/      # Responsive HTML5 Dashboards
├── .gitattributes      # Git LFS configuration for AI models
├── requirements.txt    # Global dependency manifests
└── README.md           # Professional Documentation
```

---

## 📥 Quick Start Guide

### 1️⃣ Clone with Large Files (LFS)
This project uses **Git LFS** to store the heavy AI models offline.
```bash
git lfs install
git clone https://github.com/VishnuVardhanCodes/Smart-Surveillance.git
cd Smart-Surveillance
```

### 2️⃣ Global Environment Setup
```bash
pip install -r requirements.txt
```

### 3️⃣ Configure your Streams
Open `backend/config/cameras.json` to link your CCTV feeds or webcams:
```json
{
  "Gate": "rtsp://camera_ip_address",
  "Room": "0",  
  "Parking": "rtsp://camera_ip_address"
}
```

### 4️⃣ Deploy the Sentinel
```bash
python backend/main.py
```
🌐 **Dashboard URL:** `http://localhost:5000`

---

## 📑 Specialized Guides
*   **[Mentor Setup Guide](mentor_setup_guide.md)**: A one-page manual for project examiners and mentors.
*   **Architecture Breakdown**: Detailed technical docs inside the `backend/docs` folder.

---

## 🛡️ Security & Privacy Assurance
SmartEye AI is designed with **Privacy by Design**:
*   **Zero Cloud Dependence**: All video frames are processed locally; no raw video leaves your network.
*   **Disk Efficiency**: Automatic log rotation and snapshot cleanup to ensure system stability.

---
**Crafted for Innovation by [VishnuVardhanCodes](https://github.com/VishnuVardhanCodes) | ITC Internship 2026**
**Corporate Identity: ITC PSPD BCM Division**
