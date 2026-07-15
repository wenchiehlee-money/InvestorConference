import json
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

# 24 Stock IDs that have empty dates in README
stock_ids = [
    "2301", "2308", "2317", "2324", "2330", "2347", "2356", "2357", 
    "2382", "2408", "2412", "2454", "2458", "2480", "3022", "3034", 
    "3231", "4938", "6231", "6996", "7734", "7765", "7769", "8299"
]

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def expected_quarter(date_str: str) -> tuple[str | None, str | None]:
    """Return (year, quarter) the fiscal quarter reported on a given conference date."""
    if not date_str:
        return None, None
    try:
        y, mo = int(date_str[:4]), int(date_str[5:7])
    except (ValueError, IndexError):
        return None, None
    if 1 <= mo <= 4:
        return str(y - 1), "4"
    if 5 <= mo <= 6:
        return str(y), "1"
    if 7 <= mo <= 9:
        return str(y), "2"
    return str(y), "3"

def main():
    date_map = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=UA)
        
        for sid in stock_ids:
            print(f"Querying {sid}...")
            page = ctx.new_page()
            
            popup_html = [None]
            def on_popup(popup):
                try:
                    popup.wait_for_load_state("domcontentloaded", timeout=10000)
                    popup_html[0] = popup.content()
                except Exception:
                    pass
                
            ctx.on("page", on_popup)
            
            try:
                page.goto("https://mops.twse.com.tw/mops/#/web/t100sb07_1", wait_until="domcontentloaded", timeout=20000)
                page.fill("#co_id", sid)
                page.click("button.mainBtn")
                
                # Wait for popup up to 8s
                for _ in range(80):
                    if popup_html[0]:
                        break
                    page.wait_for_timeout(100)
                    
                if popup_html[0]:
                    html = popup_html[0]
                    pdfs = re.findall(rf'({re.escape(sid)}\d{{8}}[A-Z]\d{{3}}\.pdf)', html)
                    for fn in set(pdfs):
                        date_raw = fn[len(sid):len(sid)+8]
                        date_formatted = f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:8]}"
                        y, q = expected_quarter(date_formatted)
                        if y and q:
                            key = f"{sid}_{y}_q{q}"
                            date_map[key] = date_formatted
                    print(f"  Found {len(pdfs)} PDFs for {sid}")
                else:
                    print(f"  No popup captured for {sid}")
            except Exception as e:
                print(f"  Error querying {sid}: {e}")
            finally:
                page.close()
                ctx.remove_listener("page", on_popup)
                
        browser.close()
        
    # Save to file
    with open("mops_historical_dates.json", "w", encoding="utf-8") as f:
        json.dump(date_map, f, indent=2, ensure_ascii=False)
    print("Done. Saved to mops_historical_dates.json")

if __name__ == "__main__":
    main()
