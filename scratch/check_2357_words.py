import sys
import re
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def check_file_words(filepath, words):
    path = Path(filepath)
    if not path.exists():
        print(f"File {filepath} does not exist.")
        return
    print(f"\n================ Checking {filepath} ================")
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    for w in words:
        matches = [(i+1, line) for i, line in enumerate(lines) if w in line]
        print(f"Word '{w}': found {len(matches)} times:")
        for idx, line in matches:
            print(f"  Line {idx}: {line}")

# Words to check in 2357_2026_q1_FIN.srt
check_file_words("2357/2357_2026_q1_FIN.srt", [
    "2020年", "新南幣", "出貨遞嚴", "營縮", "法稅會", "法收費", "四月群", 
    "GDC", "全異能", "Rubin", "Entropic", "連成長", "繼增長"
])

# Words to check in 2357_2025_q4_GT.srt
check_file_words("2357/2357_2025_q4_GT.srt", [
    "法律說明會", "稅後經歷", "2022年", "史燕森", "謝元", "Sensen", "Openclaw"
])

# Words to check in 2357_2025_q4_qa.md
check_file_words("2357/2357_2025_q4_qa.md", [
    "46:67", "46:47"
])

# Words to check in 2357_2025_q4.md (or similar files under 2357)
# Wait, let's search for files matching *2357_2025_q4* in 2357/
print("\nFiles in 2357 matching 2025_q4:")
for p in Path("2357").glob("*2025_q4*"):
    print(f"  {p}")

check_file_words("2357/2357_2025_q4_alphaspread_transcript.md", [
    "財務時報", "銀售", "4.9%", "許仙月"
])
