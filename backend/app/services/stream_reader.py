import os
import threading
import time
from typing import Optional
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
        self.cap: Optional[cv2.VideoCapture] = None

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

    def _get_capture_source(self) -> cv2.VideoCapture:
        logger.info(f"Connecting to primary stream: {settings.VIDEO_STREAM_URL}")
        cap = cv2.VideoCapture(settings.VIDEO_STREAM_URL)
        if not cap.isOpened():
            logger.warning(f"Primary stream unreachable. Falling back to: {settings.FALLBACK_VIDEO_PATH}")
            # Check relative fallback path
            fallback = settings.FALLBACK_VIDEO_PATH
            if not os.path.exists(fallback):
                # Try relative to backend dir
                fallback = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), fallback)
            cap = cv2.VideoCapture(fallback)
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
                    logger.info("End of stream/file reached. Reopening stream/looping fallback...")
                    self.cap.release()
                    time.sleep(0.5)
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

            # Single-pass JPEG encoding optimization (Shared for all connected clients)
            ret_enc, buffer = cv2.imencode('.jpg', annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), settings.JPEG_QUALITY])
            encoded_bytes = buffer.tobytes() if ret_enc else None

            global_state.set_annotated_frame(annotated_frame, encoded_jpeg=encoded_bytes)
            global_state.update_metrics(metrics)

            # CPU Throttling to maintain target FPS
            elapsed = time.time() - loop_start
            sleep_duration = max(0.001, target_frame_time - elapsed)
            time.sleep(sleep_duration)

        if self.cap:
            self.cap.release()
