# Mentor Setup Guide: SmartEye AI Sentinel

This guide contains everything your mentor needs to run the **ITC PSPD BCM | SmartEye AI Sentinel** application on their local machine.

## 1. What to Send to Your Mentor

You should compress (Zip) the full project folder but **exclude** unnecessary files to keep the size small:

| **Include ✅** | **Exclude ❌** |
| :--- | :--- |
| `backend/` (All files) | `__pycache__/` |
| `frontend/` (All files) | `node_modules/` (If any) |
| `requirements.txt` | `.venv/` or `env/` |
| `README.md` | `.git/` folder |
| `.env` (If created) | Large raw video logs (optional) |

---

## 2. Offline Readiness 📶
The application is designed to run **100% offline** after the initial setup. 

- **AI Models:** All models (YOLO & OCR) are stored locally in `backend/models/`.
- **Assets:** Frontend styles and sounds are loaded from `frontend/static/` instead of online CDNs.
- **Requirement:** Internet is only needed **once** to run `pip install -r requirements.txt`. After that, you can disconnect and the system will work perfectly.

---

## 3. Prerequisites for the Mentor

The mentor's laptop will need:
1.  **Python 3.8 to 3.11** (Recommended: 3.10)
2.  **Web Browser** (Chrome or Edge)
3.  **Active Internet Connection** (First run downloads the YOLOv8 AI model automatically).

---

## 3. Setup & Execution Steps

Directly share these steps with your mentor:

### Step 1: Extract & Open Terminal
Extract the zip folder and open a terminal (PowerShell or CMD) inside the `smart surveillance` root directory.

### Step 2: Create a Virtual Environment (Recommended)
This keeps the mentor's system clean:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Step 3: Install Required Libraries
Run this command to install all AI and Web dependencies automatically:
```powershell
pip install -r requirements.txt
```

### Step 4: Run the Application
Start the Flask server:
```powershell
python backend/main.py
```

### Step 5: Access the Dashboard
Once the terminal shows "Running on http://0.0.0.0:5000", open the browser and go to:
**`http://localhost:5000`**

---

## 4. Key Features to Demonstrate
*   **Live Dashboard:** Real-time multi-camera detection (uses placeholders if no real cameras are linked).
*   **Analytics:** Human, Two-Wheeler, and Vehicle counts.
*   **History Logs:** Full database view of all past detections.
*   **Search Page:** Filter detections by Date, Time, or Number Plate.
*   **Daily Reports:** Automatically generated PDF reports with AI-driven charts.

---

> [!NOTE]
> On the very first run, the system will download `yolov8n.pt` (approx. 6MB). This is normal and only happens once.
