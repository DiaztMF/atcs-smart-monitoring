import urllib.request

paths = [
    "",
    "api/streams",
    "api/server",
    "admin",
    "flv",
    "hls",
    "streams",
    "cameras"
]

for p in paths:
    u = f"http://surakarta.atcsindonesia.info:8888/{p}"
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = resp.read(512)
            print(f"[PORT 8888] {u} -> Status {resp.status}, Content: {data[:120]}")
    except Exception as e:
        print(f"[PORT 8888] {u} -> {e}")

for p in paths:
    u = f"http://surakarta.atcsindonesia.info/{p}"
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = resp.read(512)
            print(f"[PORT 80] {u} -> Status {resp.status}, Content: {data[:120]}")
    except Exception as e:
        print(f"[PORT 80] {u} -> {e}")
