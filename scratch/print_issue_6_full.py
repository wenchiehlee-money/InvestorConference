import requests
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

url = "https://api.github.com/repos/wenchiehlee-money/InvestorConference/issues/6"
r = requests.get(url)
if r.status_code == 200:
    data = r.json()
    print(data.get("body"))
else:
    print("Failed to fetch issue 6")
