=== foundation rules ===

# Smart Traffic Monitoring Guidelines

The Smart Traffic Monitoring guidelines are specifically curated for this full-stack real-time computer vision and traffic analytics application. These guidelines should be followed closely to ensure the best experience when developing, maintaining, and deploying the traffic load monitoring and adaptive control foundation.

## Foundational Context

This application is a real-time computer vision monitoring system that computes Passenger Car Units (PCU / Satuan Mobil Penumpang - SMP) from public CCTV FLV video streams using YOLOv11 and ByteTrack, paired with an interactive Next.js polygon ROI dashboard and its main packages & versions are below. You are an expert with them all. Ensure you abide by these specific packages & versions.

- fastapi - 0.115.0
- uvicorn[standard] - 0.30.0
- ultralytics - 8.3.0
- opencv-python-headless - 4.10.0
- pydantic - 2.9.0
- pydantic-settings - 2.5.0
- numpy - 1.26.0
- websockets - 13.0.0
- next - 14.2.0
- react - 18.3.0
- react-dom - 18.3.0
- typescript - 5.5.0
- tailwindcss - 3.4.0
- recharts - 2.12.0
- lucide-react - 0.400.0

## Skills Activation

This project has domain-specific skills available in `**/skills/**`. You MUST activate the relevant skill whenever you work in that domain—don't wait until you're stuck.

## Conventions

- You must follow all existing code conventions used in this application. When creating or editing a file, check sibling files for the correct structure, approach, and naming.
- Use descriptive names for variables and methods. For example, `calculate_passenger_car_unit`, not `calc_pcu_val`.
- Check for existing components to reuse before writing a new one.
- You must always normalize frontend canvas polygon coordinates to the range `0.0 ... 1.0` before transmitting to the backend.
- You must always compute vehicle ground-contact points using the bottom-center reference point `((x1 + x2) / 2, y2)` for spatial ROI testing on tilted perspective CCTV camera feeds.
- You must maintain thread safety across stream readers, inference workers, MJPEG frame broadcasters, and WebSocket metric publishers using centralized locks or queues.

## Verification Scripts

- Do not create verification scripts when existing manual checks or build processes cover that functionality and prove they work.

## Application Structure & Architecture

- Stick to the existing directory structure; don't create new base folders without approval.
  - `backend/app/api` - REST API endpoints and WebSocket connection handlers.
  - `backend/app/core` - Application settings, thread-safe global state, and logging configurations.
  - `backend/app/services` - Video stream readers, YOLOv11 detectors, ByteTrack trackers, ROI analyzers, and MJPEG generators.
  - `backend/sample_data` - Synthetic fallback video clips for offline demonstration and testing.
  - `frontend/src/app` - Next.js App Router root layout, global styles, and dashboard pages.
  - `frontend/src/components` - Interactive Canvas ROI overlays, MJPEG stream players, metric cards, charts, and activity feeds.
  - `frontend/src/hooks` - Custom React hooks for WebSocket connections, state synchronization, and reconnection logic.
  - `frontend/src/types` - TypeScript type definitions and shared data contracts.
- Do not change the application's dependencies without approval.

## Frontend Bundling

- If the user doesn't see a frontend change reflected in the UI, it could mean they need to restart the development server or rebuild. Ask them to run the appropriate dev or build command.

## Documentation Files

- You must only create documentation files if explicitly requested by the user.

## Replies

- Be concise in your explanations—focus on what's important rather than explaining obvious details.

=== fastapi rules ===

# FastAPI

## Tools

