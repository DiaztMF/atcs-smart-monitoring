# UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the Smart Traffic Monitoring Next.js frontend into a modern Light Theme dashboard with a 12-column (7:5) layout matching the reference UI, while preserving Indonesian terminology, Lucide icons, PKJI/MKJI vehicle distribution standards, and interactive canvas ROI editing.

**Architecture:** Next.js App Router modular component architecture with client-side reactive state managed via WebSocket (`/ws/metrics`) and REST endpoints. Clean separation of concerns across top KPI cards, live CCTV HUD player with canvas overlay, PKJI bento grid, adaptive green split bar, direction summary cards, Recharts volume line chart, detection event table, and CCTV modal.

**Tech Stack:** Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS 3.4, Lucide React, Recharts 2.12.

## Global Constraints

- Use Indonesian language for all UI titles, badges, metrics, and modal texts.
- Use Lucide React icons instead of raw emojis.
- Enforce PKJI / MKJI vehicle categories: Sepeda Motor (0.5 SMP), Mobil Penumpang (1.0 SMP), Bus (1.3 SMP), Truk (1.3 SMP).
- Ensure canvas ROI coordinates are normalized to `[0.0 ... 1.0]` when saving to backend `/api/v1/roi`.
- Preserve responsive layout: mobile stacked (`flex-col`), desktop 12-column grid (`lg:grid-cols-12`).
- Strict TypeScript: no `any` types.

---

### Task 1: Typography, Global Styles, & Tailwind Theme Configuration

**Files:**
- Modify: `frontend/tailwind.config.ts`
- Modify: `frontend/src/app/layout.tsx`
- Modify: `frontend/src/app/globals.css`

**Interfaces:**
- Produces: Tailwind font variables `font-sans` (Inter) and `font-mono` (JetBrains Mono), color tokens (`background: #f8fafc`, `card: #ffffff`, `border: #e2e8f0`, `inbound: #059669`, `outbound: #d97706`).

- [ ] **Step 1: Configure Tailwind theme and custom fonts**

Update `frontend/tailwind.config.ts` with font families and color palette.

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#f8fafc",
        foreground: "#0f172a",
        card: "#ffffff",
        border: "#e2e8f0",
        inbound: {
          50: "#ecfdf5",
          100: "#d1fae5",
          200: "#a7f3d0",
          500: "#10b981",
          600: "#059669",
          700: "#047857",
        },
        outbound: {
          50: "#fffbeb",
          100: "#fef3c7",
          200: "#fde68a",
          500: "#f59e0b",
          600: "#d97706",
          700: "#b45309",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "Inter", "system-ui", "-apple-system", "sans-serif"],
        mono: ["var(--font-jetbrains)", "JetBrains Mono", "ui-monospace", "monospace"],
      },
      boxShadow: {
        card: "0 1px 3px rgba(0, 0, 0, 0.04)",
        tooltip: "0 4px 12px rgba(0, 0, 0, 0.08)",
      },
    },
  },
  plugins: [],
};
export default config;
```

- [ ] **Step 2: Update Layout with Google Fonts (Inter & JetBrains Mono)**

Update `frontend/src/app/layout.tsx` to load Inter and JetBrains Mono fonts via `next/font/google`.

```tsx
import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Smart Traffic Monitoring - PKJI Analytics Dashboard",
  description: "Real-time traffic load monitoring and adaptive control using YOLOv11 and PKJI standards",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="bg-background text-foreground font-sans antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
```

- [ ] **Step 3: Update `globals.css` with clean scrollbar and base utilities**

Update `frontend/src/app/globals.css`.

- [ ] **Step 4: Commit Task 1 changes**

```bash
git add frontend/tailwind.config.ts frontend/src/app/layout.tsx frontend/src/app/globals.css
git commit -m "feat(ui): configure Inter/JetBrains fonts, theme tokens, and global styles"
```

---

### Task 2: Data Models & Types Definition

**Files:**
- Modify: `frontend/src/types/index.ts`

**Interfaces:**
- Produces: `TrafficMetrics`, `DirectionMetrics`, `Breakdown`, `ROICoordinates`, `StreamPreset`, `StreamSourceInfo`, `DetectionLogEvent`.

- [ ] **Step 1: Update type contracts in `frontend/src/types/index.ts`**

Define explicit TypeScript interfaces matching backend payloads and frontend event feeds:

```typescript
export interface VehicleBreakdownCounts {
  motorcycle: number;
  car: number;
  bus: number;
  truck: number;
}

export type DensityLevel = 'LANCAR' | 'SEDANG' | 'PADAT' | 'MACET';

export interface DirectionMetrics {
  total_smp: number;
  smp_per_minute: number;
  density_level: DensityLevel;
  breakdown: VehicleBreakdownCounts;
}

