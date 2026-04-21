from ultralytics import YOLO


class YOLODetector:
    def __init__(
        self,
        model_path: str,
        target_class_ids: set[int],
        detection_confidence: float,
        person_confidence: float,
        detection_iou: float,
        imgsz: int,
    ):
        self.model = YOLO(model_path)
        self.target_class_ids = target_class_ids
        self.detection_confidence = detection_confidence
        self.person_confidence = person_confidence
        self.detection_iou = detection_iou
        self.imgsz = imgsz

    def detect(self, frame):
        """Return detections in (xyxy, conf, class_name, class_id) format."""
        results = self.model.predict(
            source=frame,
            verbose=False,
            conf=self.detection_confidence,
            iou=self.detection_iou,
            imgsz=self.imgsz,
        )
        parsed = []

        if not results:
            return parsed

        result = results[0]
        names = result.names

        for box in result.boxes:
            cls_idx = int(box.cls.item())
            if cls_idx not in self.target_class_ids:
                continue

            conf = float(box.conf.item())
            # Force stricter confidence on person to reduce false person detections.
            if cls_idx == 0 and conf < self.person_confidence:
                continue

            class_name = names.get(cls_idx, str(cls_idx))
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
            parsed.append(([x1, y1, x2, y2], conf, class_name, cls_idx))

        return parsed
