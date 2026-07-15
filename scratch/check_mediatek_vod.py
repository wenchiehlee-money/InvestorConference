import requests
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

url = "https://webpage-ott2b.cdn.hinet.net/webpage/vod?contentProvider=mediatek"
print(f"Fetching VOD list from: {url}")
r = requests.get(url, timeout=20)
if r.status_code != 200:
    print(f"Failed: {r.status_code}")
    exit(1)

html = r.text
print("Length of HTML:", len(html))

# Save to a scratch file so we can view it
from pathlib import Path
Path("scratch/mediatek_vod.html").write_text(html, encoding="utf-8")
print("Saved to scratch/mediatek_vod.html")

# Print lines containing "watch" or "v=" or "mediatek"
lines = html.splitlines()
found = 0
for i, line in enumerate(lines):
    if "watch" in line or "v=" in line or "mediatek" in line:
        print(f"Line {i+1}: {line.strip()}")
        found += 1
        if found > 100:
            print("... truncated ...")
            break
