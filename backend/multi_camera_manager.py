import cv2
import json
import threading
import time
import os
from detector import SurveillanceDetector


class MultiCameraManager:
    def __init__(self, config_path=None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.config_path = os.path.join(base_dir, 'config', 'cameras.json')
        else:
            self.config_path = config_path

        self.cameras   = {}   # name -> source string
        self.detectors = {}   # name -> SurveillanceDetector
        self.frames    = {}   # name -> latest processed frame
        self.status    = {}   # name -> "Online" | "Offline"
        self.counts    = {}   # name -> (in_count, out_count)
        self.lock      = threading.Lock()
        self.load_config()

    # ─────────────────────────────────────────────────────────────────────
    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                self.cameras = json.load(f)
            print(f"[CameraManager] Loaded {len(self.cameras)} camera(s).")
        except Exception as e:
            print(f"[CameraManager] Error loading config: {e}")
            self.cameras = {"Primary": "0"}

    # ─────────────────────────────────────────────────────────────────────
    def start_all(self):
        for name, source in self.cameras.items():
            cam_source = int(source) if source.isdigit() else source
            thread = threading.Thread(
                target=self._camera_loop,
                args=(name, cam_source),
                daemon=True
            )
            thread.start()
            print(f"[CameraManager] Started thread for camera: {name}")

    # ─────────────────────────────────────────────────────────────────────
    def _camera_loop(self, name: str, source):
        """Per-camera capture + detection loop (runs in its own thread)."""
        # Create a detector instance scoped to this camera
        detector = SurveillanceDetector(camera_name=name)
        with self.lock:
            self.detectors[name] = detector

        while True:
            cap = cv2.VideoCapture(source)

            if not cap.isOpened():
                print(f"[CameraManager] Could not open {name}. Retrying in 5 s…")
                with self.lock:
                    self.status[name] = "Offline"
                time.sleep(5)
                continue

            with self.lock:
                self.status[name] = "Online"

            while True:
                # Read multiple frames to clear the buffer and get the VERY LATEST one
                # This ensures we don't process "old" laggy frames
                for _ in range(5):
                    cap.grab()
                success, frame = cap.read()

                if not success:
                    print(f"[CameraManager] Lost connection: {name}. Reconnecting…")
                    with self.lock:
                        self.status[name] = "Offline"
                    break

                # Run detection (pass camera_name for role-specific logic)
                processed_frame, counts = detector.process_frame(
                    frame, camera_name=name
                )

                with self.lock:
                    self.frames[name]  = processed_frame
                    self.counts[name]  = counts
                    self.status[name]  = "Online"

            cap.release()
            time.sleep(2)

    # ─────────────────────────────────────────────────────────────────────
    # Public accessors
    # ─────────────────────────────────────────────────────────────────────
    def get_frame(self, name: str):
        with self.lock:
            return self.frames.get(name)

    def get_status(self, name: str) -> str:
        with self.lock:
            return self.status.get(name, "Offline")

    def get_counts(self, name: str) -> tuple:
        """Returns (in_count, out_count)."""
        with self.lock:
            return self.counts.get(name, (0, 0))

    def get_gender_counts(self, name: str) -> tuple:
        """
        Returns (male_count, female_count) for the given camera.
        Only meaningful for the Room camera.
        """
        with self.lock:
            detector = self.detectors.get(name)
        if detector is None:
            return (0, 0)
        return detector.get_gender_counts()

    def get_all_camera_names(self) -> list:
        return list(self.cameras.keys())
