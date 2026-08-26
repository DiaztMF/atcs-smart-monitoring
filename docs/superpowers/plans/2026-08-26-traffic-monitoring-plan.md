# Real-Time Traffic Load Monitoring (SMP) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-ready real-time computer vision traffic monitoring and Passenger Car Unit (SMP / Satuan Mobil Penumpang) counting system from dynamic FLV/HLS CCTV streams with an interactive Next.js polygon ROI dashboard and live stream switcher, optimized 100% for free-tier deployments.

**Architecture:** Monorepo consisting of a FastAPI backend (YOLOv11 Nano + ByteTrack + OpenCV C++ spatial point-in-polygon) streaming MJPEG video and broadcasting WebSocket metrics, coupled with a Next.js 14 frontend featuring an interactive HTML5 Canvas polygon overlay with normalized coordinates ($0.0 \dots 1.0$), CCTV preset selector and custom URL input modal, real-time Recharts traffic density visualizations, and vehicle breakdown metrics.

**Tech Stack:** 
- Backend: Python 3.10+, FastAPI 0.115.0, Uvicorn 0.30.0, Ultralytics 8.3.0 (YOLOv11n), Lapx 0.5.2, OpenCV Headless 4.10.0, Pydantic 2.9.0, Pytest 8.3.0, WebSockets 13.0.0.
- Frontend: Next.js 14.2.35 (App Router), React 18.3.0, TypeScript 5.5.0, Tailwind CSS 3.4.0, Recharts 2.12.7, Lucide React 0.400.0.

## Global Constraints

- You must use Python 3.10+ syntax and strict TypeScript (`tsconfig.json` strict mode, no `any`).
- You must enforce PKJI / MKJI SMP equivalents: Motorcycle = 0.5, Car = 1.0, Bus = 1.3, Truck = 1.3.
- You must calculate ground contact points using bottom-center reference: `((x1 + x2) / 2, y2)`.
- You must normalize canvas coordinates to `0.0 ... 1.0` before sending to the backend.
- You must use `cv2.pointPolygonTest` for spatial point-in-polygon checks.
- You must maintain thread safety across stream readers, inference workers, and broadcasters using `state.py`.
- You must purge tracking history for IDs unseen for >60 frames.
- You must support dynamic stream switching via `/api/v1/stream-source`.

---

### Task 13: Backend Dynamic CCTV Stream Switcher & Preset Registry

**Files:**
- Modify: `backend/app/core/config.py`
- Modify: `backend/app/core/state.py`
- Modify: `backend/app/services/stream_reader.py`
- Modify: `backend/app/api/endpoints.py`
- Modify: `backend/tests/test_api.py`

**Interfaces:**
- Consumes: `global_state`, `StreamReaderWorker`
- Produces:
  - `GET /api/v1/stream-source`: returns active stream name, URL, and preset array
  - `POST /api/v1/stream-source`: switches video stream on the fly and resets counters

- [ ] **Step 1: Update core/config.py and core/state.py with CCTV Presets**
- [ ] **Step 2: Add dynamic switch_stream method in stream_reader.py**
- [ ] **Step 3: Add endpoints in api/endpoints.py**
- [ ] **Step 4: Add pytest test cases in tests/test_api.py**
- [ ] **Step 5: Run backend tests**

---

### Task 14: Frontend CCTV Preset Selector Modal & Dynamic Stream Input

**Files:**
- Modify: `frontend/src/types/index.ts`
- Create: `frontend/src/components/CCTVSelectorModal.tsx`
- Modify: `frontend/src/components/VideoPlayer.tsx`
- Modify: `frontend/src/app/page.tsx`

**Interfaces:**
- Consumes: `StreamSourceInfo` from `@/types`
- Produces: Interactive CCTV modal with ATCS presets & custom URL stream submission

- [ ] **Step 1: Update frontend/src/types/index.ts with StreamSource types**
- [ ] **Step 2: Implement CCTVSelectorModal.tsx**
- [ ] **Step 3: Integrate switcher trigger button in VideoPlayer.tsx**
- [ ] **Step 4: Wire up state and API calls in page.tsx**
- [ ] **Step 5: Run frontend build verification**
