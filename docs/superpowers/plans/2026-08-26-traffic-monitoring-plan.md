# Real-Time Traffic Load Monitoring (SMP) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-ready real-time computer vision traffic monitoring and Passenger Car Unit (SMP / Satuan Mobil Penumpang) counting system from FLV CCTV streams with an interactive Next.js polygon ROI dashboard, optimized 100% for free-tier deployments.

**Architecture:** Monorepo consisting of a FastAPI backend (YOLOv11 Nano + ByteTrack + OpenCV C++ spatial point-in-polygon) streaming MJPEG video and broadcasting WebSocket metrics, coupled with a Next.js 14 frontend featuring an interactive HTML5 Canvas polygon overlay with normalized coordinates ($0.0 \dots 1.0$), real-time Recharts traffic density visualizations, and vehicle breakdown metrics.

**Tech Stack:** 
- Backend: Python 3.10+, FastAPI 0.115.0, Uvicorn 0.30.0, Ultralytics 8.3.0 (YOLOv11n), OpenCV Headless 4.10.0, Pydantic 2.9.0, Pytest 8.3.0, WebSockets 13.0.0.
- Frontend: Next.js 14.2.0 (App Router), React 18.3.0, TypeScript 5.5.0, Tailwind CSS 3.4.0, Recharts 2.12.0, Lucide React 0.400.0.

## Global Constraints

- You must use Python 3.10+ syntax and strict TypeScript (`tsconfig.json` strict mode, no `any`).
- You must enforce PKJI / MKJI SMP equivalents: Motorcycle = 0.5, Car = 1.0, Bus = 1.3, Truck = 1.3.
- You must calculate ground contact points using bottom-center reference: `((x1 + x2) / 2, y2)`.
- You must normalize canvas coordinates to `0.0 ... 1.0` before sending to the backend.
- You must use `cv2.pointPolygonTest` for spatial point-in-polygon checks.
- You must maintain thread safety across stream readers, inference workers, and broadcasters using `state.py`.
- You must purge tracking history for IDs unseen for >60 frames.

---

### Task 1: Backend Scaffolding, Core Config, Structured Logging & Thread-Safe State Management

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/logging.py`
- Create: `backend/app/core/state.py`
- Test: `backend/tests/test_state.py`

**Interfaces:**
- Consumes: None
- Produces: 
  - `AppSettings` in `config.py` (Pydantic BaseSettings)
  - `GlobalStateManager` and `global_state` instance in `state.py` with methods:
    - `set_raw_frame(frame: np.ndarray) -> None`
    - `get_raw_frame() -> Optional[np.ndarray]`
    - `set_annotated_frame(frame: np.ndarray) -> None`
    - `get_annotated_frame() -> Optional[np.ndarray]`
    - `update_metrics(metrics: Dict[str, Any]) -> None`
    - `get_metrics() -> Dict[str, Any]`
    - `set_roi(direction: str, polygon: List[Tuple[float, float]]) -> None`
    - `get_roi(direction: str) -> List[Tuple[float, float]]`
    - `reset_counters() -> None`

- [ ] **Step 1: Write backend requirements.txt**

Create `backend/requirements.txt`:
```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
ultralytics==8.3.0
opencv-python-headless==4.10.0.84
pydantic==2.9.0
pydantic-settings==2.5.0
numpy==1.26.0
websockets==13.0.0
pytest==8.3.0
httpx==0.27.0
```

- [ ] **Step 2: Write failing test for GlobalStateManager**

Create `backend/tests/test_state.py`:
```python
import pytest
import numpy as np
from app.core.state import GlobalStateManager

def test_global_state_frame_and_metrics():
    state = GlobalStateManager()
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    state.set_raw_frame(dummy_frame)
    retrieved_raw = state.get_raw_frame()
    assert retrieved_raw is not None
    assert retrieved_raw.shape == (480, 640, 3)
    
    state.set_annotated_frame(dummy_frame)
    retrieved_annotated = state.get_annotated_frame()
    assert retrieved_annotated is not None
    assert retrieved_annotated.shape == (480, 640, 3)

def test_global_state_roi_and_reset():
    state = GlobalStateManager()
    polygon = [(0.1, 0.1), (0.5, 0.1), (0.5, 0.8), (0.1, 0.8)]
    state.set_roi("inbound", polygon)
    assert state.get_roi("inbound") == polygon
    
    state.update_metrics({"inbound": {"total_smp": 10.5}})
    assert state.get_metrics()["inbound"]["total_smp"] == 10.5
    
    state.reset_counters()
    assert state.get_metrics()["inbound"]["total_smp"] == 0.0
```

- [ ] **Step 3: Implement core/config.py, core/logging.py, and core/state.py**

Create `backend/app/core/config.py`:
```python
from typing import List
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    PROJECT_NAME: str = "Smart Traffic Monitoring"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["*"]
    
    # Video source: FLV stream URL or local sample file
    VIDEO_STREAM_URL: str = "http://bptdjatengdiy.dephub.go.id:8000/live/atcs_surakarta_balaikota.flv"
    FALLBACK_VIDEO_PATH: str = "sample_data/synthetic_traffic.mp4"
    TARGET_FPS: int = 12
    STREAM_WIDTH: int = 640
    STREAM_HEIGHT: int = 360
    
    # Tracking constants
    TTL_FRAME_PURGE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = AppSettings()
```

Create `backend/app/core/logging.py`:
```python
import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger("smart_monitoring")

logger = setup_logging()
```

Create `backend/app/core/state.py`:
```python
import threading
import time
from typing import Optional, Dict, Any, List, Tuple
import numpy as np

class GlobalStateManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._raw_frame: Optional[np.ndarray] = None
        self._annotated_frame: Optional[np.ndarray] = None
        self._is_stream_active: bool = False
        self._current_fps: float = 0.0
        
        # Default Polygons in Normalized Coords (0.0 ... 1.0)
        self._roi_inbound: List[Tuple[float, float]] = [
            (0.05, 0.40), (0.45, 0.40), (0.45, 0.95), (0.05, 0.95)
        ]
        self._roi_outbound: List[Tuple[float, float]] = [
            (0.55, 0.40), (0.95, 0.40), (0.95, 0.95), (0.55, 0.95)
        ]
        
        self._metrics: Dict[str, Any] = self._initial_metrics()

    def _initial_metrics(self) -> Dict[str, Any]:
        return {
            "timestamp": time.time(),
            "fps": 0.0,
            "inbound": {
                "total_smp": 0.0,
                "smp_per_minute": 0.0,
                "density_level": "LANCAR",
                "breakdown": {"motorcycle": 0, "car": 0, "bus": 0, "truck": 0}
            },
            "outbound": {
                "total_smp": 0.0,
                "smp_per_minute": 0.0,
                "density_level": "LANCAR",
                "breakdown": {"motorcycle": 0, "car": 0, "bus": 0, "truck": 0}
            },
            "recent_events": []
        }

    def set_raw_frame(self, frame: np.ndarray) -> None:
        with self._lock:
            self._raw_frame = frame
            self._is_stream_active = True

    def get_raw_frame(self) -> Optional[np.ndarray]:
        with self._lock:
            return self._raw_frame.copy() if self._raw_frame is not None else None

    def set_annotated_frame(self, frame: np.ndarray) -> None:
        with self._lock:
            self._annotated_frame = frame

    def get_annotated_frame(self) -> Optional[np.ndarray]:
        with self._lock:
            return self._annotated_frame.copy() if self._annotated_frame is not None else None

    def set_stream_status(self, is_active: bool, fps: float) -> None:
        with self._lock:
            self._is_stream_active = is_active
            self._current_fps = fps

    def get_stream_status(self) -> Tuple[bool, float]:
        with self._lock:
            return self._is_stream_active, self._current_fps

    def set_roi(self, direction: str, polygon: List[Tuple[float, float]]) -> None:
        with self._lock:
            if direction.lower() == "inbound":
                self._roi_inbound = polygon
            elif direction.lower() == "outbound":
                self._roi_outbound = polygon

    def get_roi(self, direction: str) -> List[Tuple[float, float]]:
        with self._lock:
            if direction.lower() == "inbound":
                return list(self._roi_inbound)
            elif direction.lower() == "outbound":
                return list(self._roi_outbound)
            return []

    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        with self._lock:
            self._metrics.update(metrics)

    def get_metrics(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._metrics)

    def reset_counters(self) -> None:
        with self._lock:
            self._metrics = self._initial_metrics()

