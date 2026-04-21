import math
import time
from collections import deque


class LoiteringDetector:
    def __init__(self, threshold_seconds: int, radius_px: int, alert_cooldown: int):
        self.threshold_seconds = threshold_seconds
        self.radius_px = radius_px
        self.alert_cooldown = alert_cooldown
        self.history = {}
        self.last_alert = {}

    def update(self, track_id: str, point):
        now = time.time()
        points = self.history.setdefault(track_id, deque(maxlen=300))
        points.append((now, point))

        if len(points) < 2:
            return None

        first_t, first_p = points[0]
        latest_t, latest_p = points[-1]
        elapsed = latest_t - first_t

        if elapsed < self.threshold_seconds:
            return None

        distance = math.dist(first_p, latest_p)
        if distance > self.radius_px:
            self.history[track_id].clear()
            self.history[track_id].append((now, point))
            return None

        if now - self.last_alert.get(track_id, 0) < self.alert_cooldown:
            return None

        self.last_alert[track_id] = now
        return {
            "type": "loitering",
            "object_id": track_id,
            "message": f"Track {track_id} loitering for {int(elapsed)}s",
        }
