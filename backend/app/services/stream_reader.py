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

# Offline/error frame dimensions match the standard stream output
_OFFLINE_W = 640
_OFFLINE_H = 360


def _build_offline_frame(stream_name: str, reason: str) -> np.ndarray:
    """Renders a clean 'stream offline' error card as a numpy BGR frame."""
    frame = np.zeros((_OFFLINE_H, _OFFLINE_W, 3), dtype=np.uint8)

    # Subtle dark grid background
    for x in range(0, _OFFLINE_W, 32):
        cv2.line(frame, (x, 0), (x, _OFFLINE_H), (28, 28, 28), 1)
    for y in range(0, _OFFLINE_H, 32):
        cv2.line(frame, (0, y), (_OFFLINE_W, y), (28, 28, 28), 1)

    # Central icon — broken signal "X"
    cx, cy = _OFFLINE_W // 2, _OFFLINE_H // 2 - 40
    icon_r = 28
    cv2.circle(frame, (cx, cy), icon_r + 4, (60, 60, 60), -1)
    cv2.circle(frame, (cx, cy), icon_r, (40, 40, 40), -1)
    thick = 3
    cv2.line(frame, (cx - 14, cy - 14), (cx + 14, cy + 14), (60, 80, 200), thick, cv2.LINE_AA)
    cv2.line(frame, (cx + 14, cy - 14), (cx - 14, cy + 14), (60, 80, 200), thick, cv2.LINE_AA)

    # Status label
    label = "STREAM TIDAK TERSEDIA"
    lw, lh = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)[0]
    cv2.putText(frame, label,
                (_OFFLINE_W // 2 - lw // 2, cy + icon_r + 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 180), 2, cv2.LINE_AA)

    # Camera name (truncated if too long)
    cam_label = stream_name[:42] + ("..." if len(stream_name) > 42 else "")
    cw, _ = cv2.getTextSize(cam_label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
    cv2.putText(frame, cam_label,
                (_OFFLINE_W // 2 - cw // 2, cy + icon_r + 54),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (120, 120, 120), 1, cv2.LINE_AA)

    # Reason tag
    reason_label = f"[ {reason} ]"
    rw, _ = cv2.getTextSize(reason_label, cv2.FONT_HERSHEY_SIMPLEX, 0.35, 1)[0]
    cv2.putText(frame, reason_label,
                (_OFFLINE_W // 2 - rw // 2, cy + icon_r + 76),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (70, 100, 160), 1, cv2.LINE_AA)

    # Timestamp bottom-left
    ts = time.strftime("%H:%M:%S")
    cv2.putText(frame, ts, (10, _OFFLINE_H - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (60, 60, 60), 1, cv2.LINE_AA)

    return frame


class StreamReaderWorker:
    def __init__(self, detector: TrafficDetector):
        self.detector = detector
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.cap: Optional[cv2.VideoCapture] = None
        self._reconnect_requested: bool = False
        self._offline_reason: str = "Menghubungkan..."

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
        self._offline_reason = "Menghubungkan..."
        global_state.set_active_stream(new_url, stream_name)
        self._reconnect_requested = True

    def _get_capture_source(self) -> Optional[cv2.VideoCapture]:
        active_stream = global_state.get_active_stream()
        stream_url = active_stream["url"]

        if stream_url.startswith("synthetic://"):
            logger.info("Synthetic mode selected — offline frame will display.")
            self._offline_reason = "Mode Demo Aktif"
            return None

        try:
            logger.info(f"Connecting to stream: {stream_url}")
            # FFmpeg options for live HTTPS FLV streams:
            # tls_verify=0  — skip TLS certificate validation (self-signed ATCS certs)
            # timeout       — per-read timeout in microseconds (15s)
            # reconnect_*   — auto-reconnect on dropped streams
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
                self._offline_reason = ""
                return cap
            else:
                self._offline_reason = "Gagal Membuka Stream"
                logger.warning(f"Stream did not open: {stream_url}")
        except Exception as exc:
            self._offline_reason = "Error Koneksi"
            logger.warning(f"Error opening stream {stream_url}: {exc}")

        return None

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
                        logger.warning("Stream dropped — showing offline frame and retrying in 10s.")
                        self.cap.release()
                        self.cap = None
                        self._offline_reason = "Stream Terputus — Mencoba Ulang"
                        # Wait before retry so we don't hammer a dead server
                        time.sleep(10.0)
                        self.cap = self._get_capture_source()
                        consecutive_failures = 0

            # No live frame: render offline error card instead of fallback video
            if frame is None:
                active_stream = global_state.get_active_stream()
                stream_name = active_stream.get("name", "Kamera ATCS")
                frame = _build_offline_frame(stream_name, self._offline_reason)

            frame_idx += 1
            fps_frame_counter += 1

            # FPS calculation every 1 second
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

            # Single-pass JPEG encoding (shared for all connected clients)
            ret_enc, buffer = cv2.imencode('.jpg', annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), settings.JPEG_QUALITY])
            encoded_bytes = buffer.tobytes() if ret_enc else None

            global_state.set_annotated_frame(annotated_frame, encoded_jpeg=encoded_bytes)
            global_state.update_metrics(metrics)

            # CPU throttle to maintain target FPS
            elapsed = time.time() - loop_start
            sleep_duration = max(0.001, target_frame_time - elapsed)
            time.sleep(sleep_duration)

        if self.cap:
            self.cap.release()
            self.cap = None
