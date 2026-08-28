import urllib.request
import ssl
import cv2

urls = [
    'https://surakarta.atcsindonesia.info:8086/camera/Balapan01.flv',
    'http://surakarta.atcsindonesia.info:8086/camera/Balapan01.flv',
    'https://surakarta.atcsindonesia.info/camera/Balapan01.flv',
    'http://surakarta.atcsindonesia.info/camera/Balapan01.flv',
    'http://surakarta.atcsindonesia.info:8000/camera/Balapan01.flv',
    'https://surakarta.atcsindonesia.info:8086/camera/UNS.flv',
    'http://surakarta.atcsindonesia.info:8086/camera/UNS.flv',
    'https://surakarta.atcsindonesia.info:8086/camera/Gladag.flv',
    'http://surakarta.atcsindonesia.info:8086/camera/Gladag.flv',
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

print("=== 1. HTTP/HTTPS REQUEST TEST ===")
for u in urls:
    print(f"Testing HTTP GET: {u}")
    try:
        req = urllib.request.Request(
            u,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://dishub.surakarta.go.id/',
                'Origin': 'https://dishub.surakarta.go.id'
            }
        )
        with urllib.request.urlopen(req, timeout=5, context=ctx if u.startswith('https') else None) as resp:
            print(f"  [OK] Status: {resp.status}, Content-Type: {resp.headers.get('Content-Type')}")
            chunk = resp.read(64)
            print(f"  Header bytes (FLV magic: {chunk[:3]}): {chunk[:16]}")
    except Exception as e:
        print(f"  [FAILED] Error: {e}")

print("\n=== 2. OPENCV VIDEO CAPTURE TEST ===")
test_opencv_urls = [
    'https://surakarta.atcsindonesia.info:8086/camera/Balapan01.flv',
    'http://surakarta.atcsindonesia.info:8086/camera/Balapan01.flv',
    'https://surakarta.atcsindonesia.info:8086/camera/UNS.flv',
    'http://surakarta.atcsindonesia.info:8086/camera/UNS.flv',
]

for u in test_opencv_urls:
    print(f"Testing OpenCV: {u}")
    cap = cv2.VideoCapture(u, cv2.CAP_FFMPEG)
    if cap.isOpened():
        ret, frame = cap.read()
        print(f"  [OK] cap.isOpened()=True, read() ret={ret}, shape={frame.shape if frame is not None else None}")
        cap.release()
    else:
        print(f"  [FAILED] cap.isOpened()=False")
