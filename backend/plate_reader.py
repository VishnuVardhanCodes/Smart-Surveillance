import easyocr
import cv2
import numpy as np
import os

class PlateReader:
    def __init__(self):
        # Initialize reader for English
        # model_storage_directory ensures we can keep models inside the project for offline use
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_dir = os.path.join(base_dir, 'models', 'ocr')
        os.makedirs(model_dir, exist_ok=True)
        
        self.reader = easyocr.Reader(['en'], gpu=False, model_storage_directory=model_dir)

    def read_plate(self, image):
        """
        Extract text from a cropped image of a number plate.
        """
        try:
            # Preprocessing
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Apply some thresholding/blurring if needed
            # gray = cv2.GaussianBlur(gray, (5, 5), 0)
            
            results = self.reader.readtext(gray)
            
            # Combine all detected text fragments
            plate_text = ""
            for (bbox, text, prob) in results:
                if prob > 0.3:  # Confidence threshold
                    plate_text += str(text).upper().replace(" ", "")
            
            return plate_text if plate_text else None
        except Exception as e:
            print(f"OCR Error: {e}")
            return None
