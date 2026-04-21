# Real-Time Multi-Object Tracking for Campus Security

An end-to-end deep learning + computer vision system for real-time surveillance analytics.

## Features

- YOLOv8 object detection (person, vehicles, bag-like objects)
- DeepSORT multi-object tracking with unique IDs
- Suspicious activity detection:
  - Loitering
  - Restricted-zone intrusion
  - Abandoned object
- Real-time alerting (console + UI + SQLite logging)
- MJPEG video stream API
- React dashboard with live feed and alert panel

## Project Structure

```text
project/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── alerts/
│   │   ├── loitering.py
│   │   ├── intrusion.py
│   │   └── abandoned_object.py
│   ├── database/
│   │   └── db.py
│   └── detection/
│       ├── yolo_model.py
│       ├── tracker.py
│       └── utils.py
├── frontend/
│   ├── package.json
│   ├── index.html
│   └── src/
│       ├── App.js
│       ├── VideoFeed.js
│       ├── AlertsPanel.js
│       ├── main.jsx
│       └── styles.css
├── models/
├── requirements.txt
└── README.md
```

## Tech Stack

- Backend: Python, Flask, OpenCV, PyTorch, Ultralytics YOLOv8, DeepSORT, SQLite
- Frontend: React + Vite
- Streaming: MJPEG via `/video_feed`

## Setup

### 1) Backend setup

```bash
cd project
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

### 2) Frontend setup

```bash
cd frontend
npm install
```

## Run

### Start backend

```bash
cd project/backend
python app.py
```

Backend runs on `http://localhost:8000`.

### Start frontend

```bash
cd project/frontend
npm run dev
```

Frontend runs on Vite default URL (usually `http://localhost:5173`).

## API Endpoints

- `POST /start` - Start detection loop
- `POST /stop` - Stop detection loop
- `GET /alerts?limit=100` - Fetch alert history
- `GET /video_feed` - Stream processed MJPEG video
- `GET /health` - Service health and model status

## Video Source Configuration

In `backend/config.py`:

- `VIDEO_SOURCE = "0"` for default webcam
- or set RTSP via environment variable:

```bash
# PowerShell example
$env:VIDEO_SOURCE = "rtsp://username:password@camera-ip/stream"
python app.py
```

## Model Configuration

Default model path is `yolov8n.pt` (auto-downloaded by Ultralytics if missing).

To use custom weights:

```bash
$env:MODEL_PATH = "../models/yolov8.pt"
python app.py
```

## Alert Logic

- Loitering: Person stays near same location for configured seconds
- Intrusion: Any tracked object enters restricted polygon ROI
- Abandoned object: Bag-like object remains static beyond threshold

Tune thresholds in `backend/config.py`:

- `LOITERING_SECONDS`
- `LOITERING_RADIUS_PX`
- `ABANDONED_SECONDS`
- `ABANDONED_RADIUS_PX`
- `RESTRICTED_ZONE`

## Performance Notes

- Uses frame-rate throttling via `MAX_FPS`
- Automatically benefits from GPU when PyTorch + CUDA is available
- For higher FPS, use smaller YOLO weights and reduce input resolution

## Optional Extensions (Bonus)

- Face recognition module using `face_recognition`/ArcFace
- Heatmap generation from track history
- Email/SMS alerts with SMTP/Twilio
- Role-based auth for dashboard access

## Demo Flow

1. Start backend and frontend.
2. Open dashboard.
3. Click **Start Detection**.
4. Walk/drive in frame and observe IDs and boxes.
5. Trigger events (intrusion/loitering/static bag) and verify alerts panel + DB logs.

## Notes

- `alerts.db` is created automatically in `backend/` at runtime.
- Ensure webcam access permissions are enabled for your system.
