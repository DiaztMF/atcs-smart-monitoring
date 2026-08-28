# Product Requirements Document (PRD) & UI/UX Design System Specification
## Smart Traffic Monitoring: Real-Time Computer Vision & PKJI SMP Analytics

- **Document Version:** 3.0.0 (Light Mode Professional Edition)
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

### 2.1 Aesthetic Archetype: Clean Professional Light Mode
- **Visual Style:** Minimal, professional, data-first. Terinspirasi dari dashboard kelas enterprise seperti Vercel, Linear, dan Stripe Radar — bukan command center gaming/futuristik.
- **Surface Elevation:** Solid white cards dengan shadow hierarchy yang terukur. **Tidak menggunakan glassmorphism, backdrop-blur, atau semi-transparent surfaces.**
- **Design Philosophy:** Data berbicara, chrome diam. Card hampir invisible — yang menonjol adalah angka, grafik, dan status.

### 2.2 Color Palette & Semantic Tokens

#### 2.2.1 Foundation Colors (Neutral)

| Token Name | Hex Code | Tailwind Equivalent | Semantic Usage |
|---|---|---|---|
| `--bg-base` | `#f8fafc` | `slate-50` | Latar belakang halaman utama |
| `--bg-card` | `#ffffff` | `white` | Surface kartu dan panel |
| `--bg-muted` | `#f1f5f9` | `slate-100` | Background input, hover states, nested containers |
| `--bg-video` | `#020617` | `slate-950` | Video player container (tetap gelap — natural untuk video feed) |
| `--border-default` | `#e2e8f0` | `slate-200` | Border kartu standar |
| `--border-hover` | `#cbd5e1` | `slate-300` | Border hover dan divider aktif |
| `--text-primary` | `#0f172a` | `slate-900` | Heading, KPI numbers, primary labels |
| `--text-secondary` | `#475569` | `slate-600` | Body text, descriptions |
| `--text-tertiary` | `#94a3b8` | `slate-400` | Captions, timestamps, disabled states |

#### 2.2.2 Directional Semantic Colors

| Token Name | Hex Code | Tailwind Equivalent | Semantic Usage |
|---|---|---|---|
| **Inbound Primary** | `#059669` | `emerald-600` | Teks, ikon, garis chart arah masuk |
| **Inbound Light BG** | `#ecfdf5` | `emerald-50` | Background pill/badge/tag Inbound |
| **Inbound Border** | `#a7f3d0` | `emerald-200` | Border card Inbound |
| **Inbound Canvas** | `#34d399` | `emerald-400` | Garis poligon ROI di canvas (tetap vivid untuk visibility di atas video gelap) |
| **Outbound Primary** | `#d97706` | `amber-600` | Teks, ikon, garis chart arah keluar |
| **Outbound Light BG** | `#fffbeb` | `amber-50` | Background pill/badge/tag Outbound |
| **Outbound Border** | `#fde68a` | `amber-200` | Border card Outbound |
| **Outbound Canvas** | `#fbbf24` | `amber-400` | Garis poligon ROI di canvas |

#### 2.2.3 Density Status Colors

| Status | Text Color | Background | Border | Threshold |
|---|---|---|---|---|
| **LANCAR** | `#059669` (emerald-600) | `#ecfdf5` (emerald-50) | `#a7f3d0` (emerald-200) | Beban $< 10$ SMP/menit |
| **SEDANG** | `#ca8a04` (yellow-600) | `#fefce8` (yellow-50) | `#fde047` (yellow-300) | $10 \le \text{Beban} < 25$ SMP/menit |
| **PADAT** | `#ea580c` (orange-600) | `#fff7ed` (orange-50) | `#fdba74` (orange-300) | $25 \le \text{Beban} < 40$ SMP/menit |
| **MACET** | `#dc2626` (red-600) | `#fef2f2` (red-50) | `#fca5a5` (red-300) | Beban $\ge 40$ SMP/menit |

