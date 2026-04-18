import easyocr
import cv2
import numpy as np

class PlateReader:
    def __init__(self):
        # Initialize reader for English (can add more languages)
        # Setting gpu=False as default for compatibility, set to True if GPU available
        self.reader = easyocr.Reader(['en'], gpu=False)

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
