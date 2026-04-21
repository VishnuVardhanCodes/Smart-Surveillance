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
from speed_estimator import SpeedEstimator
from gender_classifier import GenderClassifier


# ─────────────────────────────────────────────────────────────────────────────
# Camera role constants – matched against camera names from cameras.json
# ─────────────────────────────────────────────────────────────────────────────
GATE_CAMERA    = 'Gate'
ROOM_CAMERA    = 'Room'
PARKING_CAMERA = 'Parking'


class SurveillanceDetector:
    def __init__(self, model_path=None, camera_name='Main'):
        # Base directory (backend/)
        self.base_dir    = os.path.dirname(os.path.abspath(__file__))
        self.camera_name = camera_name

        if model_path is None:
            model_path = os.path.join(self.base_dir, 'yolov8n.pt')

        # Core AI components
        self.model         = YOLO(model_path)
        self.tracker       = ObjectTracker()
        self.counter       = PeopleCounter(line_position=0.6)
        self.plate_reader  = PlateReader()
        self.db            = DatabaseManager()
        self.night_detector = NightDetector()

        # ── Change 1: Speed Estimator (Gate only) ────────────────────────
        self.speed_estimator = SpeedEstimator()

        # ── Change 2: Gender Classifier (Room only) ───────────────────────
        self.gender_classifier = GenderClassifier()
        self.male_count   = 0
        self.female_count = 0

        # Which YOLO classes we care about
        self.target_classes = {
            0: 'person',
            1: 'bicycle',
            2: 'car',
            3: 'motorcycle',
            5: 'bus',
            7: 'truck'
        }

        # Per-frame live speed overlay { track_id: speed_kmh }
        self._live_speeds: dict  = {}
        self._gender_cache: dict = {}  # track_id -> gender string

        # Log paths
        self.log_file   = os.path.join(self.base_dir, 'logs', 'detections.log')
        self.system_log = os.path.join(self.base_dir, 'logs', 'system.log')

        for path in ['logs', 'images/persons', 'images/vehicles', 'images/plates']:
            full_path = os.path.join(self.base_dir, path)
            if not os.path.exists(full_path):
                os.makedirs(full_path)

    # ─────────────────────────────────────────────────────────────────────
    def log_system_event(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.system_log, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")

    # ─────────────────────────────────────────────────────────────────────
    def save_image(self, frame, obj_type, sub_dir,
                   x1=None, y1=None, x2=None, y2=None) -> str:
        """Save detected object image. Returns relative path for DB storage."""
        dir_path = os.path.join(self.base_dir, "images", sub_dir)
        os.makedirs(dir_path, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename  = f"{obj_type}_{timestamp}.jpg"
        filepath  = os.path.join(dir_path, filename)
        rel_path  = f"images/{sub_dir}/{filename}"

        if x1 is not None and y1 is not None:
            crop = frame[int(y1):int(y2), int(x1):int(x2)]
            cv2.imwrite(filepath, crop if crop.size > 0 else frame)
        else:
            cv2.imwrite(filepath, frame)

        return rel_path

    # ─────────────────────────────────────────────────────────────────────
    def process_frame(self, frame, camera_name: str = None):
        """
        Process a single video frame.

        Returns: (annotated_frame, (in_count, out_count))
        """
        camera_name = camera_name or self.camera_name
        is_gate     = (camera_name == GATE_CAMERA)
        is_room     = (camera_name == ROOM_CAMERA)
        is_parking  = (camera_name == PARKING_CAMERA)

        # run prediction with optimized thresholds
        # conf=0.20 for faster/more sensitive detection, iou=0.5 to clean up double boxes
        results    = self.model(frame, verbose=False, conf=0.20, iou=0.5)[0]
        detections = []

        for r in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = r
            if int(class_id) in self.target_classes:
                w = x2 - x1
                h = y2 - y1
                detections.append(([x1, y1, w, h], score, int(class_id)))

        # Update tracker
        tracks = self.tracker.update(detections, frame)

        # Update crossing counter
        frame_h, frame_w, _ = frame.shape
        in_count, out_count, crossed_in, crossed_out = self.counter.count(
            tracks, frame_w, frame_h
        )

        # ── Change 1: Update speed estimates for gate / parking ───────────
        active_ids = set()
        for track in tracks:
            if not track.is_confirmed():
                continue
            ltrb = track.to_ltrb()
            cx   = (ltrb[0] + ltrb[2]) / 2
            cy   = (ltrb[1] + ltrb[3]) / 2
            tid  = track.track_id
            active_ids.add(tid)

            if is_gate or is_parking:
                speed = self.speed_estimator.update(tid, cx, cy)
                self._live_speeds[tid] = speed

        # Cleanup speeds and gender cache for lost tracks
        self.speed_estimator.cleanup(active_ids)
        for tid in list(self._live_speeds.keys()):
            if tid not in active_ids:
                del self._live_speeds[tid]
        
        for tid in list(self._gender_cache.keys()):
            if tid not in active_ids:
                del self._gender_cache[tid]

        # ── Handle crossing events ────────────────────────────────────────
        for track in crossed_in + crossed_out:
            event_type = 'Entry' if track in crossed_in else 'Exit'
            class_id   = track.get_det_class()
            obj_type   = self.target_classes.get(class_id, "unknown")
            ltrb       = track.to_ltrb()
            tid        = track.track_id

            x1, y1, x2, y2 = int(ltrb[0]), int(ltrb[1]), int(ltrb[2]), int(ltrb[3])
            crop = frame[y1:y2, x1:x2]

            # ── Number-plate OCR: Gate AND Parking cameras ─────────────
            plate_number = None
            plate_img_path = None
            if obj_type in ['car', 'bus', 'truck', 'motorcycle']:
                if is_gate or is_parking:
                    if crop.size > 0:
                        plate_number = self.plate_reader.read_plate(crop)
                    if plate_number:
                        # Save a dedicated plate crop image
                        plate_img_path = self.save_image(
                            frame, f"plate_{obj_type}", "plates",
                            x1, y1, x2, y2
                        )
                        self.log_system_event(
                            f"PLATE: {plate_number} | {obj_type} | "
                            f"{event_type} | {camera_name}"
                        )

            # ── Speed (Gate / Parking) ────────────────────────────────
            speed_kmh = None
            if (is_gate or is_parking) and obj_type != 'person':
                speed_kmh = self._live_speeds.get(tid, 0.0)

            # ── Gender classification (Room camera – persons only) ────
            gender = None
            if is_room and obj_type == 'person':
                if crop.size > 0:
                    gender = self.gender_classifier.classify(crop)
                    # Update running male/female counts on crossing
                    if gender == 'Male':
                        self.male_count += 1
                    elif gender == 'Female':
                        self.female_count += 1

            # ── Save evidence image ───────────────────────────────────
            sub_dir   = "persons" if obj_type == 'person' else "vehicles"
            img_path  = self.save_image(frame, obj_type, sub_dir)

            # ── Night alert ───────────────────────────────────────────
            if self.night_detector.should_trigger_alert(obj_type):
                alert_img = self.save_image(
                    frame, f"night_{obj_type}", "vehicles",
                    x1, y1, x2, y2
                )
                self.db.insert_night_alert(
                    obj_type, alert_img, plate_number, camera_name
                )
                self.log_system_event(
                    f"NIGHT ALERT: {obj_type} at {camera_name}"
                )

            # ── Persist to DB ─────────────────────────────────────────
            self.db.insert_detection(
                object_type  = obj_type,
                image_path   = img_path,
                event_type   = event_type,
                track_id     = tid,
                plate_number = plate_number,
                camera_name  = camera_name,
                speed_kmh    = speed_kmh,
                gender       = gender,
                plate_img_path = plate_img_path,
            )
            self.log_system_event(
                f"EVENT: {obj_type} ({event_type}) at {camera_name}"
                + (f" | {speed_kmh:.1f} km/h" if speed_kmh else "")
                + (f" | Plate: {plate_number}" if plate_number else "")
                + (f" | Gender: {gender}" if gender else "")
            )

        # ── Visualization ─────────────────────────────────────────────────
        for track in tracks:
            if not track.is_confirmed():
                continue
            ltrb     = track.to_ltrb()
            obj_type = self.target_classes.get(track.get_det_class(), "unknown")
            tid      = track.track_id
            color    = (0, 255, 0) if obj_type == 'person' else (255, 165, 0)

            cv2.rectangle(
                frame,
                (int(ltrb[0]), int(ltrb[1])),
                (int(ltrb[2]), int(ltrb[3])),
                color, 2
            )

            # Build label
            label = f"{obj_type} #{tid}"

            # ── Append speed on Gate / Parking ─────────────────────
            if (is_gate or is_parking) and obj_type != 'person':
                spd = self._live_speeds.get(tid, 0.0)
                label += f"  {spd:.1f} km/h"

            # ── Append gender on Room (Cached version) ───────────────
            if is_room and obj_type == 'person':
                if tid not in self._gender_cache:
                    ltrb2 = track.to_ltrb()
                    crop2 = frame[int(ltrb2[1]):int(ltrb2[3]),
                                  int(ltrb2[0]):int(ltrb2[2])]
                    if crop2.size > 0:
                        g = self.gender_classifier.classify(crop2)
                        self._gender_cache[tid] = g
                
                g = self._gender_cache.get(tid, "Unknown")
                label += f"  {g}"
                # Colour-code: blue=Male, pink=Female
                color = (255, 80, 0) if g == 'Male' else (147, 20, 255)
                cv2.rectangle(
                    frame,
                    (int(ltrb[0]), int(ltrb[1])),
                    (int(ltrb[2]), int(ltrb[3])),
                    color, 2
                )

            cv2.putText(
                frame, label,
                (int(ltrb[0]), int(ltrb[1]) - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
            )

        # ── Entry / Exit boundary line ────────────────────────────────────
        line_y    = int(self.counter.line_position * frame_h)
        buffer_px = int(self.counter.buffer_size * frame_h / 2)

        cv2.line(frame, (0, line_y - buffer_px), (frame_w, line_y - buffer_px),
                 (100, 100, 100), 1)
        cv2.line(frame, (0, line_y + buffer_px), (frame_w, line_y + buffer_px),
                 (100, 100, 100), 1)
        cv2.line(frame, (0, line_y), (frame_w, line_y), (0, 255, 255), 3)
        cv2.putText(frame, "ENTRY / EXIT BOUNDARY",
                    (10, line_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        return frame, (in_count, out_count)

    # ─────────────────────────────────────────────────────────────────────
    def get_gender_counts(self) -> tuple:
        """Return (male_count, female_count) for this detector instance."""
        return self.male_count, self.female_count
