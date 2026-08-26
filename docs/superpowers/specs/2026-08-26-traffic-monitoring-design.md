# Product Requirements Document (PRD) & UI/UX Design System Specification
## Smart Traffic Monitoring: Real-Time Computer Vision & PKJI SMP Analytics

- **Document Version:** 2.0.0 (Master Comprehensive Edition)
- **Project Name:** Smart Traffic Monitoring (SMP / PCU Analytics)
- **Target Platform:** Web Desktop & Tablet (Optimized for 1920x1080 and 1440x900 Command Center Dashboards)
- **Core Architecture:** Next.js 14 (App Router) + FastAPI (YOLOv11n + ByteTrack) + WebSocket Real-Time Stream

---

## 1. Executive Summary & Product Vision

### 1.1 Purpose
Sistem monitoring lalu lintas berbasis Computer Vision yang mengukur beban jalan dua arah (**Inbound** vs **Outbound**) secara *real-time* dengan standar **Satuan Mobil Penumpang (SMP / Passenger Car Unit - PCU)** sesuai **Pedoman Kapasitas Jalan Indonesia (PKJI / MKJI)**. Data beban ini dirancang sebagai fondasi kontrol lampu lalu lintas adaptif 4-arah (*Adaptive Traffic Light Control System*).

### 1.2 Core Capabilities
1. **Dynamic Video Ingestion:** Memproses live stream FLV/HLS CCTV publik ATCS (Surakarta & kota lain) serta synthetic demo fallback.
2. **Interactive Spatial ROI Canvas:** Pengguna dapat menggambar dan mengedit poligon area deteksi (Inbound & Outbound) langsung di atas video dengan normalisasi koordinat $0.0 \dots 1.0$.
3. **Ground-Contact Wheel Point Tracking:** Menggunakan titik kontak ban bawah $( \frac{x_1 + x_2}{2}, y_2 )$ untuk akurasi perspektif kamera CCTV miring.
4. **Real-Time Rolling Window SMP:** Menghitung total beban akumulasi dan laju beban 60 detik (*rolling window*) menggunakan `collections.deque`.
5. **Adaptive Signal Recommendation Engine:** Menghitung estimasi rekomendasi durasi lampu hijau (dalam detik) berdasarkan rasio beban Inbound vs Outbound.

---

## 2. Design System Tokens & Visual Language

### 2.1 Aesthetic Archetype: Dark High-Tech Command Center (Glassmorphism)
- **Visual Style:** Futuristic, clean, utilitarian, high-density traffic monitoring command center.
- **Surface Elevation:** Semi-transparent dark surfaces with background blur, 1px subtle borders, crisp accent highlights.

### 2.2 Color Palette & Semantic Tokens

| Token Name | Hex Code | RGB / Alpha | Semantic Usage |
|---|---|---|---|
| `--bg-base` | `#07090e` | `rgb(7, 9, 14)` | Canvas / Background layar utama |
| `--bg-panel` | `#0f172a` | `rgba(15, 23, 42, 0.75)` | Kartu / Panel glassmorphism |
| `--bg-surface-dark` | `#020617` | `rgba(2, 6, 23, 0.90)` | Container internal, dropdown, modal header |
| `--border-subtle` | `#1e293b` | `rgba(30, 41, 59, 0.80)` | Border panel standar |
| `--border-highlight` | `#334155` | `rgba(51, 65, 85, 0.60)` | Border hover / divider |
| **Inbound Primary** | `#10b981` | `rgb(16, 185, 129)` | Arah Masuk, Poligon Inbound, Badge Hijau Emerald |
| **Inbound Secondary** | `#064e3b` | `rgba(6, 78, 59, 0.50)` | Background tag/pill Inbound |
| **Outbound Primary** | `#f59e0b` | `rgb(245, 158, 11)` | Arah Keluar, Poligon Outbound, Badge Amber |
| **Outbound Secondary** | `#78350f` | `rgba(120, 53, 15, 0.50)` | Background tag/pill Outbound |
| **Status: Lancar** | `#10b981` | `Emerald-500` | Beban $< 10$ SMP/menit (Lancar / Smooth) |
| **Status: Sedang** | `#eab308` | `Yellow-500` | $10 \le \text{Beban} < 25$ SMP/menit (Sedang / Moderate) |
| **Status: Padat** | `#f97316` | `Orange-500` | $25 \le \text{Beban} < 40$ SMP/menit (Padat / Dense) |
| **Status: Macet** | `#ef4444` | `Rose-500` | Beban $\ge 40$ SMP/menit (Macet / Congested) |