### 2.3 Typography System
- **Primary Font Family:** `Inter` (wajib dimuat via Google Fonts / `next/font/google`). Fallback: `system-ui, -apple-system, sans-serif`.
- **Monospace Font Family:** `JetBrains Mono` (wajib dimuat via Google Fonts / `next/font/google`). Fallback: `ui-monospace, monospace`.
- **Scale Hierarchy:**
  - `Display / KPI`: 28px – 32px / `font-bold` / JetBrains Mono / `tracking-tight` / `text-slate-900`
  - `H1 / Dashboard Header`: 20px / `font-semibold` / Inter / `leading-tight` / `text-slate-900`
  - `H2 / Card Title`: 14px / `font-semibold` / Inter / `text-slate-700`
  - `Body`: 13px / `font-normal` / Inter / `text-slate-600`
  - `Caption / Micro`: 10px – 11px / `font-medium` / JetBrains Mono / `text-slate-400`

### 2.4 Elevation & Shadow System
Tidak menggunakan glassmorphism. Hierarki kedalaman dibangun dari shadow saja:

| Level | CSS `box-shadow` | Tailwind | Usage |
|---|---|---|---|
| **Level 0** | none | `shadow-none` | Flat inline elements |
| **Level 1** | `0 1px 2px rgba(0,0,0,0.05)` | `shadow-sm` | Cards resting state |
| **Level 2** | `0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)` | `shadow` | Cards hover state, dropdowns |
| **Level 3** | `0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06)` | `shadow-md` | Modals, floating toolbars |
| **Level 4** | `0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05)` | `shadow-lg` | Modal overlay panels |

### 2.5 Border Radius System

| Token | Value | Usage |
|---|---|---|
| `--radius-sm` | `6px` / `rounded-md` | Buttons, badges, inputs |
| `--radius-md` | `8px` / `rounded-lg` | Cards, panels |
| `--radius-lg` | `12px` / `rounded-xl` | Modals, video container |
| `--radius-full` | `9999px` / `rounded-full` | Pills, status dots |

### 2.6 Spacing Grid
Semua spacing menggunakan **4px base unit** secara konsisten:

| Token | px | Tailwind | Usage |
|---|---|---|---|
| `--space-1` | 4px | `p-1` | Micro padding |
| `--space-2` | 8px | `p-2` | Badge internal, icon gaps |
| `--space-3` | 12px | `p-3` | Compact card padding |
| `--space-4` | 16px | `p-4` | Standard card padding, section gaps |
| `--space-5` | 20px | `p-5` | Comfortable card padding |
| `--space-6` | 24px | `p-6` | Page margin, large section gaps |
| `--space-8` | 32px | `p-8` | Page outer padding desktop |

### 2.7 Interaction & Micro-Animation Tokens

| Interaction | Property | Value |
|---|---|---|
| **Card Hover** | `box-shadow` transition | `shadow-sm` → `shadow` over `150ms ease` |
| **Card Hover** | `border-color` transition | `slate-200` → `slate-300` over `150ms ease` |
| **Button Hover** | `background-color` transition | Darken 1 shade over `100ms ease` |
| **Button Active** | `transform` | `scale(0.98)` over `50ms` |
| **Badge Pulse (LIVE)** | `opacity` animation | `animate-pulse` (2s infinite) — hanya pada badge LIVE di video |
| **Chart Data** | Entry animation | Tidak ada — `isAnimationActive={false}` untuk real-time data integrity |
| **WebSocket Pill** | Status change | `transition-colors duration-300` saat switch connected/disconnected |
| **Modal** | Enter/Exit | `opacity 0→1` + `translateY(8px→0)` over `200ms ease-out` |

---

## 3. Information Architecture & Layout Structure

Dashboard dirancang dalam **12-Column Responsive Grid**:

