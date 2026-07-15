import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_url = os.getenv("OCR_API_URL", "http://mac-mini.tail28f10.ts.net:5001/ocr")
print("Testing OCR API connection to:", api_url)
try:
    r = requests.get(api_url, timeout=5)
    print("Status code:", r.status_code)
    print("Response text:", r.text[:200])
except Exception as e:
    print("Connection failed:", e)
