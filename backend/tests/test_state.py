import pytest
import numpy as np
from app.core.state import GlobalStateManager

def test_global_state_frame_and_metrics():
    state = GlobalStateManager()
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    dummy_jpeg = b"\xff\xd8\xff\xe0dummyjpeg"
    
    state.set_raw_frame(dummy_frame)
    retrieved_raw = state.get_raw_frame()
    assert retrieved_raw is not None
    assert retrieved_raw.shape == (480, 640, 3)
    
    state.set_annotated_frame(dummy_frame, encoded_jpeg=dummy_jpeg)
    retrieved_annotated = state.get_annotated_frame()
    assert retrieved_annotated is not None
    assert retrieved_annotated.shape == (480, 640, 3)
    assert state.get_encoded_jpeg() == dummy_jpeg

def test_global_state_roi_and_reset():
    state = GlobalStateManager()
    polygon = [(0.1, 0.1), (0.5, 0.1), (0.5, 0.8), (0.1, 0.8)]
    state.set_roi("inbound", polygon)
    assert state.get_roi("inbound") == polygon
    
    state.update_metrics({"inbound": {"total_smp": 10.5}})
    assert state.get_metrics()["inbound"]["total_smp"] == 10.5
    
    state.reset_counters()
    assert state.get_metrics()["inbound"]["total_smp"] == 0.0
