import os
import threading
import time
from collections import deque
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from alerts.abandoned_object import AbandonedObjectDetector
from alerts.intrusion import IntrusionDetector
from alerts.loitering import LoiteringDetector
from config import Config
from database.db import AlertRepository
from detection.tracker import DeepSortTracker
from detection.utils import centroid_from_bbox, draw_restricted_zone, encode_jpeg
from detection.yolo_model import YOLODetector


BASE_DIR = Path(__file__).resolve().parent
_candidate_model = (BASE_DIR / Config.MODEL_PATH).resolve()
MODEL_PATH = str(_candidate_model) if _candidate_model.exists() else Config.MODEL_PATH


class VideoAnalyticsService:
    def __init__(self):
        self.detector = YOLODetector(
            model_path=MODEL_PATH,
            target_class_ids=Config.TARGET_CLASS_IDS,
            detection_confidence=Config.DETECTION_CONFIDENCE,
            person_confidence=Config.PERSON_CONFIDENCE,
            detection_iou=Config.DETECTION_IOU,
            imgsz=Config.INFERENCE_IMGSZ,
        )
        self.tracker = DeepSortTracker(
            max_age=Config.TRACKER_MAX_AGE,
            n_init=Config.TRACKER_N_INIT,
            max_cosine_distance=Config.TRACKER_MAX_COS_DISTANCE,
            class_smoothing_window=Config.CLASS_SMOOTHING_WINDOW,
        )
        self.db = AlertRepository(str(BASE_DIR / Config.DB_PATH))

        self.loitering = LoiteringDetector(
            threshold_seconds=Config.LOITERING_SECONDS,
            radius_px=Config.LOITERING_RADIUS_PX,
            alert_cooldown=Config.ALERT_COOLDOWN_SECONDS,
        )
        self.intrusion = IntrusionDetector(
            restricted_zone=Config.RESTRICTED_ZONE,
            alert_cooldown=Config.ALERT_COOLDOWN_SECONDS,
        )
        self.abandoned = AbandonedObjectDetector(
            bag_classes=Config.BAG_CLASSES,
            threshold_seconds=Config.ABANDONED_SECONDS,
            radius_px=Config.ABANDONED_RADIUS_PX,
            alert_cooldown=Config.ALERT_COOLDOWN_SECONDS,
        )

        self.running = False
        self.worker = None
        self.frame_lock = threading.Lock()
        self.latest_frame = None
        self.recent_alerts = deque(maxlen=50)

    def _build_capture(self):
        source = Config.VIDEO_SOURCE
        if isinstance(source, str) and source.isdigit():
            source = int(source)
        return cv2.VideoCapture(source)

    def start(self):
        if self.running:
            return False

        self.running = True
        self.worker = threading.Thread(target=self._loop, daemon=True)
        self.worker.start()
        return True

    def stop(self):
        self.running = False
        if self.worker and self.worker.is_alive():
            self.worker.join(timeout=2)
        return True

    def _loop(self):
        cap = self._build_capture()
        if not cap.isOpened():
            self.running = False
            return

        frame_interval = 1.0 / max(1, Config.MAX_FPS)

        while self.running:
            start_time = time.time()
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.05)
                continue

            detections = self.detector.detect(frame)
            tracks = self.tracker.update(detections, frame)

            draw_restricted_zone(frame, Config.RESTRICTED_ZONE)

            for t in tracks:
                bbox = t["bbox"]
                class_name = t["class_name"]
                track_id = t["track_id"]
                center = centroid_from_bbox(bbox)

                x1, y1, x2, y2 = bbox
                cv2.rectangle(frame, (x1, y1), (x2, y2), (51, 204, 51), 2)
                cv2.putText(
                    frame,
                    f"{class_name} ID:{track_id}",
                    (x1, max(25, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )

                alerts = [
                    self.loitering.update(track_id, center) if class_name == "person" else None,
                    self.intrusion.update(track_id, center, class_name),
                    self.abandoned.update(track_id, center, class_name),
                ]

                for alert in alerts:
                    if not alert:
                        continue
                    self.db.add_alert(alert["object_id"], alert["type"], alert["message"])
                    self.recent_alerts.appendleft({"timestamp": time.time(), **alert})
                    print(f"[ALERT] {alert['type'].upper()} | {alert['message']}")

            # Overlay latest alerts for quick visual feedback.
            for idx, a in enumerate(list(self.recent_alerts)[:4]):
                cv2.putText(
                    frame,
                    f"ALERT: {a['type']} - {a['message']}",
                    (10, 28 + idx * 24),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2,
                )

            with self.frame_lock:
                self.latest_frame = frame.copy()

            elapsed = time.time() - start_time
            if elapsed < frame_interval:
                time.sleep(frame_interval - elapsed)

        cap.release()

    def generate_frames(self):
        while True:
            with self.frame_lock:
                frame = self.latest_frame.copy() if self.latest_frame is not None else None

            if frame is None:
                # Small placeholder frame while stream warms up.
                frame = np.full((480, 640, 3), 245, dtype=np.uint8)
                cv2.putText(frame, "Waiting for stream...", (180, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)

            jpg = encode_jpeg(frame)
            if jpg is None:
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n"
            )
            time.sleep(0.03)


app = Flask(__name__)
CORS(app)
service = VideoAnalyticsService()


@app.route("/start", methods=["POST"])
def start_detection():
    started = service.start()
    return jsonify({"status": "running" if started else "already_running"})


@app.route("/stop", methods=["POST"])
def stop_detection():
    service.stop()
    return jsonify({"status": "stopped"})


@app.route("/alerts", methods=["GET"])
def get_alerts():
    limit = int(request.args.get("limit", 100))
    return jsonify(service.db.get_alerts(limit=limit))


@app.route("/video_feed", methods=["GET"])
def video_feed():
    return Response(service.generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify(
        {
            "status": "ok",
            "running": service.running,
            "model_path": str(MODEL_PATH),
            "model_exists": os.path.exists(MODEL_PATH),
        }
    )


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, threaded=True)
