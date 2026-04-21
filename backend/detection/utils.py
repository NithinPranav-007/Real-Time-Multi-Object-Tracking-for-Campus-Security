import cv2
import numpy as np


def centroid_from_bbox(bbox):
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) // 2, (y1 + y2) // 2)


def point_in_polygon(point, polygon):
    poly = np.array(polygon, dtype=np.int32)
    return cv2.pointPolygonTest(poly, point, False) >= 0


def draw_restricted_zone(frame, polygon):
    pts = np.array(polygon, dtype=np.int32).reshape((-1, 1, 2))
    cv2.polylines(frame, [pts], isClosed=True, color=(0, 0, 255), thickness=2)
    cv2.putText(
        frame,
        "Restricted Zone",
        tuple(polygon[0]),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2,
    )


def encode_jpeg(frame):
    ok, buffer = cv2.imencode(".jpg", frame)
    if not ok:
        return None
    return buffer.tobytes()