- Run development server via command line: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` (utilizes Uvicorn ASGI server with hot-reload).
- Run production server via command line: `uvicorn app.main:app --host 0.0.0.0 --port 7860` (utilizes Hugging Face Spaces port allocation).

## Searching Documentation (IMPORTANT)

- Always refer to FastAPI v0.115+ official documentation for lifespan context managers, dependency injection, and WebSocket lifecycle management.
- Always refer to Pydantic v2 documentation for `BaseSettings`, `model_validator`, and schema serialization.

## API & Route Patterns

- You must use `lifespan` async context managers on the FastAPI application instance for starting and terminating background stream ingestion tasks—never use deprecated `@app.on_event("startup")`.
- You must return streaming video via `StreamingResponse(mjpeg_generator(), media_type="multipart/x-mixed-replace; boundary=frame")`.
- You must handle WebSocket disconnections cleanly by catching `WebSocketDisconnect` and removing the active connection from the global client registry to prevent stale socket write exceptions.

=== nextjs rules ===

# Next.js

## Tools

- Run development server via command line: `npm run dev` (utilizes Next.js App Router dev server on port 3000).
- Production build: `npm run build`.
- Production start: `npm run start`.
- Linting: `npm run lint`.

## Searching Documentation (IMPORTANT)

- Always refer to Next.js 14 App Router documentation for client and server component boundaries, streaming metadata, and environment variable resolution.
- Always prefix client-accessible environment variables with `NEXT_PUBLIC_` (e.g., `NEXT_PUBLIC_BACKEND_URL`, `NEXT_PUBLIC_WS_URL`).

## Component & Rendering Patterns

- You must declare `'use client'` at the top of interactive components containing hooks, canvas listeners, or WebSocket subscriptions (e.g., `CanvasROI.tsx`, `VideoPlayer.tsx`, `TrafficChart.tsx`).
- You must avoid running canvas DOM operations or WebSocket connections on the server; always isolate browser-specific APIs inside `useEffect` hooks.
- Direct DOM canvas scaling must always account for CSS layout dimensions versus actual canvas drawing buffer dimensions (`canvas.width = rect.width`, `canvas.height = rect.height`).

=== python rules ===

# Python

- You must use Python 3.10+ syntax, type annotations (`typing.Dict`, `typing.List`, `typing.Optional`, `typing.Tuple`), and asynchronous patterns (`asyncio`, `async def`).
- Naming conventions: snake_case for functions and variables (`calculate_smp_density`, `inbound_polygon_contour`), PascalCase for classes (`SpatialROITracker`, `TrackedVehicle`), and UPPER_SNAKE_CASE for constants (`DEFAULT_SMP_WEIGHTS`, `MAX_FRAME_BUFFER_SIZE`).
- You must use native C++ bindings through `cv2.pointPolygonTest` for point-in-polygon evaluations instead of pure Python iterations to preserve low CPU overhead.
- You must enforce a time-to-live (TTL) frame expiration mechanism on vehicle tracking caches to purge IDs inactive for more than 60 consecutive frames.

=== typescript rules ===

# TypeScript

- You must enable strict mode in `tsconfig.json` and provide explicit types for all function signatures, component props, and API response models.
- Naming conventions: PascalCase for types, interfaces, and React components (`TrafficMetrics`, `CanvasROIProps`), camelCase for variables, methods, and hooks (`useWebSocket`, `normalizedPoints`).
- You must strictly forbid the use of `any`—use defined union types or unknown with type narrowing guards.
- You must define explicit interfaces for all incoming WebSocket payloads matching the backend schema:
  ```typescript
  export interface DirectionMetrics {
    total_smp: number;
    smp_per_minute: number;
    density_level: 'LANCAR' | 'SEDANG' | 'PADAT' | 'MACET';
    breakdown: {
      motorcycle: number;
      car: number;
      bus: number;
      truck: number;
    };
  }
  ```

=== ultralytics-yolov11 rules ===

# Ultralytics YOLOv11 & ByteTrack

- You must use the lightweight `yolo11n.pt` Nano weights for CPU inference to maintain high throughput in free-tier environments.
- Target COCO class filtering must be restricted to indices `[2, 3, 5, 7]` representing `car`, `motorcycle`, `bus`, and `truck`.
- You must execute tracking with persistence enabled: `model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)`.
- You must apply Indonesian Highway Capacity Manual (PKJI / MKJI) passenger car unit equivalents:
  - Motorcycle = `0.5` SMP
  - Passenger Car = `1.0` SMP
  - Bus = `1.3` SMP
  - Truck = `1.3` SMP
- You must throttle CPU processing loop adaptively to maintain a steady 10–15 FPS target rate, avoiding thread starvation.

=== tailwindcss rules ===

# Tailwind CSS

- You must use Tailwind CSS utility classes with dark-mode optimized glassmorphism aesthetics (`bg-slate-900/80`, `backdrop-blur-md`, `border-slate-800`).
- Directional indicator color semantics must remain consistent across all views:
  - Inbound traffic: Emerald / Cyan palette (`emerald-500`, `cyan-400`).
  - Outbound traffic: Amber / Rose palette (`amber-500`, `rose-500`).
- Responsive layouts must default to mobile-first stacked containers (`flex-col`) and expand to desktop grid columns (`lg:grid-cols-12`).

=== deployment rules ===

# Deployment

- Backend is structured for 100% free-tier deployment on Hugging Face Spaces (Docker CPU runtime) or local/Cloudflare Tunnel.
- Frontend is structured for deployment on Vercel (Next.js App Router).
- Containerization must rely on a multi-stage or lean single-stage `python:3.10-slim` base image with essential runtime libraries (`libgl1`, `libglib2.0-0`, `ffmpeg`).

=== tests rules ===

# Test Enforcement

- Backend unit and integration testing is powered by `pytest`.
- Run tests via command line: `pytest backend/tests -v`.
- Test suites must verify:
  - PKJI SMP calculation weights and mathematical aggregations.
  - Spatial point-in-polygon boundary checks and coordinate scaling.
  - Vehicle tracking TTL cache purge and anti-double-count state transitions.
  - REST endpoint contracts and WebSocket payload serialization integrity.
