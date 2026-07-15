import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

content_path = Path("C:/Users/WJLEE/.gemini/antigravity-cli/brain/00a2dabb-fabc-4b25-b7eb-bc3381c8f490/.system_generated/steps/148/content.md")
lines = content_path.read_text(encoding="utf-8").splitlines()

for i in range(390, min(540, len(lines))):
    print(f"{i+1}: {lines[i]}")
