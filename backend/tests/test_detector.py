import pytest
import numpy as np
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
    assert np.any(annotated > 0)

def test_detector_dry_run_detect_and_track():
    detector = TrafficDetector(model_name="yolo11n.pt", dry_run=True)
    frame = np.zeros((360, 640, 3), dtype=np.uint8)
    
    inbound_poly = [(0.1, 0.1), (0.4, 0.1), (0.4, 0.9), (0.1, 0.9)]
    outbound_poly = [(0.6, 0.1), (0.9, 0.1), (0.9, 0.9), (0.6, 0.9)]
    
    annotated, metrics = detector.detect_and_track(frame, 1, inbound_poly, outbound_poly)
    assert annotated.shape == (360, 640, 3)
    assert "inbound" in metrics
    assert "outbound" in metrics
    assert "recent_events" in metrics
