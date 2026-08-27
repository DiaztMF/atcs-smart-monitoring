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
        self._cap_lock = threading.Lock()
        self._cap: Optional[cv2.VideoCapture] = None
        self._is_connecting: bool = False
        self._offline_reason: str = "Menghubungkan..."

    # ------------------------------------------------------------------
    # Public cap accessor (thread-safe)
    # ------------------------------------------------------------------
    def _get_cap(self) -> Optional[cv2.VideoCapture]:
        with self._cap_lock:
            return self._cap

    def _set_cap(self, cap: Optional[cv2.VideoCapture]) -> None:
        with self._cap_lock:
            if self._cap is not None:
                self._cap.release()
            self._cap = cap

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def start(self) -> None:
        if not self.running:
            self.running = True
            self._offline_reason = "Menghubungkan..."
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            logger.info("Stream reader worker started.")
            # Kick off initial connection asynchronously
            self._spawn_connect_thread()

    def stop(self) -> None:
        self.running = False
        self._set_cap(None)
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        logger.info("Stream reader worker stopped.")

    def switch_stream(self, new_url: str, stream_name: str) -> None:
        """Switches stream source without blocking the MJPEG loop."""
        logger.info(f"Switching stream source to: {stream_name} ({new_url})")
        self._offline_reason = "Menghubungkan..."
        global_state.set_active_stream(new_url, stream_name)
        # Drop current cap immediately so offline frame shows right away
        self._set_cap(None)
        # Connect to new source in background thread
        self._spawn_connect_thread()

    # ------------------------------------------------------------------
    # Async connect (runs in its own short-lived thread)
    # ------------------------------------------------------------------
    def _spawn_connect_thread(self) -> None:
        if self._is_connecting:
            return  # already attempting; skip duplicate
        t = threading.Thread(target=self._connect_to_stream, daemon=True)
        t.start()

    def _connect_to_stream(self) -> None:
        self._is_connecting = True
        active_stream = global_state.get_active_stream()
        stream_url = active_stream["url"]

        if stream_url.startswith("synthetic://"):
            logger.info("Synthetic mode — showing offline frame.")
            self._offline_reason = "Mode Demo Aktif"
            self._set_cap(None)
            self._is_connecting = False
            return

        try:
            logger.info(f"Connecting to stream: {stream_url}")
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
                logger.info(f"Stream connected: {stream_url}")
                self._offline_reason = ""
                self._set_cap(cap)
            else:
                self._offline_reason = "Gagal Membuka Stream"
                logger.warning(f"Stream did not open: {stream_url}")
                self._set_cap(None)
        except Exception as exc:
            self._offline_reason = "Error Koneksi"
            logger.warning(f"Error opening stream {stream_url}: {exc}")
            self._set_cap(None)

        self._is_connecting = False

    # ------------------------------------------------------------------
    # Main frame loop
    # ------------------------------------------------------------------
    def _run_loop(self) -> None:
        frame_idx = 0
        consecutive_failures = 0
        target_frame_time = 1.0 / max(1, settings.TARGET_FPS)
        fps_timer = time.time()
        fps_frame_counter = 0
        current_fps = 0.0

        while self.running:
            loop_start = time.time()
            frame: Optional[np.ndarray] = None

            cap = self._get_cap()
            if cap is not None and cap.isOpened():
                ret, captured_frame = cap.read()
                if ret and captured_frame is not None:
                    frame = captured_frame
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    if consecutive_failures > 5:
                        logger.warning("Stream dropped — showing offline frame and retrying in 10s.")
                        self._set_cap(None)
                        self._offline_reason = "Stream Terputus — Mencoba Ulang"
                        consecutive_failures = 0
                        # Schedule reconnect after 10s without blocking this loop
                        threading.Thread(
                            target=self._delayed_reconnect, args=(10.0,), daemon=True
                        ).start()

            # No live frame: render offline error card
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

            # Resize to standardized processing dimensions
            resized_frame = cv2.resize(frame, (settings.STREAM_WIDTH, settings.STREAM_HEIGHT))
            global_state.set_raw_frame(resized_frame)
            global_state.set_stream_status(True, current_fps)

            # Retrieve active ROIs
            inbound_poly = global_state.get_roi("inbound")
            outbound_poly = global_state.get_roi("outbound")

            # AI inference & spatial tracking
            annotated_frame, metrics = self.detector.detect_and_track(
                frame=resized_frame,
                current_frame_idx=frame_idx,
                inbound_poly=inbound_poly,
                outbound_poly=outbound_poly
            )

            metrics["fps"] = current_fps

            # Single-pass JPEG encoding shared across all MJPEG clients
            ret_enc, buffer = cv2.imencode(
                '.jpg', annotated_frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), settings.JPEG_QUALITY]
            )
            encoded_bytes = buffer.tobytes() if ret_enc else None

            global_state.set_annotated_frame(annotated_frame, encoded_jpeg=encoded_bytes)
            global_state.update_metrics(metrics)

            # CPU throttle to maintain target FPS
            elapsed = time.time() - loop_start
            sleep_duration = max(0.001, target_frame_time - elapsed)
            time.sleep(sleep_duration)

        self._set_cap(None)

    def _delayed_reconnect(self, delay_seconds: float) -> None:
        """Waits then attempts reconnect — avoids hammering a dead server."""
        time.sleep(delay_seconds)
        if self.running:
            self._spawn_connect_thread()
