from flask import Flask, render_template, Response, request, jsonify, send_from_directory
import cv2
import threading
from detector import SurveillanceDetector
from database import DatabaseManager
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
detector = SurveillanceDetector()
db = DatabaseManager()

# Global variables for status and counts
latest_counts = (0, 0)
# Configuration from .env
env_camera = os.getenv('CCTV_RTSP_URL', '0')
# Convert to int if it's a local camera index (like '0', '1')
camera_source = int(env_camera) if env_camera.isdigit() else env_camera

def gen_frames():
    global latest_counts
    cap = cv2.VideoCapture(camera_source)
    
    while True:
        success, frame = cap.read()
        if not success:
            # Reconnect or handle error
            cap = cv2.VideoCapture(camera_source)
            continue
        
        # Process frame
        processed_frame, counts = detector.process_frame(frame)
        latest_counts = counts
        
        # Encode as JPEG
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/counts')
def get_counts():
    return jsonify({
        'in': latest_counts[0],
        'out': latest_counts[1]
    })

@app.route('/history')
def history():
    detections = db.get_all_detections()
    return render_template('history.html', detections=detections)

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/api/search', methods=['POST'])
def api_search():
    data = request.json
    results = db.search_detections(
        date=data.get('date'),
        time=data.get('time'),
        plate_number=data.get('plate_number')
    )
    # Convert sqlite3.Row to dict
    serialized = [dict(row) for row in results]
    return jsonify(serialized)

@app.route('/api/logs')
def get_logs():
    log_path = 'logs/detections.log'
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            lines = f.readlines()
            # Clean and return last 10 logs
            return jsonify([line.strip() for line in lines[-12:]]) 
    return jsonify([])

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

if __name__ == '__main__':
    # Ensure images directories are served as static files if needed
    # (Alternatively, configure Flask to serve from the images/ folder)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
