import sys
import os
import csv
import re
from pathlib import Path
from datetime import date as _date

sys.path.append(str(Path(".").resolve()))

from ingest import (
    download_mops_pdfs,
    download_pdfs,
    update_readme,
    _csv_row_yq,
    detect_market
)

def main():
    csv_path = Path("raw_event_upcoming_earnings.csv")
    if not csv_path.exists():
        print("CSV file not found!")
        return

    start_limit = _date(2026, 5, 1)
    end_limit = _date(2026, 7, 7)

    target_events = []

    with open(csv_path, encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            evt_name = row.get("事件名稱", "")
            date_str = row.get("開始日期", "")
            evt_class = row.get("類別", "")
            remarks = row.get("備註", "")

            if not evt_name or not date_str:
                continue

            try:
                ev_date = _date.fromisoformat(date_str)
            except ValueError:
                continue

            if start_limit <= ev_date <= end_limit:
                m = re.search(r'[（(](\w+)[）)]', evt_name)
                sid = m.group(1) if m else None
                if not sid:
                    continue
                
                # Only care about TW stock investor conferences
                if not sid.isdigit() or evt_class != "法說會":
                    continue

                exp_year, exp_q = _csv_row_yq(evt_name, remarks, date_str)
                target_events.append({
                    "sid": sid,
                    "year": exp_year,
                    "quarter": exp_q,
                    "date": date_str,
                    "name": evt_name,
                    "class": evt_class
                })

    print(f"Found {len(target_events)} TW stock investor conference events between 5/1 and 7/7.")
    
    downloaded_count = 0

    for idx, ev in enumerate(target_events, 1):
        sid = ev["sid"]
        year = ev["year"]
        quarter = ev["quarter"]
        date_str = ev["date"]
        
        print(f"\n[{idx}/{len(target_events)}] Processing {sid} {year} Q{quarter} (Date: {date_str}) ...")
        
        # Create directory
        save_dir = Path(sid)
        save_dir.mkdir(exist_ok=True)
        
        # 1. Download from MOPS
        conf_date = date_str.replace("-", "")
        mops_res = download_mops_pdfs(sid, conf_date, year, quarter, save_dir)
        if mops_res:
            print(f"  MOPS downloaded: {[p.name for p in mops_res]}")
            downloaded_count += len(mops_res)
            
        # 2. Download from known direct URLs
        direct_res = download_pdfs(sid, year, quarter, save_dir)
        if direct_res:
            print(f"  Direct downloaded: {[p.name for p in direct_res]}")
            downloaded_count += len(direct_res)

    print(f"\nFinished download. Total files downloaded/already exist: {downloaded_count}")
    
    print("\nRegenerating README.md...")
    update_readme()
    print("README.md regenerated successfully.")

if __name__ == "__main__":
    main()
