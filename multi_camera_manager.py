import cv2
import json
import threading
import time
from detector import SurveillanceDetector

class MultiCameraManager:
    def __init__(self, config_path='config/cameras.json'):
        self.config_path = config_path
        self.cameras = {}
        self.detectors = {}
        self.frames = {}
        self.status = {}
        self.counts = {}
        self.lock = threading.Lock()
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                self.cameras = json.load(f)
            print(f"Loaded {len(self.cameras)} cameras from config.")
        except Exception as e:
            print(f"Error loading camera config: {e}")
            self.cameras = {"Primary": "0"}

    def start_all(self):
        for name, source in self.cameras.items():
            # Source can be '0' (string) or rtsp URL
            cam_source = int(source) if source.isdigit() else source
            thread = threading.Thread(target=self._camera_loop, args=(name, cam_source), daemon=True)
            thread.start()
            print(f"Started thread for camera: {name}")

    def _camera_loop(self, name, source):
        detector = SurveillanceDetector()
        self.detectors[name] = detector
        
        while True:
            cap = cv2.VideoCapture(source)
            if not cap.isOpened():
                print(f"Warning: Could not open camera {name}. Retrying...")
                with self.lock:
                    self.status[name] = "Offline"
                time.sleep(5)
                continue

            with self.lock:
                self.status[name] = "Online"

            while True:
                success, frame = cap.read()
                if not success:
                    print(f"Connection lost for camera {name}. Reconnecting...")
                    with self.lock:
                        self.status[name] = "Offline"
                    break
                
                # Process frame with camera name context for logging
                processed_frame, counts = detector.process_frame(frame, camera_name=name)
                
                with self.lock:
                    self.frames[name] = processed_frame
                    self.counts[name] = counts
                    self.status[name] = "Online"

            cap.release()
            time.sleep(2)

    def get_frame(self, name):
        with self.lock:
            return self.frames.get(name)

    def get_status(self, name):
        with self.lock:
            return self.status.get(name, "Offline")

    def get_counts(self, name):
        with self.lock:
            return self.counts.get(name, (0, 0))

    def get_all_camera_names(self):
        return list(self.cameras.keys())