### 2.3 Typography System
- **Primary Font Family:** Inter / Plus Jakarta Sans / System UI.
- **Monospace Font Family:** JetBrains Mono / Fira Code (untuk angka metrik, timestamp, koordinat, FPS).
- **Scale Hierarchy:**
  - `Display / KPI`: 28px – 32px / Bold / Monospace (`tracking-tight`)
  - `H1 / Dashboard Header`: 20px / Bold / Sans (`leading-tight`)
  - `H2 / Card Title`: 14px / SemiBold / Sans
  - `Body`: 13px / Regular / Sans (`text-slate-300`)
  - `Caption / Micro`: 10px – 11px / Medium / Monospace (`text-slate-400`)

---

## 3. Information Architecture & Layout Structure

Dashboard dirancang dalam **12-Column Responsive Grid**:

```
+---------------------------------------------------------------------------------------------------+
|  HEADER COMMAND STRIP: Brand | Active CCTV Status | Stream Switcher Trigger | WebSocket Pulse     |
+---------------------------------------------------------------------------------------------------+
|  EXECUTIVE KPI BAR: Total Vehicles | Total Inbound SMP | Total Outbound SMP | Green Light Split   |
+--------------------------------------------------------------------+------------------------------+
|  LEFT COLUMN (7 COLUMNS / ~60% WIDTH)                              | RIGHT COLUMN (5 COLUMNS)     |
|                                                                    |                              |
|  +--------------------------------------------------------------+  |  +------------------------+  |
|  | VIDEO PLAYER & INTERACTIVE CANVAS (16:9 Aspect Ratio)        |  |  | INBOUND SMP CARD (Emerald) |  |
|  | - Live Stream MJPEG Overlay                                  |  |  | - Total Accumulation   |  |
|  | - Transparent Polygon ROI Canvas (Inbound / Outbound)        |  |  | - 60s Rolling Rate     |  |
|  | - Floating HUD: FPS Counter, Camera Badge, Status Pulse      |  |  | - Density Rating Badge |  |
|  +--------------------------------------------------------------+  |  +------------------------+  |
|  | FLOATING / BOTTOM ROI TOOLBAR                                |  |  +------------------------+  |
|  | [View Mode] [Draw Inbound] [Draw Outbound] [Clear] [Reset]   |  |  | OUTBOUND SMP CARD (Amber) |  |
|  +--------------------------------------------------------------+  |  | - Total Accumulation   |  |
|                                                                    |  | - 60s Rolling Rate     |  |
|  +--------------------------------------------------------------+  |  | - Density Rating Badge |  |
|  | PKJI VEHICLE DISTRIBUTION BENTO (4 Grid Cards)               |  |  +------------------------+  |
|  | - Sepeda Motor (0.5 SMP)  | - Mobil Penumpang (1.0 SMP)      |  |                              |
|  | - Bus Besar (1.3 SMP)     | - Truk / Angkutan (1.3 SMP)      |  |  +------------------------+  |
|  +--------------------------------------------------------------+  |  | REAL-TIME TRAFFIC CHART   |  |
|                                                                    |  | - Recharts Dynamic Line   |  |
|  +--------------------------------------------------------------+  |  | - 20 Rolling Ticks (Sec)  |  |
|  | ADAPTIVE SIGNAL RECOMMENDATION PANEL                         |  |  +------------------------+  |
|  | - Inbound Green: 35s (58%) vs Outbound Green: 25s (42%)      |  |                              |
|  +--------------------------------------------------------------+  |  +------------------------+  |
|                                                                    |  | RECENT DETECTION LOG   |  |
|                                                                    |  | - 15 Last Events Table |  |
|                                                                    |  +------------------------+  |
+--------------------------------------------------------------------+------------------------------+
```

