import requests
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

url = "https://ottlive-ott2b2.cdn.hinet.net/mediatek/index.html"
print(f"Fetching MediaTek index from: {url}")
r = requests.get(url, timeout=20)
if r.status_code != 200:
    print(f"Failed: {r.status_code}")
    exit(1)

html = r.text
print("Length of HTML:", len(html))

from pathlib import Path
Path("scratch/mediatek_index.html").write_text(html, encoding="utf-8")
print("Saved to scratch/mediatek_index.html")

# Look for any url, src, or iframe, or script block
import re
urls = re.findall(r'(https?://[^\s"\'<>]+)', html)
print(f"Found {len(urls)} URLs:")
for u in urls[:50]:
    print("  ", u)
