import time
from collections import Counter, defaultdict, deque

from deep_sort_realtime.deepsort_tracker import DeepSort


class DeepSortTracker:
    def __init__(
        self,
        max_age: int,
        n_init: int,
        max_cosine_distance: float,
        class_smoothing_window: int,
    ):
        self.tracker = DeepSort(
            max_age=max_age,
            n_init=n_init,
            nms_max_overlap=1.0,
            max_cosine_distance=max_cosine_distance,
            nn_budget=100,
            embedder="mobilenet",
            half=True,
        )
        self.class_votes = defaultdict(lambda: deque(maxlen=class_smoothing_window))
        self.last_seen = {}

    def update(self, detections, frame):
        """
        Convert detections to DeepSORT format and return confirmed tracks.
        Input detections: [([x1, y1, x2, y2], conf, class_name, class_id), ...]
        """
        ds_detections = []
        for bbox, conf, class_name, _class_id in detections:
            x1, y1, x2, y2 = bbox
            w = max(0, x2 - x1)
            h = max(0, y2 - y1)
            ds_detections.append(([x1, y1, w, h], conf, class_name))

        tracks = self.tracker.update_tracks(ds_detections, frame=frame)

        parsed_tracks = []
        now = time.time()
        seen_ids = set()

        for track in tracks:
            if not track.is_confirmed():
                continue

            track_id = str(track.track_id)
            seen_ids.add(track_id)
            self.last_seen[track_id] = now

            raw_class = str(track.det_class) if track.det_class else "unknown"
            if raw_class != "unknown":
                self.class_votes[track_id].append(raw_class)

            votes = self.class_votes.get(track_id)
            stable_class = Counter(votes).most_common(1)[0][0] if votes else raw_class

            ltrb = track.to_ltrb()
            x1, y1, x2, y2 = [int(v) for v in ltrb]
            parsed_tracks.append(
                {
                    "track_id": track_id,
                    "bbox": [x1, y1, x2, y2],
                    "class_name": stable_class,
                    "confidence": float(track.det_conf) if track.det_conf is not None else 0.0,
                }
            )

        # Cleanup stale class history to prevent memory growth.
        stale_ids = [tid for tid, ts in self.last_seen.items() if now - ts > 60]
        for tid in stale_ids:
            self.last_seen.pop(tid, None)
            self.class_votes.pop(tid, None)

        return parsed_tracks
