import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

content = Path("2480/2480_2026_q1_FIN.srt").read_text(encoding="utf-8")

def check_range(start_t, end_t):
    print(f"\n--- Checking range {start_t} to {end_t} ---")
    lines = content.splitlines()
    for line in lines:
        m = re.match(r'^\((\d{2}):(\d{2})', line)
        if m:
            mm, ss = map(int, m.groups())
            sec = mm * 60 + ss
            if start_t <= sec <= end_t:
                print(line)

import re
check_range(90, 115)  # 01:30 - 01:55
check_range(2560, 2595) # 42:40 - 42:59
check_range(540, 560)   # 09:00 - 09:20
check_range(720, 750)   # 12:00 - 12:30
check_range(150, 180)   # 02:30 - 03:00
check_range(220, 250)   # 03:40 - 04:10
check_range(260, 290)   # 04:20 - 04:50
check_range(770, 795)   # 12:50 - 13:15
check_range(800, 825)   # 13:20 - 13:45
check_range(1140, 1165) # 19:00 - 19:25
check_range(1190, 1215) # 19:50 - 20:15
check_range(1250, 1280) # 20:50 - 21:20
check_range(1830, 1870) # 30:30 - 31:10
check_range(1960, 1990) # 32:40 - 33:10
check_range(2065, 2100) # 34:25 - 35:00
check_range(3020, 3050) # 50:20 - 50:50