global_state = GlobalStateManager()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest backend/tests/test_state.py -v`
Expected: PASS (2 passed)

---

### Task 2: Spatial ROI Tracker & PKJI Passenger Car Unit (SMP) Calculation Engine

**Files:**
- Create: `backend/app/services/roi_tracker.py`
- Create: `backend/tests/test_roi_tracker.py`

**Interfaces:**
- Consumes: `global_state` from `backend.app.core.state`
- Produces: `SpatialROITracker` class with methods:
  - `calculate_bottom_center(bbox: Tuple[int, int, int, int]) -> Tuple[int, int]`
  - `normalize_coordinate(point: Tuple[int, int], frame_w: int, frame_h: int) -> Tuple[float, float]`
  - `denormalize_polygon(polygon: List[Tuple[float, float]], frame_w: int, frame_h: int) -> np.ndarray`
  - `is_point_in_polygon(point: Tuple[int, int], polygon_contour: np.ndarray) -> bool`
  - `process_vehicle_track(track_id: int, class_name: str, bbox: Tuple[int, int, int, int], frame_w: int, frame_h: int, current_frame_idx: int) -> Optional[Dict[str, Any]]`
  - `purge_inactive_tracks(current_frame_idx: int) -> None`
  - `get_metrics_summary() -> Dict[str, Any]`

- [ ] **Step 1: Write failing test for SpatialROITracker**

Create `backend/tests/test_roi_tracker.py`:
```python
import pytest
import numpy as np
from app.services.roi_tracker import SpatialROITracker, SMP_WEIGHTS

def test_smp_weights_standard():
    assert SMP_WEIGHTS["motorcycle"] == 0.5
    assert SMP_WEIGHTS["car"] == 1.0
    assert SMP_WEIGHTS["bus"] == 1.3
    assert SMP_WEIGHTS["truck"] == 1.3

def test_bottom_center_calculation():
    tracker = SpatialROITracker()
    # bbox: (x1, y1, x2, y2)
    bbox = (100, 50, 200, 150)
    bc_x, bc_y = tracker.calculate_bottom_center(bbox)
    assert bc_x == 150  # (100 + 200) / 2
    assert bc_y == 150  # y2

def test_spatial_polygon_and_counting():
    tracker = SpatialROITracker(ttl_frames=60)
    frame_w, frame_h = 1000, 1000
    
    # Define normalized polygon: (0.1, 0.1) to (0.4, 0.4) -> pixels (100, 100) to (400, 400)
    polygon = [(0.1, 0.1), (0.4, 0.1), (0.4, 0.4), (0.1, 0.4)]
    tracker.set_polygon("inbound", polygon)
    
    # Vehicle 1 inside inbound ROI at frame 1
    bbox_inside = (150, 150, 250, 250) # bottom-center is (200, 250) -> inside
    event = tracker.process_vehicle_track(
        track_id=1, class_name="car", bbox=bbox_inside,
        frame_w=frame_w, frame_h=frame_h, current_frame_idx=1
    )
    assert event is not None
    assert event["direction"] == "inbound"
    assert event["vehicle_type"] == "car"
    assert event["smp"] == 1.0
    
    # Ensure same track_id in next frame is NOT double counted
    event_duplicate = tracker.process_vehicle_track(
        track_id=1, class_name="car", bbox=bbox_inside,
        frame_w=frame_w, frame_h=frame_h, current_frame_idx=2
    )
    assert event_duplicate is None
    
    summary = tracker.get_metrics_summary()
    assert summary["inbound"]["total_smp"] == 1.0
    assert summary["inbound"]["breakdown"]["car"] == 1

def test_ttl_purge():
    tracker = SpatialROITracker(ttl_frames=10)
    frame_w, frame_h = 1000, 1000
    polygon = [(0.1, 0.1), (0.4, 0.1), (0.4, 0.4), (0.1, 0.4)]
    tracker.set_polygon("inbound", polygon)
    
    bbox = (150, 150, 250, 250)
    tracker.process_vehicle_track(1, "car", bbox, frame_w, frame_h, current_frame_idx=1)
    assert 1 in tracker.active_tracks
    
    # Fast forward to frame 20 (delta > 10 frames)
    tracker.purge_inactive_tracks(current_frame_idx=20)
    assert 1 not in tracker.active_tracks
```

- [ ] **Step 2: Implement app/services/roi_tracker.py**

Create `backend/app/services/roi_tracker.py`:
```python
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import cv2
import numpy as np
from app.core.logging import logger

SMP_WEIGHTS: Dict[str, float] = {
    "motorcycle": 0.5,
    "car": 1.0,
    "bus": 1.3,
    "truck": 1.3
}

@dataclass
class TrackedVehicleState:
    track_id: int
    class_name: str
    smp_value: float
    last_seen_frame: int
    counted_inbound: bool = False
    counted_outbound: bool = False

class SpatialROITracker:
    def __init__(self, ttl_frames: int = 60):
        self.ttl_frames = ttl_frames
        self.active_tracks: Dict[int, TrackedVehicleState] = {}
        self.inbound_polygon: List[Tuple[float, float]] = []
        self.outbound_polygon: List[Tuple[float, float]] = []
        
        self.inbound_counts: Dict[str, int] = {"motorcycle": 0, "car": 0, "bus": 0, "truck": 0}
        self.outbound_counts: Dict[str, int] = {"motorcycle": 0, "car": 0, "bus": 0, "truck": 0}
        
        self.inbound_smp: float = 0.0
        self.outbound_smp: float = 0.0
        
        self.recent_events: List[Dict[str, Any]] = []
        self.start_time: float = time.time()
        self.recent_timestamps: List[Tuple[float, str, float]] = [] # (timestamp, direction, smp)

    def set_polygon(self, direction: str, polygon: List[Tuple[float, float]]) -> None:
        if direction.lower() == "inbound":
            self.inbound_polygon = polygon
        elif direction.lower() == "outbound":
            self.outbound_polygon = polygon

    def calculate_bottom_center(self, bbox: Tuple[int, int, int, int]) -> Tuple[int, int]:
        x1, y1, x2, y2 = bbox
        return int((x1 + x2) / 2), int(y2)

    def denormalize_polygon(self, polygon: List[Tuple[float, float]], frame_w: int, frame_h: int) -> np.ndarray:
        points = [[int(pt[0] * frame_w), int(pt[1] * frame_h)] for pt in polygon]
        return np.array(points, dtype=np.int32).reshape((-1, 1, 2))

    def is_point_in_polygon(self, point: Tuple[int, int], polygon_contour: np.ndarray) -> bool:
        if len(polygon_contour) < 3:
            return False
        # cv2.pointPolygonTest returns >= 0 if inside or on boundary
        return cv2.pointPolygonTest(polygon_contour, (float(point[0]), float(point[1])), False) >= 0

    def process_vehicle_track(
        self,
        track_id: int,
        class_name: str,
        bbox: Tuple[int, int, int, int],
        frame_w: int,
        frame_h: int,
        current_frame_idx: int
    ) -> Optional[Dict[str, Any]]:
        normalized_class = class_name.lower()
        if normalized_class not in SMP_WEIGHTS:
            return None
        
        smp_val = SMP_WEIGHTS[normalized_class]
        
        if track_id not in self.active_tracks:
            self.active_tracks[track_id] = TrackedVehicleState(
                track_id=track_id,
                class_name=normalized_class,
                smp_value=smp_val,
                last_seen_frame=current_frame_idx
            )
        
        v_state = self.active_tracks[track_id]
        v_state.last_seen_frame = current_frame_idx
        
        ground_point = self.calculate_bottom_center(bbox)
        event = None
        now_ts = time.time()
        
        # Inbound check
        if self.inbound_polygon and not v_state.counted_inbound:
            inbound_contour = self.denormalize_polygon(self.inbound_polygon, frame_w, frame_h)
            if self.is_point_in_polygon(ground_point, inbound_contour):
                v_state.counted_inbound = True
                self.inbound_counts[normalized_class] += 1
                self.inbound_smp += smp_val
                self.recent_timestamps.append((now_ts, "inbound", smp_val))
                event = {
                    "id": f"evt_{track_id}_{int(now_ts * 1000)}",
                    "timestamp": time.strftime("%H:%M:%S"),
                    "direction": "inbound",
                    "vehicle_type": normalized_class,
                    "smp": smp_val
                }
                self.recent_events.insert(0, event)
                if len(self.recent_events) > 15:
                    self.recent_events.pop()
                return event

        # Outbound check
        if self.outbound_polygon and not v_state.counted_outbound:
            outbound_contour = self.denormalize_polygon(self.outbound_polygon, frame_w, frame_h)
            if self.is_point_in_polygon(ground_point, outbound_contour):
                v_state.counted_outbound = True
                self.outbound_counts[normalized_class] += 1
                self.outbound_smp += smp_val
                self.recent_timestamps.append((now_ts, "outbound", smp_val))
                event = {
                    "id": f"evt_{track_id}_{int(now_ts * 1000)}",
                    "timestamp": time.strftime("%H:%M:%S"),
                    "direction": "outbound",
                    "vehicle_type": normalized_class,
                    "smp": smp_val
                }
                self.recent_events.insert(0, event)
                if len(self.recent_events) > 15:
                    self.recent_events.pop()
                return event

        return None

    def purge_inactive_tracks(self, current_frame_idx: int) -> None:
        expired_ids = [
            t_id for t_id, state in self.active_tracks.items()
            if (current_frame_idx - state.last_seen_frame) > self.ttl_frames
        ]
        for t_id in expired_ids:
            del self.active_tracks[t_id]

    def _calculate_density_level(self, smp_per_min: float) -> str:
        if smp_per_min < 10.0:
            return "LANCAR"
        elif smp_per_min < 25.0:
            return "SEDANG"
        elif smp_per_min < 40.0:
            return "PADAT"
        return "MACET"

    def get_metrics_summary(self) -> Dict[str, Any]:
        now = time.time()
        one_min_ago = now - 60.0
        
        # Filter rolling 1 minute timestamps
        self.recent_timestamps = [item for item in self.recent_timestamps if item[0] >= one_min_ago]
        
        inbound_last_min_smp = sum(item[2] for item in self.recent_timestamps if item[1] == "inbound")
        outbound_last_min_smp = sum(item[2] for item in self.recent_timestamps if item[1] == "outbound")
        
        return {
            "timestamp": now,
            "inbound": {
                "total_smp": round(self.inbound_smp, 1),
                "smp_per_minute": round(inbound_last_min_smp, 1),
                "density_level": self._calculate_density_level(inbound_last_min_smp),
                "breakdown": dict(self.inbound_counts)
            },
            "outbound": {
                "total_smp": round(self.outbound_smp, 1),
                "smp_per_minute": round(outbound_last_min_smp, 1),
                "density_level": self._calculate_density_level(outbound_last_min_smp),
                "breakdown": dict(self.outbound_counts)
            },
            "recent_events": list(self.recent_events)
        }

    def reset(self) -> None:
        self.active_tracks.clear()
        self.inbound_counts = {"motorcycle": 0, "car": 0, "bus": 0, "truck": 0}
        self.outbound_counts = {"motorcycle": 0, "car": 0, "bus": 0, "truck": 0}
        self.inbound_smp = 0.0
        self.outbound_smp = 0.0
        self.recent_events.clear()
        self.recent_timestamps.clear()
