from flask import Flask, render_template, Response, request, jsonify, send_from_directory, send_file
import cv2
import os
import threading
from multi_camera_manager import MultiCameraManager
from database import DatabaseManager
from report_generator import ReportGenerator
from datetime import datetime

app = Flask(__name__)
db = DatabaseManager()
camera_manager = MultiCameraManager()
report_gen = ReportGenerator(db)

# Start background processes
camera_manager.start_all()
report_gen.run_scheduler()

@app.route('/')
def index():
    cameras = camera_manager.get_all_camera_names()
    return render_template('dashboard.html', cameras=cameras)

@app.route('/video_feed/<camera_name>')
def video_feed(camera_name):
    def gen_frames():
        while True:
            frame = camera_manager.get_frame(camera_name)
            if frame is None:
                # Show offline placeholder
                placeholder = cv2.imread('static/images/offline.jpg')
                if placeholder is None:
                    # Create black frame with text if image missing
                    import numpy as np
                    placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(placeholder, f"Camera {camera_name} Offline", (150, 240), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                ret, buffer = cv2.imencode('.jpg', placeholder)
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/camera_states')
def camera_states():
    states = {}
    for name in camera_manager.get_all_camera_names():
        counts = camera_manager.get_counts(name)
        states[name] = {
            'status': camera_manager.get_status(name),
            'in': counts[0],
            'out': counts[1]
        }
    return jsonify(states)

@app.route('/api/night_alerts')
def night_alerts():
    alerts = db.get_recent_night_alerts(5)
    return jsonify([dict(row) for row in alerts])

@app.route('/api/stats')
def get_global_stats():
    stats = db.get_global_stats()
    return jsonify(stats)

@app.route('/api/generate_report')
def generate_report():
    date_str = datetime.now().strftime("%Y-%m-%d")
    filepath = report_gen.generate_daily_report(date_str)
    return send_file(filepath, as_attachment=True)

@app.route('/history')
def history():
    detections = db.get_all_detections()
    return render_template('history.html', detections=detections)

@app.route('/reports')
def reports_page():
    report_files = os.listdir('reports/daily_reports')
    pdfs = [f for f in report_files if f.endswith('.pdf')]
    return render_template('reports.html', report_files=sorted(pdfs, reverse=True))

@app.route('/humans')
def humans():
    detections = db.get_detections_by_category(['person'])
    return render_template('history.html', title="HUMAN DETECTIONS", detections=detections)

@app.route('/bikes')
def bikes():
    detections = db.get_detections_by_category(['motorcycle', 'bicycle'])
    return render_template('history.html', title="TWO-WHEELER DETECTIONS", detections=detections)

@app.route('/vehicles')
def vehicles():
    detections = db.get_detections_by_category(['car', 'bus', 'truck'])
    return render_template('history.html', title="VEHICLE DETECTIONS", detections=detections)

@app.route('/api/logs')
def get_logs():
    log_path = 'logs/system.log'
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            lines = f.readlines()
            return jsonify([line.strip() for line in lines[-15:]])
    return jsonify([])

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
