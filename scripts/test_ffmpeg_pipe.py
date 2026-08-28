import subprocess
import numpy as np
import cv2
import time

url = "https://surakarta.atcsindonesia.info:8086/camera/Balapan01.flv"
width = 704
height = 576

cmd = [
    "ffmpeg",
    "-tls_verify", "0",
    "-user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "-i", url,
    "-f", "rawvideo",
    "-pix_fmt", "bgr24",
    "-an",
    "-sn",
    "pipe:1"
]

print(f"Launching FFmpeg pipeline for {url}...")
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=width * height * 3 * 10)

frame_size = width * height * 3
start_time = time.time()
frame_count = 0

for i in range(10):
    raw_frame = proc.stdout.read(frame_size)
    if len(raw_frame) != frame_size:
        print(f"Incomplete frame read: {len(raw_frame)} / {frame_size}")
        break
    frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((height, width, 3))
    frame_count += 1
    print(f"  Frame {frame_count}: shape={frame.shape}, mean_brightness={frame.mean():.1f}")

proc.kill()
print(f"\n[SUCCESS] Captured {frame_count} live frames from Balapan01 in {time.time() - start_time:.2f}s!")
