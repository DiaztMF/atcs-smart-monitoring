# UI Redesign Specification: Smart Traffic Monitoring Dashboard

**Tanggal:** 27 Agustus 2026  
**Status:** Disetujui (Approved)  
**Branch:** `redesign-ui`

---

## 1. Ringkasan Proyek

Redesign antarmuka (UI) dashboard **Smart Traffic Monitoring** mengacu pada referensi dashboard modern (`C:\Users\advan\Downloads\Smart Traffic Monitoring Dashboard`) dengan tata letak 12-kolom (rasio 7:5), Light Theme modern, tipografi presisi Inter & JetBrains Mono, dan frame video CCTV bergaya HUD gelap.

Pembaruan ini mempertahankan:
1. **Bahasa Indonesia** sebagai bahasa utama pada seluruh label, status, dan teks antarmuka.
2. **Ikon Lucide** (vektor bersih) sebagai pengganti emoji mentah.
3. **Standar PKJI / MKJI** (Panduan Kapasitas Jalan Indonesia) untuk representasi bobot SMP (Satuan Mobil Penumpang) dan kategori kendaraan.
4. **Interaktivitas Canvas ROI** untuk pengaturan area pemantauan Inbound dan Outbound secara dinamis.

---

## 2. Sistem Desain & Tema Visual

### 2.1 Palet Warna
- **Background Utama:** `#f8fafc` (Slate 50)
- **Kartu & Surface:** `#ffffff` (Putih murni) dengan border `#e2e8f0` (Slate 200) dan bayangan `shadow-[0_1px_3px_rgba(0,0,0,0.04)]`
- **Aksen Arah Masuk (Inbound):**
  - Background Badge/Box: `bg-emerald-50`
  - Teks: `text-emerald-700`
  - Border: `border-emerald-200`
  - Bar/Indikator: `bg-emerald-500` / `#059669`
- **Aksen Arah Keluar (Outbound):**
  - Background Badge/Box: `bg-amber-50`
  - Teks: `text-amber-700`
  - Border: `border-amber-200`
  - Bar/Indikator: `bg-amber-500` / `#d97706`
- **Status Kepadatan Lalu Lintas:**
  - `LANCAR`: `bg-emerald-50 text-emerald-700` + dot `bg-emerald-500`
  - `SEDANG`: `bg-yellow-50 text-yellow-700` + dot `bg-yellow-500`
  - `PADAT`: `bg-orange-50 text-orange-700` + dot `bg-orange-500`
  - `MACET`: `bg-red-50 text-red-700` + dot `bg-red-500`

### 2.2 Tipografi
- **Body & Label:** Inter (`sans-serif`)
- **Nilai Numerik, Telemetri, Timestamp, & Kode:** JetBrains Mono (`monospace`)

---

## 3. Struktur Layout & Komponen

### 3.1 Header (`Header.tsx` / `page.tsx`)
- **Logo & Judul:** Box hitam rounded `ST` + teks `Smart Traffic Monitoring`.
- **Lokasi/Kamera Aktif:** Badge teks monospaced nama kamera aktif (misal `CAM-03 / ATCS Surakarta Balai Kota`).
- **Indikator WebSocket:** Badge `Terhubung` (pulse hijau) atau `Terputus` (pulse merah).
- **Tombol "Ganti CCTV":** Membuka modal pemilihan sumber aliran video.

### 3.2 Top KPI Row (4 Kartu)
- **Total Kendaraan:** Total akumulasi kendaraan masuk + keluar.
- **SMP Masuk (Inbound):** Total nilai SMP masuk dengan aksen hijau emerald dan subtitle jumlah kendaraan.
- **SMP Keluar (Outbound):** Total nilai SMP keluar dengan aksen kuning/oranye amber dan subtitle jumlah kendaraan.
- **Rasio Sinyal Hijau (Green Split):** Persentase beban masuk terhadap total beban kendaraan.

### 3.3 Kolom Kiri (7 Kolom Grid)
1. **Video Player (`VideoPlayer.tsx`)**:
   - Aspek rasio 16:9 (`aspect-video`), kontainer `bg-slate-950 rounded-xl overflow-hidden border border-slate-800`.
   - Streaming MJPEG langsung dari `/api/v1/video-feed`.
   - HUD Overlay: Tag kamera (kiri atas), Badge `LIVE` merah & FPS counter (kanan atas), Timestamp lokal monospaced (kiri bawah).
   - Canvas ROI Interaktif: Poligon Inbound (hijau) & Outbound (amber).
2. **Toolbar ROI (`ROIToolbar.tsx` / `VideoPlayer.tsx`)**:
   - Mode switcher: `Inbound` vs `Outbound`.
   - Aksi: `Reset ROI`, `Edit / Selesai Gambar`, `Simpan ROI`, dan `Reset Counter`.
