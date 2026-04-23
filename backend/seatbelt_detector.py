import cv2
import os
from ultralytics import YOLO

class SeatbeltDetector:
    def __init__(self, model_path=None):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Default model path if not provided
        if model_path is None:
            # We assume a model exists specifically for seatbelt detection
            model_path = os.path.join(self.base_dir, 'models', 'seatbelt_model.pt')
            
            # Fallback if the specific model doesn't exist
            if not os.path.exists(model_path):
                fallback = os.path.join(self.base_dir, 'yolov8n.pt')
                if os.path.exists(fallback):
                    model_path = fallback

        self.model = YOLO(model_path)
        
        # Class names (driver, seatbelt, no_seatbelt)
        # Assuming mapping: 0: driver, 1: seatbelt, 2: no_seatbelt or similar
        self.classes = ['driver', 'seatbelt', 'no_seatbelt']

    def detect(self, vehicle_crop):
        """
        Detect seatbelt/no_seatbelt on a cropped vehicle image.
        Returns: (has_seatbelt, confidence, detections)
        """
        if vehicle_crop is None or vehicle_crop.size == 0:
            return None, 0.0, []

        results = self.model(vehicle_crop, verbose=False, conf=0.3)[0]
        
        detections = []
        has_seatbelt = False
        no_seatbelt = False
        
        for r in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = r
            label = self.model.names[int(class_id)].lower()
            
            detections.append({
                'box': [x1, y1, x2, y2],
                'score': score,
                'label': label
            })
            
            if 'no_seatbelt' in label or 'no-seatbelt' in label:
                no_seatbelt = True
            elif 'seatbelt' in label:
                has_seatbelt = True

        if no_seatbelt:
            return False, results.boxes.conf.max().item() if len(results.boxes.conf) > 0 else 0.0, detections
        
        if has_seatbelt:
            return True, results.boxes.conf.max().item() if len(results.boxes.conf) > 0 else 0.0, detections
            
        return None, 0.0, detections
