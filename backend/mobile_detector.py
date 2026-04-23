import cv2
import os
from ultralytics import YOLO

class MobileDetector:
    def __init__(self, model_path=None):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Default model path if not provided
        if model_path is None:
            # We assume a model exists specifically for mobile usage detection
            model_path = os.path.join(self.base_dir, 'models', 'mobile_usage_model.pt')
            
            # Fallback if the specific model doesn't exist
            if not os.path.exists(model_path):
                fallback = os.path.join(self.base_dir, 'yolov8n.pt')
                if os.path.exists(fallback):
                    model_path = fallback

        self.model = YOLO(model_path)
        
        # Class names (driver, mobile_phone, etc.)
        # Assuming mapping: 0: driver, 1: mobile_phone, etc.
        # Note: 'cell phone' is class 67 in standard COCO
        self.classes = ['driver', 'mobile_phone']

    def detect(self, vehicle_crop):
        """
        Detect mobile phone usage on a cropped vehicle image.
        Returns: (is_using_phone, confidence, detections)
        """
        if vehicle_crop is None or vehicle_crop.size == 0:
            return None, 0.0, []

        results = self.model(vehicle_crop, verbose=False, conf=0.25)[0]
        
        detections = []
        is_using_phone = False
        
        for r in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = r
            label = self.model.names[int(class_id)].lower()
            
            detections.append({
                'box': [x1, y1, x2, y2],
                'score': score,
                'label': label
            })
            
            # Check for cell phone or mobile phone labels
            if 'phone' in label or 'cell' in label:
                is_using_phone = True

        if is_using_phone:
            return True, results.boxes.conf.max().item() if len(results.boxes.conf) > 0 else 0.0, detections
            
        return False, 0.0, detections

    def detect_talking(self, person_crop):
        """
        Specific logic for detecting talking while walking.
        Checks if phone is in the upper 40% of the person's crop (near face).
        """
        is_using, score, detections = self.detect(person_crop)
        if not is_using:
            return False, 0.0, []

        near_face = False
        h, w = person_crop.shape[:2]
        
        for d in detections:
            if 'phone' in d['label'] or 'cell' in d['label']:
                # Box is [x1, y1, x2, y2]
                y1 = d['box'][1]
                # If phone is in upper 40% of person's height
                if y1 < (h * 0.4):
                    near_face = True
                    break
        
        return near_face, score, detections
