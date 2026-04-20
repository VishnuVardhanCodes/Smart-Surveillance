import numpy as np
import time

class PeopleCounter:
    def __init__(self, line_position=0.5, orientation='horizontal', buffer_size=0.1):
        """
        line_position: relative position (0.0 to 1.0) of the virtual line
        orientation: 'horizontal' or 'vertical'
        buffer_size: relative size of the buffer zone to prevent jitter triggers
        """
        self.line_position = line_position
        self.orientation = orientation
        self.buffer_size = buffer_size
        self.entry_count = 0
        self.exit_count = 0
        
        # track_id -> {'last_pos': float, 'state': int, 'last_seen': float}
        # state: -1 (above/left), 0 (in buffer), 1 (below/right)
        self.tracked_objects = {} 
        
        # Persistence: how long to keep track history (in seconds)
        self.persistence_timeout = 5.0 

    def count(self, tracks, frame_width, frame_height):
        """
        Update counts using a buffer-zone crossing logic.
        Uses a state machine for each track ID.
        """
        dim = frame_height if self.orientation == 'horizontal' else frame_width
        line_coord = self.line_position * dim
        buffer_half = (self.buffer_size * dim) / 2
        
        upper_bound = line_coord - buffer_half
        lower_bound = line_coord + buffer_half
        
        crossed_in = []
        crossed_out = []
        
        current_time = time.time()
        current_ids = [track.track_id for track in tracks]
        
        # Cleanup old tracked objects (persistence)
        for tid in list(self.tracked_objects.keys()):
            if tid not in current_ids:
                if current_time - self.tracked_objects[tid]['last_seen'] > self.persistence_timeout:
                    del self.tracked_objects[tid]

        for track in tracks:
            if not track.is_confirmed():
                continue
            
            track_id = track.track_id
            ltrb = track.to_ltrb()
            
            # Calculate centroid
            cx = (ltrb[0] + ltrb[2]) / 2
            cy = (ltrb[1] + ltrb[3]) / 2
            
            pos = cy if self.orientation == 'horizontal' else cx
            
            # Determine current state relative to buffer
            if pos < upper_bound:
                new_state = -1 # Above/Left
            elif pos > lower_bound:
                new_state = 1  # Below/Right
            else:
                new_state = 0  # Inside Buffer
                
            if track_id not in self.tracked_objects:
                # Initialize new track
                self.tracked_objects[track_id] = {
                    'last_pos': pos,
                    'state': new_state,
                    'last_seen': current_time,
                    'triggered_in': False,
                    'triggered_out': False
                }
            else:
                obj = self.tracked_objects[track_id]
                old_state = obj['state']
                
                # Check for full crossing
                # ENTRY (IN): -1 -> 1 (Top to Bottom)
                if old_state == -1 and new_state == 1:
                    if not obj['triggered_in']:
                        self.entry_count += 1
                        obj['triggered_in'] = True
                        obj['triggered_out'] = False # Reset other side to allow return
                        crossed_in.append(track)
                
                # EXIT (OUT): 1 -> -1 (Bottom to Top)
                elif old_state == 1 and new_state == -1:
                    if not obj['triggered_out']:
                        self.exit_count += 1
                        obj['triggered_out'] = True
                        obj['triggered_in'] = False # Reset other side to allow return
                        crossed_out.append(track)
                
                # Update state if it moved strictly outside the buffer
                if new_state != 0:
                    obj['state'] = new_state
                
                obj['last_pos'] = pos
                obj['last_seen'] = current_time
            
        return self.entry_count, self.exit_count, crossed_in, crossed_out

    def get_counts(self):
        return self.entry_count, self.exit_count

    def reset(self):
        self.entry_count = 0
        self.exit_count = 0
        self.tracked_objects = {}