3. **Bento Grid Distribusi Kendaraan PKJI (`VehicleBreakdown.tsx`)**:
   - 4 kategori kendaraan dengan **ikon Lucide**:
     - Sepeda Motor (`Bike`, 0.5 SMP)
     - Mobil Penumpang (`Car`, 1.0 SMP)
     - Bus (`Bus`, 1.3 SMP)
     - Truk (`Truck`, 1.3 SMP)
   - Tiap kartu memuat badge counter `IN` (Emerald) dan `OUT` (Amber).
4. **Rasio Sinyal Adaptif (`AdaptiveSignalSplit.tsx`)**:
   - Menampilkan pembagian durasi waktu hijau persimpangan adaptif (`Inbound %` vs `Outbound %`) dengan progress bar teranimasi dan indikator waktu siklus.

### 3.4 Kolom Kanan (5 Kolom Grid)
1. **Kartu Trafik Masuk (Inbound)**:
   - Aksen `border-l-4 border-l-emerald-500`.
   - Badge status kepadatan (`LANCAR` / `SEDANG` / `PADAT` / `MACET`).
   - 3 kolom data: Total Kendaraan (`text-[32px]`), Total SMP (`text-[20px]`), dan Laju Volume (`SMP/menit`).
2. **Kartu Trafik Keluar (Outbound)**:
   - Aksen `border-l-4 border-l-amber-500`.
   - Badge status kepadatan (`LANCAR` / `SEDANG` / `PADAT` / `MACET`).
   - 3 kolom data: Total Kendaraan (`text-[32px]`), Total SMP (`text-[20px]`), dan Laju Volume (`SMP/menit`).
3. **Grafik Garis Volume Real-time (`TrafficChart.tsx`)**:
   - Komponen Recharts dengan garis Inbound (Emerald `#059669`) dan Outbound (Amber `#d97706`).
   - Grid halus, sumbu waktu monospaced, dan tooltip kustom.
4. **Tabel Log Deteksi Real-time (`LiveFeed.tsx`)**:
   - Menampilkan riwayat deteksi real-time terakumulasi dari delta WebSocket.
   - Kolom: `Waktu`, `Jenis Kendaraan` (dengan ikon Lucide), `Jalur`, `Status / Estimasi`, dan Badge Arah `MASUK` / `KELUAR`.

### 3.5 Modal Pemilihan CCTV (`CCTVSelectorModal.tsx`)
- Desain Light Theme modern.
- Daftar preset kamera CCTV terverifikasi dengan informasi lokasi, status feed, dan tombol switch cepat.
- Dukungan custom URL video stream (FLV/HLS/MP4).

---

## 4. Aliran Data & Integrasi Backend

| Endpoint / Channel | Tipe | Deskripsi |
|---|---|---|
| `ws://.../ws/metrics` | WebSocket | Aliran payload telemetri real-time tiap 1 detik (inbound, outbound, breakdown, smp_per_minute, density_level). |
| `GET /api/v1/roi` | REST GET | Mengambil koordinat ROI tersimpan dari backend. |
| `POST /api/v1/roi` | REST POST | Menyimpan koordinat poligon yang telah dinormalisasi `[0.0 ... 1.0]`. |
| `GET /api/v1/stream-source` | REST GET | Mengambil daftar preset CCTV dan feed kamera aktif. |
| `POST /api/v1/stream-source` | REST POST | Mengubah feed aliran video aktif. |
| `POST /api/v1/reset-counter` | REST POST | Mereset akumulasi counter kendaraan ke nol. |
| `GET /api/v1/video-feed` | REST Stream | Aliran frame video MJPEG dengan anotasi bounding box YOLOv11 & ByteTrack. |

---

## 5. Rencana Verifikasi

1. **Verifikasi Komponen Visual:**
   - Memastikan font Inter & JetBrains Mono ter-load dengan benar.
   - Memastikan seluruh palet Light Theme, border `#e2e8f0`, dan bayangan konsisten.
   - Memastikan ikon Lucide terpasang di semua kartu kendaraan dan tabel log (tanpa emoji).
2. **Verifikasi Fungsional & State:**
   - Verifikasi koneksi WebSocket dan pembaruan metrik real-time.
   - Verifikasi interaktivitas penggambaran poligon ROI dan pengiriman koordinat normalisasi ke backend.
   - Verifikasi fungsionalitas pergantian CCTV dan reset counter.
3. **Build & Type Check:**
   - `npm run build` dan `npm run lint` pada folder `frontend` untuk memastikan zero TypeScript/ESLint errors.
