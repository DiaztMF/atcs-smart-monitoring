# Smart Traffic Monitoring (SMP / PCU)
Sistem monitoring dan penghitung beban lalu lintas real-time berbasis Computer Vision untuk mengukur beban jalan dua arah (PKJI / SMP) sebagai fondasi kontrol lampu lalu lintas adaptif 4-arah.

## Pages / Routes

| Route | Page | Description |
|---|---|---|
| `/` | Dashboard Utama | Live MJPEG player, interactive polygon ROI canvas, real-time charts & vehicle breakdown |
| `/api/v1/stream` | Stream Endpoint | Real-time multipart MJPEG annotated stream |
| `/api/v1/roi` | ROI Endpoint | GET/POST koordinat poligon ter-normalisasi ($0.0 \dots 1.0$) dengan validasi minimal 3 titik |
| `/api/v1/health` | Health Check | Status live stream, active worker, dan inference FPS |
| `/api/v1/reset-counter` | Reset Counter | Mereset seluruh akumulasi beban SMP dan histori tracking |
| `/ws/metrics` | WebSocket Broadcaster | JSON stream metrik lalu lintas real-time (rolling window 60 detik) tiap 1 detik |

## Project Structure

```text
Smart-Monitoring/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints.py        # REST API endpoints (ROI CRUD, health, reset)
│   │   │   └── websocket.py        # WebSocket metrics broadcast handler
│   │   ├── core/
│   │   │   ├── config.py           # Application settings & environment configuration
│   │   │   ├── logging.py          # Structured logging configuration
│   │   │   └── state.py            # Thread-safe global state & pre-encoded JPEG buffer
│   │   ├── services/
│   │   │   ├── detector.py         # YOLOv11 + ByteTrack AI inference service
│   │   │   ├── mjpeg_stream.py     # Multi-client optimized MJPEG generator
│   │   │   ├── roi_tracker.py      # Spatial ROI, bottom-center wheel point & PKJI SMP engine
│   │   │   └── stream_reader.py    # Background worker pembaca FLV stream / fallback video
│   │   └── main.py                 # FastAPI application entrypoint with lifespan manager
│   ├── default_roi.json            # Persistent default ROI coordinates
│   ├── requirements.txt            # Python dependencies (FastAPI, YOLOv11, OpenCV, etc.)
│   └── Dockerfile                  # Hugging Face Spaces CPU optimized image
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── globals.css         # Tailwind dark theme & glassmorphism styling
│   │   │   ├── layout.tsx          # Root layout
│   │   │   └── page.tsx            # Main traffic analytics dashboard
│   │   ├── components/
│   │   │   ├── CanvasROI.tsx       # Interactive HTML5 Canvas ROI overlay
│   │   │   ├── LiveFeed.tsx        # Real-time event log kendaraan terhitung
│   │   │   ├── MetricsCard.tsx     # Kartu metrik beban jalan & density badge
│   │   │   ├── TrafficChart.tsx    # Grafik tren beban lalu lintas (Recharts)
│   │   │   ├── VehicleBreakdown.tsx # Breakdown jumlah kendaraan per kelas PKJI
│   │   │   └── VideoPlayer.tsx     # MJPEG stream viewer & ROI toolbar
│   │   ├── hooks/
│   │   │   └── useWebSocket.ts     # Custom WebSocket hook with auto-reconnection
│   │   └── types/
│   │       └── index.ts            # TypeScript shared contracts
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
└── README.md
```

## Tech Stack

- **FastAPI** — Server ASGI berkinerja tinggi dengan WebSocket native dan lifespan async context manager
- **Ultralytics YOLOv11 Nano** — Model object detection terkini dengan efisiensi FLOPs tinggi untuk inferensi CPU free-tier
- **ByteTrack** — Multi-object tracker berbasis Kalman Filter untuk pelacakan ID unik kendaraan yang stabil
- **OpenCV Headless** — Pemrosesan frame video, single-pass JPEG encoding, dan komputasi spasial C++ `pointPolygonTest`
- **Next.js 14** — Framework React modern berbasis App Router dengan performa tinggi
- **Tailwind CSS** — Utilitas CSS bertema dark glassmorphism modern
- **Recharts** — Library visualisasi data reaktif untuk grafik beban lalu lintas real-time

## Scripts

| Script | Command | Description |
|---|---|---|
| Backend Dev | `uvicorn app.main:app --port 8000 --reload` | Menjalankan server backend FastAPI (dari folder `backend`) |
| Backend Tests | `pytest backend/tests -v` | Menjalankan seluruh pengujian unit dan integrasi backend |
| Generate Clip | `python backend/sample_data/generate_sample_video.py` | Membuat file video sintetis untuk fallback demo offline |
| Frontend Dev | `npm run dev` | Menjalankan server development Next.js (dari folder `frontend`) |
| Frontend Build | `npm run build` | Melakukan build bundle produksi Next.js |

## Quick Start

1. **Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   python sample_data/generate_sample_video.py
   uvicorn app.main:app --port 8000 --reload
   ```

2. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Akses dashboard melalui browser di `http://localhost:3000`.
