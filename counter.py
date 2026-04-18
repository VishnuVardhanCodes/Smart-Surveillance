import numpy as np

class PeopleCounter:
    def __init__(self, line_position=0.5, orientation='horizontal'):
        """
        line_position: relative position (0.0 to 1.0) of the virtual line
        orientation: 'horizontal' or 'vertical'
        """
        self.line_position = line_position
        self.orientation = orientation
        self.entry_count = 0
        self.exit_count = 0
        self.tracked_objects = {}  # track_id -> last_position

    def count(self, tracks, frame_width, frame_height):
        """
        Update counts based on track movements across the line.
        """
        line_coord = self.line_position * (frame_height if self.orientation == 'horizontal' else frame_width)
        
        for track in tracks:
            if not track.is_confirmed():
                continue
            
            track_id = track.track_id
            ltrb = track.to_ltrb()
            
            # Calculate centroid
            cx = (ltrb[0] + ltrb[2]) / 2
            cy = (ltrb[1] + ltrb[3]) / 2
            
            current_pos = cy if self.orientation == 'horizontal' else cx
            
            if track_id in self.tracked_objects:
                prev_pos = self.tracked_objects[track_id]
                
                # Check line crossing
                if prev_pos < line_coord <= current_pos:
                    self.entry_count += 1
                elif prev_pos > line_coord >= current_pos:
                    self.exit_count += 1
            
            self.tracked_objects[track_id] = current_pos
            
        return self.entry_count, self.exit_count

    def get_counts(self):
        return self.entry_count, self.exit_count

    def reset(self):
        self.entry_count = 0
        self.exit_count = 0
        self.tracked_objects = {}
