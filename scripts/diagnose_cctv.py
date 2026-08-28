import urllib.request
import re

url = "http://surakarta.atcsindonesia.info"
try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
        print(f"Homepage fetched! Length: {len(html)}")
        # Look for video URLs or stream URLs
        streams = re.findall(r'(https?://[^\s"\'<>]+\.(?:flv|m3u8|mp4)|[^\s"\'<>]+\.flv)', html, re.IGNORECASE)
        print("Found streams in HTML:", set(streams))
        # Look for script tags or iframes or video players
        players = re.findall(r'<(?:video|iframe|script)[^>]+>', html, re.IGNORECASE)
        print(f"Found {len(players)} video/iframe/script tags:")
        for p in players[:10]:
            print(" ", p)
except Exception as e:
    print(f"Error fetching {url}: {e}")
