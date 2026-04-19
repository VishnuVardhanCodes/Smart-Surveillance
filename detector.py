import cv2
import os
import time
from datetime import datetime
from ultralytics import YOLO
from tracker import ObjectTracker
from counter import PeopleCounter
from plate_reader import PlateReader
from database import DatabaseManager
from night_detector import NightDetector

class SurveillanceDetector:
    def __init__(self, model_path='yolov8n.pt'):
        # Load YOLOv8 model
        self.model = YOLO(model_path)
        self.tracker = ObjectTracker()
        self.counter = PeopleCounter(line_position=0.6)
        self.plate_reader = PlateReader()
        self.db = DatabaseManager()
        self.night_detector = NightDetector()
        
        self.target_classes = {
            0: 'person',
            1: 'bicycle',
            2: 'car',
            3: 'motorcycle',
            5: 'bus',
            7: 'truck'
        }
        
        # Log directory
        self.log_file = 'logs/detections.log'
        self.system_log = 'logs/system.log'
        for path in ['logs', 'images/persons', 'images/vehicles', 'images/plates']:
            if not os.path.exists(path):
                os.makedirs(path)

    def log_system_event(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.system_log, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")

    def save_image(self, frame, obj_type, sub_dir, x1=None, y1=None, x2=None, y2=None):
        """Save detected object image with timestamp. Optional crop support."""
        dir_path = f"images/{sub_dir}"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{obj_type}_{timestamp}.jpg"
        filepath = os.path.join(dir_path, filename)
        
        if x1 is not None and y1 is not None:
            # Save cropped image
            crop = frame[int(y1):int(y2), int(x1):int(x2)]
            if crop.size > 0:
                cv2.imwrite(filepath, crop)
            else:
                cv2.imwrite(filepath, frame)
        else:
            cv2.imwrite(filepath, frame)
            
        return filepath.replace('\\', '/')

    def process_frame(self, frame, camera_name='Main'):
        """Process a single frame for detection and tracking."""
        results = self.model(frame, verbose=False)[0]
        
        detections = []
        for r in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = r
            if int(class_id) in self.target_classes:
                w = x2 - x1
                h = y2 - y1
                detections.append(([x1, y1, w, h], score, int(class_id)))

        # Update Tracker
        tracks = self.tracker.update(detections, frame)
        
        # Update People Count
        h, w, _ = frame.shape
        in_count, out_count, crossed_in, crossed_out = self.counter.count(tracks, w, h)
        
        # Handle Events
        for track in crossed_in + crossed_out:
            event_type = 'Entry' if track in crossed_in else 'Exit'
            class_id = track.get_det_class()
            obj_type = self.target_classes.get(class_id, "unknown")
            ltrb = track.to_ltrb()
            
            # 1. OCR for Vehicles
            plate_number = None
            if obj_type in ['car', 'bus', 'truck', 'motorcycle']:
                crop = frame[int(ltrb[1]):int(ltrb[3]), int(ltrb[0]):int(ltrb[2])]
                if crop.size > 0:
                    plate_number = self.plate_reader.read_plate(crop)
            
            # 2. Save Evidence
            img_path = self.save_image(frame, obj_type, f"{obj_type}s" if obj_type == 'person' else "vehicles")
            
            # 3. Handle Night Alert
            if self.night_detector.should_trigger_alert(obj_type):
                alert_img = self.save_image(frame, f"night_{obj_type}", "vehicles", ltrb[0], ltrb[1], ltrb[2], ltrb[3])
                self.db.insert_night_alert(obj_type, alert_img, plate_number, camera_name)
                self.log_system_event(f"NIGHT ALERT: {obj_type} detected at {camera_name}")
            
            # 4. Standard Detection Log
            self.db.insert_detection(obj_type, img_path, event_type, track.track_id, plate_number, camera_name)
            self.log_system_event(f"EVENT: {obj_type} ({event_type}) at {camera_name}")

        # Visualization
        for track in tracks:
            if not track.is_confirmed(): continue
            ltrb = track.to_ltrb()
            obj_type = self.target_classes.get(track.get_det_class(), "unknown")
            color = (0, 255, 0) if obj_type == 'person' else (255, 165, 0)
            cv2.rectangle(frame, (int(ltrb[0]), int(ltrb[1])), (int(ltrb[2]), int(ltrb[3])), color, 2)
            cv2.putText(frame, f"{obj_type} {track.track_id}", (int(ltrb[0]), int(ltrb[1]) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        line_y = int(self.counter.line_position * h)
        cv2.line(frame, (0, line_y), (w, line_y), (255, 255, 0), 2)
        return frame, (in_count, out_count)
