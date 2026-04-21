import time

from detection.utils import point_in_polygon


class IntrusionDetector:
    def __init__(self, restricted_zone, alert_cooldown: int):
        self.restricted_zone = restricted_zone
        self.alert_cooldown = alert_cooldown
        self.last_alert = {}

    def update(self, track_id: str, point, class_name: str):
        if not point_in_polygon(point, self.restricted_zone):
            return None

        now = time.time()
        key = f"{track_id}:{class_name}"
        if now - self.last_alert.get(key, 0) < self.alert_cooldown:
            return None

        self.last_alert[key] = now
        return {
            "type": "intrusion",
            "object_id": track_id,
            "message": f"{class_name} {track_id} entered restricted zone",
        }
