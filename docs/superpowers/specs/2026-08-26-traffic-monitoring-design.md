# Design Document: Sistem Monitoring dan Penghitung Beban Lalu Lintas Real-Time Berbasis Computer Vision

**Tanggal:** 2026-08-26  
**Status:** Approved by User  
**Tujuan:** Mengukur beban jalan dua arah berstandar Satuan Mobil Penumpang (SMP) secara real-time dari video stream CCTV publik (FLV) sebagai fondasi kontrol lampu lalu lintas adaptif 4 arah, berjalan 100% pada ekosistem free-tier (FastAPI + YOLOv11 + ByteTrack + Next.js).

---

## 1. Arsitektur Sistem & Struktur Monorepo

### 1.1 Diagram Arsitektur
```
+-----------------------------------------------------------------------------------------+
|                                      BACKEND (FastAPI)                                  |
|                                                                                         |
|  +--------------------+      +--------------------+      +---------------------------+  |
|  |   Stream Reader    | ---> |  Detection Engine  | ---> |   Spatial ROI Tracker     |  |
|  | (FLV/Fallback Vid) |      | (YOLO11n+ByteTrack)|      | (Bottom-Center & PKJI SMP)|  |
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
+-----------------------------------------------------------------------------------------+
```

### 1.2 Struktur Folder
```text
Smart-Monitoring/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints.py       # REST API: CRUD ROI (/api/v1/roi), status, reset counter
│   │   │   └── websocket.py       # WebSocket broadcaster metrik statistik (/ws/metrics)
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py          # App settings (Pydantic Settings, CORS, Stream URLs)
│   │   │   ├── state.py           # Thread-safe global state & buffer manager
│   │   │   └── logging.py         # Structured logging configuration
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── stream_reader.py   # Background worker pembaca FLV stream / fallback video
│   │   │   ├── detector.py        # Pipeline YOLOv11n + ByteTrack persistent tracker
│   │   │   ├── roi_tracker.py     # Logika spasial poligon, Bottom-Center raycast, hitung SMP
│   │   │   └── mjpeg_stream.py    # Generator multipart/x-mixed-replace JPEG frames
│   │   └── main.py                # Entrypoint FastAPI & lifecycle manager
│   ├── sample_data/               # Sample video clip untuk offline/fallback demo
│   ├── requirements.txt           # fastapi, uvicorn, ultralytics, opencv-python-headless, etc.
│   └── Dockerfile                 # Hugging Face Spaces CPU optimized Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CanvasROI.tsx      # Canvas overlay untuk penentuan poligon Inbound/Outbound
│   │   │   ├── VideoPlayer.tsx    # Komponen render stream MJPEG + HUD status
│   │   │   ├── MetricsCard.tsx    # Card metrik SMP, density level, dan laju kendaraan/jam
│   │   │   ├── VehicleBreakdown.tsx # Breakdown jumlah kendaraan (Motor, Mobil, Bus, Truk)
│   │   │   ├── TrafficChart.tsx   # Grafik histori laju beban SMP real-time (Recharts)
│   │   │   └── LiveFeed.tsx       # Real-time event log kendaraan yang terhitung
│   │   ├── hooks/
│   │   │   └── useWebSocket.ts    # Custom hook pengelola koneksi WebSocket & auto-reconnect
│   │   ├── types/
│   │   │   └── index.ts           # Definisi TypeScript interface (Metrics, ROI, VehicleEvent)
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
* **Object Tracking:** ByteTrack (`track(source=..., persist=True, tracker="bytetrack.yaml")`).

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
* **Formula Perhitungan:**
  $$\text{SMP}_{\text{inbound}} = \sum (N_{\text{motor, in}} \times 0.5) + (N_{\text{mobil, in}} \times 1.0) + (N_{\text{bus, in}} \times 1.3) + (N_{\text{truk, in}} \times 1.3)$$
  $$\text{SMP}_{\text{outbound}} = \sum (N_{\text{motor, out}} \times 0.5) + (N_{\text{mobil, out}} \times 1.0) + (N_{\text{bus, out}} \times 1.3) + (N_{\text{truk, out}} \times 1.3)$$
* **Klasifikasi Tingkat Kepadatan (*Density Level*):**
  * $\text{SMP/menit} < 10 \implies$ **LANCAR (Smooth - Green)**
  * $10 \le \text{SMP/menit} < 25 \implies$ **SEDANG (Moderate - Yellow)**
  * $25 \le \text{SMP/menit} < 40 \implies$ **PADAT (Dense - Orange)**
  * $\text{SMP/menit} \ge 40 \implies$ **MACET (Congested - Red)**

### 2.4 State Management & Anti-Double-Count dengan TTL Purge
* `state.py` menyimpan state kendaraan yang dilacak:
  ```python
  class TrackedObject:
      track_id: int
      class_name: str
      smp_value: float
      counted_inbound: bool = False
      counted_outbound: bool = False
      last_seen_frame: int
  ```
* **Status Transisi:** `OUTSIDE` $\rightarrow$ `INSIDE_ROI` $\rightarrow$ `COUNTED`.
* **Memory Purge:** Objek yang tidak terdeteksi selama lebih dari 60 frame berturut-turut akan dihapus dari *active tracking memory* untuk mencegah memori membengkak (*leak prevention*).

---

## 3. API Contract & Data Schema

### 3.1 REST Endpoints
1. `GET /api/v1/health`  
   * **Response:** `{"status": "ok", "stream_active": true, "fps": 12.5}`
2. `GET /api/v1/roi`  
   * **Response:**
     ```json
     {
       "inbound": [[0.1, 0.4], [0.4, 0.4], [0.4, 0.9], [0.1, 0.9]],
       "outbound": [[0.6, 0.4], [0.9, 0.4], [0.9, 0.9], [0.6, 0.9]]
     }
     ```
3. `POST /api/v1/roi`  
   * **Request Body:**
     ```json
     {
       "inbound": [[0.1, 0.4], [0.4, 0.4], [0.4, 0.9], [0.1, 0.9]],
       "outbound": [[0.6, 0.4], [0.9, 0.4], [0.9, 0.9], [0.6, 0.9]]
     }
     ```
   * **Response:** `{"status": "success", "message": "ROI updated successfully"}`
4. `POST /api/v1/reset-counter`  
   * **Response:** `{"status": "success", "message": "Counters reset to zero"}`
5. `GET /api/v1/stream`  
   * **Response Content-Type:** `multipart/x-mixed-replace; boundary=frame` (MJPEG video stream dengan bounding box dan visualisasi poligon ROI).

### 3.2 WebSocket Stream (`/ws/metrics`)
* **Interval:** Broadcast 1 detik sekali.
* **Payload Format:**
  ```json
  {
    "timestamp": 1771982400.12,
    "fps": 12.4,
    "inbound": {
      "total_smp": 45.5,
      "smp_per_minute": 14.2,
      "density_level": "SEDANG",
      "breakdown": {
        "motorcycle": 35,
        "car": 21,
        "bus": 2,
        "truck": 4
      }
    },
    "outbound": {
      "total_smp": 38.0,
      "smp_per_minute": 11.5,
      "density_level": "SEDANG",
      "breakdown": {
        "motorcycle": 28,
        "car": 18,
        "bus": 1,
        "truck": 3
      }
    },
    "recent_events": [
      {
        "id": "evt_1092",
        "timestamp": "14:30:15",
        "direction": "inbound",
        "vehicle_type": "car",
        "smp": 1.0
      }
    ]
  }
  ```

---

## 4. Frontend & Interactive Canvas

### 4.1 UI Layout (Dark/Modern Glassmorphism)
* **Top Navigation:** Status CCTV Live (Surakarta Balai Kota / Fallback), Status WebSocket, FPS Indicator, dan Tombol Setting/ROI.
* **Main Area (Grid 2 Kolom):**
  * **Kiri (Video & Canvas):**
    * MJPEG `<img />` stream viewer.
    * Overlay HTML5 `<canvas />` untuk pembuatan titik poligon (klik untuk menambah titik, double click untuk menutup poligon).
    * Toolbar: Mode Inbound (Green/Cyan), Mode Outbound (Orange/Red), Clear ROI, Save ROI, Reset Counters.
  * **Kanan (Metrik & Visualisasi):**
    * Inbound vs Outbound SMP Comparison Cards (Indikator SMP Kumulatif, SMP/Menit, Density Badge).
    * Breakdown Card per Tipe Kendaraan dengan koefisien SMP masing-masing.
    * Real-time Line Chart (Beban Lalu Lintas SMP 5 Menit Terakhir).
    * Live Event Activity Feed (10 riwayat kendaraan terakhir terhitung).

---

## 5. Resiliency, Performance & Deployment

1. **Stream Reconnection:**  
   * `stream_reader.py` memonitor kegagalan baca frame dengan batas toleransi 5 frame gagal sebelum melakukan reconnect otomatis dengan *exponential backoff* (1s, 2s, 4s, max 10s).
   * Disediakan file sampel video MP4/AVI sintetis di `backend/sample_data/` sebagai auto-fallback saat stream FLV publik unreachable.
2. **CPU Free-Tier Throttling:**  
   * Loop inferensi dibatasi pada 10–15 FPS menggunakan `time.sleep` adaptif berdasarkan delta waktu komputasi frame.
3. **Deployment Strategy:**  
   * **Backend:** Hugging Face Spaces (Docker runtime) / Cloudflare Tunnel / Local.
   * **Frontend:** Vercel (Next.js App Router).
   * Variabel lingkungan `NEXT_PUBLIC_BACKEND_URL` dan `NEXT_PUBLIC_WS_URL` fleksibel untuk URL lokal maupun remote.

---

## 6. Rencana Pengujian (Testing Strategy)
* **Backend Unit Tests:**
  * Pengujian perhitungan SMP sesuai bobot PKJI (`test_roi_tracker.py`).
  * Pengujian `pointPolygonTest` dan normalisasi koordinat ($0.0 \dots 1.0$).
  * Pengujian memory purge TTL pada `state.py`.
* **Integration Tests:**
  * Endpoint REST `/api/v1/roi` dan `/api/v1/reset-counter`.
  * Endpoint WebSocket broadcast `/ws/metrics`.
* **Frontend Component & Hook Tests:**
  * Pengecekan rendering canvas dan kalkulasi koordinat relatif.
  * Pengecekan hook `useWebSocket` auto-reconnection logic.
