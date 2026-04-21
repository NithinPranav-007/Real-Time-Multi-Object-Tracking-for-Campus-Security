import math
import time


class AbandonedObjectDetector:
    def __init__(self, bag_classes: set[str], threshold_seconds: int, radius_px: int, alert_cooldown: int):
        self.bag_classes = bag_classes
        self.threshold_seconds = threshold_seconds
        self.radius_px = radius_px
        self.alert_cooldown = alert_cooldown
        self.state = {}
        self.last_alert = {}

    def update(self, track_id: str, point, class_name: str):
        if class_name not in self.bag_classes:
            return None

        now = time.time()
        obj = self.state.get(track_id)

        if obj is None:
            self.state[track_id] = {
                "first_seen": now,
                "anchor": point,
            }
            return None

        anchor = obj["anchor"]
        distance = math.dist(anchor, point)

        if distance > self.radius_px:
            self.state[track_id] = {
                "first_seen": now,
                "anchor": point,
            }
            return None

        static_duration = now - obj["first_seen"]
        if static_duration < self.threshold_seconds:
            return None

        if now - self.last_alert.get(track_id, 0) < self.alert_cooldown:
            return None

        self.last_alert[track_id] = now
        return {
            "type": "abandoned_object",
            "object_id": track_id,
            "message": f"Possible abandoned {class_name} (track {track_id})",
        }
