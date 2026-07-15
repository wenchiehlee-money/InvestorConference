import requests
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

url = "https://www.mediatek.com/investor-relations/financial-information"
print(f"Fetching MediaTek IR page from: {url}")
r = requests.get(url, timeout=20)
if r.status_code != 200:
    print(f"Failed: {r.status_code}")
    exit(1)

html = r.text
print("Length of HTML:", len(html))

# Look for hinet or watch or webcast
urls = re.findall(r'(https?://[^\s"\'<>]+)', html)
matching = [u for u in urls if "hinet" in u or "webcast" in u or "watch" in u or "ottlive" in u]
print(f"Found {len(matching)} matching URLs:")
for u in matching:
    print("  ", u)
