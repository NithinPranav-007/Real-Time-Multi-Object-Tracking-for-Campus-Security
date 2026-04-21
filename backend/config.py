import os


class Config:
    HOST = "0.0.0.0"
    PORT = 8000
    DEBUG = True

    # Video source: 0 for webcam, or RTSP URL.
    VIDEO_SOURCE = os.environ.get("VIDEO_SOURCE", "0")

    # YOLO model weights path.
    # yolov8s is more accurate than yolov8n and still practical for real-time use.
    MODEL_PATH = os.environ.get("MODEL_PATH", "yolov8s.pt")

    # YOLO accuracy/performance tuning.
    DETECTION_CONFIDENCE = float(os.environ.get("DETECTION_CONFIDENCE", "0.35"))
    PERSON_CONFIDENCE = float(os.environ.get("PERSON_CONFIDENCE", "0.45"))
    DETECTION_IOU = float(os.environ.get("DETECTION_IOU", "0.50"))
    INFERENCE_IMGSZ = int(os.environ.get("INFERENCE_IMGSZ", "960"))

    # Tracking and activity thresholds.
    TARGET_CLASS_IDS = {0, 2, 3, 5, 7, 24, 26, 28}
    TARGET_CLASSES = {"person", "car", "truck", "bus", "motorcycle", "backpack", "handbag", "suitcase"}
    BAG_CLASSES = {"backpack", "handbag", "suitcase"}
    LOITERING_SECONDS = 15
    LOITERING_RADIUS_PX = 50
    ABANDONED_SECONDS = 20
    ABANDONED_RADIUS_PX = 35

    # Restricted polygon points as (x, y) tuples in pixel coordinates.
    # Tune this for your camera view.
    RESTRICTED_ZONE = [(100, 100), (550, 100), (550, 450), (100, 450)]

    ALERT_COOLDOWN_SECONDS = 10
    MAX_FPS = 20
    DB_PATH = "alerts.db"

    # DeepSORT tuning for fewer ID switches and stabler labeling.
    TRACKER_MAX_AGE = int(os.environ.get("TRACKER_MAX_AGE", "25"))
    TRACKER_N_INIT = int(os.environ.get("TRACKER_N_INIT", "3"))
    TRACKER_MAX_COS_DISTANCE = float(os.environ.get("TRACKER_MAX_COS_DISTANCE", "0.18"))
    CLASS_SMOOTHING_WINDOW = int(os.environ.get("CLASS_SMOOTHING_WINDOW", "25"))
