import cv2
import urllib.request

test_urls = [
    # RTMP Streams
    "rtmp://surakarta.atcsindonesia.info/camera/Balapan01",
    "rtmp://surakarta.atcsindonesia.info:1935/camera/Balapan01",
    "rtmp://surakarta.atcsindonesia.info/live/Balapan01",
    "rtmp://surakarta.atcsindonesia.info:1935/live/Balapan01",
    
    # Port 8888 (Node-Media-Server default HTTP-FLV / HLS)
    "http://surakarta.atcsindonesia.info:8888/camera/Balapan01.flv",
    "http://surakarta.atcsindonesia.info:8888/live/Balapan01.flv",
    "http://surakarta.atcsindonesia.info:8888/camera/Balapan01/index.m3u8",
    
    # Port 80 (Standard HTTP)
    "http://surakarta.atcsindonesia.info/camera/Balapan01.flv",
    "http://surakarta.atcsindonesia.info:80/camera/Balapan01.flv",
    "http://surakarta.atcsindonesia.info/live/Balapan01.flv",
]

print("=== 1. TESTING HTTP ENDPOINTS ON PORT 8888 & 80 ===")
for u in test_urls:
    if u.startswith("http"):
        print(f"Testing: {u}")
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                print(f"  [OK] Status: {resp.status}, Content-Type: {resp.headers.get('Content-Type')}")
                chunk = resp.read(32)
                print(f"  Received: {chunk[:10]}")
        except Exception as e:
            print(f"  [FAILED] {e}")

print("\n=== 2. TESTING OPENCV ON RTMP & HTTP PORTS ===")
for u in test_urls:
    print(f"OpenCV testing: {u}")
    cap = cv2.VideoCapture(u, cv2.CAP_FFMPEG)
    if cap.isOpened():
        ret, frame = cap.read()
        print(f"  [SUCCESS!!!] Opened! read={ret}, shape={frame.shape if frame is not None else None}")
        cap.release()
        break
    else:
        print(f"  [FAILED] Not opened")