```

- [ ] **Step 3: Run test to verify it passes**

Run: `pytest backend/tests/test_roi_tracker.py -v`
Expected: PASS (4 passed)

---

### Task 3: YOLOv11 + ByteTrack AI Detector Service with Bottom-Center Wheel Point Tracking

**Files:**
- Create: `backend/app/services/detector.py`
- Create: `backend/tests/test_detector.py`

**Interfaces:**
- Consumes: `SpatialROITracker`, `AppSettings`, `global_state`
- Produces: `TrafficDetector` class with methods:
  - `detect_and_track(frame: np.ndarray, current_frame_idx: int) -> Tuple[np.ndarray, Dict[str, Any]]`
  - `draw_visualizations(frame: np.ndarray, tracks_data: List[Dict], inbound_poly: List, outbound_poly: List) -> np.ndarray`

- [ ] **Step 1: Write test for TrafficDetector initialization and annotation logic**

Create `backend/tests/test_detector.py`:
```python
import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from app.services.detector import TrafficDetector

def test_detector_draw_visualizations():
    detector = TrafficDetector(model_name="yolo11n.pt", dry_run=True)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    inbound_poly = [(0.1, 0.1), (0.4, 0.1), (0.4, 0.9), (0.1, 0.9)]
    outbound_poly = [(0.6, 0.1), (0.9, 0.1), (0.9, 0.9), (0.6, 0.9)]
    
    annotated = detector.draw_visualizations(
        frame=frame,
        tracks_data=[{"track_id": 1, "class_name": "car", "bbox": (100, 100, 200, 200), "smp": 1.0}],
        inbound_poly=inbound_poly,
        outbound_poly=outbound_poly
    )
    assert annotated.shape == (480, 640, 3)
    # Check that pixels are altered (not completely black)
    assert np.any(annotated > 0)
```

- [ ] **Step 2: Implement app/services/detector.py**

Create `backend/app/services/detector.py`:
```python
from typing import Tuple, List, Dict, Any, Optional
import cv2
import numpy as np
from ultralytics import YOLO
from app.core.logging import logger
from app.services.roi_tracker import SpatialROITracker, SMP_WEIGHTS

# COCO indices: 2=car, 3=motorcycle, 5=bus, 7=truck
TARGET_CLASSES = [2, 3, 5, 7]
CLASS_MAP = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}

