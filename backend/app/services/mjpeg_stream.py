import time
from typing import Generator
import cv2
import numpy as np
from app.core.state import global_state

def generate_mjpeg_frames() -> Generator[bytes, None, None]:
    """
    Generates continuous multipart/x-mixed-replace JPEG frames from the global state.
    Uses pre-encoded JPEG bytes from the background worker to avoid redundant per-client CPU re-encoding.
    """
    while True:
        jpeg_bytes = global_state.get_encoded_jpeg()
        
        if jpeg_bytes is None:
            # Generate fallback standby frame
            standby_frame = np.zeros((360, 640, 3), dtype=np.uint8)
            cv2.putText(
                standby_frame,
                "CONNECTING TO CCTV STREAM...",
                (140, 180),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 220, 220),
                2
            )
            ret, buf = cv2.imencode('.jpg', standby_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 65])
            if ret:
                jpeg_bytes = buf.tobytes()

        if jpeg_bytes is not None:
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + jpeg_bytes + b'\r\n'
            )
        
        time.sleep(0.06) # Stream ~15 FPS to clients