```
+---------------------------------------------------------------------------------------------------+
|  HEADER STRIP: Brand | Active CCTV Status | Stream Switcher Trigger | WebSocket Pulse             |
+---------------------------------------------------------------------------------------------------+
|  EXECUTIVE KPI BAR: Total Vehicles | Total Inbound SMP | Total Outbound SMP | Green Light Split   |
+--------------------------------------------------------------------+------------------------------+
|  LEFT COLUMN (7 COLUMNS / ~60% WIDTH)                              | RIGHT COLUMN (5 COLUMNS)     |
|                                                                    |                              |
|  +--------------------------------------------------------------+  |  +------------------------+  |
|  | VIDEO PLAYER & INTERACTIVE CANVAS (16:9 Aspect Ratio)        |  |  | INBOUND SMP CARD       |  |
|  | - Dark container (slate-950) for optimal video contrast       |  |  | - Emerald left accent  |  |
|  | - Transparent Polygon ROI Canvas (Inbound / Outbound)        |  |  | - Total Accumulation   |  |
|  | - Floating HUD: FPS Counter, Camera Badge, Status Pulse      |  |  | - 60s Rolling Rate     |  |
|  +--------------------------------------------------------------+  |  | - Density Rating Badge |  |
|  | FLOATING ROI TOOLBAR (shadow-md, bg-white)                   |  |  +------------------------+  |
|  | [View Mode] [Draw Inbound] [Draw Outbound] [Clear] [Reset]   |  |  +------------------------+  |
|  +--------------------------------------------------------------+  |  | OUTBOUND SMP CARD      |  |
|                                                                    |  | - Amber left accent    |  |
|  +--------------------------------------------------------------+  |  | - Total Accumulation   |  |
|  | PKJI VEHICLE DISTRIBUTION BENTO (4 Grid Cards)               |  |  | - 60s Rolling Rate     |  |
|  | - Sepeda Motor (0.5 SMP)  | - Mobil Penumpang (1.0 SMP)      |  |  | - Density Rating Badge |  |
|  | - Bus Besar (1.3 SMP)     | - Truk / Angkutan (1.3 SMP)      |  |  +------------------------+  |
|  +--------------------------------------------------------------+  |                              |
|                                                                    |  +------------------------+  |
|  +--------------------------------------------------------------+  |  | REAL-TIME TRAFFIC CHART|  |
|  | ADAPTIVE SIGNAL RECOMMENDATION PANEL                         |  |  | - Dual-line Recharts   |  |
|  | - Inbound Green: 35s (58%) vs Outbound Green: 25s (42%)      |  |  | - 20 Rolling Ticks     |  |
|  +--------------------------------------------------------------+  |  +------------------------+  |
|                                                                    |                              |
|                                                                    |  +------------------------+  |
|                                                                    |  | RECENT DETECTION LOG   |  |
|                                                                    |  | - 15 Last Events Table |  |
|                                                                    |  +------------------------+  |
+--------------------------------------------------------------------+------------------------------+
```

---

## 4. Component-by-Component Detailed UX Specification

### 4.1 Header Strip
- **Container:** `bg-white border-b border-slate-200` — clean top bar, bukan floating glass panel.
- **Left Slot:** Icon Traffic Light (`text-emerald-600`), Judul `"Smart Traffic Monitoring"` (`text-slate-900 font-semibold text-lg`), Sub-teks `"PKJI Standard — SMP Analytics"` (`text-slate-500 text-xs`).
- **Right Slot:**
  - **Button `"Ganti CCTV"`:** `bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 rounded-lg` — tidak emerald/colored, netral dan clean.
  - **WebSocket Status Pill:**
    - Connected: `bg-emerald-50 text-emerald-700 border border-emerald-200` + green dot `animate-pulse`.
    - Disconnected: `bg-red-50 text-red-700 border border-red-200` + red dot blinking.

### 4.2 Executive KPI Bar (BARU — tidak ada di implementasi saat ini)
- **Container:** Row 4 kartu KPI compact di bawah header.
- **Cards:** `bg-white border border-slate-200 rounded-lg shadow-sm p-4`.
- **Masing-masing KPI:**
  1. **Total Kendaraan Terdeteksi:** Ikon Activity. Jumlah total integer semua kendaraan (In + Out).
  2. **Beban Inbound (SMP):** Ikon ArrowDownLeft `text-emerald-600`. Angka mono bold.
  3. **Beban Outbound (SMP):** Ikon ArrowUpRight `text-amber-600`. Angka mono bold.
  4. **Rekomendasi Green Split:** Ikon TrafficCone. Menampilkan rasio `"58% : 42%"`.
- **Format Angka:** JetBrains Mono, `text-2xl font-bold text-slate-900`. Label di bawah: `text-xs text-slate-500`.

