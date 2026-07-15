import requests
import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def fetch_issue(number):
    url = f"https://api.github.com/repos/wenchiehlee-money/InvestorConference/issues/{number}"
    print(f"\n================ Issue #{number} ================")
    r = requests.get(url)
    if r.status_code != 200:
        print(f"Failed to fetch issue #{number}: {r.status_code}")
        return
    data = r.json()
    print("Title:", data.get("title"))
    print("Body:")
    print(data.get("body"))

fetch_issue(6)
fetch_issue(7)
fetch_issue(4)