---

## 4. Component-by-Component Detailed UX Specification

### 4.1 Header Command Strip
- **Left Slot:** Icon CPU/Traffic, Judul `"Smart Traffic Monitoring"`, Sub-teks `"PKJI Standard Passenger Car Unit (SMP) Analytics"`.
- **Right Slot:**
  - **Button `"Pilih / Ganti CCTV"`:** Menampilkan modal switcher dengan ikon Video.
  - **WebSocket Live Pill:** Hijau menyala `"WebSocket Terhubung"` saat aktif, Merah berkedip `"WebSocket Terputus"` saat reconnecting.

### 4.2 Video Stream Player & Interactive Canvas (`VideoPlayer.tsx` & `CanvasROI.tsx`)
- **Container Aspect:** Fixed 16:9 rasio kontainer hitam beresolusi native 640x360 diskalakan responsif.
- **HUD Badges:**
  - Kiri Atas: Nama Kamera Aktif (misal: `"ATCS Surakarta — Simpang Balai Kota"`) + Badge Merah/Hijau `"LIVE"`.
  - Kanan Atas: FPS Counter berkedip halus (`"12.4 FPS"`).
- **Canvas Interaction Rules:**
  - *Mode View:* Kursor default, canvas `pointer-events-none`.
  - *Mode Draw Inbound:* Kursor crosshair, garis putus-putus hijau neon `#34d399`, titik simpul putih bergaris hitam. Klik 1x untuk tambah titik, Double Click untuk mengunci dan menyimpan poligon.
  - *Mode Draw Outbound:* Kursor crosshair, garis putus-putus kuning/amber `#fbbf24`.
  - *Validasi:* Poligon wajib minimal 3 titik ($N \ge 3$).
- **Toolbar Aksi:**
  - `[View Only]`, `[Draw Inbound (Green)]`, `[Draw Outbound (Amber)]`, `[Clear Polygons]`, `[Reset Counters]`.

### 4.3 CCTV Preset & Stream Switcher Modal (`CCTVSelectorModal.tsx`)
- **Trigger:** Tombol di Header atau Video Player.
- **Preset List (1-Click Switch):**
  1. `ATCS Surakarta — Simpang Balai Kota` (Jl. Jend. Sudirman)
  2. `ATCS Surakarta — Simpang Gladak` (Pusat Kota)
  3. `ATCS Surakarta — Simpang Kerten` (Jl. Slamet Riyadi)
  4. `ATCS Surakarta — Simpang Gendengan` (Purwosari)
  5. `Synthetic Traffic Simulator` (In-Memory Demo Loop)
- **Custom URL Input Section:**
  - Input teks `URL Streaming (FLV / HLS / MP4 / RTSP)` dengan placeholder `http://.../live.flv`.
  - Input teks `Nama Kamera (Opsional)`.
  - Tombol Submit `"Hubungkan CCTV Kustom"`.

### 4.4 PKJI Vehicle Distribution Bento (`VehicleBreakdown.tsx`)
- **4 Grid Cards:**
  1. **Sepeda Motor (MC):** Nilai bobot `0.5 SMP`, Ikon Bike. Counter: `N In` vs `N Out`.
  2. **Mobil Penumpang (LV):** Nilai bobot `1.0 SMP`, Ikon Car. Counter: `N In` vs `N Out`.
  3. **Bus (HV):** Nilai bobot `1.3 SMP`, Ikon Bus. Counter: `N In` vs `N Out`.
  4. **Truk / Angkutan Berat (HV):** Nilai bobot `1.3 SMP`, Ikon Truck. Counter: `N In` vs `N Out`.

### 4.5 Metrics Cards (`MetricsCard.tsx`)
- **Inbound Card:** Border `#10b981/40`, background `#10b981/5`.
  - Total Akumulasi SMP (`45.5 SMP`).
  - Rolling Laju Kepadatan 60 Detik (`14.2 SMP/mnt`).
  - Badge Status: `LANCAR` / `SEDANG` / `PADAT` / `MACET`.
