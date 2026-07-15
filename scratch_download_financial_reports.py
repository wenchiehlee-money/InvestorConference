import sys
import os
import csv
import re
import subprocess
from pathlib import Path
from datetime import date as _date

sys.path.append(str(Path(".").resolve()))

from ingest import update_readme, _csv_row_yq

def modify_mops_config(config_path: Path):
    """Modify MOPS config to allow downloading all PDFs including English version."""
    content = config_path.read_text(encoding="utf-8")
    
    # Replace TARGET_FILE_PATTERNS
    # We do a direct string replace to be 100% safe
    old_patterns = 'TARGET_FILE_PATTERNS = [\n    r"A12\\.pdf$",       # Pattern from company 8272\n    r"A13\\.pdf$",       # Pattern from company 2330 (old)\n    r"AI1\\.pdf$",       # Pattern from company 2330 (current) - NEW\n    r"A1[0-9]\\.pdf$"    # Generic individual report pattern\n]'
    new_patterns = 'TARGET_FILE_PATTERNS = [\n    r"\\.pdf$"\n]'
    
    # Windows/Linux line endings normalization for the search
    content_norm = content.replace('\r\n', '\n')
    
    if old_patterns in content_norm:
        content_norm = content_norm.replace(old_patterns, new_patterns)
    else:
        # Fallback regex if formatting slightly differs
        content_norm = re.sub(
            r'TARGET_FILE_PATTERNS\s*=\s*\[[^\]]*\]',
            'TARGET_FILE_PATTERNS = [r"\\.pdf$"]',
            content_norm,
            flags=re.DOTALL
        )
        
    old_excluded = 'EXCLUDED_KEYWORDS = [\n    "英文版",            # English versions\n    r"AIA\\.pdf",        # English consolidated (from real data)\n    r"AE2\\.pdf"         # English parent-subsidiary (from real data)\n]'
    new_excluded = 'EXCLUDED_KEYWORDS = []'
    
    if old_excluded in content_norm:
        content_norm = content_norm.replace(old_excluded, new_excluded)
    else:
        # Fallback regex
        content_norm = re.sub(
            r'EXCLUDED_KEYWORDS\s*=\s*\[[^\]]*\]',
            'EXCLUDED_KEYWORDS = []',
            content_norm,
            flags=re.DOTALL
        )
        
    # Write back with original platform line endings
    if '\r\n' in content:
        content_norm = content_norm.replace('\n', '\r\n')
        
    config_path.write_text(content_norm, encoding="utf-8")
    print("[Config] Temporarily modified MOPS config to download all PDFs.")

def restore_mops_config(mops_dir: Path):
    """Restore MOPS config using git checkout."""
    try:
        subprocess.run(
            ["git", "checkout", "mops_downloader/config.py"],
            cwd=mops_dir,
            check=True
        )
        print("[Config] Restored MOPS config successfully.")
    except Exception as e:
        print(f"[Config] Failed to restore MOPS config: {e}")

def main():
    mops_dir = Path("../MOPS").resolve()
    mops_config_path = mops_dir / "mops_downloader" / "config.py"
    
    if not mops_config_path.exists():
        print(f"MOPS config not found at {mops_config_path}")
        return
        
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
                
                # Only care about TW stock financial reports (財報 or 財報公告)
                if not sid.isdigit() or evt_class not in ["財報", "財報公告"]:
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

    print(f"Found {len(target_events)} TW stock financial report events between 5/1 and 7/7.")
    if not target_events:
        return

    # Modify config before download
    modify_mops_config(mops_config_path)

    try:
        # Run downloads
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        for idx, ev in enumerate(target_events, 1):
            sid = ev["sid"]
            year = ev["year"]
            quarter = ev["quarter"]
            
            print(f"\n[{idx}/{len(target_events)}] Downloading financial reports for {sid} ({year} Q{quarter}) ...")
            
            cmd = [
                sys.executable, "-m", "mops_downloader.cli",
                "--company_id", sid,
                "--year", str(year),
                "--quarter", str(quarter),
                "--output", str(mops_dir / "downloads"),
                "--only-missing-files"
            ]
            
            try:
                # We run it with a timeout of 180 seconds per company
                subprocess.run(cmd, cwd=mops_dir, env=env, timeout=180)
            except subprocess.TimeoutExpired:
                print(f"  --> Timeout downloading for {sid}")
            except Exception as e:
                print(f"  --> Failed to download for {sid}: {e}")
                
    finally:
        # Restore config afterwards
        restore_mops_config(mops_dir)

    print("\nRegenerating README.md...")
    update_readme()
    print("README.md regenerated successfully.")

if __name__ == "__main__":
    main()
