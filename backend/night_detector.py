from datetime import datetime
import os

class NightDetector:
    def __init__(self, start_hour=22, end_hour=6):
        self.start_hour = start_hour
        self.end_hour = end_hour

    def is_night_time(self):
        """Check if current time is within night hours."""
        now = datetime.now().hour
        if self.start_hour > self.end_hour:
            # Case for overnight range, e.g., 22:00 to 06:00
            return now >= self.start_hour or now < self.end_hour
        else:
            # Case for range within same day (unlikely for night but possible)
            return self.start_hour <= now < self.end_hour

    def should_trigger_alert(self, object_type):
        """Determine if an alert should be triggered based on time and detected object."""
        if self.is_night_time():
            # Suspicious activity is usually persons or vehicles at night
            return object_type in ['person', 'car', 'motorcycle', 'truck', 'bus']
        return False

    def get_night_hours_str(self):
        return f"{self.start_hour:02d}:00 - {self.end_hour:02d}:00"