### 4.3 Video Stream Player & Interactive Canvas (`VideoPlayer.tsx` & `CanvasROI.tsx`)
- **Container:** `bg-slate-950 rounded-xl overflow-hidden shadow-md` — video container TETAP GELAP. Ini industry standard, video CCTV butuh dark chrome untuk kontras optimal.
- **Aspect Ratio:** Fixed 16:9, native 640x360, diskalakan responsif.
- **HUD Badges (di atas video, tetap light-on-dark untuk readability):**
  - Kiri Atas: Nama Kamera + Badge `"LIVE"` (`bg-red-500 text-white text-xs px-2 py-0.5 rounded-full animate-pulse`).
  - Kanan Atas: FPS Counter (`bg-black/50 text-white text-xs font-mono px-2 py-1 rounded-md`).
- **Canvas Interaction Rules:**
  - *Mode View:* Kursor default, canvas `pointer-events-none`.
  - *Mode Draw Inbound:* Kursor crosshair, garis putus-putus `#34d399` (emerald-400), titik simpul putih bergaris hitam.
  - *Mode Draw Outbound:* Kursor crosshair, garis putus-putus `#fbbf24` (amber-400).
  - *Validasi:* Poligon wajib minimal 3 titik ($N \ge 3$).
- **ROI Toolbar (di bawah video, terpisah):**
  - Container: `bg-white border border-slate-200 rounded-lg shadow-sm p-2 flex gap-2`.
  - Buttons: `px-3 py-1.5 text-xs font-medium rounded-md`.
  - Active state: `bg-emerald-50 text-emerald-700 border-emerald-200` (Inbound) / `bg-amber-50 text-amber-700 border-amber-200` (Outbound).
  - Inactive: `bg-slate-50 text-slate-600 hover:bg-slate-100`.
  - Destructive (Clear/Reset): `text-red-600 hover:bg-red-50`.

### 4.4 CCTV Preset & Stream Switcher Modal (`CCTVSelectorModal.tsx`)
- **Overlay:** `bg-black/40` (light dimming, bukan heavy dark overlay).
- **Modal Panel:** `bg-white rounded-xl shadow-lg border border-slate-200 p-6 max-w-lg`.
- **Header:** `text-lg font-semibold text-slate-900` + close button `text-slate-400 hover:text-slate-600`.
- **Preset List:** Each item `px-4 py-3 rounded-lg hover:bg-slate-50 border border-transparent hover:border-slate-200 cursor-pointer transition-all`. Active preset: `bg-emerald-50 border-emerald-200 text-emerald-700`.
- **Custom URL Section:** Standard form inputs `bg-slate-50 border border-slate-200 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500`.
- **Submit Button:** `bg-slate-900 text-white hover:bg-slate-800 rounded-md px-4 py-2 text-sm font-medium`.

### 4.5 PKJI Vehicle Distribution Bento (`VehicleBreakdown.tsx`)
- **Container:** Grid 2×2 (`grid grid-cols-2 gap-3`).
- **Each Card:** `bg-white border border-slate-200 rounded-lg shadow-sm p-4 hover:shadow transition-shadow`.
- **Layout per Card:**
  - Top row: Ikon kendaraan (`text-slate-400 w-5 h-5`) + Nama (`text-sm font-medium text-slate-700`) + Badge bobot (`bg-slate-100 text-slate-500 text-xs font-mono px-1.5 py-0.5 rounded`).
  - Bottom row: Dua kolom counter:
    - Inbound: `text-emerald-600 font-mono font-bold` + label `"In"` kecil.
    - Outbound: `text-amber-600 font-mono font-bold` + label `"Out"` kecil.

### 4.6 Metrics Cards (`MetricsCard.tsx`)
- **Inbound Card:**
  - `bg-white border border-slate-200 rounded-lg shadow-sm`.
  - Left accent strip: `4px solid #059669` (emerald-600) di border-left.
  - Icon container: `bg-emerald-50 text-emerald-600 p-2 rounded-lg`.
  - Density Badge: `bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full px-2.5 py-0.5 text-xs font-semibold`.
- **Outbound Card:**
  - Sama strukturnya, ganti emerald → amber (`#d97706`, `amber-50`, `amber-600`, `amber-200`).
