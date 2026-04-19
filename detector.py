import cv2
import os
import time
from datetime import datetime
from ultralytics import YOLO
from tracker import ObjectTracker
from counter import PeopleCounter
from plate_reader import PlateReader
from database import DatabaseManager

class SurveillanceDetector:
    def __init__(self, model_path='yolov8n.pt'):
        # Load YOLOv8 model (default is nano for speed)
        self.model = YOLO(model_path)
        self.tracker = ObjectTracker()
        self.counter = PeopleCounter(line_position=0.6)
        self.plate_reader = PlateReader()
        self.db = DatabaseManager()
        
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
        if not os.path.exists('logs'):
            os.makedirs('logs')

    def log_event(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")

    def save_image(self, frame, obj_type, sub_dir):
        """Save detected object image with timestamp."""
        dir_path = f"images/{sub_dir}"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{obj_type}_{timestamp}.jpg"
        filepath = os.path.join(dir_path, filename)
        cv2.imwrite(filepath, frame)
        # Ensure the path stored in DB uses forward slashes for the web UI
        return filepath.replace('\\', '/')

    def process_frame(self, frame):
        """Process a single frame for detection and tracking."""
        # 1. YOLO Detection
        results = self.model(frame, verbose=False)[0]
        
        detections = []
        for r in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = r
            if int(class_id) in self.target_classes:
                w = x2 - x1
                h = y2 - y1
                detections.append(([x1, y1, w, h], score, int(class_id)))

        # 2. Update Tracker
        tracks = self.tracker.update(detections, frame)
        
        # 3. Update People Count & Get Events
        h, w, _ = frame.shape
        in_count, out_count, crossed_in, crossed_out = self.counter.count(tracks, w, h)
        
        # 4. Handle Crossing Events
        # Handle Entries
        for track in crossed_in:
            class_id = track.get_det_class()
            obj_type = self.target_classes.get(class_id, "unknown")
            # Save Image and Log Entry
            img_path = self.save_image(frame, obj_type, f"{obj_type}s" if obj_type == 'person' else "vehicles")
            self.db.insert_detection(obj_type, img_path, event_type='Entry', track_id=track.track_id)
            self.log_event(f"EVENT: {obj_type} (ID: {track.track_id}) ENTERED across line")

        # Handle Exits
        for track in crossed_out:
            class_id = track.get_det_class()
            obj_type = self.target_classes.get(class_id, "unknown")
            # Log Exit (optional: save image too)
            img_path = self.save_image(frame, obj_type, f"{obj_type}s" if obj_type == 'person' else "vehicles")
            self.db.insert_detection(obj_type, img_path, event_type='Exit', track_id=track.track_id)
            self.log_event(f"EVENT: {obj_type} (ID: {track.track_id}) EXITED across line")

        # 5. Draw visualization
        for track in tracks:
            if not track.is_confirmed():
                continue
                
            track_id = track.track_id
            ltrb = track.to_ltrb()
            class_id = track.get_det_class()
            obj_type = self.target_classes.get(class_id, "unknown")
            
            # Draw bounding box
            color = (0, 255, 0) if obj_type == 'person' else (255, 165, 0)
            cv2.rectangle(frame, (int(ltrb[0]), int(ltrb[1])), (int(ltrb[2]), int(ltrb[3])), color, 2)
            cv2.putText(frame, f"{obj_type} {track_id}", (int(ltrb[0]), int(ltrb[1]) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Draw counting line
        line_y = int(self.counter.line_position * h)
        cv2.line(frame, (0, line_y), (w, line_y), (255, 255, 0), 2)
        cv2.putText(frame, f"IN: {in_count} OUT: {out_count}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        return frame, (in_count, out_count)
