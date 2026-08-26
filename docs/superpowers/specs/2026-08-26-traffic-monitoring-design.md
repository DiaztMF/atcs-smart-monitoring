# Design Document: Sistem Monitoring dan Penghitung Beban Lalu Lintas Real-Time Berbasis Computer Vision

**Tanggal:** 2026-08-26  
**Status:** Approved & Enhanced  
**Tujuan:** Mengukur beban jalan dua arah berstandar Satuan Mobil Penumpang (SMP) secara real-time dari video stream CCTV publik (FLV/HLS/MP4/RTSP) sebagai fondasi kontrol lampu lalu lintas adaptif 4 arah, berjalan 100% pada ekosistem free-tier (FastAPI + YOLOv11 + ByteTrack + Next.js), dilengkapi fitur **Dynamic CCTV Switcher & Preset Selector**.

---

## 1. Arsitektur Sistem & Struktur Monorepo

### 1.1 Diagram Arsitektur
```
+-----------------------------------------------------------------------------------------+
|                                      BACKEND (FastAPI)                                  |
|                                                                                         |
|  +--------------------+      +--------------------+      +---------------------------+  |
|  |   Stream Reader    | ---> |  Detection Engine  | ---> |   Spatial ROI Tracker     |  |
|  | (Dynamic FLV/RTSP) |      | (YOLO11n+ByteTrack)|      | (Bottom-Center & PKJI SMP)|  |
|  +--------------------+      +--------------------+      +---------------------------+  |
|            |                           |                               |                |
|            +---------------------------+-------------------------------+                |
|                                        v                                                |
|                             Global State Manager                                        |
|                     (Thread-safe Queue/Locks in state.py)                               |
|                                        |                                                |
|                   +--------------------+--------------------+                           |
|                   v                                         v                           |
|         MJPEG Video Stream                        WebSocket Broadcast                   |
|        (/api/v1/stream)                              (/ws/metrics)                      |
+-------------------|-----------------------------------------|---------------------------+
                    |                                         |
                    v                                         v
+-----------------------------------------------------------------------------------------+
|                                    FRONTEND (Next.js)                                   |
|                                                                                         |
|  +--------------------------------+       +------------------------------------------+  |
|  |      Video Stream Player       |       |       Interactive HTML5 Canvas ROI       |  |
|  |  (MJPEG Display + Stream FPS)  | <---  |  (Normalized Coords: Inbound/Outbound)   |  |
|  +--------------------------------+       +------------------------------------------+  |
|                   |                                         |                           |
|                   +--------------------+--------------------+                           |
|                                        v                                                |
|                    +----------------------------------------+                           |
|                    |   Real-Time Traffic Dashboard (SMP)    |                           |
|                    |  (Charts, Metrics Cards, Live Activity)|                           |
|                    +----------------------------------------+                           |
|                                        |                                                |
|                    +----------------------------------------+                           |
|                    | Dynamic CCTV Switcher & Preset Selector|                           |
|                    +----------------------------------------+                           |
+-----------------------------------------------------------------------------------------+
```

### 1.2 Struktur Folder
```text
Smart-Monitoring/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints.py       # REST API: CRUD ROI (/api/v1/roi), stream source switcher, status
│   │   │   └── websocket.py       # WebSocket broadcaster metrik statistik (/ws/metrics)
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py          # App settings (Pydantic Settings, CORS, CCTV Presets)
│   │   │   ├── state.py           # Thread-safe global state & pre-encoded JPEG buffer
│   │   │   └── logging.py         # Structured logging configuration
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── stream_reader.py   # Background worker pembaca dynamic FLV stream / fallback video
│   │   │   ├── detector.py        # Pipeline YOLOv11n + ByteTrack persistent tracker
│   │   │   ├── roi_tracker.py     # Logika spasial poligon, Bottom-Center raycast, 60s rolling window SMP
│   │   │   └── mjpeg_stream.py    # Generator multipart/x-mixed-replace JPEG frames
│   │   └── main.py                # Entrypoint FastAPI & root status / healthz handler
│   ├── sample_data/               # Sample video clip generator untuk offline demo
│   ├── requirements.txt           # fastapi, uvicorn, ultralytics, lapx, opencv-python-headless, etc.
│   └── default_roi.json           # Persistent default ROI coordinates
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CanvasROI.tsx      # Canvas overlay untuk penentuan poligon Inbound/Outbound
│   │   │   ├── VideoPlayer.tsx    # Komponen render stream MJPEG + HUD status & switcher button
│   │   │   ├── CCTVSelectorModal.tsx # Dialog pemilihan preset CCTV & input URL custom
│   │   │   ├── MetricsCard.tsx    # Card metrik SMP, density level, dan laju kendaraan/menit
│   │   │   ├── VehicleBreakdown.tsx # Breakdown jumlah kendaraan (Motor, Mobil, Bus, Truk)
│   │   │   ├── TrafficChart.tsx   # Grafik histori laju beban SMP real-time (Recharts)
│   │   │   └── LiveFeed.tsx       # Real-time event log kendaraan yang terhitung
│   │   ├── hooks/
│   │   │   └── useWebSocket.ts    # Custom hook pengelola koneksi WebSocket & auto-reconnect
│   │   ├── types/
│   │   │   └── index.ts           # Definisi TypeScript interface (Metrics, ROI, StreamSource)
│   │   └── app/
│   │       ├── globals.css        # Tailwind CSS styling
│   │       ├── layout.tsx         # Root layout
│   │       └── page.tsx           # Dashboard utama
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── next.config.js
├── docs/
│   └── superpowers/specs/
│       └── 2026-08-26-traffic-monitoring-design.md
└── README.md
```

