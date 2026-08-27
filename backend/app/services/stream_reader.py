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
        self.synthetic_frame_counter: int = 0
        self._reconnect_requested: bool = False

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
            self.cap = None
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        logger.info("Stream reader worker stopped.")

    def switch_stream(self, new_url: str, stream_name: str) -> None:
        """Dynamically switches stream source on the fly without restarting server."""
        logger.info(f"Switching stream source to: {stream_name} ({new_url})")
        global_state.set_active_stream(new_url, stream_name)
        self._reconnect_requested = True

    def _get_capture_source(self) -> Optional[cv2.VideoCapture]:
        active_stream = global_state.get_active_stream()
        stream_url = active_stream["url"]

        if stream_url.startswith("synthetic://"):
            logger.info("Synthetic traffic simulation selected as active stream.")
            return None

        try:
            logger.info(f"Connecting to stream: {stream_url}")
            # Pass FFmpeg options for live HTTPS FLV streams:
            # - tls_verify=0  : skip TLS certificate validation (self-signed certs on ATCS servers)
            # - timeout       : per-read timeout in microseconds (15s)
            # - reconnect_*   : auto-reconnect on dropped streams
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
                "rtsp_transport;tcp|"
                "tls_verify;0|"
                "timeout;15000000|"
                "reconnect;1|"
                "reconnect_streamed;1|"
                "reconnect_delay_max;5"
            )
            cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
            if cap.isOpened():
                return cap
        except Exception as e:
            logger.warning(f"Error opening stream {stream_url}: {e}")
        # Fallback local video paths if remote fails
        candidates = [
            settings.FALLBACK_VIDEO_PATH,
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "sample_data", "synthetic_traffic.mp4"),
            "sample_data/synthetic_traffic.mp4",
            "backend/sample_data/synthetic_traffic.mp4"
        ]
        
        for cand in candidates:
            if os.path.exists(cand):
                try:
                    logger.warning(f"Using fallback video file: {cand}")
                    cap = cv2.VideoCapture(cand)
                    if cap.isOpened():
                        return cap
                except Exception as e:
                    logger.warning(f"Error opening fallback file {cand}: {e}")

        logger.warning("No video source or fallback file available. Utilizing real-time in-memory synthetic stream generator.")
        return None

    def _generate_synthetic_memory_frame(self) -> np.ndarray:
        """Generates dynamic synthetic CCTV frames in memory if no video source is accessible."""
        self.synthetic_frame_counter += 1
        i = self.synthetic_frame_counter
        
        frame = np.full((360, 640, 3), 45, dtype=np.uint8)
        
        # Road lane markers
        cv2.line(frame, (320, 0), (320, 360), (255, 255, 255), 2)
        cv2.line(frame, (100, 0), (100, 360), (200, 200, 200), 2)
        cv2.line(frame, (540, 0), (540, 360), (200, 200, 200), 2)
        
        # Simulated moving Inbound Car (top to bottom)
        car_y = int((i * 4) % 360)
        cv2.rectangle(frame, (180, car_y), (250, min(360, car_y + 60)), (180, 50, 50), -1)
        cv2.putText(frame, "SIMULATED VEHICLE (INBOUND)", (130, max(20, car_y - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # Simulated moving Outbound Motorcycle (bottom to top)
        moto_y = int((360 - (i * 5)) % 360)
        cv2.rectangle(frame, (400, moto_y), (430, min(360, moto_y + 40)), (50, 180, 50), -1)
        cv2.putText(frame, "SIMULATED MOTOR (OUTBOUND)", (360, max(20, moto_y - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        return frame

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
            frame = None

            # Handle dynamic stream switch request
            if self._reconnect_requested:
                if self.cap is not None:
                    self.cap.release()
                    self.cap = None
                self.cap = self._get_capture_source()
                self._reconnect_requested = False
                consecutive_failures = 0

            if self.cap is not None and self.cap.isOpened():
                ret, captured_frame = self.cap.read()
                if ret and captured_frame is not None:
                    frame = captured_frame
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    if consecutive_failures > 5:
                        logger.info("Restarting/looping video stream source...")
                        self.cap.release()
                        time.sleep(0.5)
                        self.cap = self._get_capture_source()
                        consecutive_failures = 0
            
            # If no physical frame captured from video, use in-memory synthetic frame
            if frame is None:
                frame = self._generate_synthetic_memory_frame()

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
            self.cap = None
