import subprocess
import csv
import io
import re
import json
import sys
from pathlib import Path

sys.path.append(str(Path(".").resolve()))

from ingest import _csv_row_yq, update_readme

def get_git_commits():
    try:
        res = subprocess.run(
            ["git", "log", "--pretty=format:%H", "--", "raw_event_upcoming_earnings.csv"],
            capture_output=True, encoding="utf-8", errors="replace", check=True
        )
        return res.stdout.splitlines()
    except Exception as e:
        print(f"Error getting git commits: {e}")
        return []

def get_csv_at_commit(commit_hash):
    res = subprocess.run(
        ["git", "show", f"{commit_hash}:raw_event_upcoming_earnings.csv"],
        capture_output=True, encoding="utf-8", errors="replace"
    )
    if res.returncode == 0:
        return res.stdout
    return None

def main():
    commits = get_git_commits()
    print(f"Found {len(commits)} commits modifying raw_event_upcoming_earnings.csv")
    
    extracted_dates = {}
    
    # We load the existing mops_historical_dates.json if it exists to preserve them
    json_path = Path("mops_historical_dates.json")
    if json_path.exists():
        try:
            extracted_dates = json.loads(json_path.read_text(encoding="utf-8"))
            print(f"Loaded {len(extracted_dates)} existing historical dates from JSON.")
        except Exception:
            pass
            
    # Hardcoded known historical dates for very old quarters (2025/2024)
    # derived from web search
    hardcoded_dates = {
        "2330_2025_q1": "2025-04-17",
        "2330_2025_q2": "2025-07-17",
        "2330_2025_q3": "2025-10-16",
        "2330_2025_q4": "2026-01-15",
        "2454_2025_q1": "2025-04-30",
        "2454_2025_q2": "2025-08-12",
        "2454_2025_q3": "2025-10-31",
        "2454_2025_q4": "2026-02-04",
        "2357_2024_q4": "2025-03-11",
        "2357_2025_q3": "2025-11-11",
        "2357_2025_q4": "2026-03-10",
        "2382_2025_q1": "2025-05-13",
        "2382_2025_q2": "2025-08-12",
        "2382_2025_q3": "2025-11-12",
        "2382_2025_q4": "2025-12-04",
        "2347_2025_q4": "2026-03-19",
        "2356_2025_q4": "2026-03-20",
        "2412_2025_q4": "2026-02-26",
        "2458_2025_q4": "2026-03-17",
        "2480_2025_q4": "2026-03-10",
        "3022_2025_q4": "2026-03-18",
        "3034_2025_q4": "2026-03-19",
        "3231_2025_q4": "2026-03-19",
        "4938_2025_q4": "2026-03-25",
        "7765_2025_q4": "2026-03-05",
        "7769_2025_q4": "2026-03-18",
        "8299_2025_q4": "2026-03-17"
    }
    
    # Merge hardcoded dates first (they can be overwritten by exact git history if found)
    for k, v in hardcoded_dates.items():
        if k not in extracted_dates:
            extracted_dates[k] = v

    # Limit to last 250 commits for speed
    max_commits = min(len(commits), 250)
    print(f"Extracting events from the latest {max_commits} commits...")
    
    for idx, commit_hash in enumerate(commits[:max_commits], 1):
        if idx % 50 == 0:
            print(f"  Processed {idx}/{max_commits} commits...")
            
        csv_content = get_csv_at_commit(commit_hash)
        if not csv_content:
            continue
            
        try:
            reader = csv.DictReader(io.StringIO(csv_content))
            for row in reader:
                evt_name = row.get("事件名稱", "")
                date_str = row.get("開始日期", "")
                evt_class = row.get("類別", "")
                remarks = row.get("備註", "")
                
                if not evt_name or not date_str or evt_class != "法說會":
                    continue
                    
                m = re.search(r'[（(](\w+)[）)]', evt_name)
                sid = m.group(1) if m else None
                if not sid or not sid.isdigit():
                    continue
                    
                y, q = _csv_row_yq(evt_name, remarks, date_str)
                if y and q:
                    key = f"{sid}_{y}_q{q}"
                    if key not in extracted_dates:
                        extracted_dates[key] = date_str
        except Exception:
            continue
            
    print(f"Total historical dates captured: {len(extracted_dates)}")
    
    # Save back to mops_historical_dates.json
    json_path.write_text(json.dumps(extracted_dates, indent=2, ensure_ascii=False), encoding="utf-8")
    print("mops_historical_dates.json updated successfully.")
    
    # Run update_readme
    print("Regenerating README.md...")
    update_readme()
    print("README.md regenerated successfully.")

if __name__ == "__main__":
    main()
