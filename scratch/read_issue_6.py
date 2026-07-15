import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

content_path = Path("C:/Users/WJLEE/.gemini/antigravity-cli/brain/00a2dabb-fabc-4b25-b7eb-bc3381c8f490/.system_generated/steps/148/content.md")
lines = content_path.read_text(encoding="utf-8").splitlines()

in_table = False
for line in lines:
    if "分析 2480" in line or "字幕轉錄錯誤" in line:
        in_table = True
    if in_table:
        print(line)
        if "Issue actions" in line:
            break
