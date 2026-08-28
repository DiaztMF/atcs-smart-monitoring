# Smart Traffic Monitoring

Real-time computer vision traffic analytics engine computing Indonesian Highway Capacity Manual (PKJI / MKJI) Passenger Car Units (PCU / SMP) from live ATCS CCTV feeds using YOLOv11, ByteTrack, FastAPI, and Next.js 14.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black?logo=next.js&logoColor=white)](https://nextjs.org/)
[![Ultralytics](https://img.shields.io/badge/YOLOv11-Ultralytics-blue)](https://docs.ultralytics.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Table of Contents

- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [1. Clone Repository](#1-clone-repository)
  - [2. Backend Setup](#2-backend-setup)
  - [3. Frontend Setup](#3-frontend-setup)
- [Quick Start](#quick-start)
  - [Option A: One-Click Dev Server (Windows)](#option-a-one-click-dev-server-windows)
  - [Option B: Manual Terminal Execution](#option-b-manual-terminal-execution)
- [What is Smart Traffic Monitoring?](#what-is-smart-traffic-monitoring)
- [Why Smart Traffic Monitoring?](#why-smart-traffic-monitoring)
- [API & Data Contracts](#api--data-contracts)
  - [REST Endpoints](#rest-endpoints)
  - [WebSocket Metrics Broadcaster](#websocket-metrics-broadcaster)
  - [PKJI / MKJI SMP Weight Standards](#pkji--mkji-smp-weight-standards)
- [Examples & Workflows](#examples--workflows)
  - [Configuring Polygon ROI](#configuring-polygon-roi)
  - [Switching Live CCTV Feeds](#switching-live-cctv-feeds)
  - [Consuming WebSocket Metrics in Python](#consuming-websocket-metrics-in-python)
  - [Generating Synthetic Offline Fallback Video](#generating-synthetic-offline-fallback-video)
  - [Running Automated Tests](#running-automated-tests)
- [Configuration & Environment Variables](#configuration--environment-variables)
- [License](#license)
- [Architecture & Development Guides](#architecture--development-guides)
- [Contributing](#contributing)

---

## Installation

### Prerequisites

Make sure your machine has the following tools installed before starting:

- **Python 3.10+** (Python 3.10, 3.11, 3.12, or 3.13)
- **Node.js 18.17+** or **20+** and **npm**
- **FFmpeg** (required by OpenCV for decoding live FLV/HLS CCTV video streams)
- **Git**

### 1. Clone Repository

```bash
git clone https://github.com/DiaztMF/atcs-smart-monitoring.git
cd atcs-smart-monitoring
```

### 2. Backend Setup

Set up a Python virtual environment and install backend dependencies:

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment (Linux/macOS)
python3 -m venv venv
source venv/bin/activate

# Create and activate virtual environment (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

> **Note on YOLO Model Weights:** The lightweight `yolo11n.pt` model file is included in the repository. If missing, Ultralytics downloads it automatically upon first startup.

### 3. Frontend Setup

From the repository root, install frontend packages using `npm`:

```bash
cd frontend
npm install
```

TypeScript definitions and Tailwind CSS configurations are pre-bundled.

---

## Quick Start

### Option A: One-Click Dev Server (Windows)

If you are on Windows, double-click or run [run_dev.bat](file:///d:/Project/Web%20Project/Enuma/Smart-Monitoring/run_dev.bat) from the root folder:

```cmd
run_dev.bat
```

This launches both the FastAPI backend on port `8000` and the Next.js frontend on port `3000` in separate terminal windows.

### Option B: Manual Terminal Execution

#### Terminal 1 — Backend (FastAPI)

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 2 — Frontend (Next.js)

```bash
cd frontend
npm run dev
```

Once running, access the services in your browser:

- **Web Dashboard:** [http://localhost:3000](http://localhost:3000)
- **Backend Service Root:** [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Live Annotated MJPEG Stream:** [http://localhost:8000/api/v1/stream](http://localhost:8000/api/v1/stream)

---

## What is Smart Traffic Monitoring?

Smart Traffic Monitoring is an end-to-end traffic vision system designed to monitor Indonesian road networks in real time. It ingests public ATCS (Area Traffic Control System) CCTV camera video streams (FLV / RTSP / HLS) and calculates directional road load using the official **Indonesian Highway Capacity Manual (PKJI / MKJI)** Passenger Car Unit (*Satuan Mobil Penumpang - SMP*) standard.

Key capabilities:
- **Vehicle Detection & Tracking:** Detects motorcycles, passenger cars, buses, and heavy trucks using YOLOv11 Nano combined with ByteTrack for persistent vehicle identity tracking across frames.
- **Perspective-Correct Spatial Spatial ROI:** Uses vehicle bottom-center tire contact points `((x1 + x2)/2, y2)` against customizable multi-point polygons to eliminate false counts caused by camera tilt angles.
- **Adaptive Rolling Window:** Measures cumulative SMP counts and 60-second rolling-window throughput (SMP/minute) to classify road conditions (LANCAR, SEDANG, PADAT, MACET).
- **Interactive Web Dashboard:** Allows operators to draw, drag, and update multi-point polygon ROIs directly over the live video canvas, switch between 60+ ATCS live camera presets, and view real-time traffic charts and adaptive traffic light signal split recommendations.

---

## Why Smart Traffic Monitoring?

Traditional traffic monitoring often relies on physical inductive road loops, pneumatic road tubes, or manual tally counters. These methods are expensive to install, damage road surfaces, and cannot differentiate between vehicle types according to Indonesian transport standards.

This system takes a software-first approach:

- **Zero Dedicated Hardware Needed:** Runs on existing public ATCS CCTV streams.
- **High CPU Efficiency:** Uses YOLOv11 Nano and OpenCV C++ bindings (`cv2.pointPolygonTest`), achieving steady 10–15 FPS throughput on standard multi-core CPUs without requiring dedicated GPUs.
- **PKJI Standard Compliance:** Correctly weights traffic by vehicle class (e.g. 1 bus = 1.3 SMP, 1 motorcycle = 0.5 SMP) rather than treating all vehicles as equal counts.
- **Anti-Double-Count State Machine:** Employs a directional counting state machine with a 60-frame Time-To-Live (TTL) cache eviction to ensure vehicles are counted exactly once as they cross the ROI boundary.
- **Built-in Offline Resilience:** Automatically fails over to a local synthetic traffic stream when external live CCTV feeds experience network dropouts.

---

## API & Data Contracts

### REST Endpoints

All REST routes are prefixed with `/api/v1`.

| Method | Route | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Health status, active stream name, and current inference FPS |
| `GET` | `/api/v1/stream` | Multi-client annotated MJPEG video stream (`multipart/x-mixed-replace`) |
| `GET` | `/api/v1/roi` | Retrieves current inbound and outbound normalized polygon coordinates |
| `POST` | `/api/v1/roi` | Updates inbound and outbound polygon coordinates |
| `GET` | `/api/v1/stream-source` | Lists the active video source and 60+ available ATCS presets |
| `POST` | `/api/v1/stream-source` | Switches video input to a custom FLV/RTSP URL or preset camera |
| `POST` | `/api/v1/reset-counter` | Clears all accumulated SMP metrics and resets the tracking cache |

#### `POST /api/v1/roi` Request Body

Coordinates are normalized floats between `0.0` and `1.0`. Polygons require a minimum of 3 points (or an empty array `[]` to clear).

```json
{
  "inbound": [
    [0.05, 0.40],
    [0.45, 0.40],
    [0.45, 0.95],
    [0.05, 0.95]
  ],
  "outbound": [
    [0.55, 0.40],
    [0.95, 0.40],
    [0.95, 0.95],
    [0.55, 0.95]
  ]
}
```

#### `POST /api/v1/stream-source` Request Body

```json
{
  "url": "https://surakarta.atcsindonesia.info:8086/camera/BalaiKota.flv",
  "name": "ATCS Surakarta — Balai Kota"
}
```

---

### WebSocket Metrics Broadcaster

- **Endpoint:** `ws://localhost:8000/ws/metrics`
- **Broadcast Interval:** 1 second

#### Payload Schema

```json
{
  "timestamp": 1724835600.123,
  "fps": 12.4,
  "inbound": {
    "total_smp": 14.5,
    "smp_per_minute": 6.5,
    "density_level": "LANCAR",
    "breakdown": {
      "motorcycle": 7,
      "car": 8,
      "bus": 1,
      "truck": 1
    }
  },
  "outbound": {
    "total_smp": 22.0,
    "smp_per_minute": 14.0,
    "density_level": "SEDANG",
    "breakdown": {
      "motorcycle": 12,
      "car": 12,
      "bus": 2,
      "truck": 1
    }
  },
  "recent_events": [
    {
      "id": "evt_42_1724835600100",
      "timestamp": "16:00:00",
      "direction": "inbound",
      "vehicle_type": "car",
      "smp": 1.0
    }
  ]
}
```

---

### PKJI / MKJI SMP Weight Standards

The application applies vehicle conversion values defined in the Indonesian Highway Capacity Manual:

| COCO Class ID | Vehicle Class | PKJI Equivalent (SMP / PCU) | Description |
|---|---|---|---|
| `3` | Motorcycle (`motorcycle`) | **0.5 SMP** | Sepeda motor / roda dua |
| `2` | Passenger Car (`car`) | **1.0 SMP** | Mobil penumpang, taksi, minibus, sedan |
| `5` | Bus (`bus`) | **1.3 SMP** | Bus kota, bus pariwisata, medium/large bus |
| `7` | Truck (`truck`) | **1.3 SMP** | Truk ringan, truk sedang, kendaraan berat |

#### Density Level Classification (Based on 60-second rolling SMP/min)

| Threshold | Density Level | Status Indicator | Action / Recommendation |
|---|---|---|---|
| `< 10.0 SMP/min` | **LANCAR** | 🟢 Emerald | Arus bebas, waktu hijau seimbang |
| `10.0 – 25.0 SMP/min` | **SEDANG** | 🟡 Amber | Arus stabil, waktu siklus normal |
| `25.0 – 40.0 SMP/min` | **PADAT** | 🟠 Orange | Peningkatan antrean, perpanjang split hijau |
| `> 40.0 SMP/min` | **MACET** | 🔴 Rose | Hambatan kritis, prioritaskan pelepasan antrean |

---

## Examples & Workflows

### Configuring Polygon ROI

You can set custom detection zones either via the web dashboard canvas or directly via the REST API:

```bash
curl -X POST http://localhost:8000/api/v1/roi \
  -H "Content-Type: application/json" \
  -d '{
    "inbound": [[0.1, 0.2], [0.4, 0.2], [0.4, 0.8], [0.1, 0.8]],
    "outbound": [[0.6, 0.2], [0.9, 0.2], [0.9, 0.8], [0.6, 0.8]]
  }'
```

### Switching Live CCTV Feeds

Switch the active video ingestion worker to any public FLV stream:

```bash
curl -X POST http://localhost:8000/api/v1/stream-source \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://surakarta.atcsindonesia.info:8086/camera/Purwosari.flv",
    "name": "ATCS Surakarta — Purwosari"
  }'
```

To switch back to offline demo mode:

```bash
curl -X POST http://localhost:8000/api/v1/stream-source \
  -H "Content-Type: application/json" \
  -d '{
    "url": "synthetic://demo",
    "name": "Mode Demo Offline"
  }'
```

### Consuming WebSocket Metrics in Python

```python
import asyncio
import json
import websockets

async def listen_traffic_metrics():
    uri = "ws://localhost:8000/ws/metrics"
    async with websockets.connect(uri) as websocket:
        print("Connected to Smart Traffic Monitoring WebSocket...")
        while True:
            raw_message = await websocket.recv()
            data = json.loads(raw_message)
            print(f"[{data.get('fps', 0)} FPS] Inbound SMP/min: {data['inbound']['smp_per_minute']} | Density: {data['inbound']['density_level']}")

if __name__ == "__main__":
    asyncio.run(listen_traffic_metrics())
```

### Generating Synthetic Offline Fallback Video

If testing in an environment without internet access to live CCTV streams, generate an animated synthetic traffic video:

```bash
python backend/sample_data/generate_sample_video.py
```

This creates `sample_data/synthetic_traffic.mp4`, containing animated simulated vehicles for offline detection.

### Running Automated Tests

Run the full pytest suite to verify SMP math, ROI spatial test logic, TTL eviction, and API contracts:

```bash
pytest backend/tests -v
```

Expected output:

```text
backend/tests/test_api.py::test_health_endpoint PASSED
backend/tests/test_api.py::test_stream_source_endpoints PASSED
backend/tests/test_api.py::test_roi_get_and_post_valid PASSED
backend/tests/test_api.py::test_roi_post_validation_error_fewer_than_3_points PASSED
backend/tests/test_api.py::test_roi_post_validation_error_out_of_bounds PASSED
backend/tests/test_api.py::test_reset_counter PASSED
backend/tests/test_detector.py::test_detector_draw_visualizations PASSED
backend/tests/test_detector.py::test_detector_dry_run_detect_and_track PASSED
backend/tests/test_roi_tracker.py::test_smp_weights_standard PASSED
backend/tests/test_roi_tracker.py::test_bottom_center_calculation PASSED
backend/tests/test_roi_tracker.py::test_spatial_polygon_and_counting PASSED
backend/tests/test_roi_tracker.py::test_rolling_window_deque_expiration PASSED
backend/tests/test_roi_tracker.py::test_ttl_purge PASSED
backend/tests/test_state.py::test_global_state_frame_and_metrics PASSED
backend/tests/test_state.py::test_global_state_roi_and_reset PASSED
backend/tests/test_stream_service.py::test_mjpeg_generator_yields_valid_frames PASSED

======================= 16 passed in 2.50s =======================
```

---

## Configuration & Environment Variables

### Backend Settings

Backend configurations can be supplied via environment variables or a `.env` file in the `backend/` directory:

| Variable | Type | Default | Description |
|---|---|---|---|
| `VIDEO_STREAM_URL` | `string` | `https://surakarta.atcsindonesia.info:8086/camera/BalaiKota.flv` | Default live CCTV stream URL |
| `FALLBACK_VIDEO_PATH` | `string` | `sample_data/synthetic_traffic.mp4` | Path to offline fallback video |
| `TARGET_FPS` | `int` | `12` | Ingestion and inference target frame rate |
| `STREAM_WIDTH` | `int` | `640` | Video frame processing width |
| `STREAM_HEIGHT` | `int` | `360` | Video frame processing height |
| `JPEG_QUALITY` | `int` | `65` | Compression quality for MJPEG broadcaster (1-100) |
| `TTL_FRAME_PURGE` | `int` | `60` | Inactive vehicle track cache expiration (frames) |
| `ROI_PERSISTENCE_PATH` | `string` | `default_roi.json` | JSON path for saving persistent ROI coordinates |
| `CORS_ORIGINS` | `list` | `["http://localhost:3000", "http://localhost:8000"]` | Allowed CORS origins for web clients |

### Frontend Settings

Configured in `frontend/.env.local` or environment variables:

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_BACKEND_URL` | `http://localhost:8000` | Backend HTTP REST endpoint base URL |
| `NEXT_PUBLIC_WS_URL` | `ws://localhost:8000/ws/metrics` | Backend WebSocket metrics streaming URL |

---

## License

This project is licensed under the MIT License — see the [LICENSE](./LICENSE) file for details.

---

## Architecture & Development Guides

For deeper technical context and behavioral guidelines when developing or contributing:

- **[AGENTS.md](./AGENTS.md)** — Architectural conventions, PKJI calculation standards, bottom-center wheel spatial anchor rules, thread-safety models, and testing requirements.

---

## Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run backend tests to verify mathematical and API integrity:
   ```bash
   pytest backend/tests -v
   ```
4. Run frontend lint checks:
   ```bash
   cd frontend
   npm run lint
   ```
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request
