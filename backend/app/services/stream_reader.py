import os
import subprocess
import threading
import time
from typing import Optional, Tuple
import cv2
import numpy as np
from app.core.config import settings
from app.core.logging import logger
from app.core.state import global_state
from app.services.detector import TrafficDetector

# Standard dimensions
_STREAM_W = settings.STREAM_WIDTH
_STREAM_H = settings.STREAM_HEIGHT


def _build_offline_frame(stream_name: str, reason: str) -> np.ndarray:
    """Renders a clean 'stream offline' error card as a numpy BGR frame."""
    frame = np.zeros((_STREAM_H, _STREAM_W, 3), dtype=np.uint8)

    # Subtle dark grid background
    for x in range(0, _STREAM_W, 32):
        cv2.line(frame, (x, 0), (x, _STREAM_H), (28, 28, 28), 1)
    for y in range(0, _STREAM_H, 32):
        cv2.line(frame, (0, y), (_STREAM_W, y), (28, 28, 28), 1)

    # Central icon — broken signal "X"
    cx, cy = _STREAM_W // 2, _STREAM_H // 2 - 40
    icon_r = 28
    cv2.circle(frame, (cx, cy), icon_r + 4, (60, 60, 60), -1)
    cv2.circle(frame, (cx, cy), icon_r, (40, 40, 40), -1)
    thick = 3
    cv2.line(frame, (cx - 14, cy - 14), (cx + 14, cy + 14), (60, 80, 200), thick, cv2.LINE_AA)
    cv2.line(frame, (cx + 14, cy - 14), (cx - 14, cy + 14), (60, 80, 200), thick, cv2.LINE_AA)

    # Status label
    label = "STREAM TIDAK TERSEDIA"
    lw, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)[0]
    cv2.putText(frame, label,
                (_STREAM_W // 2 - lw // 2, cy + icon_r + 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 180), 2, cv2.LINE_AA)

    # Camera name (truncated if too long)
    cam_label = stream_name[:42] + ("..." if len(stream_name) > 42 else "")
    cw, _ = cv2.getTextSize(cam_label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
    cv2.putText(frame, cam_label,
                (_STREAM_W // 2 - cw // 2, cy + icon_r + 54),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (120, 120, 120), 1, cv2.LINE_AA)

    # Reason tag
    reason_label = f"[ {reason} ]"
    rw, _ = cv2.getTextSize(reason_label, cv2.FONT_HERSHEY_SIMPLEX, 0.35, 1)[0]
    cv2.putText(frame, reason_label,
                (_STREAM_W // 2 - rw // 2, cy + icon_r + 76),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (70, 100, 160), 1, cv2.LINE_AA)

    # Timestamp bottom-left
    ts = time.strftime("%H:%M:%S")
    cv2.putText(frame, ts, (10, _STREAM_H - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (60, 60, 60), 1, cv2.LINE_AA)

    return frame


class FFmpegStreamCapture:
    """Robust rawvideo reader using standalone FFmpeg process with full TLS/HTTPS support."""
    def __init__(self, url: str, width: int = _STREAM_W, height: int = _STREAM_H):
        self.url = url
        self.width = width
        self.height = height
        self.frame_size = width * height * 3
        self.process: Optional[subprocess.Popen] = None
        self._open_process()

    def _open_process(self):
        cmd = [
            "ffmpeg",
            "-nostdin",
            "-loglevel", "error",
            "-tls_verify", "0",
            "-rw_timeout", "3000000",
            "-user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "-i", self.url,
            "-vf", f"scale={self.width}:{self.height}",
            "-f", "rawvideo",
            "-pix_fmt", "bgr24",
            "-an",
            "-sn",
            "pipe:1"
        ]
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=self.frame_size * 5
            )
        except Exception as e:
            logger.error(f"Failed to spawn FFmpeg process for {self.url}: {e}")
            self.process = None

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        if self.process is None or self.process.stdout is None:
            return False, None
        
        try:
            raw_frame = self.process.stdout.read(self.frame_size)
            if len(raw_frame) != self.frame_size:
                return False, None
            frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((self.height, self.width, 3))
            return True, frame
        except Exception:
            return False, None

    def release(self):
        if self.process is not None:
            try:
                self.process.kill()
            except Exception:
                pass
            self.process = None


class StreamReaderWorker:
    def __init__(self, detector: TrafficDetector):
        self.detector = detector
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self._stream_lock = threading.Lock()
        self._stream_cap: Optional[FFmpegStreamCapture] = None
        self._cv_cap: Optional[cv2.VideoCapture] = None
        self._is_connecting: bool = False
        self._offline_reason: str = "Menghubungkan..."

    # ------------------------------------------------------------------
    # Capture source management (thread-safe)
    # ------------------------------------------------------------------
    def _close_sources(self) -> None:
        with self._stream_lock:
            if self._stream_cap is not None:
                self._stream_cap.release()
                self._stream_cap = None
            if self._cv_cap is not None:
                self._cv_cap.release()
                self._cv_cap = None

    def _read_active_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        with self._stream_lock:
            if self._stream_cap is not None:
                return self._stream_cap.read()
            if self._cv_cap is not None and self._cv_cap.isOpened():
                ret, frame = self._cv_cap.read()
                if ret and frame is not None:
                    if frame.shape[1] != _STREAM_W or frame.shape[0] != _STREAM_H:
                        frame = cv2.resize(frame, (_STREAM_W, _STREAM_H))
                    return True, frame
        return False, None

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
            self._spawn_connect_thread()

    def stop(self) -> None:
        self.running = False
        self._close_sources()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        logger.info("Stream reader worker stopped.")

    def switch_stream(self, new_url: str, stream_name: str) -> None:
        """Switches stream source without blocking the MJPEG loop."""
        logger.info(f"Switching stream source to: {stream_name} ({new_url})")
        self._offline_reason = "Menghubungkan..."
        global_state.set_active_stream(new_url, stream_name)
        self._close_sources()
        self._spawn_connect_thread()

    # ------------------------------------------------------------------
    # Async connect (runs in background thread)
    # ------------------------------------------------------------------
    def _spawn_connect_thread(self) -> None:
        t = threading.Thread(target=self._connect_to_stream, daemon=True)
        t.start()

    def _connect_to_stream(self) -> None:
        if self._is_connecting:
            return
        self._is_connecting = True
        active_stream = global_state.get_active_stream()
        stream_url = active_stream["url"]

        if stream_url.startswith("synthetic://"):
            logger.info("Synthetic mode — showing offline frame.")
            self._offline_reason = "Mode Demo Aktif"
            self._close_sources()
            self._is_connecting = False
            return

        try:
            logger.info(f"Connecting to stream: {stream_url}")
            
            # If HTTP/HTTPS/FLV/RTMP stream, use standalone FFmpeg pipeline
            if stream_url.startswith("http://") or stream_url.startswith("https://") or stream_url.startswith("rtmp://"):
                ffmpeg_cap = FFmpegStreamCapture(stream_url, _STREAM_W, _STREAM_H)
                # Test reading 1 frame to confirm connection
                ret, frame = ffmpeg_cap.read()
                if ret and frame is not None:
                    with self._stream_lock:
                        self._close_sources()
                        self._stream_cap = ffmpeg_cap
                    self._offline_reason = ""
                    logger.info(f"FFmpeg stream connected successfully: {stream_url}")
                else:
                    ffmpeg_cap.release()
                    self._offline_reason = "Gagal Membuka Stream (Kamera Offline)"
                    logger.warning(f"Stream did not produce frames: {stream_url}")
            else:
                # Local video file path
                cv_cap = cv2.VideoCapture(stream_url)
                if cv_cap.isOpened():
                    with self._stream_lock:
                        self._close_sources()
                        self._cv_cap = cv_cap
                    self._offline_reason = ""
                else:
                    self._offline_reason = "Gagal Membuka File Video"
        except Exception as exc:
            self._offline_reason = "Error Koneksi"
            logger.warning(f"Error opening stream {stream_url}: {exc}")

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

            ret, captured_frame = self._read_active_frame()
            if ret and captured_frame is not None:
                frame = captured_frame
                consecutive_failures = 0
            else:
                consecutive_failures += 1
                if consecutive_failures > 15:
                    self._close_sources()
                    if not self._is_connecting:
                        self._offline_reason = "Stream Terputus — Mencoba Ulang"
                        consecutive_failures = 0
                        threading.Thread(
                            target=self._delayed_reconnect, args=(8.0,), daemon=True
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

            global_state.set_raw_frame(frame)
            global_state.set_stream_status(True, current_fps)

            # Retrieve active ROIs
            inbound_poly = global_state.get_roi("inbound")
            outbound_poly = global_state.get_roi("outbound")

            # AI inference & spatial tracking
            annotated_frame, metrics = self.detector.detect_and_track(
                frame=frame,
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

        self._close_sources()

    def _delayed_reconnect(self, delay_seconds: float) -> None:
        """Waits then attempts reconnect."""
        time.sleep(delay_seconds)
        if self.running:
            self._spawn_connect_thread()