---

## 2. Spesifikasi Backend & Pipeline AI

### 2.1 Model AI & Tracking
* **Model:** Ultralytics YOLOv11 Nano (`yolo11n.pt`) untuk efisiensi inferensi pada environment CPU.
* **Filter Kelas COCO Target:**
  * Kelas ID 3: `motorcycle`
  * Kelas ID 2: `car`
  * Kelas ID 5: `bus`
  * Kelas ID 7: `truck`
* **Object Tracking:** ByteTrack (`track(source=..., persist=True, tracker="bytetrack.yaml")`) dengan dependency `lapx`.

### 2.2 Geometri Spasial & Titik Kontak Roda (Bottom-Center)
* Titik evaluasi kontak aspal kendaraan dihitung dari koordinat bounding box:
  $$P_{\text{wheel}} = \left( \frac{x_1 + x_2}{2}, y_2 \right)$$
* Pengecekan spasial poligon menggunakan OpenCV C++ binding native:
  $$\text{inside} = \text{cv2.pointPolygonTest}(\text{contour}, P_{\text{wheel}}, \text{False}) \ge 0$$
* Format koordinat poligon yang diterima dari frontend dinormalisasi ($0.0 \dots 1.0$), kemudian diskalakan ke dimensi frame video aktual:
  $$x_{\text{pixel}} = x_{\text{norm}} \times W_{\text{frame}}, \quad y_{\text{pixel}} = y_{\text{norm}} \times H_{\text{frame}}$$

### 2.3 Standar Perhitungan SMP (Pedoman Kapasitas Jalan Indonesia / PKJI)
* **Koefisien Ekivalen Mobil Penumpang (emp):**
  * Sepeda Motor (`motorcycle`) = **0.5 SMP**
  * Mobil Penumpang (`car`) = **1.0 SMP**
  * Bus (`bus`) = **1.3 SMP**
  * Truk (`truck`) = **1.3 SMP**
* **Rolling Window 60-Detik (`collections.deque`):**
  Metrik `smp_per_minute` dihitung secara dinamis dari jumlah akumulasi SMP kendaraan yang melintasi poligon dalam 60 detik terakhir.
* **Klasifikasi Tingkat Kepadatan (*Density Level*):**
  * $\text{SMP/menit} < 10 \implies$ **LANCAR (Smooth - Green)**
  * $10 \le \text{SMP/menit} < 25 \implies$ **SEDANG (Moderate - Yellow)**
  * $25 \le \text{SMP/menit} < 40 \implies$ **PADAT (Dense - Orange)**
  * $\text{SMP/menit} \ge 40 \implies$ **MACET (Congested - Red)**

### 2.4 State Management & Dynamic Stream Switching
* `state.py` mengelola:
  * Active stream URL dan stream name.
  * Single-pass pre-encoded JPEG bytes buffer untuk optimasi konkurensi client.
  * Active ROIs dengan validasi minimal 3 titik ($N \ge 3$).
  * Rolling tracking history dengan TTL purge 60 frame.

---

## 3. API Contract & Data Schema

### 3.1 REST Endpoints
1. `GET /api/v1/health`  
   * **Response:** `{"status": "ok", "stream_active": true, "fps": 12.5}`
