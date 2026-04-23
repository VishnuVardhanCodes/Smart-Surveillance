import cv2
import os
from ultralytics import YOLO

class HelmetDetector:
    def __init__(self, model_path=None):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Default model path if not provided
        if model_path is None:
            # We assume a model exists specifically for PPE
            # If not, it will fall back to a standard yolov8n.pt if it's there
            # but ideally the user should provide the ppe-specific weights.
            model_path = os.path.join(self.base_dir, 'models', 'ppe_helmet.pt')
            
            # Fallback if the specific model doesn't exist (for development/demo)
            if not os.path.exists(model_path):
                # Search in backend/yolov8n.pt as a last resort fallback
                fallback = os.path.join(self.base_dir, 'yolov8n.pt')
                if os.path.exists(fallback):
                    model_path = fallback

        self.model = YOLO(model_path)
        
        # Class names for the PPE model (person, helmet, no_helmet)
        # These indices depend on the specific training. 
        # Standard PPE datasets often use: 0: helmet, 1: no_helmet, 2: person
        # or similar. We will map them based on name if possible.
        self.ppe_classes = ['helmet', 'no_helmet', 'person']

    def detect(self, person_crop):
        """
        Detect helmet/no_helmet on a cropped person image.
        Returns: (has_helmet, confidence, results_boxes)
        """
        if person_crop is None or person_crop.size == 0:
            return None, 0.0, []

        results = self.model(person_crop, verbose=False, conf=0.3)[0]
        
        detections = []
        has_helmet = False
        no_helmet = False
        
        for r in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = r
            label = self.model.names[int(class_id)].lower()
            
            detections.append({
                'box': [x1, y1, x2, y2],
                'score': score,
                'label': label
            })
            
            if 'no_helmet' in label:
                no_helmet = True
            elif 'helmet' in label:
                has_helmet = True

        # If we see "no_helmet", it's a violation even if "helmet" is also detected (false positive)
        if no_helmet:
            return False, results.boxes.conf.max().item() if len(results.boxes.conf) > 0 else 0.0, detections
        
        if has_helmet:
            return True, results.boxes.conf.max().item() if len(results.boxes.conf) > 0 else 0.0, detections
            
        # If neither is detected, we return None (uncertain)
        return None, 0.0, detections
