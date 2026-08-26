import time
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
    bbox = (100, 50, 200, 150)
    bc_x, bc_y = tracker.calculate_bottom_center(bbox)
    assert bc_x == 150  # (100 + 200) / 2
    assert bc_y == 150  # y2

def test_spatial_polygon_and_counting():
    tracker = SpatialROITracker(ttl_frames=60)
    frame_w, frame_h = 1000, 1000
    
    polygon = [(0.1, 0.1), (0.4, 0.1), (0.4, 0.4), (0.1, 0.4)]
    tracker.set_polygon("inbound", polygon)
    
    # Vehicle 1 inside inbound ROI at frame 1
    bbox_inside = (150, 150, 250, 250)
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
    assert summary["inbound"]["smp_per_minute"] == 1.0
    assert summary["inbound"]["breakdown"]["car"] == 1

def test_rolling_window_deque_expiration():
    tracker = SpatialROITracker()
    # Inject an event with timestamp from 70 seconds ago
    old_time = time.time() - 70.0
    tracker.rolling_events_deque.append((old_time, "inbound", 1.0))
    # Inject a recent event
    tracker.rolling_events_deque.append((time.time(), "inbound", 0.5))
    
    summary = tracker.get_metrics_summary()
    # Old event (1.0 SMP) should be evicted; only recent (0.5 SMP) remains in rolling window
    assert summary["inbound"]["smp_per_minute"] == 0.5
    assert len(tracker.rolling_events_deque) == 1

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
