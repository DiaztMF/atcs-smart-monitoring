import pytest
import numpy as np
from app.core.state import global_state
from app.services.mjpeg_stream import generate_mjpeg_frames

def test_mjpeg_generator_yields_valid_frames():
    dummy_jpeg = b"\xff\xd8\xff\xe0dummy_pre_encoded_bytes"
    dummy_frame = np.full((360, 640, 3), 120, dtype=np.uint8)
    global_state.set_annotated_frame(dummy_frame, encoded_jpeg=dummy_jpeg)
    
    gen = generate_mjpeg_frames()
    first_chunk = next(gen)
    assert b'--frame\r\n' in first_chunk
    assert b'Content-Type: image/jpeg\r\n\r\n' in first_chunk
    assert dummy_jpeg in first_chunk
