import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def print_srt_range(filepath, start_time_str, end_time_str):
    path = Path(filepath)
    if not path.exists():
        return
    print(f"\n--- Context in {filepath} ---")
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if start_time_str in line:
            for j in range(max(0, i-5), min(len(lines), i+6)):
                print(f"  Line {j+1}: {lines[j]}")

print_srt_range("2357/2357_2026_q1_FIN.srt", "03:11", "03:12")
print_srt_range("2357/2357_2026_q1_FIN.srt", "03:53", "03:54")
print_srt_range("2357/2357_2026_q1_FIN.srt", "20:51", "20:52")
print_srt_range("2357/2357_2025_q4_GT.srt", "03:05", "03:06")
print_srt_range("2357/2357_2025_q4_GT.srt", "17:21", "17:22")
print_srt_range("2357/2357_2025_q4_GT.srt", "19:02", "19:03")
print_srt_range("2357/2357_2025_q4_qa.md", "問題 6", "webcast")
