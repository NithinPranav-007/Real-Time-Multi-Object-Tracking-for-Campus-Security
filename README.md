# 🛡️ Real-Time Multi-Object Tracking for Campus Security

[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/backend-Flask-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Frontend](https://img.shields.io/badge/frontend-React%20%2B%20Vite-blueviolet.svg)](https://vitejs.dev/)
[![Deep Learning](https://img.shields.io/badge/AI%2FML-YOLOv8%20%2B%20DeepSORT-green.svg)](https://github.com/ultralytics/ultralytics)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#)

An enterprise-grade, end-to-end computer vision and deep learning surveillance system designed for real-time campus security monitoring. The application integrates state-of-the-art object detection (YOLOv8) with robust multi-object tracking (DeepSORT) to monitor live CCTV feeds, detect security violations, and immediately alert campus operators via an interactive web dashboard.

---

## 📸 System Dashboard Preview

Below is the conceptual visual interface layout for the security monitor:

```text
+------------------------------------------------------------------------------------------+
|  🛡️ CAMPUS SECURITY INTELLIGENCE                             [ STATUS: ACTIVE ]          |
+------------------------------------------------------------------------------------------+
|  Controls: [ START DETECTION ] (Green)    [ STOP DETECTION ] (Red)   System Alert: OK    |
+--------------------+---------------------------------------------------------------------+
| STATISTICS         |  INTRUSIONS: 12        LOITERING: 4          ABANDONED BAGS: 1      |
+--------------------+---------------------+-----------------------------------------------+
| LIVE SURVEILLANCE FEED                   | RECENT ALERTS PANEL                           |
| +--------------------------------------+ | +-------------------------------------------+ |
| |                                      | | | [INTRUSION]   06-09 14:15:20 | ID: 12      | |
| |     [Person ID: 4]                   | | | Person entered restricted loading zone  | |
| |     +----------+                     | | +-------------------------------------------+ |
| |     |   (o_o)  |    / Restricted \   | | | [LOITERING]   06-09 14:14:10 | ID: 8       | |
| |     |   /| |   |   /  Zone        \  | | | Individual remaining static near lobby   | |
| |     |   / \    |  /                \ | | +-------------------------------------------+ |
| |     +----------+ /                  \| | | [ABANDONED]   06-09 14:12:02 | ID: 15      | |
| |                 /____________________| | | Suitcase left unattended > 20s            | |
| +--------------------------------------+ | +-------------------------------------------+ |
+------------------------------------------+-----------------------------------------------+
```

---

## 🏗️ System Architecture

The project features a decoupled, asynchronous architecture separating computationally heavy computer vision inference from the web UI.

```mermaid
graph TD
    %% Define System Nodes
    VideoSource[Camera Feed / Webcam / RTSP] -->|OpenCV VideoCapture| AppServer[Flask API Service]
    
    subgraph Backend Pipeline [Backend Engine: app.py]
        AppServer -->|Frame Stream| DetectionEngine[YOLODetector: YOLOv8s]
        DetectionEngine -->|Bboxes & Confidences| TrackingEngine[DeepSortTracker: DeepSORT]
        TrackingEngine -->|Stabilized Object Paths| RulesEngine{Security Rules Evaluator}
        
        RulesEngine -->|Condition Met| Loitering[Loitering Detector]
        RulesEngine -->|In Restricted Poly| Intrusion[Intrusion Detector]
        RulesEngine -->|Static Bag-class > 20s| Abandoned[Abandoned Object Detector]
        
        Loitering -->|New Alert| AlertDB[(SQLite: alerts.db)]
        Intrusion -->|New Alert| AlertDB
        Abandoned -->|New Alert| AlertDB
        
        Loitering -.->|Push Queue| MJPEGStream[MJPEG Video Generator]
        Intrusion -.->|Push Queue| MJPEGStream
        Abandoned -.->|Push Queue| MJPEGStream
        
        MJPEGStream -->|Render Overlays & Boxes| FrameBuffer[Shared Thread-safe Frame]
    end

    %% Define UI Connections
    ReactUI[React Web Dashboard] -->|POST /start| AppServer
    ReactUI -->|POST /stop| AppServer
    ReactUI -->|GET /video_feed| FrameBuffer
    ReactUI -->|GET /alerts (Polling)| AlertDB
```

---

## ✨ Key Features & Analytic Engines

### 1. Object Detection & ID Association
*   **YOLOv8 Framework:** Uses the `yolov8s.pt` (Small) model checkpoint by default, strike-weighting the optimal balance between inference speed and detection accuracy for micro-servers.
*   **DeepSORT Tracker:** Employs a Deep Cosine Metric Learning (MobileNet embedder) tracker to maintain persistent object tracking IDs across frames, minimizing ID switches during occlusions.
*   **Class Voting & Smoothing:** Features a slide-window voting queue (`CLASS_SMOOTHING_WINDOW = 25`) to prevent class labeling flickers (e.g., classifying a car as a truck for a brief frame).

### 2. Specialized Security Rules
*   **Loitering Detection:** Triggers an alert if a `person` remains within a specified pixel radius (`LOITERING_RADIUS_PX = 50`) for more than `LOITERING_SECONDS = 15`.
*   **Restricted Zone Intrusion:** Utilizes ray-casting algorithms (`cv2.pointPolygonTest`) to alert the second any tracked vehicle or person crosses a custom-defined restricted polygon boundary (`RESTRICTED_ZONE`).
*   **Abandoned Bag Alerting:** Monitors baggage categories (`backpack`, `handbag`, `suitcase`). If a bag becomes stationary and its parent tracker leaves the proximity, it flags the item as abandoned after `ABANDONED_SECONDS = 20`.

---

## 📁 Project Structure

```text
project/
├── backend/
│   ├── app.py                      # Main entrypoint & Flask API Server
│   ├── config.py                   # System configuration & threshold limits
│   ├── alerts/
│   │   ├── __init__.py
│   │   ├── loitering.py            # Loitering algorithm engine
│   │   ├── intrusion.py            # Polygon intrusion checker
│   │   └── abandoned_object.py     # Unattended baggage logic
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py                   # SQLite database manager & repository pattern
│   └── detection/
│       ├── __init__.py
│       ├── yolo_model.py           # YOLOv8 inference wrapper
│       ├── tracker.py              # DeepSORT tracking abstraction
│       └── utils.py                # Centroid, drawing, & JPEG encoding utilities
├── frontend/
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js              # Vite server configuration
│   └── src/
│       ├── main.jsx                # React app renderer
│       ├── App.jsx                 # Dashboard shell & state management
│       ├── VideoFeed.jsx           # Live stream rendering panel
│       ├── AlertsPanel.jsx         # Real-time alert feed interface
│       └── styles.css              # Custom Neo-Brutalist stylesheet
├── models/                         # Local storage directory for .pt weight files
├── requirements.txt                # Python environment specifications
└── README.md                       # Documentation (This file)
```

---

## 🛠️ Tech Stack & Dependencies

*   **Backend:** Python 3.8+, Flask, Flask-CORS, PyTorch (CUDA supported), OpenCV, Ultralytics YOLOv8, `deep-sort-realtime`.
*   **Database:** SQLite3 (standard library, thread-safe write locks).
*   **Frontend:** React 18, Vite, CSS Custom Properties (Neo-Brutalist theme featuring custom HSL palettes and fluid layouts).

---

## ⚙️ System Configuration

You can customize the detection performance and alert thresholds in [backend/config.py](file:///d:/Projects/DLCV%20shaam%20project/project/backend/config.py):

| Parameter | Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `VIDEO_SOURCE` | `str`/`int` | `"0"` | `"0"` for default USB webcam, or a RTSP URL stream. |
| `MODEL_PATH` | `str` | `"yolov8s.pt"` | Checkpoint to load (downloads automatically if missing). |
| `DETECTION_CONFIDENCE`| `float` | `0.35` | Global confidence threshold for YOLOv8. |
| `PERSON_CONFIDENCE` | `float` | `0.45` | Stricter filter specifically on people to reduce false positives. |
| `DETECTION_IOU` | `float` | `0.50` | Intersection-over-Union threshold for YOLO NMS. |
| `INFERENCE_IMGSZ` | `int` | `960` | Input resolution size scaled prior to inference. |
| `LOITERING_SECONDS` | `int` | `15` | Minimum seconds in radius to qualify as loitering. |
| `LOITERING_RADIUS_PX` | `int` | `50` | Maximum pixel movement radius allowed during loitering. |
| `ABANDONED_SECONDS` | `int` | `20` | Stationary threshold before a bag is flagged. |
| `RESTRICTED_ZONE` | `list` | `[(100, 100), ...]` | Polygon coordinates mapping the restricted camera area. |
| `ALERT_COOLDOWN_SECONDS`| `int`| `10` | Rate limiter on individual tracking alerts. |
| `MAX_FPS` | `int` | `20` | Throttling speed limit to regulate CPU usage. |
| `TRACKER_MAX_COS_DISTANCE`|`float`| `0.18` | Threshold representing maximum cosine distance for DeepSORT association. |

---

## 🚀 Installation & Setup

### Prerequisites

Ensure you have the following installed on your machine:
*   [Python 3.8+](https://www.python.org/downloads/)
*   [Node.js (v16+)](https://nodejs.org/)
*   CUDA Toolkit (Optional, but highly recommended for GPU acceleration)

### Step 1: Clone the Repository & Setup Backend

Navigate to the project root directory:

```bash
cd project
```

Create and activate a virtual environment:

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

Upgrade package manager and install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: Install Frontend Dependencies

Open a separate terminal window and navigate to the frontend directory:

```bash
cd project/frontend
npm install
```

---

## 🏃 Running the Application

### 1. Start the Flask Backend

From your backend-activated terminal, run:

```bash
cd project/backend
python app.py
```

The server will start listening on **`http://localhost:8000`**.

### 2. Start the React Frontend

From your frontend terminal, run:

```bash
cd project/frontend
npm run dev
```

The Vite dev server will boot up, typically at **`http://localhost:5173`**. Open this URL in your web browser.

---

## 📡 REST API Documentation

The backend exposes the following RESTful API endpoints:

### 1. Toggle Detection Engine
*   **Start Processing Loop**
    *   **Endpoint:** `POST /start`
    *   **Response:** `{"status": "running"}` or `{"status": "already_running"}`
*   **Stop Processing Loop**
    *   **Endpoint:** `POST /stop`
    *   **Response:** `{"status": "stopped"}`

### 2. Retrieve Violations Log
*   **Get Alert History**
    *   **Endpoint:** `GET /alerts?limit=N`
    *   **Query Params:** `limit` (Optional, defaults to 100)
    *   **Response Format:**
        ```json
        [
          {
            "timestamp": "2026-06-09T14:00:23.456Z",
            "object_id": "4",
            "type": "loitering",
            "message": "Track 4 loitering for 18s"
          }
        ]
        ```

### 3. Video Stream
*   **Get Processed MJPEG Stream**
    *   **Endpoint:** `GET /video_feed`
    *   **Response Type:** `multipart/x-mixed-replace; boundary=frame`
    *   **Note:** Designed to be embedded directly into React/HTML using standard image tags: `<img src="http://localhost:8000/video_feed" />`.

### 4. Health Check
*   **Verify Engine & Model Health**
    *   **Endpoint:** `GET /health`
    *   **Response Format:**
        ```json
        {
          "status": "ok",
          "running": true,
          "model_path": "yolov8s.pt",
          "model_exists": true
        }
        ```

---

## 💡 Performance Tuning

*   **GPU Acceleration:** To enable CUDA execution, ensure you install PyTorch with CUDA support matched to your GPU driver:
    ```bash
    pip install torch --extra-index-url https://download.pytorch.org/whl/cu118
    ```
*   **Optimizing Framerates:** If running on a low-power CPU (like a Raspberry Pi or office workstation):
    1.  Switch the model to `yolov8n.pt` (Nano weights) inside `config.py`.
    2.  Decrease the `INFERENCE_IMGSZ` option in `config.py` to `640` or `480` to speed up YOLO inference times.
    3.  Lower the `MAX_FPS` configuration to `10` or `12`.
