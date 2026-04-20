from deep_sort_realtime.deepsort_tracker import DeepSort

class ObjectTracker:
    def __init__(self):
        # Initialize DeepSORT tracker
        # max_age: Maximum number of missed misses before a track is deleted
        # n_init: Number of consecutive frames to confirm a track
        self.tracker = DeepSort(max_age=30, n_init=3, nms_max_overlap=1.0, max_cosine_distance=0.2)

    def update(self, detections, frame):
        """
        Update tracker with current detections
        detections: list of [ [x1, y1, w, h], score, class_id ]
        frame: current video frame
        """
        tracks = self.tracker.update_tracks(detections, frame=frame)
        return tracks
