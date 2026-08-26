import collections
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import cv2
import numpy as np
from app.core.logging import logger

# PKJI (Pedoman Kapasitas Jalan Indonesia) SMP Equivalents
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
        
        # Cumulative breakdown counts
        self.inbound_counts: Dict[str, int] = {"motorcycle": 0, "car": 0, "bus": 0, "truck": 0}
        self.outbound_counts: Dict[str, int] = {"motorcycle": 0, "car": 0, "bus": 0, "truck": 0}
        
        # Cumulative total SMP
        self.inbound_total_smp: float = 0.0
        self.outbound_total_smp: float = 0.0
        
        # Rolling Window (60-second) for SMP/minute: deque of (timestamp, direction, smp_value)
        self.rolling_events_deque: collections.deque = collections.deque()
        
        # Live activity feed (last 15 events)
        self.recent_events: List[Dict[str, Any]] = []

    def set_polygon(self, direction: str, polygon: List[Tuple[float, float]]) -> None:
        if direction.lower() == "inbound":
            self.inbound_polygon = polygon
        elif direction.lower() == "outbound":
            self.outbound_polygon = polygon

    def calculate_bottom_center(self, bbox: Tuple[int, int, int, int]) -> Tuple[int, int]:
        """Calculates vehicle ground-contact wheel reference point ((x1 + x2) / 2, y2)."""
        x1, y1, x2, y2 = bbox
        return int((x1 + x2) / 2), int(y2)

    def denormalize_polygon(self, polygon: List[Tuple[float, float]], frame_w: int, frame_h: int) -> np.ndarray:
        points = [[int(pt[0] * frame_w), int(pt[1] * frame_h)] for pt in polygon]
        return np.array(points, dtype=np.int32).reshape((-1, 1, 2))

    def is_point_in_polygon(self, point: Tuple[int, int], polygon_contour: np.ndarray) -> bool:
        if len(polygon_contour) < 3:
            return False
        # cv2.pointPolygonTest returns >= 0 if point is inside or on boundary
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
        now_ts = time.time()
        
        # Check Inbound Polygon
        if self.inbound_polygon and not v_state.counted_inbound:
            inbound_contour = self.denormalize_polygon(self.inbound_polygon, frame_w, frame_h)
            if self.is_point_in_polygon(ground_point, inbound_contour):
                v_state.counted_inbound = True
                self.inbound_counts[normalized_class] += 1
                self.inbound_total_smp += smp_val
                self.rolling_events_deque.append((now_ts, "inbound", smp_val))
                
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

        # Check Outbound Polygon
        if self.outbound_polygon and not v_state.counted_outbound:
            outbound_contour = self.denormalize_polygon(self.outbound_polygon, frame_w, frame_h)
            if self.is_point_in_polygon(ground_point, outbound_contour):
                v_state.counted_outbound = True
                self.outbound_counts[normalized_class] += 1
                self.outbound_total_smp += smp_val
                self.rolling_events_deque.append((now_ts, "outbound", smp_val))
                
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
        cutoff_time = now - 60.0
        
        # Evict events older than 60 seconds from the left of the deque
        while self.rolling_events_deque and self.rolling_events_deque[0][0] < cutoff_time:
            self.rolling_events_deque.popleft()
            
        inbound_last_min_smp = sum(item[2] for item in self.rolling_events_deque if item[1] == "inbound")
        outbound_last_min_smp = sum(item[2] for item in self.rolling_events_deque if item[1] == "outbound")
        
        return {
            "timestamp": now,
            "inbound": {
                "total_smp": round(self.inbound_total_smp, 1),
                "smp_per_minute": round(inbound_last_min_smp, 1),
                "density_level": self._calculate_density_level(inbound_last_min_smp),
                "breakdown": dict(self.inbound_counts)
            },
            "outbound": {
                "total_smp": round(self.outbound_total_smp, 1),
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
        self.inbound_total_smp = 0.0
        self.outbound_total_smp = 0.0
        self.rolling_events_deque.clear()
        self.recent_events.clear()
