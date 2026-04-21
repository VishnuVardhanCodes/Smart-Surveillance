"""
speed_estimator.py
Estimates the speed (km/h) of tracked objects using frame-to-frame
centroid displacement, calibrated pixels-per-meter ratio, and camera FPS.
"""

import time
import math


# ─────────────────────────────────────────────────────────────────────────────
# Tunable constants  (adjust once real camera specs are known)
# ─────────────────────────────────────────────────────────────────────────────
PIXELS_PER_METER = 20.0   # How many pixels ≈ 1 metre in the gate camera view
CAMERA_FPS       = 25.0   # Nominal FPS of Gate camera stream
SMOOTH_ALPHA     = 0.3    # EMA smoothing factor (0 = very smooth, 1 = raw)


class SpeedEstimator:
    """
    Maintains per-track centroid history and computes a smoothed speed
    estimate in km/h for each confirmed object.

    Usage (inside process_frame):
        speed = self.speed_estimator.update(track_id, cx, cy)
    """

    def __init__(self,
                 pixels_per_meter: float = PIXELS_PER_METER,
                 camera_fps: float = CAMERA_FPS,
                 smooth_alpha: float = SMOOTH_ALPHA):
        self.ppm        = pixels_per_meter
        self.fps        = camera_fps
        self.alpha      = smooth_alpha
        # track_id -> {'cx': float, 'cy': float, 'ts': float, 'speed': float}
        self._history: dict = {}

    def update(self, track_id: int, cx: float, cy: float) -> float:
        """
        Call once per frame for each confirmed track.

        Returns:
            Smoothed speed in km/h (float, >= 0).  Returns 0.0 on the
            first frame for a new track.
        """
        now = time.time()

        if track_id not in self._history:
            self._history[track_id] = {
                'cx': cx, 'cy': cy,
                'ts': now, 'speed': 0.0
            }
            return 0.0

        prev = self._history[track_id]
        dt   = now - prev['ts']

        if dt <= 0:
            return prev['speed']

        # Euclidean pixel displacement
        pixel_dist = math.hypot(cx - prev['cx'], cy - prev['cy'])

        # Convert to metres, then to km/h
        metres_per_sec = (pixel_dist / self.ppm) / dt
        raw_speed_kmh  = metres_per_sec * 3.6

        # Exponential moving average to smooth jitter
        smooth_speed = (self.alpha * raw_speed_kmh
                        + (1 - self.alpha) * prev['speed'])

        # Update history
        self._history[track_id] = {
            'cx': cx, 'cy': cy,
            'ts': now, 'speed': smooth_speed
        }

        return round(smooth_speed, 1)

    def get_speed(self, track_id: int) -> float:
        """Return the last known speed for a track (0.0 if unknown)."""
        return self._history.get(track_id, {}).get('speed', 0.0)

    def remove(self, track_id: int) -> None:
        """Remove a track from history when it is lost."""
        self._history.pop(track_id, None)

    def cleanup(self, active_track_ids: set) -> None:
        """Purge history entries for tracks no longer being tracked."""
        stale = [tid for tid in self._history if tid not in active_track_ids]
        for tid in stale:
            del self._history[tid]