class TrafficDetector:
    def __init__(self, model_name: str = "yolo11n.pt", ttl_frames: int = 60, dry_run: bool = False):
        self.dry_run = dry_run
        self.model = None if dry_run else YOLO(model_name)
        self.roi_tracker = SpatialROITracker(ttl_frames=ttl_frames)

    def update_polygons(self, inbound_poly: List[Tuple[float, float]], outbound_poly: List[Tuple[float, float]]):
        self.roi_tracker.set_polygon("inbound", inbound_poly)
        self.roi_tracker.set_polygon("outbound", outbound_poly)

    def detect_and_track(
        self,
        frame: np.ndarray,
        current_frame_idx: int,
        inbound_poly: List[Tuple[float, float]],
        outbound_poly: List[Tuple[float, float]]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        h, w = frame.shape[:2]
        self.update_polygons(inbound_poly, outbound_poly)
        
        tracks_to_render = []
        
        if not self.dry_run and self.model is not None:
            try:
                # Run YOLOv11 tracking with ByteTrack
                results = self.model.track(
                    source=frame,
                    persist=True,
                    classes=TARGET_CLASSES,
                    tracker="bytetrack.yaml",
                    verbose=False
                )
                
                if results and len(results) > 0 and results[0].boxes is not None:
                    boxes = results[0].boxes
                    if boxes.id is not None:
                        track_ids = boxes.id.int().cpu().tolist()
                        cls_ids = boxes.cls.int().cpu().tolist()
                        xyxy = boxes.xyxy.int().cpu().tolist()
                        
                        for box_coords, track_id, cls_id in zip(xyxy, track_ids, cls_ids):
                            class_name = CLASS_MAP.get(cls_id, "car")
                            bbox = (box_coords[0], box_coords[1], box_coords[2], box_coords[3])
                            smp_val = SMP_WEIGHTS.get(class_name, 1.0)
                            
                            self.roi_tracker.process_vehicle_track(
                                track_id=track_id,
                                class_name=class_name,
                                bbox=bbox,
                                frame_w=w,
                                frame_h=h,
                                current_frame_idx=current_frame_idx
                            )
                            
                            tracks_to_render.append({
                                "track_id": track_id,
                                "class_name": class_name,
                                "bbox": bbox,
                                "smp": smp_val
                            })
            except Exception as e:
                logger.error(f"Inference error in detector: {e}")

        self.roi_tracker.purge_inactive_tracks(current_frame_idx)
        annotated_frame = self.draw_visualizations(frame, tracks_to_render, inbound_poly, outbound_poly)
        metrics = self.roi_tracker.get_metrics_summary()
        
        return annotated_frame, metrics

    def draw_visualizations(
        self,
        frame: np.ndarray,
        tracks_data: List[Dict[str, Any]],
        inbound_poly: List[Tuple[float, float]],
        outbound_poly: List[Tuple[float, float]]
    ) -> np.ndarray:
        annotated = frame.copy()
        h, w = annotated.shape[:2]
        
        # Draw Inbound Polygon (Emerald / Cyan: BGR (220, 200, 0))
        if inbound_poly:
            in_pts = np.array([[int(p[0]*w), int(p[1]*h)] for p in inbound_poly], np.int32).reshape((-1, 1, 2))
            cv2.polylines(annotated, [in_pts], isClosed=True, color=(220, 200, 0), thickness=2)
            cv2.putText(annotated, "INBOUND ROI", (in_pts[0][0][0], max(20, in_pts[0][0][1] - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 200, 0), 2)
        
        # Draw Outbound Polygon (Amber / Rose: BGR (0, 140, 255))
        if outbound_poly:
            out_pts = np.array([[int(p[0]*w), int(p[1]*h)] for p in outbound_poly], np.int32).reshape((-1, 1, 2))
            cv2.polylines(annotated, [out_pts], isClosed=True, color=(0, 140, 255), thickness=2)
            cv2.putText(annotated, "OUTBOUND ROI", (out_pts[0][0][0], max(20, out_pts[0][0][1] - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 140, 255), 2)

        # Draw vehicle bounding boxes & ground contact points
        for track in tracks_data:
            x1, y1, x2, y2 = track["bbox"]
            t_id = track["track_id"]
            c_name = track["class_name"]
            smp = track["smp"]
            
            # Ground-contact bottom-center point
            bc_x, bc_y = int((x1 + x2) / 2), int(y2)
            cv2.circle(annotated, (bc_x, bc_y), 4, (0, 255, 255), -1)
            
            # Box & label
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"#{t_id} {c_name} ({smp} SMP)"
            cv2.putText(annotated, label, (x1, max(15, y1 - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

        return annotated

    def reset(self):
        self.roi_tracker.reset()
```

- [ ] **Step 3: Run test to verify it passes**

Run: `pytest backend/tests/test_detector.py -v`
Expected: PASS (1 passed)

---

### Task 4: Video Stream Ingestion (FLV Reader with Auto-Reconnect & Fallback Sample Stream) and MJPEG Frame Generator

**Files:**
- Create: `backend/app/services/stream_reader.py`
- Create: `backend/app/services/mjpeg_stream.py`
- Create: `backend/sample_data/generate_sample_video.py`
- Test: `backend/tests/test_stream_service.py`

**Interfaces:**
- Consumes: `AppSettings`, `global_state`, `TrafficDetector`
- Produces: 
  - `StreamReaderWorker` background thread controller
  - `generate_mjpeg_frames()` generator yielding bytes with boundary `frame`

- [ ] **Step 1: Write script to generate local fallback sample video clip**

Create `backend/sample_data/generate_sample_video.py`:
```python
import cv2
import numpy as np
import os

def create_synthetic_traffic_clip(output_path="backend/sample_data/synthetic_traffic.mp4", num_frames=150):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 15.0, (640, 360))
    
    for i in range(num_frames):
        frame = np.full((360, 640, 3), 40, dtype=np.uint8) # dark road background
        # Draw road lanes
        cv2.line(frame, (320, 0), (320, 360), (200, 200, 200), 2)
        cv2.line(frame, (100, 0), (100, 360), (255, 255, 255), 2)
        cv2.line(frame, (540, 0), (540, 360), (255, 255, 255), 2)
        
        # Simulated moving car (Inbound: moving top to bottom)
        car_y = int((i * 4) % 360)
        cv2.rectangle(frame, (180, car_y), (250, car_y + 60), (0, 0, 220), -1)
        cv2.putText(frame, "SIMULATED VEHICLE (INBOUND)", (150, max(20, car_y - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # Simulated moving motorcycle (Outbound: moving bottom to top)
        moto_y = int((360 - (i * 5)) % 360)
        cv2.rectangle(frame, (400, moto_y), (430, moto_y + 40), (0, 220, 0), -1)
        cv2.putText(frame, "SIMULATED MOTOR (OUTBOUND)", (370, max(20, moto_y - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        out.write(frame)
    out.release()
    print(f"Synthetic video generated at {output_path}")

if __name__ == "__main__":
    create_synthetic_traffic_clip()
```

- [ ] **Step 2: Implement app/services/stream_reader.py**

Create `backend/app/services/stream_reader.py`:
```python
import threading
import time
import cv2
import numpy as np
from app.core.config import settings
from app.core.logging import logger
from app.core.state import global_state
from app.services.detector import TrafficDetector

class StreamReaderWorker:
    def __init__(self, detector: TrafficDetector):
        self.detector = detector
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.cap = None

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            logger.info("Stream reader worker started.")

    def stop(self):
        self.running = False
        if self.cap is not None:
            self.cap.release()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        logger.info("Stream reader worker stopped.")

    def _get_capture_source(self):
        logger.info(f"Connecting to primary stream: {settings.VIDEO_STREAM_URL}")
        cap = cv2.VideoCapture(settings.VIDEO_STREAM_URL)
        if not cap.isOpened():
            logger.warning(f"Primary stream unreachable. Falling back to: {settings.FALLBACK_VIDEO_PATH}")
            cap = cv2.VideoCapture(settings.FALLBACK_VIDEO_PATH)
        return cap

    def _run_loop(self):
        frame_idx = 0
        consecutive_failures = 0
        self.cap = self._get_capture_source()
        target_frame_time = 1.0 / max(1, settings.TARGET_FPS)
        fps_timer = time.time()
        fps_frame_counter = 0
        current_fps = 0.0

        while self.running:
            loop_start = time.time()
            if self.cap is None or not self.cap.isOpened():
                time.sleep(1.0)
                self.cap = self._get_capture_source()
                continue

            ret, frame = self.cap.read()
            if not ret or frame is None:
                consecutive_failures += 1
                if consecutive_failures > 5:
                    logger.warning("Multiple stream read failures. Reopening stream/looping fallback...")
                    self.cap.release()
                    time.sleep(1.0)
                    self.cap = self._get_capture_source()
                    consecutive_failures = 0
                time.sleep(0.05)
                continue

            consecutive_failures = 0
            frame_idx += 1
            fps_frame_counter += 1
            
            # FPS Calculation every 1 second
            if time.time() - fps_timer >= 1.0:
                current_fps = round(fps_frame_counter / (time.time() - fps_timer), 1)
                fps_frame_counter = 0
                fps_timer = time.time()

            # Resize frame to standardized processing dimensions
            resized_frame = cv2.resize(frame, (settings.STREAM_WIDTH, settings.STREAM_HEIGHT))
            global_state.set_raw_frame(resized_frame)
            global_state.set_stream_status(True, current_fps)

            # Retrieve active ROIs
            inbound_poly = global_state.get_roi("inbound")
            outbound_poly = global_state.get_roi("outbound")

            # Run AI Inference & Spatial tracking
            annotated_frame, metrics = self.detector.detect_and_track(
                frame=resized_frame,
                current_frame_idx=frame_idx,
                inbound_poly=inbound_poly,
                outbound_poly=outbound_poly
            )
            
            metrics["fps"] = current_fps
            global_state.set_annotated_frame(annotated_frame)
            global_state.update_metrics(metrics)

            # CPU Throttling to maintain target FPS
            elapsed = time.time() - loop_start
            sleep_duration = max(0.001, target_frame_time - elapsed)
            time.sleep(sleep_duration)

        if self.cap:
            self.cap.release()
```

- [ ] **Step 3: Implement app/services/mjpeg_stream.py**

Create `backend/app/services/mjpeg_stream.py`:
```python
import time
from typing import Generator
import cv2
import numpy as np
from app.core.state import global_state

def generate_mjpeg_frames() -> Generator[bytes, None, None]:
    """Generates continuous multipart/x-mixed-replace JPEG frames from global_state."""
    while True:
        frame = global_state.get_annotated_frame()
        if frame is None:
            # Fallback frame while loading
            frame = np.zeros((360, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "CONNECTING TO LIVE TRAFFIC STREAM...", (100, 180),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            time.sleep(0.1)

        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
        if not ret:
            time.sleep(0.05)
            continue

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.06) # ~15 FPS stream output
```

- [ ] **Step 4: Write test for MJPEG frame generator**

Create `backend/tests/test_stream_service.py`:
```python
import pytest
import numpy as np
from app.core.state import global_state
from app.services.mjpeg_stream import generate_mjpeg_frames

def test_mjpeg_generator_yields_valid_frames():
    dummy = np.full((360, 640, 3), 120, dtype=np.uint8)
    global_state.set_annotated_frame(dummy)
    
    gen = generate_mjpeg_frames()
    first_chunk = next(gen)
    assert b'--frame\r\n' in first_chunk
    assert b'Content-Type: image/jpeg\r\n\r\n' in first_chunk
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest backend/tests/test_stream_service.py -v`
Expected: PASS (1 passed)

---

### Task 5: FastAPI Application Lifecycle, REST Endpoints & WebSocket Metrics Broadcaster

**Files:**
- Create: `backend/app/api/endpoints.py`
- Create: `backend/app/api/websocket.py`
- Create: `backend/app/main.py`
- Create: `backend/Dockerfile`
- Test: `backend/tests/test_api.py`

**Interfaces:**
- Consumes: `global_state`, `StreamReaderWorker`, `generate_mjpeg_frames`
- Produces:
  - `app` FastAPI instance in `backend/app/main.py`
  - REST endpoints: `GET /api/v1/health`, `GET/POST /api/v1/roi`, `POST /api/v1/reset-counter`, `GET /api/v1/stream`
  - WebSocket endpoint: `/ws/metrics`

- [ ] **Step 1: Write test for REST endpoints and WebSocket metrics serialization**

Create `backend/tests/test_api.py`:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.state import global_state

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"

def test_roi_get_and_post():
    new_roi = {
        "inbound": [[0.1, 0.2], [0.3, 0.2], [0.3, 0.8], [0.1, 0.8]],
        "outbound": [[0.6, 0.2], [0.8, 0.2], [0.8, 0.8], [0.6, 0.8]]
    }
    post_res = client.post("/api/v1/roi", json=new_roi)
    assert post_res.status_code == 200
    
    get_res = client.get("/api/v1/roi")
    assert get_res.status_code == 200
    res_data = get_res.json()
    assert res_data["inbound"] == new_roi["inbound"]
    assert res_data["outbound"] == new_roi["outbound"]

def test_reset_counter():
    res = client.post("/api/v1/reset-counter")
    assert res.status_code == 200
    metrics = global_state.get_metrics()
    assert metrics["inbound"]["total_smp"] == 0.0
```

- [ ] **Step 2: Implement app/api/endpoints.py, app/api/websocket.py, and app/main.py**

Create `backend/app/api/endpoints.py`:
```python
from typing import List, Tuple, Dict
from pydantic import BaseModel
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.core.state import global_state
from app.services.mjpeg_stream import generate_mjpeg_frames

router = APIRouter()

class ROIModel(BaseModel):
    inbound: List[Tuple[float, float]]
    outbound: List[Tuple[float, float]]

@router.get("/health")
async def health_check():
    is_active, fps = global_state.get_stream_status()
    return {
        "status": "ok",
        "stream_active": is_active,
        "fps": fps
    }

@router.get("/roi", response_model=ROIModel)
async def get_roi():
    return {
        "inbound": global_state.get_roi("inbound"),
        "outbound": global_state.get_roi("outbound")
    }

@router.post("/roi")
async def update_roi(roi_data: ROIModel):
    global_state.set_roi("inbound", roi_data.inbound)
    global_state.set_roi("outbound", roi_data.outbound)
    return {"status": "success", "message": "ROI updated successfully"}

@router.post("/reset-counter")
async def reset_counter():
    global_state.reset_counters()
    return {"status": "success", "message": "Counters reset successfully"}

@router.get("/stream")
def video_stream():
    return StreamingResponse(
        generate_mjpeg_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
```

Create `backend/app/api/websocket.py`:
```python
import asyncio
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.logging import logger
from app.core.state import global_state

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        dead_connections = []
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)
        for dead in dead_connections:
            self.disconnect(dead)

manager = ConnectionManager()

@router.websocket("/ws/metrics")
async def websocket_metrics_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            metrics = global_state.get_metrics()
            await websocket.send_json(metrics)
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected.")
    except Exception as e:
        logger.error(f"WebSocket exception: {e}")
        manager.disconnect(websocket)
```

Create `backend/app/main.py`:
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.services.detector import TrafficDetector
from app.services.stream_reader import StreamReaderWorker
from app.api.endpoints import router as api_router
from app.api.websocket import router as ws_router

detector_instance = TrafficDetector(model_name="yolo11n.pt")
stream_worker = StreamReaderWorker(detector=detector_instance)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Smart Traffic Monitoring Server...")
    stream_worker.start()
    yield
    logger.info("Shutting down Smart Traffic Monitoring Server...")
    stream_worker.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(ws_router)
```

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Generate fallback sample video during build
RUN python sample_data/generate_sample_video.py

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

- [ ] **Step 3: Run test to verify it passes**

Run: `pytest backend/tests/test_api.py -v`
Expected: PASS (3 passed)

---

### Task 6: Frontend Scaffolding, Next.js App Router Setup, Tailwind CSS Dark Theme & TypeScript Contracts

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tailwind.config.ts`
- Create: `frontend/next.config.js`
- Create: `frontend/src/types/index.ts`
- Create: `frontend/src/app/globals.css`
- Create: `frontend/src/app/layout.tsx`

**Interfaces:**
- Consumes: None
- Produces:
  - TypeScript interfaces: `TrafficMetrics`, `DirectionMetrics`, `VehicleBreakdown`, `VehicleEvent`, `ROICoordinates`
  - Global CSS with Tailwind dark glassmorphism classes

- [ ] **Step 1: Write frontend/package.json and tsconfig.json**

Create `frontend/package.json`:
```json
{
  "name": "smart-traffic-monitoring-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev -p 3000",
    "build": "next build",
    "start": "next start -p 3000",
    "lint": "next lint"
  },
  "dependencies": {
    "clsx": "^2.1.1",
    "lucide-react": "^0.400.0",
    "next": "14.2.0",
    "react": "18.3.0",
    "react-dom": "18.3.0",
    "recharts": "^2.12.7",
    "tailwind-merge": "^2.3.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.5.0"
  }
}
```

Create `frontend/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

- [ ] **Step 2: Write frontend/tailwind.config.ts and globals.css**

Create `frontend/tailwind.config.ts`:
```ts
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
        background: "#0a0d14",
        foreground: "#f3f4f6",
        card: "#111827",
        border: "#1f2937",
        inbound: "#10b981", // Emerald
        outbound: "#f59e0b", // Amber
      },
    },
  },
  plugins: [],
};
export default config;
```

Create `frontend/src/app/globals.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --background: #0a0d14;
  --foreground: #f3f4f6;
}

body {
  color: var(--foreground);
  background: var(--background);
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

.glass-panel {
  background: rgba(17, 24, 39, 0.75);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
```

- [ ] **Step 3: Define TypeScript shared contracts in frontend/src/types/index.ts**

Create `frontend/src/types/index.ts`:
```ts
export type DensityLevel = 'LANCAR' | 'SEDANG' | 'PADAT' | 'MACET';

export interface VehicleBreakdown {
  motorcycle: number;
  car: number;
  bus: number;
  truck: number;
}

export interface DirectionMetrics {
  total_smp: number;
  smp_per_minute: number;
  density_level: DensityLevel;
  breakdown: VehicleBreakdown;
}

export interface VehicleEvent {
  id: string;
  timestamp: string;
  direction: 'inbound' | 'outbound';
  vehicle_type: 'motorcycle' | 'car' | 'bus' | 'truck';
  smp: number;
}

export interface TrafficMetrics {
  timestamp: number;
  fps: number;
  inbound: DirectionMetrics;
  outbound: DirectionMetrics;
  recent_events: VehicleEvent[];
}

export interface ROICoordinates {
  inbound: [number, number][];
  outbound: [number, number][];
}
```

Create `frontend/src/app/layout.tsx`:
```tsx
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Smart Traffic Monitoring — Real-Time Computer Vision & SMP Analytics",
  description: "Real-time traffic load monitoring and counting system based on YOLOv11 and PKJI standards",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#0a0d14] text-slate-100 antialiased selection:bg-emerald-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
```

Create `frontend/next.config.js`:
```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};

module.exports = nextConfig;
```

---

### Task 7: Frontend WebSocket Real-Time Hook & State Synchronization

**Files:**
- Create: `frontend/src/hooks/useWebSocket.ts`

**Interfaces:**
- Consumes: `TrafficMetrics` from `@/types`
- Produces: `useWebSocket(url: string)` hook returning `{ metrics, isConnected, error }`

- [ ] **Step 1: Implement frontend/src/hooks/useWebSocket.ts**

Create `frontend/src/hooks/useWebSocket.ts`:
```ts
'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { TrafficMetrics } from '@/types';

const INITIAL_METRICS: TrafficMetrics = {
  timestamp: Date.now() / 1000,
  fps: 0,
  inbound: {
    total_smp: 0,
    smp_per_minute: 0,
    density_level: 'LANCAR',
    breakdown: { motorcycle: 0, car: 0, bus: 0, truck: 0 },
  },
  outbound: {
    total_smp: 0,
    smp_per_minute: 0,
    density_level: 'LANCAR',
    breakdown: { motorcycle: 0, car: 0, bus: 0, truck: 0 },
  },
  recent_events: [],
};

export function useWebSocket(wsUrl: string) {
  const [metrics, setMetrics] = useState<TrafficMetrics>(INITIAL_METRICS);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (!wsUrl) return;
    
    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
      };

      ws.onmessage = (event) => {
        try {
          const data: TrafficMetrics = JSON.parse(event.data);
          setMetrics(data);
        } catch (err) {
          console.error("Failed to parse WebSocket JSON payload", err);
        }
      };

      ws.onerror = (evt) => {
        setError("WebSocket connection encountered an error.");
      };

      ws.onclose = () => {
        setIsConnected(false);
        // Exponential reconnect every 2.5 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 2500);
      };
    } catch (err) {
      setError("Unable to establish WebSocket connection.");
      reconnectTimeoutRef.current = setTimeout(connect, 3000);
    }
  }, [wsUrl]);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  return { metrics, isConnected, error };
}
```

---

### Task 8: Interactive HTML5 Canvas Polygon ROI Overlay & Spatial Normalization

**Files:**
- Create: `frontend/src/components/CanvasROI.tsx`

**Interfaces:**
- Consumes: `ROICoordinates` from `@/types`
- Produces: `CanvasROI` component with props `{ mode: 'inbound' | 'outbound' | 'none', roi: ROICoordinates, onSaveROI: (roi: ROICoordinates) => void }`

- [ ] **Step 1: Implement frontend/src/components/CanvasROI.tsx**

Create `frontend/src/components/CanvasROI.tsx`:
```tsx
'use client';

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { ROICoordinates } from '@/types';

interface CanvasROIProps {
  mode: 'inbound' | 'outbound' | 'view';
  roi: ROICoordinates;
  onUpdateROI: (updatedROI: ROICoordinates) => void;
}

export default function CanvasROI({ mode, roi, onUpdateROI }: CanvasROIProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [activePoints, setActivePoints] = useState<[number, number][]>([]);

  // Redraw canvas whenever ROI or active points change
  const renderCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const w = canvas.width;
    const h = canvas.height;

    // Draw Inbound saved polygon (Green/Cyan)
    if (roi.inbound && roi.inbound.length > 2) {
      ctx.beginPath();
      ctx.moveTo(roi.inbound[0][0] * w, roi.inbound[0][1] * h);
      for (let i = 1; i < roi.inbound.length; i++) {
        ctx.lineTo(roi.inbound[i][0] * w, roi.inbound[i][1] * h);
      }
      ctx.closePath();
      ctx.strokeStyle = '#10b981';
      ctx.lineWidth = 2;
      ctx.fillStyle = 'rgba(16, 185, 129, 0.15)';
      ctx.fill();
      ctx.stroke();
    }

    // Draw Outbound saved polygon (Amber/Rose)
    if (roi.outbound && roi.outbound.length > 2) {
      ctx.beginPath();
      ctx.moveTo(roi.outbound[0][0] * w, roi.outbound[0][1] * h);
      for (let i = 1; i < roi.outbound.length; i++) {
        ctx.lineTo(roi.outbound[i][0] * w, roi.outbound[i][1] * h);
      }
      ctx.closePath();
      ctx.strokeStyle = '#f59e0b';
      ctx.lineWidth = 2;
      ctx.fillStyle = 'rgba(245, 158, 11, 0.15)';
      ctx.fill();
      ctx.stroke();
    }

    // Draw currently drawn active points
    if (activePoints.length > 0) {
      ctx.beginPath();
      ctx.moveTo(activePoints[0][0] * w, activePoints[0][1] * h);
      for (let i = 1; i < activePoints.length; i++) {
        ctx.lineTo(activePoints[i][0] * w, activePoints[i][1] * h);
      }
      ctx.strokeStyle = mode === 'inbound' ? '#34d399' : '#fbbf24';
      ctx.lineWidth = 2;
      ctx.setLineDash([4, 4]);
      ctx.stroke();
      ctx.setLineDash([]);

      // Draw vertices
      for (const pt of activePoints) {
        ctx.beginPath();
        ctx.arc(pt[0] * w, pt[1] * h, 5, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.fill();
        ctx.strokeStyle = '#000000';
        ctx.stroke();
      }
    }
  }, [roi, activePoints, mode]);

  useEffect(() => {
    const handleResize = () => {
      const canvas = canvasRef.current;
      if (canvas && canvas.parentElement) {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
        renderCanvas();
      }
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [renderCanvas]);

  useEffect(() => {
    renderCanvas();
  }, [renderCanvas]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (mode === 'view') return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;

    // Normalizing to 0.0 - 1.0 range
    const normalizedPoint: [number, number] = [
      Math.max(0, Math.min(1, Number(x.toFixed(3)))),
      Math.max(0, Math.min(1, Number(y.toFixed(3)))),
    ];

    const newPoints = [...activePoints, normalizedPoint];
    setActivePoints(newPoints);
  };

  const handleDoubleClick = () => {
    if (mode === 'view' || activePoints.length < 3) return;
    const updated = { ...roi };
    if (mode === 'inbound') {
      updated.inbound = activePoints;
    } else if (mode === 'outbound') {
      updated.outbound = activePoints;
    }
    onUpdateROI(updated);
    setActivePoints([]);
  };

  return (
    <canvas
      ref={canvasRef}
      onClick={handleCanvasClick}
      onDoubleClick={handleDoubleClick}
      className={`absolute inset-0 z-10 w-full h-full ${
        mode !== 'view' ? 'cursor-crosshair' : 'pointer-events-none'
      }`}
    />
  );
}
```

---

### Task 9: Video Stream Player Component & MJPEG Live Feed HUD

**Files:**
- Create: `frontend/src/components/VideoPlayer.tsx`

**Interfaces:**
- Consumes: Stream URL from props, `CanvasROI` component
- Produces: `VideoPlayer` component with HUD overlay (FPS, Connection, ROI editor toolbar)

- [ ] **Step 1: Implement frontend/src/components/VideoPlayer.tsx**

Create `frontend/src/components/VideoPlayer.tsx`:
```tsx
'use client';

import React, { useState } from 'react';
import { Camera, Radio, CheckCircle, RefreshCw, Layers } from 'lucide-react';
import CanvasROI from './CanvasROI';
import { ROICoordinates } from '@/types';

interface VideoPlayerProps {
  streamUrl: string;
  fps: number;
  isConnected: boolean;
  roi: ROICoordinates;
  onSaveROI: (roi: ROICoordinates) => void;
  onResetCounters: () => void;
}

export default function VideoPlayer({
  streamUrl,
  fps,
  isConnected,
  roi,
  onSaveROI,
  onResetCounters,
}: VideoPlayerProps) {
  const [editMode, setEditMode] = useState<'inbound' | 'outbound' | 'view'>('view');

  return (
    <div className="glass-panel rounded-2xl overflow-hidden flex flex-col border border-slate-800 shadow-2xl">
      {/* Stream Header */}
      <div className="px-5 py-3.5 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Camera className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
              ATCS Surakarta Balai Kota (FLV)
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-950 text-emerald-400 border border-emerald-800/60">
                <Radio className="w-3 h-3 mr-1 animate-pulse" /> LIVE
              </span>
            </h2>
            <p className="text-xs text-slate-400">YOLOv11n + ByteTrack Real-Time Inference</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="text-right">
            <div className="text-xs text-slate-400">Stream Rate</div>
            <div className="text-xs font-mono font-bold text-slate-200">{fps.toFixed(1)} FPS</div>
          </div>
          <button
            onClick={onResetCounters}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg transition-colors flex items-center gap-1.5 border border-slate-700"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Reset Counters
          </button>
        </div>
      </div>

      {/* Video Stream Container with Canvas Overlay */}
      <div className="relative aspect-video w-full bg-black flex items-center justify-center overflow-hidden">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={streamUrl}
          alt="Live Traffic Video Stream"
          className="w-full h-full object-cover select-none"
        />

        <CanvasROI
          mode={editMode}
          roi={roi}
          onUpdateROI={onSaveROI}
        />
      </div>

      {/* ROI Toolbar Controls */}
      <div className="px-5 py-3 bg-slate-900/90 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <span className="text-slate-400 font-medium flex items-center gap-1.5">
            <Layers className="w-4 h-4" /> ROI Mode:
          </span>
          <button
            onClick={() => setEditMode('view')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
              editMode === 'view'
                ? 'bg-slate-700 text-white'
                : 'bg-slate-800/60 text-slate-400 hover:text-slate-200'
            }`}
          >
            View Only
          </button>
          <button
            onClick={() => setEditMode('inbound')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-colors border ${
              editMode === 'inbound'
                ? 'bg-emerald-600 text-white border-emerald-500'
                : 'bg-emerald-950/40 text-emerald-400 border-emerald-800/40 hover:bg-emerald-900/60'
            }`}
          >
            Draw Inbound (Green)
          </button>
          <button
            onClick={() => setEditMode('outbound')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-colors border ${
              editMode === 'outbound'
                ? 'bg-amber-600 text-white border-amber-500'
                : 'bg-amber-950/40 text-amber-400 border-amber-800/40 hover:bg-amber-900/60'
            }`}
          >
            Draw Outbound (Amber)
          </button>
        </div>

        {editMode !== 'view' && (
          <p className="text-slate-400 italic">
            Klik untuk membuat titik poligon, <b>Double Click</b> untuk menyimpan poligon.
          </p>
        )}
      </div>
    </div>
  );
}
```

---

### Task 10: Traffic Metrics Cards, PKJI Vehicle Breakdown, Real-Time Chart & Activity Feed

**Files:**
- Create: `frontend/src/components/MetricsCard.tsx`
- Create: `frontend/src/components/VehicleBreakdown.tsx`
- Create: `frontend/src/components/TrafficChart.tsx`
- Create: `frontend/src/components/LiveFeed.tsx`

**Interfaces:**
- Consumes: `DirectionMetrics`, `VehicleBreakdown`, `VehicleEvent` from `@/types`
- Produces: Polished visual components for traffic analytics and real-time activity log

- [ ] **Step 1: Implement MetricsCard.tsx**

Create `frontend/src/components/MetricsCard.tsx`:
```tsx
'use client';

import React from 'react';
import { ArrowDownLeft, ArrowUpRight, Activity } from 'lucide-react';
import { DirectionMetrics } from '@/types';

interface MetricsCardProps {
  title: string;
  direction: 'inbound' | 'outbound';
  data: DirectionMetrics;
}

export default function MetricsCard({ title, direction, data }: MetricsCardProps) {
  const isInbound = direction === 'inbound';
  
  const getDensityBadge = (level: string) => {
    switch (level) {
      case 'LANCAR':
        return 'bg-emerald-950 text-emerald-400 border-emerald-800';
      case 'SEDANG':
        return 'bg-yellow-950 text-yellow-400 border-yellow-800';
      case 'PADAT':
        return 'bg-orange-950 text-orange-400 border-orange-800';
      case 'MACET':
        return 'bg-rose-950 text-rose-400 border-rose-800';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col justify-between space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div
            className={`p-2 rounded-xl ${
              isInbound
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
            }`}
          >
            {isInbound ? <ArrowDownLeft className="w-5 h-5" /> : <ArrowUpRight className="w-5 h-5" />}
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-200">{title}</h3>
            <span className="text-xs text-slate-400">Arah {isInbound ? 'Masuk' : 'Keluar'}</span>
          </div>
        </div>
        <span
          className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${getDensityBadge(
            data.density_level
          )}`}
        >
          {data.density_level}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 pt-2 border-t border-slate-800/80">
        <div>
          <div className="text-xs text-slate-400">Total Akumulasi Beban</div>
          <div className="text-2xl font-bold font-mono text-slate-100">
            {data.total_smp.toFixed(1)}{' '}
            <span className="text-xs font-normal text-slate-400">SMP</span>
          </div>
        </div>
        <div>
          <div className="text-xs text-slate-400">Laju Kepadatan</div>
          <div className="text-2xl font-bold font-mono text-slate-100">
            {data.smp_per_minute.toFixed(1)}{' '}
            <span className="text-xs font-normal text-slate-400">SMP/mnt</span>
          </div>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Implement VehicleBreakdown.tsx**

Create `frontend/src/components/VehicleBreakdown.tsx`:
```tsx
'use client';

import React from 'react';
import { Bike, Car, Bus, Truck } from 'lucide-react';
import { VehicleBreakdown as BreakdownType } from '@/types';

interface VehicleBreakdownProps {
  inbound: BreakdownType;
  outbound: BreakdownType;
}

export default function VehicleBreakdown({ inbound, outbound }: VehicleBreakdownProps) {
  const items = [
    {
      label: 'Sepeda Motor',
      icon: Bike,
      inboundVal: inbound.motorcycle,
      outboundVal: outbound.motorcycle,
      smp: '0.5 SMP',
    },
    {
      label: 'Mobil Penumpang',
      icon: Car,
      inboundVal: inbound.car,
      outboundVal: outbound.car,
      smp: '1.0 SMP',
    },
    {
      label: 'Bus',
      icon: Bus,
      inboundVal: inbound.bus,
      outboundVal: outbound.bus,
      smp: '1.3 SMP',
    },
    {
      label: 'Truk / Angkutan',
      icon: Truck,
      inboundVal: inbound.truck,
      outboundVal: outbound.truck,
      smp: '1.3 SMP',
    },
  ];

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-200">Distribusi Kendaraan (PKJI)</h3>
        <span className="text-xs text-slate-400">Standar Ekivalen Mobil Penumpang</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {items.map((item) => {
          const Icon = item.icon;
          return (
            <div
              key={item.label}
              className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-2"
            >
              <div className="flex items-center justify-between text-slate-400">
                <Icon className="w-4 h-4 text-slate-300" />
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                  {item.smp}
                </span>
              </div>
              <div className="text-xs font-medium text-slate-300">{item.label}</div>
              <div className="flex items-center justify-between pt-1 border-t border-slate-800 text-xs font-mono">
                <span className="text-emerald-400 font-bold">{item.inboundVal} In</span>
                <span className="text-amber-400 font-bold">{item.outboundVal} Out</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Implement TrafficChart.tsx**

Create `frontend/src/components/TrafficChart.tsx`:
```tsx
'use client';

import React, { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

interface TrafficChartProps {
  inboundSMP: number;
  outboundSMP: number;
}

interface ChartPoint {
  time: string;
  inbound: number;
  outbound: number;
}

export default function TrafficChart({ inboundSMP, outboundSMP }: TrafficChartProps) {
  const [dataPoints, setDataPoints] = useState<ChartPoint[]>([]);

  useEffect(() => {
    const now = new Date().toLocaleTimeString('id-ID', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });

    setDataPoints((prev) => {
      const updated = [...prev, { time: now, inbound: inboundSMP, outbound: outboundSMP }];
      if (updated.length > 20) updated.shift();
      return updated;
    });
  }, [inboundSMP, outboundSMP]);

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">Tren Beban Lalu Lintas (Real-Time)</h3>
          <p className="text-xs text-slate-400">Fluktuasi Laju SMP / Menit</p>
        </div>
        <div className="flex items-center space-x-4 text-xs">
          <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Inbound
          </span>
          <span className="flex items-center gap-1.5 text-amber-400 font-medium">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> Outbound
          </span>
        </div>
      </div>

      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={dataPoints}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="time" stroke="#64748b" fontSize={10} tickLine={false} />
            <YAxis stroke="#64748b" fontSize={10} tickLine={false} domain={[0, 'auto']} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#334155',
                borderRadius: '8px',
                fontSize: '12px',
              }}
            />
            <Line
              type="monotone"
              dataKey="inbound"
              stroke="#10b981"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="outbound"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Implement LiveFeed.tsx**

Create `frontend/src/components/LiveFeed.tsx`:
```tsx
'use client';

import React from 'react';
import { Clock, ArrowDownLeft, ArrowUpRight } from 'lucide-react';
import { VehicleEvent } from '@/types';

interface LiveFeedProps {
  events: VehicleEvent[];
}

export default function LiveFeed({ events }: LiveFeedProps) {
  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-200">Aktivitas Kendaraan Terdeteksi</h3>
        <span className="text-xs text-slate-400">15 Event Terakhir</span>
      </div>

      <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
        {events.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-500">
            Menunggu deteksi kendaraan pertama...
          </div>
        ) : (
          events.map((evt) => {
            const isInbound = evt.direction === 'inbound';
            return (
              <div
                key={evt.id}
                className="p-2.5 rounded-xl bg-slate-900/70 border border-slate-800/80 flex items-center justify-between text-xs"
              >
                <div className="flex items-center space-x-2.5">
                  <span
                    className={`p-1 rounded-md ${
                      isInbound
                        ? 'bg-emerald-500/10 text-emerald-400'
                        : 'bg-amber-500/10 text-amber-400'
                    }`}
                  >
                    {isInbound ? <ArrowDownLeft className="w-3.5 h-3.5" /> : <ArrowUpRight className="w-3.5 h-3.5" />}
                  </span>
                  <div>
                    <span className="font-semibold capitalize text-slate-200">
                      {evt.vehicle_type}
                    </span>
                    <span className="text-slate-400 ml-1.5">({evt.smp} SMP)</span>
                  </div>
                </div>

                <div className="flex items-center space-x-1.5 text-slate-400 font-mono text-[11px]">
                  <Clock className="w-3 h-3" />
                  <span>{evt.timestamp}</span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
```

---

### Task 11: Main Dashboard Assembly & Full System Integration

**Files:**
- Create: `frontend/src/app/page.tsx`

**Interfaces:**
- Consumes: All components (`VideoPlayer`, `MetricsCard`, `VehicleBreakdown`, `TrafficChart`, `LiveFeed`, `useWebSocket`)
- Produces: Complete Next.js dashboard

- [ ] **Step 1: Implement frontend/src/app/page.tsx**

Create `frontend/src/app/page.tsx`:
```tsx
'use client';

import React, { useState, useEffect } from 'react';
import { Cpu, Wifi, WifiOff } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import VideoPlayer from '@/components/VideoPlayer';
import MetricsCard from '@/components/MetricsCard';
import VehicleBreakdown from '@/components/VehicleBreakdown';
import TrafficChart from '@/components/TrafficChart';
import LiveFeed from '@/components/LiveFeed';
import { ROICoordinates } from '@/types';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/metrics';

export default function Dashboard() {
  const { metrics, isConnected } = useWebSocket(WS_URL);
  const [roi, setROI] = useState<ROICoordinates>({
    inbound: [],
    outbound: [],
  });

  // Fetch initial ROIs from Backend
  useEffect(() => {
    fetch(`${BACKEND_URL}/api/v1/roi`)
      .then((res) => res.json())
      .then((data) => setROI(data))
      .catch((err) => console.error('Failed to load initial ROI:', err));
  }, []);

  const handleSaveROI = async (updatedROI: ROICoordinates) => {
    setROI(updatedROI);
    try {
      await fetch(`${BACKEND_URL}/api/v1/roi`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedROI),
      });
    } catch (err) {
      console.error('Failed to update ROI:', err);
    }
  };

  const handleResetCounters = async () => {
    try {
      await fetch(`${BACKEND_URL}/api/v1/reset-counter`, { method: 'POST' });
    } catch (err) {
      console.error('Failed to reset counters:', err);
    }
  };

  return (
    <main className="min-h-screen p-4 sm:p-6 lg:p-8 space-y-6 max-w-[1600px] mx-auto">
      {/* Header Bar */}
      <header className="glass-panel px-6 py-4 rounded-2xl border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-100 tracking-tight">
              Smart Traffic Monitoring (SMP / PCU)
            </h1>
            <p className="text-xs text-slate-400">
              Fondasi Sistem Kontrol Lampu Lalu Lintas Adaptif 4-Arah Berbasis Computer Vision
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
            {isConnected ? (
              <>
                <Wifi className="w-4 h-4 text-emerald-400" />
                <span className="text-emerald-400 font-medium">WS Connected</span>
              </>
            ) : (
              <>
                <WifiOff className="w-4 h-4 text-rose-400" />
                <span className="text-rose-400 font-medium">WS Disconnected</span>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Main Grid: Left Video Stream & Canvas, Right Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Live Stream Player & Interactive Canvas */}
        <div className="lg:col-span-7 space-y-6">
          <VideoPlayer
            streamUrl={`${BACKEND_URL}/api/v1/stream`}
            fps={metrics.fps}
            isConnected={isConnected}
            roi={roi}
            onSaveROI={handleSaveROI}
            onResetCounters={handleResetCounters}
          />

          <VehicleBreakdown
            inbound={metrics.inbound.breakdown}
            outbound={metrics.outbound.breakdown}
          />
        </div>

        {/* Right Column: Inbound/Outbound Cards, Chart, Activity Log */}
        <div className="lg:col-span-5 space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <MetricsCard
              title="Inbound Traffic"
              direction="inbound"
              data={metrics.inbound}
            />
            <MetricsCard
              title="Outbound Traffic"
              direction="outbound"
              data={metrics.outbound}
            />
          </div>

          <TrafficChart
            inboundSMP={metrics.inbound.smp_per_minute}
            outboundSMP={metrics.outbound.smp_per_minute}
          />

          <LiveFeed events={metrics.recent_events} />
        </div>
      </div>
    </main>
  );
}
```

---

### Task 12: End-to-End Verification, Documentation & Production Readiness

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write comprehensive project documentation in README.md**

Create `README.md`:
```markdown
# Smart Traffic Monitoring (SMP / PCU)

Sistem Monitoring dan Penghitung Beban Lalu Lintas Real-Time Berbasis Computer Vision untuk Pengukuran Beban Jalan Dua Arah (PKJI / SMP) sebagai Fondasi Kontrol Lampu Lalu Lintas Adaptif 4-Arah.

## Pages / Routes

| Route | Page | Description |
|---|---|---|
| `/` | Dashboard Utama | Live MJPEG player, interactive polygon ROI canvas, real-time charts & vehicle breakdown |
| `/api/v1/stream` | Stream Endpoint | Real-time multipart MJPEG annotated stream |
| `/api/v1/roi` | ROI Endpoint | GET/POST koordinat poligon ter-normalisasi ($0.0 \dots 1.0$) |
| `/api/v1/health` | Health Check | Status live stream and inference FPS |
| `/ws/metrics` | WebSocket Broadcaster | JSON stream metrik lalu lintas real-time tiap 1 detik |

## Project Structure

```text
Smart-Monitoring/
├── backend/
│   ├── app/
│   │   ├── api/          # REST & WebSocket routes
│   │   ├── core/         # Config, state management, logging
│   │   ├── services/     # Stream reader, detector, ROI tracker, MJPEG
│   │   └── main.py       # FastAPI application entrypoint
│   ├── sample_data/      # Fallback synthetic traffic clip generator
│   └── Dockerfile        # Hugging Face Spaces CPU optimized image
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js App Router root layout & dashboard
│   │   ├── components/   # Interactive Canvas, VideoPlayer, Charts, MetricsCard
│   │   ├── hooks/        # WebSocket auto-reconnect hook
│   │   └── types/        # TypeScript contracts
└── README.md
```

## Tech Stack

- **FastAPI** — High-performance asynchronous backend server
- **Ultralytics YOLOv11** — Lightweight Nano object detection model for CPU inference
- **ByteTrack** — Multi-object tracking with persistent track IDs
- **OpenCV** — Frame processing and native C++ pointPolygonTest calculations
- **Next.js 14** — Modern React App Router dashboard
- **Tailwind CSS** — Glassmorphism dark-theme styling
- **Recharts** — Real-time reactive traffic density graphs

## Scripts

| Script | Command | Description |
|---|---|---|
| Backend Dev | `cd backend && uvicorn app.main:app --reload --port 8000` | Start FastAPI backend |
| Backend Tests | `pytest backend/tests -v` | Run full test suite |
| Frontend Dev | `cd frontend && npm run dev` | Start Next.js dashboard on port 3000 |
| Frontend Build | `cd frontend && npm run build` | Build Next.js production bundle |

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
```

- [ ] **Step 2: Run all backend tests to verify 100% test pass rate**

Run: `pytest backend/tests -v`
Expected: PASS
