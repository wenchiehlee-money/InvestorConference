import sys
import re
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

srt_path = Path("2480/2480_2026_q1_FIN.srt")
content = srt_path.read_text(encoding="utf-8")

words_to_check = [
    "敦洋科技", "飛行科技", "獨樣科", "公開資訊觀測", "Sysco", "Luba", 
    "PalAuto", "CrawlStrike", "Head5", "OpenTag", "SichuX", "DeepSync", 
    "ChainGPT", "網頁房", "最後一禮物", "PowerApple", "ProseWire", 
    "應付", "8例", "水利表", "美股盈餘", "三體別", "工作佔於", "法定於公"
]

for w in words_to_check:
    matches = [line for line in content.splitlines() if w in line]
    print(f"Word '{w}': found {len(matches)} times:")
    for m in matches:
        print(f"  {m}")
