import json
import os
import threading
import time
from typing import Optional, Dict, Any, List, Tuple
import numpy as np
from app.core.config import settings
from app.core.logging import logger

class GlobalStateManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._raw_frame: Optional[np.ndarray] = None
        self._annotated_frame: Optional[np.ndarray] = None
        self._encoded_jpeg_bytes: Optional[bytes] = None
        self._is_stream_active: bool = False
        self._current_fps: float = 0.0
        
        # Load ROI from persistent JSON file or fallback
        self._roi_inbound: List[Tuple[float, float]] = []
        self._roi_outbound: List[Tuple[float, float]] = []
        self._load_persistent_roi()
        
        self._metrics: Dict[str, Any] = self._initial_metrics()

    def _load_persistent_roi(self) -> None:
        roi_file = settings.ROI_PERSISTENCE_PATH
        if os.path.exists(roi_file):
            try:
                with open(roi_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._roi_inbound = [tuple(p) for p in data.get("inbound", [])]
                    self._roi_outbound = [tuple(p) for p in data.get("outbound", [])]
                    logger.info("Successfully loaded persistent ROI from default_roi.json")
                    return
            except Exception as e:
                logger.error(f"Error loading {roi_file}: {e}")

        # Fallback default polygons
        self._roi_inbound = [
            (0.05, 0.40), (0.45, 0.40), (0.45, 0.95), (0.05, 0.95)
        ]
        self._roi_outbound = [
            (0.55, 0.40), (0.95, 0.40), (0.95, 0.95), (0.55, 0.95)
        ]

    def _save_persistent_roi(self) -> None:
        try:
            data = {
                "inbound": [list(p) for p in self._roi_inbound],
                "outbound": [list(p) for p in self._roi_outbound]
            }
            with open(settings.ROI_PERSISTENCE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving ROI to {settings.ROI_PERSISTENCE_PATH}: {e}")

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

    def set_annotated_frame(self, frame: np.ndarray, encoded_jpeg: Optional[bytes] = None) -> None:
        with self._lock:
            self._annotated_frame = frame
            if encoded_jpeg is not None:
                self._encoded_jpeg_bytes = encoded_jpeg

    def get_annotated_frame(self) -> Optional[np.ndarray]:
        with self._lock:
            return self._annotated_frame.copy() if self._annotated_frame is not None else None

    def get_encoded_jpeg(self) -> Optional[bytes]:
        with self._lock:
            return self._encoded_jpeg_bytes

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
            self._save_persistent_roi()

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