export interface TrafficMetrics {
  timestamp: number;
  inbound: DirectionMetrics;
  outbound: DirectionMetrics;
}

export type Point = [number, number];

export interface ROICoordinates {
  inbound: Point[];
  outbound: Point[];
}

export interface StreamPreset {
  name: string;
  url: string;
  description?: string;
}

export interface StreamSourceInfo {
  active_source: {
    name: string;
    url: string;
  };
  presets: StreamPreset[];
}

export type VehicleType = 'motorcycle' | 'car' | 'bus' | 'truck';
export type DirectionType = 'IN' | 'OUT';

export interface DetectionLogEvent {
  id: string;
  time: string;
  type: VehicleType;
  direction: DirectionType;
  lane: string;
  status: string;
}
```

- [ ] **Step 2: Commit Task 2 changes**

```bash
git add frontend/src/types/index.ts
git commit -m "feat(types): refine TypeScript contracts for metrics, ROI, and detection logs"
```

---

### Task 3: Top KPI Row Component (`MetricsCard.tsx`)

**Files:**
- Modify: `frontend/src/components/MetricsCard.tsx`

**Interfaces:**
- Consumes: `totalVehicles: number`, `inboundSMP: number`, `outboundSMP: number`, `inboundCount: number`, `outboundCount: number`, `greenSplit: number`.
- Produces: `<KPIRow ... />` rendering 4 top cards with JetBrains Mono numbers, clean slate labels, and subtle borders.

- [ ] **Step 1: Implement KPIRow with 4 clean KPI cards**

Cards:
1. Total Kendaraan (`totalVehicles`, sub: "Total terakumulasi")
2. SMP Masuk (`inboundSMP.toFixed(1)`, sub: `${inboundCount} kendaraan masuk`, accent: `text-emerald-700`)
3. SMP Keluar (`outboundSMP.toFixed(1)`, sub: `${outboundCount} kendaraan keluar`, accent: `text-amber-700`)
4. Rasio Sinyal Hijau (`${greenSplit}%`, sub: "Rasio Beban Masuk / Keluar")

- [ ] **Step 2: Commit Task 3 changes**

```bash
git add frontend/src/components/MetricsCard.tsx
git commit -m "feat(ui): implement modern 4-card KPI row component"
```

---

### Task 4: Video Player & Integrated Canvas ROI Toolbar (`VideoPlayer.tsx`)

**Files:**
- Modify: `frontend/src/components/VideoPlayer.tsx`

**Interfaces:**
- Consumes: `streamUrl: string`, `cameraName: string`, `roi: ROICoordinates`, `onSaveROI: (roi: ROICoordinates) => void`, `onResetCounters: () => void`.
- Produces: HUD overlay (Camera ID, LIVE badge, FPS counter, Monospace local time clock), interactive HTML5 Canvas ROI drawing/editing, and ROI toolbar (`Inbound` / `Outbound` mode switcher, `Edit Poligon / Simpan`, `Reset ROI`, `Reset Counter`).

- [ ] **Step 1: Implement Canvas ROI drawing engine with coordinate normalization `0.0 ... 1.0`**
- [ ] **Step 2: Implement CCTV HUD overlay (LIVE badge, FPS, timestamp, camera ID)**
- [ ] **Step 3: Implement clean Light Theme ROI toolbar directly under the video container**
- [ ] **Step 4: Commit Task 4 changes**

```bash
git add frontend/src/components/VideoPlayer.tsx
git commit -m "feat(ui): implement CCTV HUD video player and integrated canvas ROI toolbar"
```

---

### Task 5: PKJI / MKJI Vehicle Breakdown Bento Grid (`VehicleBreakdown.tsx`)

**Files:**
- Modify: `frontend/src/components/VehicleBreakdown.tsx`

**Interfaces:**
- Consumes: `inbound: VehicleBreakdownCounts`, `outbound: VehicleBreakdownCounts`.
- Produces: 4 bento vehicle cards with Lucide icons (`Bike`, `Car`, `Bus`, `Truck`), PKJI SMP factor badges (0.5 SMP, 1.0 SMP, 1.3 SMP, 1.3 SMP), and dual IN (emerald-50) & OUT (amber-50) counters.

- [ ] **Step 1: Implement PKJI vehicle distribution bento grid**
- [ ] **Step 2: Commit Task 5 changes**

```bash
git add frontend/src/components/VehicleBreakdown.tsx
git commit -m "feat(ui): implement PKJI vehicle distribution bento grid with Lucide icons"
```

---

### Task 6: Direction Summary Cards & Adaptive Signal Split (`TrafficDirectionCard.tsx` & `AdaptiveSignalSplit.tsx`)

**Files:**
- Create: `frontend/src/components/TrafficDirectionCard.tsx`
- Create: `frontend/src/components/AdaptiveSignalSplit.tsx`

**Interfaces:**
- `TrafficDirectionCard`: Consumes `direction: 'inbound' | 'outbound'`, `metrics: DirectionMetrics`, `totalVehicles: number`. Renders status badge (`LANCAR`, `SEDANG`, `PADAT`, `MACET`), total count, SMP total, and volume rate (`SMP/menit`).
- `AdaptiveSignalSplit`: Consumes `greenSplit: number`, `cycleTimeSeconds?: number`. Renders dual animated progress bar (Emerald % vs Amber %) with directional labels.

- [ ] **Step 1: Implement `TrafficDirectionCard.tsx`**
- [ ] **Step 2: Implement `AdaptiveSignalSplit.tsx`**
- [ ] **Step 3: Commit Task 6 changes**

```bash
git add frontend/src/components/TrafficDirectionCard.tsx frontend/src/components/AdaptiveSignalSplit.tsx
git commit -m "feat(ui): create direction summary cards and adaptive signal split component"
```

---

### Task 7: Volume Line Chart Component (`TrafficChart.tsx`)

**Files:**
- Modify: `frontend/src/components/TrafficChart.tsx`

**Interfaces:**
- Consumes: `data: { time: string; inbound: number; outbound: number }[]`.
- Produces: Responsive Recharts line chart (height 140px) with custom tooltip, Inbound (emerald) & Outbound (amber) curves, and monospaced axes.

- [ ] **Step 1: Implement line chart with clean light styling and custom tooltip**
- [ ] **Step 2: Commit Task 7 changes**

```bash
git add frontend/src/components/TrafficChart.tsx
git commit -m "feat(ui): refine real-time traffic volume line chart"
```

---

### Task 8: Real-Time Detection Log Table (`LiveFeed.tsx`)

**Files:**
- Modify: `frontend/src/components/LiveFeed.tsx`

**Interfaces:**
- Consumes: `events: DetectionLogEvent[]`.
- Produces: Scrollable real-time table with columns `WAKTU | JENIS KENDARAAN | JALUR | STATUS | ARAH`, Lucide icons, and IN/OUT badges.

- [ ] **Step 1: Implement Detection Log table component**
- [ ] **Step 2: Commit Task 8 changes**

```bash
git add frontend/src/components/LiveFeed.tsx
git commit -m "feat(ui): implement real-time detection log feed table"
```

---

### Task 9: CCTV Selector Modal (`CCTVSelectorModal.tsx`)

**Files:**
- Modify: `frontend/src/components/CCTVSelectorModal.tsx`

**Interfaces:**
- Consumes: `isOpen: boolean`, `onClose: () => void`, `streamInfo: StreamSourceInfo | null`, `onSelectSource: (url: string, name: string) => void`.
- Produces: Light Theme modal with CCTV presets list, camera active indicators, and custom URL input.

- [ ] **Step 1: Implement modern Light Theme CCTV selector modal**
- [ ] **Step 2: Commit Task 9 changes**

```bash
git add frontend/src/components/CCTVSelectorModal.tsx
git commit -m "feat(ui): update CCTV selector modal with light theme aesthetic"
```

---

### Task 10: Page Layout Assembly & State Integration (`page.tsx`)

**Files:**
- Modify: `frontend/src/app/page.tsx`

**Interfaces:**
- Assembles: `Header`, `KPIRow`, Left 7-Col Grid (`VideoPlayer`, `VehicleBreakdown`, `AdaptiveSignalSplit`), Right 5-Col Grid (`TrafficDirectionCard` Inbound/Outbound, `TrafficChart`, `LiveFeed`), and `CCTVSelectorModal`.
- Manages: WebSocket connection, delta tracking for `DetectionLogEvent`s, chart history buffer (20 points), ROI fetch/save, and stream switching.

- [ ] **Step 1: Implement full dashboard layout and state logic in `page.tsx`**
- [ ] **Step 2: Commit Task 10 changes**

```bash
git add frontend/src/app/page.tsx
git commit -m "feat(ui): assemble complete redesigned dashboard layout and state synchronization"
```

---

### Task 11: End-to-End Build & Verification

**Files:**
- Test / Verify all frontend and backend components.

- [ ] **Step 1: Run frontend build check**
Run: `npm --prefix frontend run build`
Expected: Zero build errors.

- [ ] **Step 2: Run frontend lint check**
Run: `npm --prefix frontend run lint`
Expected: Zero ESLint errors.

- [ ] **Step 3: Run backend pytest suite**
Run: `pytest backend/tests -v`
Expected: All tests pass.

- [ ] **Step 4: Commit final verification adjustments**
```bash
git commit --allow-empty -m "chore: verify build and test suite passing"
```
