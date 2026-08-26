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
        
        # Draw Inbound Polygon (Emerald/Cyan: BGR (220, 200, 0))
        if inbound_poly and len(inbound_poly) >= 3:
            in_pts = np.array([[int(p[0]*w), int(p[1]*h)] for p in inbound_poly], np.int32).reshape((-1, 1, 2))
            cv2.polylines(annotated, [in_pts], isClosed=True, color=(220, 200, 0), thickness=2)
            cv2.putText(annotated, "INBOUND ROI", (in_pts[0][0][0], max(20, in_pts[0][0][1] - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 200, 0), 2)
        
        # Draw Outbound Polygon (Amber/Rose: BGR (0, 140, 255))
        if outbound_poly and len(outbound_poly) >= 3:
            out_pts = np.array([[int(p[0]*w), int(p[1]*h)] for p in outbound_poly], np.int32).reshape((-1, 1, 2))
            cv2.polylines(annotated, [out_pts], isClosed=True, color=(0, 140, 255), thickness=2)
            cv2.putText(annotated, "OUTBOUND ROI", (out_pts[0][0][0], max(20, out_pts[0][0][1] - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 140, 255), 2)

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