- **Outbound Card:** Border `#f59e0b/40`, background `#f59e0b/5`.
  - Total Akumulasi SMP (`38.0 SMP`).
  - Rolling Laju Kepadatan 60 Detik (`11.5 SMP/mnt`).
  - Badge Status Kepadatan.

### 4.6 Real-Time Traffic Trend Chart (`TrafficChart.tsx`)
- **Type:** Responsive Multi-line Chart (Recharts).
- **Lines:**
  - Inbound Line: `#10b981` (Emerald), stroke width 2px, no dots.
  - Outbound Line: `#f59e0b` (Amber), stroke width 2px, no dots.
- **X-Axis:** Waktu `HH:MM:SS` (20 tick data point terakhir).
- **Y-Axis:** Laju `SMP/menit`.
- **Tooltip:** Dark background `#0f172a`, border `#334155`.

### 4.7 Adaptive Traffic Light Split Recommendation Module
- **Formula Durasi Sinyal Lampu Hijau:**
  $$\text{Rasio}_{\text{in}} = \frac{\text{SMP}_{\text{in}}}{\text{SMP}_{\text{in}} + \text{SMP}_{\text{out}}}, \quad T_{\text{green, in}} = T_{\text{cycle}} \times \text{Rasio}_{\text{in}}$$
- **Visual Display:** Progress bar split dua warna (Emerald vs Amber) menunjukkan alokasi detik lampu hijau adaptif (misal: Cycle Time = 60 detik $\implies$ Inbound 35 detik, Outbound 25 detik).

### 4.8 Live Activity Detection Feed (`LiveFeed.tsx`)
- **Tampilan:** List scrollable maksimal 15 event terbaru.
- **Item Format:** Badge Arah (Inbound / Outbound) + Tipe Kendaraan (Kapital) + Bobot SMP + Timestamp jam:menit:detik.

---

## 5. Data Contract & Backend API Reference

### 5.1 REST Endpoints

| Method | Route | Request Body | Response Format |
|---|---|---|---|
| `GET` | `/` | None | HTML Server Status Dashboard |
| `GET` | `/healthz` | None | `{"status": "ok", "service": "..."}` |
| `GET` | `/api/v1/health` | None | `{"status": "ok", "stream_active": true, "fps": 12.4, "active_stream": {...}}` |
| `GET` | `/api/v1/stream-source` | None | `{"active_source": {"url": "...", "name": "..."}, "presets": [...]}` |
| `POST` | `/api/v1/stream-source` | `{"url": "...", "name": "..."}` | `{"status": "success", "active_source": {...}}` |
| `GET` | `/api/v1/roi` | None | `{"inbound": [[0.1, 0.4], ...], "outbound": [[0.6, 0.4], ...]}` |
| `POST` | `/api/v1/roi` | `{"inbound": [...], "outbound": [...]}` *(Min 3 pts)* | `{"status": "success", "message": "ROI updated successfully"}` |
| `POST` | `/api/v1/reset-counter` | None | `{"status": "success", "message": "Counters reset successfully"}` |
| `GET` | `/api/v1/stream` | None | `multipart/x-mixed-replace; boundary=frame` (MJPEG) |

### 5.2 WebSocket Live Payload Contract (`/ws/metrics`)

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
      "id": "evt_1092_1771982400000",
      "timestamp": "14:30:15",
      "direction": "inbound",
      "vehicle_type": "car",
      "smp": 1.0
    }
  ]
}
```

---

## 6. Edge Cases & UX States

1. **Stream Putus / Kamera Offline:**
   - Video player tidak boleh blank; otomatis menampilkan *in-memory synthetic simulator* dengan banner kuning `"Menggunakan Simulator Sintetis"`.
2. **WebSocket Reconnecting:**
   - Header badge beralih ke warna merah dengan ikon putus dan teks `"Menghubungkan Ulang WebSocket..."` tanpa membuat UI freeze.
3. **Canvas Drawing Error:**
   - Jika pengguna double click dengan $<3$ titik, canvas menampilkan tooltip peringatan `"Minimal 3 titik untuk membuat area poligon"`.
4. **Cold Start & Reset:**
   - Tombol Reset Counters menghapus memori pelacakan aktif tanpa merusak koneksi WebSocket.