2. `GET /api/v1/stream-source`  
   * **Response:**
     ```json
     {
       "active_source": {
         "id": "surakarta_balaikota",
         "name": "ATCS Surakarta — Simpang Balai Kota",
         "url": "http://bptdjatengdiy.dephub.go.id:8000/live/atcs_surakarta_balaikota.flv"
       },
       "presets": [
         {
           "id": "surakarta_balaikota",
           "name": "ATCS Surakarta — Simpang Balai Kota",
           "url": "http://bptdjatengdiy.dephub.go.id:8000/live/atcs_surakarta_balaikota.flv"
         },
         {
           "id": "surakarta_gladak",
           "name": "ATCS Surakarta — Simpang Gladak",
           "url": "http://bptdjatengdiy.dephub.go.id:8000/live/atcs_surakarta_gladak.flv"
         },
         {
           "id": "surakarta_kerten",
           "name": "ATCS Surakarta — Simpang Kerten",
           "url": "http://bptdjatengdiy.dephub.go.id:8000/live/atcs_surakarta_kerten.flv"
         },
         {
           "id": "surakarta_gendengan",
           "name": "ATCS Surakarta — Simpang Gendengan",
           "url": "http://bptdjatengdiy.dephub.go.id:8000/live/atcs_surakarta_gendengan.flv"
         },
         {
           "id": "synthetic_loop",
           "name": "Synthetic Traffic Simulator (In-Memory Fallback)",
           "url": "synthetic://traffic_loop"
         }
       ]
     }
     ```
3. `POST /api/v1/stream-source`  
   * **Request Body:**
     ```json
     {
       "url": "http://bptdjatengdiy.dephub.go.id:8000/live/atcs_surakarta_gladak.flv",
       "name": "ATCS Surakarta — Simpang Gladak"
     }
     ```
   * **Response:** `{"status": "success", "message": "Stream source switched successfully", "active_source": {...}}`
4. `GET /api/v1/roi`  
   * **Response:** `{"inbound": [...], "outbound": [...]}`
5. `POST /api/v1/roi` (Validasi $N \ge 3$ atau $N = 0$)  
   * **Response:** `{"status": "success", "message": "ROI updated successfully"}`
6. `POST /api/v1/reset-counter`  
   * **Response:** `{"status": "success", "message": "Counters reset to zero"}`
7. `GET /api/v1/stream`  
   * **Response Content-Type:** `multipart/x-mixed-replace; boundary=frame`

### 3.2 WebSocket Stream (`/ws/metrics`)
* **Interval:** Broadcast 1 detik sekali.
* **Payload:** Metrik real-time mencakup total SMP, rolling SMP/menit (60s), density level, vehicle breakdown per arah, dan 15 recent events.

---

## 4. Frontend & Interactive Canvas

### 4.1 UI Layout (Dark/Modern Glassmorphism)
* **Top Navigation:** Status CCTV Live, Status WebSocket, FPS Indicator, dan Tombol **"Ganti Kamera / Input URL"**.
* **Stream Source Switcher Modal (`CCTVSelectorModal.tsx`):**
  * Grid preset kamera ATCS siap pakai (Balai Kota, Gladak, Kerten, Gendengan, Synthetic Fallback).
  * Input Form URL Custom (mendukung stream FLV / HLS / MP4 / RTSP dari berbagai kota/sumber).
* **Video Player & Canvas (`VideoPlayer.tsx`, `CanvasROI.tsx`):**
  * MJPEG `<img />` stream viewer dengan HUD camera name & FPS.
  * Overlay Canvas ROI Inbound & Outbound ($0.0 \dots 1.0$).
* **Analytics Panel (`MetricsCard.tsx`, `VehicleBreakdown.tsx`, `TrafficChart.tsx`, `LiveFeed.tsx`):**
  * Perbandingan beban jalan Inbound vs Outbound.
  * Visualisasi Recharts tren SMP/menit secara reaktif.
  * Log 15 kendaraan terakhir yang terhitung secara akurat.

---

## 5. Resiliency, Performance & Deployment
1. **Dynamic Reconnection:** `stream_reader.py` mendukung switch stream *on-the-fly* tanpa perlu restart server atau uvicorn instance.
2. **In-Memory Fallback:** Jika URL kamera publik sedang mati/unreachable, sistem secara otomatis beralih ke *real-time in-memory traffic generator*.
3. **Target Environment:**
   * Backend: Render.com / Hugging Face / Docker Container.
   * Frontend: Vercel App Router.