- **Values:**
  - Total Akumulasi: `text-2xl font-bold font-mono text-slate-900` + label `"SMP"` (`text-xs text-slate-400`).
  - Rolling Rate: `text-2xl font-bold font-mono text-slate-900` + label `"SMP/mnt"`.
  - Divider: `border-t border-slate-100` (bukan `border-slate-800`).

### 4.7 Real-Time Traffic Trend Chart (`TrafficChart.tsx`)
- **Container:** `bg-white border border-slate-200 rounded-lg shadow-sm p-5`.
- **Lines:**
  - Inbound: `#059669` (emerald-600), stroke width 2px, no dots.
  - Outbound: `#d97706` (amber-600), stroke width 2px, no dots.
- **Grid:** `stroke="#e2e8f0"` (slate-200), strokeDasharray `"3 3"`.
- **Axis:** `stroke="#94a3b8"` (slate-400), fontSize 10px.
- **Tooltip:** `backgroundColor: "#ffffff"`, `borderColor: "#e2e8f0"`, `color: "#0f172a"`, `borderRadius: "8px"`, `boxShadow: "0 4px 6px rgba(0,0,0,0.07)"`.
- **Legend dots:** Inbound `bg-emerald-600`, Outbound `bg-amber-600`.

### 4.8 Adaptive Traffic Light Split Recommendation Module
- **Container:** `bg-white border border-slate-200 rounded-lg shadow-sm p-5`.
- **Formula:**
  $$\text{Rasio}_{\text{in}} = \frac{\text{SMP}_{\text{in}}}{\text{SMP}_{\text{in}} + \text{SMP}_{\text{out}}}, \quad T_{\text{green, in}} = T_{\text{cycle}} \times \text{Rasio}_{\text{in}}$$
- **Visual:** Horizontal split progress bar dengan `rounded-full h-3 overflow-hidden bg-slate-100`. Segment kiri: `bg-emerald-500`. Segment kanan: `bg-amber-500`. Label di bawah bar: `"Inbound 35s (58%)"` dan `"Outbound 25s (42%)"` (`text-sm font-medium`).

### 4.9 Live Activity Detection Feed (`LiveFeed.tsx`)
- **Container:** `bg-white border border-slate-200 rounded-lg shadow-sm`.
- **Header:** `px-5 py-3 border-b border-slate-100` — title `text-sm font-semibold text-slate-700`.
- **List:** Scrollable, max 15 events. Setiap item: `px-5 py-2.5 border-b border-slate-50 last:border-b-0 hover:bg-slate-50`.
- **Item Format:**
  - Direction badge: `text-xs font-medium px-2 py-0.5 rounded-full` — Inbound: `bg-emerald-50 text-emerald-700`, Outbound: `bg-amber-50 text-amber-700`.
  - Vehicle type: `text-sm font-medium text-slate-700` (kapital).
  - SMP weight: `font-mono text-sm text-slate-500`.
  - Timestamp: `font-mono text-xs text-slate-400` (format `HH:MM:SS`).

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
   - Video player tidak boleh blank; otomatis menampilkan *in-memory synthetic simulator* dengan banner `bg-amber-50 border border-amber-200 text-amber-700` bertuliskan `"Menggunakan Simulator Sintetis"`.
2. **WebSocket Reconnecting:**
   - Header pill beralih ke `bg-red-50 text-red-700 border-red-200` dengan dot merah berkedip dan teks `"Menghubungkan Ulang WebSocket..."` — tanpa membuat UI freeze.
3. **Canvas Drawing Error:**
   - Jika pengguna double click dengan $<3$ titik, tampilkan toast notification `bg-white shadow-lg border border-slate-200 rounded-lg` dengan pesan `"Minimal 3 titik untuk membuat area poligon"`.
4. **Cold Start & Reset:**
   - Tombol Reset Counters menghapus memori pelacakan aktif tanpa merusak koneksi WebSocket.
5. **Empty State (Belum Ada Data):**
   - KPI cards menampilkan `"—"` sebagai placeholder value (`text-slate-300 font-mono`) bukan `0` — membedakan antara "belum ada data" vs "memang nol".
