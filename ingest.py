import sys
import shutil
import subprocess
import re
import warnings
import requests
from pathlib import Path

# Suppress InsecureRequestWarning for MOPS (Taiwan gov site SSL quirks on Windows)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# Smart Ingestion — Multi-Stock Support
# Version 5.0: standalone script inside InvestorConference repo

INVESTOR_CONFERENCE_REPO = Path(__file__).parent

# ── Company Name Lookup ───────────────────────────────────────────────────────
# (stock_id) -> (english_name, chinese_name)
KNOWN_TW_STOCKS = {
    "2330": ("TSMC", "台積電"),
    "2357": ("ASUS", "華碩"),
    "2317": ("Foxconn", "鴻海"),
    "2454": ("MediaTek", "聯發科"),
    "2382": ("Quanta", "廣達"),
    "3711": ("ASE", "日月光投控"),
    "2308": ("Delta Electronics", "台達電"),
    "2412": ("Chunghwa Telecom", "中華電信"),
    "2881": ("Fubon Financial", "富邦金"),
    "1301": ("Formosa Plastics", "台塑"),
    "6505": ("Formosa Petrochemical", "台塑化"),
    "2303": ("United Microelectronics", "聯電"),
    "2886": ("Mega Financial", "兆豐金"),
    "5871": ("CHAILEASE", "中租控股"),
    "2480": ("Stark Technology", "敦陽科"),
    "3231": ("Wistron", "緯創"),
    "3034": ("Novatek", "聯詠"),
    "8299": ("Phison", "群聯"),
    "4938": ("Pegatron", "和碩"),
    "2356": ("Inventec", "英業達"),
}

# Companies that host earnings call MP4 directly on their own IR site
# (stock_id -> IR earnings-call page URL)
# Simple requests-based scraper: looks for /documents/...mp4 links (e.g. STI Liferay portal)
KNOWN_TW_DIRECT_IR = {
    "2480": "https://www.sti.com.tw/web/official/earnings-call",  # Liferay portal, MP4 in /documents/
}

# JS-rendered IR pages: need Playwright to intercept network or scan DOM for video URLs
# (stock_id -> IR earnings-call page URL)
KNOWN_TW_PLAYWRIGHT_IR = {
    "2382": "https://www.quantatw.com/Quanta/chinese/investment/financials_icp.aspx",  # 廣達 — JS-rendered
    "8299": "https://www.phison.com/zh-tw/investor-relations/shareholder-services/investor-meeting-information",  # 群聯 — YouTube links in DOM
    "2330": "https://ottlive.hinet.net/webapp/tsmc/watch?v=2766",      # 台積電 2025Q4 — ottlive HLS m3u8 intercept
    "2454": "https://ottlive.hinet.net/webapp/mediatek/watch?v=3556",  # 聯發科 2025Q4 — ottlive HLS m3u8 intercept
    "2308": "https://www.deltaww.com/zh-TW/investors/analyst-meeting", # 台達電 — ccdntech.com HLS, video URL in HTML source
}

# IR portal URLs for Taiwan stocks that host webcast on their own IR sites
# (stock_id -> IR page URL)
KNOWN_TW_IR = {
    "2357": "https://www.asus.com/event/Investor/C/",  # ASUS — uses webcast-eqs.com
}

# Per-company PDF attachment URL templates (optional, keyed by stock_id)
# Use {year} and {quarter} placeholders
KNOWN_PDF_ATTACHMENTS = {
    "2357": [
        ("ir", "https://www.asus.com/event/Investor/Content/attachment/{year}Q{quarter}%20IR(Chinese).pdf"),
        ("qa", "https://www.asus.com/event/Investor/Content/attachment/{year}Q{quarter}_QA(Chinese).pdf"),
    ],
}

# IR portal URLs for US stocks (ticker -> IR URL)
KNOWN_US_IR = {
    "NVDA": "https://investor.nvidia.com/events-and-presentations/events/default.aspx",
    "AAPL": "https://investor.apple.com/investor-relations/events-and-presentations/",
    "MSFT": "https://www.microsoft.com/en-us/Investor/events/FY-2024/",
    "TSLA": "https://ir.tesla.com/events-and-presentations/events",
    "AMD":  "https://ir.amd.com/events-and-presentations",
}

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"


def detect_market(stock_id: str) -> str:
    """Detect if stock is Taiwan (numeric) or US (alphabetic)."""
    return "TW" if stock_id.isdigit() else "US"


def get_company_name(stock_id: str) -> tuple:
    """Return (english_name, chinese_name) for a stock ID."""
    if stock_id in KNOWN_TW_STOCKS:
        return KNOWN_TW_STOCKS[stock_id]

    if stock_id.isdigit():
        try:
            resp = requests.get(
                "https://openapi.twse.com.tw/v1/opendata/t187ap03_L", timeout=10,
            )
            for item in resp.json():
                if item.get("公司代號") == stock_id:
                    chi = item.get("公司簡稱", stock_id)
                    return (chi, chi)
        except Exception:
            pass

    return (stock_id, stock_id)


# ── TWSE irconference.twse.com.tw Direct Downloader ──────────────────────────

def scrape_tw_direct_ir(stock_id: str, ir_url: str, year: str, quarter: str) -> tuple:
    """
    Scrape a company IR page that hosts MP4 directly (e.g. STI Liferay portal).
    Looks for /documents/...mp4 links and picks the one matching year+quarter.

    Returns (mp4_url, conf_date_str) where conf_date_str is YYYYMMDD, or (None, None).
    Example: https://www.sti.com.tw/web/official/earnings-call
      → /documents/36928/73640/敦陽科法人說明會-20260310+0658-1.mp4/...
    Date pattern: YYYYMMDD in filename, match by year+quarter calendar mapping.
    """
    base = re.match(r'(https?://[^/]+)', ir_url).group(1)
    print(f"[Direct-IR] Fetching {ir_url} ...")
    try:
        resp = requests.get(ir_url, headers={"User-Agent": UA}, timeout=15, verify=False)
        html = resp.text.replace("&amp;", "&")

        # Collect all MP4 document links
        mp4_links = re.findall(r'(/documents/[^\s"\'<>&]+\.mp4[^\s"\'<>&]*)', html)
        if not mp4_links:
            print(f"[Direct-IR] No MP4 links found.")
            return None, None

        print(f"[Direct-IR] Found {len(mp4_links)} MP4 link(s).")

        # Quarter → expected conference month range
        if quarter == "4":
            target_year = str(int(year) + 1)
            month_min, month_max = 1, 4   # Q4 call held Jan–Apr of next year
        else:
            q_end = {"1": 3, "2": 6, "3": 9}[quarter]
            target_year = year
            month_min, month_max = q_end, q_end + 3

        for link in mp4_links:
            m = re.search(r'(\d{8})', link)
            if not m:
                continue
            date_str = m.group(1)
            y, mo = date_str[:4], int(date_str[4:6])
            if y == target_year and month_min <= mo <= month_max:
                full_url = f"{base}{link}"
                print(f"[Direct-IR] Matched: {full_url[:80]}...")
                return full_url, date_str

        # Fallback: first link (most recent)
        m = re.search(r'(\d{8})', mp4_links[0])
        date_str = m.group(1) if m else ""
        full_url = f"{base}{mp4_links[0]}"
        print(f"[Direct-IR] No exact match — using first: {full_url[:80]}...")
        return full_url, date_str

    except Exception as e:
        print(f"[Direct-IR] Failed: {e}")
    return None, None


# ── Taiwan IR Site Scraper ────────────────────────────────────────────────────

def scrape_tw_ir(stock_id: str, ir_url: str, year: str, quarter: str) -> str | None:
    """
    Scrape a Taiwan company's IR page for the earnings call webcast URL.

    ASUS (2357) example:
      IR page  : https://www.asus.com/event/Investor/C/
      HTML link: <a href='https://www.webcast-eqs.com/asus25q4/tc'>2025年第四季法人說明會</a>
      Slug rule: asus{YY}q{Q}  (e.g. asus25q4 for 2025 Q4)
    """
    print(f"[TW-IR] Fetching {ir_url} ...")
    try:
        resp = requests.get(ir_url, timeout=15, headers={"User-Agent": UA})
        html = resp.text

        webcast_urls = re.findall(
            r'https?://(?:www\.|asia\.)?webcast-eqs\.com/[a-zA-Z0-9]+/[a-zA-Z]+',
            html
        )
        if not webcast_urls:
            print(f"[TW-IR] No webcast-eqs.com links found.")
            return None

        print(f"[TW-IR] Found {len(webcast_urls)} webcast link(s).")

        yy = year[-2:]   # "2025" → "25"
        q  = quarter     # "4"
        slug_re = re.compile(rf'[a-zA-Z]+{re.escape(yy)}q{re.escape(q)}', re.IGNORECASE)

        for url in webcast_urls:
            slug = url.rstrip('/').split('/')[-2]
            if slug_re.match(slug):
                print(f"[TW-IR] Matched: {url}")
                return url

        # Fallback: first link (most recent entry at top of page)
        print(f"[TW-IR] No exact match — using first: {webcast_urls[0]}")
        return webcast_urls[0]

    except Exception as e:
        print(f"[TW-IR] Fetch failed: {e}")

    return None


# ── webcast-eqs.com Login + HLS Stream Extraction ────────────────────────────

def extract_webcast_eqs_stream(webcast_url: str) -> str | None:
    """
    Obtain the real HLS (.m3u8) stream URL from a webcast-eqs.com replay page.

    Flow:
      1. requests: GET register page → extract CSRF token + session cookie
      2. requests: POST registration form → get authenticated session cookie
      3. Playwright: load player page with session cookie, intercept network
                     requests until an .m3u8 URL is captured
    """
    # Derive the registration URL (replace /tc or /en suffix with /register/.../tc)
    # webcast_url e.g. https://www.webcast-eqs.com/asus25q4/tc
    base = webcast_url.rstrip('/')
    parts = base.split('/')
    lang = parts[-1]                        # "tc" or "en"
    code = parts[-2]                        # "asus25q4"
    register_url = f"https://www.webcast-eqs.com/register/{code}/{lang}"

    print(f"[webcast-eqs] Logging in via {register_url} ...")

    # ── Step 1 & 2: requests-based login ─────────────────────────────────────
    session = requests.Session()
    session.headers.update({"User-Agent": UA})

    try:
        r1 = session.get(register_url, timeout=15)
        token_m = re.search(r'name="_token"\s+value="([^"]+)"', r1.text)
        if not token_m:
            print(f"[webcast-eqs] Could not find CSRF token.")
            return None
        token = token_m.group(1)

        r2 = session.post(
            f"https://www.webcast-eqs.com/active-collection/{code}",
            data={
                "_token":         token,
                "activeCollection": "1",
                "language":       lang,
                "name":           "Investor",
                "company":        "Individual",
                "email":          "investor@example.com",
                "identitiy":      "投資者",   # note: typo in original form field name
                "disclaimer":     "accepted",
            },
            allow_redirects=True,
            headers={
                "Referer": register_url,
                "Origin":  "https://www.webcast-eqs.com",
            },
            timeout=20,
        )

        if "register" in r2.url:
            print(f"[webcast-eqs] Login failed (redirected back to register).")
            return None

        print(f"[webcast-eqs] Logged in → {r2.url}")

    except Exception as e:
        print(f"[webcast-eqs] Login request failed: {e}")
        return None

    # Convert requests cookies to Playwright format
    pw_cookies = [
        {"name": c.name, "value": c.value, "domain": ".webcast-eqs.com", "path": "/"}
        for c in session.cookies
    ]

    # ── Step 3: Playwright intercepts the HLS stream request ─────────────────
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(f"[webcast-eqs] playwright not installed. Run: pip install playwright && python -m playwright install chromium")
        return None

    m3u8_url = None

    def on_request(request):
        nonlocal m3u8_url
        if m3u8_url is None and ".m3u8" in request.url:
            m3u8_url = request.url
            print(f"[webcast-eqs] HLS stream: {m3u8_url}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(user_agent=UA)
            ctx.add_cookies(pw_cookies)

            page = ctx.new_page()
            page.on("request", on_request)

            print(f"[webcast-eqs] Loading player page ...")
            page.goto(webcast_url, wait_until="domcontentloaded")

            # Wait up to 25 s for the player to start the HLS stream
            for _ in range(25):
                if m3u8_url:
                    break
                page.wait_for_timeout(1000)

            browser.close()

    except Exception as e:
        print(f"[webcast-eqs] Playwright error: {e}")

    if not m3u8_url:
        print(f"[webcast-eqs] No HLS stream intercepted.")

    return m3u8_url


# ── MOPS Scraper (Taiwan) ─────────────────────────────────────────────────────

def scrape_mops_tw(stock_id: str, year: str, quarter: str) -> str | None:
    """
    Query MOPS (公開資訊觀測站) 法說會影音 for a Taiwan-listed stock.
    Returns a YouTube URL or direct media URL if found, else None.
    """
    roc_year = int(year) - 1911
    print(f"[MOPS] Querying {stock_id} {year}(民{roc_year}) Q{quarter} ...")

    try:
        resp = requests.post(
            "https://mops.twse.com.tw/mops/web/ajax_t100sb04",
            data={
                "encodeURIComponent": "1",
                "step": "1", "firstin": "1", "off": "1",
                "co_id": stock_id,
                "year":  str(roc_year),
                "season": quarter,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer":      "https://mops.twse.com.tw/mops/web/t100sb04",
                "User-Agent":   UA,
            },
            timeout=15,
            verify=False,
        )
        html = resp.text

        yt_ids = re.findall(r'(?:v=|embed/|video/|youtu\.be/)([a-zA-Z0-9_-]{11})', html)
        if yt_ids:
            url = f"https://www.youtube.com/watch?v={yt_ids[0]}"
            print(f"[MOPS] Found YouTube: {url}")
            return url

        media = re.findall(r'href=["\']([^"\']*\.(?:mp4|m4a|mp3|wav)[^"\']*)["\']', html)
        if media:
            print(f"[MOPS] Found media: {media[0]}")
            return media[0]

        print(f"[MOPS] No media found (JS-rendered or no record).")

    except Exception as e:
        print(f"[MOPS] Failed: {e}")

    return None


# ── MOPS Playwright Scraper ───────────────────────────────────────────────────

def scrape_mops_playwright(stock_id: str, year: str, quarter: str) -> dict:
    """
    Use Playwright to navigate mops.twse.com.tw/mops/#/web/t100sb07_1,
    type the stock_id, intercept the ajax_t100sb07_1 XHR request,
    then parse the response for video URL and PDF filenames.

    Returns dict with keys:
      'ajax_url'  : full ajax URL (with encrypted parameters)
      'video_url' : irconference.twse.com.tw MP4 URL or None
      'pdfs'      : list of (filename, mopsov_url) tuples
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[MOPS-PW] playwright not installed.")
        return {}

    result = {"ajax_url": None, "video_url": None, "pdfs": []}
    ajax_url_captured = [None]

    print(f"[MOPS-PW] Launching browser for stock {stock_id} ...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(user_agent=UA)

            # MOPS opens the result in a NEW PAGE (popup) — intercept context.on("page")
            def on_new_page(popup):
                url = popup.url
                if "ajax_t100sb07_1" in url and ajax_url_captured[0] is None:
                    ajax_url_captured[0] = url
                    print(f"[MOPS-PW] Popup URL: {url[:100]}...")

            ctx.on("page", on_new_page)

            page = ctx.new_page()
            page.goto("https://mops.twse.com.tw/mops/#/web/t100sb07_1",
                      wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)

            # Fill stock_id into #co_id (confirmed selector)
            page.fill("#co_id", stock_id)
            print(f"[MOPS-PW] Filled #co_id with {stock_id}")
            page.wait_for_timeout(500)

            # Click 查詢 button (button.mainBtn confirmed)
            page.click("button.mainBtn")
            print(f"[MOPS-PW] Clicked 查詢")

            # Wait for popup up to 15s
            for _ in range(15):
                if ajax_url_captured[0]:
                    break
                page.wait_for_timeout(1000)

            browser.close()
    except Exception as e:
        print(f"[MOPS-PW] Browser error: {e}")
        return result

    if not ajax_url_captured[0]:
        print(f"[MOPS-PW] No popup with ajax_t100sb07_1 detected.")
        return result

    result["ajax_url"] = ajax_url_captured[0]

    # Fetch the ajax URL and parse for video + PDFs
    try:
        resp = requests.get(
            ajax_url_captured[0],
            headers={"User-Agent": UA,
                     "Referer": "https://mops.twse.com.tw/mops/"},
            timeout=15, verify=False,
        )
        html = resp.text

        # Video: irconference.twse.com.tw MP4 (may be absolute or relative)
        vids = re.findall(r'(https?://irconference\.twse\.com\.tw/[^\s"\'<>]+\.mp4)', html)
        if not vids:
            # Sometimes the URL is relative: /irconference/...mp4 or just the filename
            vids_rel = re.findall(r'(?:href|src)=["\']([^"\']*irconference[^"\']*\.mp4)["\']', html, re.I)
            vids = [v if v.startswith("http") else f"http://irconference.twse.com.tw/{v.lstrip('/')}"
                    for v in vids_rel]
        if vids:
            result["video_url"] = vids[0]
            print(f"[MOPS-PW] Video: {vids[0]}")
        else:
            print(f"[MOPS-PW] No video URL found in MOPS response.")

        # PDFs: {stock_id}YYYYMMDD{M|E}001.pdf
        pdfs = re.findall(rf'({re.escape(stock_id)}\d{{8}}[A-Z]\d{{3}}\.pdf)', html)
        for fn in dict.fromkeys(pdfs):   # deduplicate preserving order
            url = f"https://mopsov.twse.com.tw/nas/STR/{fn}"
            result["pdfs"].append((fn, url))
            print(f"[MOPS-PW] PDF: {fn}")

    except Exception as e:
        print(f"[MOPS-PW] Parse error: {e}")

    return result


# ── JS-rendered Direct-IR Scraper (Playwright) ───────────────────────────────

def scrape_playwright_direct_ir(stock_id: str, ir_url: str, year: str, quarter: str) -> tuple:
    """
    Use Playwright to render a JS-heavy IR page and intercept video URLs.

    Intercepts network responses for .mp4 / .m3u8 and also scans DOM for
    <video src>, <source src>, and <iframe src> with video players.
    Matches by year+quarter calendar range.

    Returns (video_url, conf_date_str) or (None, None).

    Example: quantatw.com — JS dynamically loads icp player with MP4 links.
    Quarter date mapping:
      Q4 → target_year=year+1, months Jan–Apr
      Q1 → target_year=year, months Apr–Jun
      Q2 → target_year=year, months Jul–Sep
      Q3 → target_year=year, months Oct–Dec
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[PW-IR] playwright not installed — pip install playwright && playwright install chromium")
        return None, None

    # Quarter → expected conference month range
    if quarter == "4":
        target_year = str(int(year) + 1)
        month_min, month_max = 1, 4
    elif quarter == "1":
        target_year = year
        month_min, month_max = 4, 6
    elif quarter == "2":
        target_year = year
        month_min, month_max = 7, 9
    else:  # Q3
        target_year = year
        month_min, month_max = 10, 12

    captured_videos = []   # list of (url, date_str)

    def on_response(response):
        url = response.url
        # Intercept any .mp4 or .m3u8 network request
        if re.search(r'\.(mp4|m3u8|flv)(\?|$)', url, re.I):
            m = re.search(r'(\d{8})', url)
            date_str = m.group(1) if m else ""
            captured_videos.append((url, date_str))
            print(f"[PW-IR] Intercepted video: {url[:80]}...")

    print(f"[PW-IR] Launching browser for {ir_url} ...")
    dom_videos = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=UA)
            page.on("response", on_response)

            page.goto(ir_url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)  # let lazy JS finish

            # Scan DOM for video/source/iframe src attrs
            for attr in ["video[src]", "source[src]", "a[href]"]:
                try:
                    els = page.query_selector_all(attr)
                    for el in els:
                        src = el.get_attribute("src") or el.get_attribute("href") or ""
                        if re.search(r'\.(mp4|m3u8|flv)(\?|$)', src, re.I):
                            m = re.search(r'(\d{8})', src)
                            date_str = m.group(1) if m else ""
                            dom_videos.append((src, date_str))
                            print(f"[PW-IR] DOM video: {src[:80]}...")
                        elif re.search(r'(?:youtu\.be/|youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})', src):
                            dom_videos.append((src, ""))
                            print(f"[PW-IR] DOM YouTube: {src[:80]}...")
                except Exception:
                    pass

            browser.close()
    except Exception as e:
        print(f"[PW-IR] Browser error: {e}")
        return None, None

    all_videos = captured_videos + dom_videos
    if not all_videos:
        print(f"[PW-IR] No video URLs found on {ir_url}")
        return None, None

    print(f"[PW-IR] Total video candidates: {len(all_videos)}")

    # Try to match by year+quarter date range
    for url, date_str in all_videos:
        if len(date_str) == 8:
            y, mo = date_str[:4], int(date_str[4:6])
            if y == target_year and month_min <= mo <= month_max:
                print(f"[PW-IR] Matched Q{quarter} {year}: {url[:80]}...")
                return url, date_str

    # For YouTube URLs without date: check title via yt-dlp
    yt_candidates = [(u, d) for u, d in all_videos
                     if re.search(r'(?:youtu\.be/|youtube\.com/watch)', u)]
    if yt_candidates:
        q_str = f"Q{quarter}"
        for yt_url, _ in yt_candidates:
            try:
                r = subprocess.run(
                    ["yt-dlp", "--get-title", "--no-warnings", yt_url],
                    capture_output=True, encoding="utf-8", errors="replace", timeout=15,
                )
                title = r.stdout.strip()
                if target_year in title or (year in title and q_str.lower() in title.lower()):
                    print(f"[PW-IR] YouTube title match: {title}")
                    return yt_url, ""
            except Exception:
                continue
        # No title match — use first YouTube candidate (most recent = first on page)
        url, _ = yt_candidates[0]
        print(f"[PW-IR] YouTube fallback (first on page): {url[:80]}...")
        return url, ""

    # Fallback: first intercepted (most recent)
    url, date_str = all_videos[0]
    print(f"[PW-IR] No exact Q{quarter} {year} match — using first: {url[:80]}...")
    return url, date_str


# ── IR Site Scraper (US) ──────────────────────────────────────────────────────

def scrape_ir_site(ir_url: str, year: str, quarter: str) -> str | None:
    """Scrape a US IR page for YouTube video IDs matching year/quarter."""
    print(f"[IR] Fetching {ir_url} ...")
    try:
        resp = requests.get(ir_url, timeout=15, headers={"User-Agent": UA})
        html = resp.text

        yt_ids = re.findall(r'(?:v=|embed/|video/|youtu\.be/)([a-zA-Z0-9_-]{11})', html)
        if not yt_ids:
            print(f"[IR] No YouTube IDs found (likely JS-rendered).")
            return None

        print(f"[IR] Found {len(yt_ids)} YouTube ID(s).")
        q_str = f"Q{quarter}"
        for vid_id in yt_ids:
            check_url = f"https://www.youtube.com/watch?v={vid_id}"
            try:
                r = subprocess.run(
                    ["yt-dlp", "--get-title", "--no-warnings", check_url],
                    capture_output=True, encoding="utf-8", errors="replace", timeout=10,
                )
                title = r.stdout.strip()
                if year in title and q_str.lower() in title.lower():
                    print(f"[IR] Matched: {title}")
                    return check_url
            except Exception:
                continue

        fallback = f"https://www.youtube.com/watch?v={yt_ids[0]}"
        print(f"[IR] No exact match — using first: {fallback}")
        return fallback

    except Exception as e:
        print(f"[IR] Failed: {e}")

    return None


# ── yt-dlp Downloader ─────────────────────────────────────────────────────────

def download_audio(source: str, output_path: Path,
                   match_title: str = None, no_check_cert: bool = False) -> bool:
    """
    Download audio from a URL or yt-dlp search query.
    Returns True if output file exists after the attempt.
    """
    cmd = [
        "yt-dlp", source,
        "--extract-audio",
        "--audio-format", "m4a",
        "--audio-quality", "0",
        "--output", str(output_path),
        "--no-playlist",
        "--no-warnings",
    ]
    if match_title:
        cmd += ["--match-filter", f"title~='{match_title}'"]
    if no_check_cert:
        cmd += ["--no-check-certificates"]

    print(f"[yt-dlp] {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")

    if not output_path.exists() and result.stderr:
        lines = [l for l in result.stderr.splitlines() if l.strip()]
        for line in lines[-3:]:
            print(f"[yt-dlp] {line}")

    return output_path.exists()


# ── MOPS PDF Downloader ───────────────────────────────────────────────────────

def download_mops_pdfs(stock_id: str, conf_date: str, year: str, quarter: str,
                       save_dir: Path) -> list:
    """
    Download 法說會簡報 PDFs from mopsov.twse.com.tw/nas/STR/.
    Naming: {stock_id}{YYYYMMDD}{M|E}001.pdf  (M=中文, E=英文)
    conf_date: YYYYMMDD string from conference MP4 filename.
    Tries conf_date and ±2 days to handle filing-vs-conference date mismatch.
    Saves as {stock_id}_{year}_q{quarter}_ir.pdf / _ir_en.pdf.
    """
    if not conf_date:
        return []

    from datetime import datetime, timedelta
    base_url = "https://mopsov.twse.com.tw/nas/STR/"
    referer  = "https://mopsov.twse.com.tw/mops/web/t100sb07"

    try:
        base_dt = datetime.strptime(conf_date, "%Y%m%d")
    except ValueError:
        return []

    suffix_map = [("M", f"{stock_id}_{year}_q{quarter}_ir.pdf"),
                  ("E", f"{stock_id}_{year}_q{quarter}_ir_en.pdf")]
    downloaded = []

    for lang_code, dest_name in suffix_map:
        dest = save_dir / dest_name
        if dest.exists():
            print(f"[MOPS-PDF] Already exists: {dest_name}")
            downloaded.append(dest)
            continue
        found = False
        for delta in range(-2, 3):          # try ±2 days
            probe_date = (base_dt + timedelta(days=delta)).strftime("%Y%m%d")
            fn  = f"{stock_id}{probe_date}{lang_code}001.pdf"
            url = base_url + fn
            try:
                r = requests.get(
                    url,
                    headers={"User-Agent": UA, "Referer": referer},
                    timeout=20, verify=False,
                )
                if r.status_code == 200 and r.content[:4] == b"%PDF":
                    dest.write_bytes(r.content)
                    print(f"[MOPS-PDF] ✓ {fn} → {dest_name} ({len(r.content)//1024}KB)")
                    downloaded.append(dest)
                    found = True
                    break
            except Exception:
                continue
        if not found:
            print(f"[MOPS-PDF] ✗ {lang_code} PDF not found (tried ±2 days around {conf_date})")

    return downloaded


# ── PDF Downloader ────────────────────────────────────────────────────────────

def download_pdfs(stock_id: str, year: str, quarter: str,
                  save_dir: Path) -> list:
    """
    Download PDF attachments (IR slides, Q&A) for a given stock/year/quarter.
    Returns list of downloaded Path objects.
    """
    templates = KNOWN_PDF_ATTACHMENTS.get(stock_id, [])
    if not templates:
        return []

    downloaded = []
    for suffix, url_template in templates:
        url = url_template.format(year=year, quarter=quarter)
        filename = f"{stock_id}_{year}_q{quarter}_{suffix}.pdf"
        dest = save_dir / filename

        if dest.exists():
            print(f"[PDF] Already downloaded: {dest}")
            downloaded.append(dest)
            continue

        print(f"[PDF] Downloading {suffix.upper()}: {url}")
        try:
            resp = requests.get(url, timeout=30, headers={"User-Agent": UA}, stream=True)
            if resp.status_code == 200:
                with open(dest, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=65536):
                        f.write(chunk)
                print(f"[PDF] ✓ Saved: {dest} ({dest.stat().st_size // 1024} KB)")
                downloaded.append(dest)
            else:
                print(f"[PDF] ✗ HTTP {resp.status_code}: {url}")
        except Exception as e:
            print(f"[PDF] ✗ Failed: {e}")

    return downloaded


# ── README Generator ─────────────────────────────────────────────────────────

def update_readme() -> None:
    """Regenerate README.md from repo state + upcoming_earnings.csv."""
    import csv as _csv

    repo = INVESTOR_CONFERENCE_REPO
    audio_pat  = re.compile(r'^(\d{4})_(\d{4})_q(\d)\.(mp3|m4a|wav)$', re.I)
    pdf_cn_pat = re.compile(r'^(\d{4})_(\d{4})_q(\d)_ir\.pdf$', re.I)
    pdf_en_pat = re.compile(r'^(\d{4})_(\d{4})_q(\d)_ir_en\.pdf$', re.I)

    entries = {}  # key=(stock_id, year, quarter) → dict

    def _entry(stock_id, year, qnum):
        key = (stock_id, year, qnum)
        if key not in entries:
            entries[key] = {"stock_id": stock_id, "year": year, "quarter": qnum,
                            "audio_min": None, "audio_path": None, "pdf_cn": None, "pdf_en": None}
        return entries[key]

    for d in sorted(repo.iterdir()):
        if not d.is_dir() or not re.match(r'^\d{4}$', d.name):
            continue
        stock_id = d.name
        for f in sorted(d.iterdir()):
            m = audio_pat.match(f.name)
            if m:
                _, year, qnum, _ = m.groups()
                e = _entry(stock_id, year, qnum)
                e["audio_path"] = f"{stock_id}/{f.name}"
                try:
                    r = subprocess.run(
                        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                         "-of", "csv=p=0", str(f)],
                        capture_output=True, encoding="utf-8", errors="replace", timeout=15,
                    )
                    e["audio_min"] = float(r.stdout.strip()) / 60
                except Exception:
                    pass
            m2 = pdf_cn_pat.match(f.name)
            if m2:
                _, year, qnum = m2.groups()[:3]
                _entry(stock_id, year, qnum)["pdf_cn"] = f"{stock_id}/{f.name}"
            m3 = pdf_en_pat.match(f.name)
            if m3:
                _, year, qnum = m3.groups()[:3]
                _entry(stock_id, year, qnum)["pdf_en"] = f"{stock_id}/{f.name}"

    rows = list(entries.values())

    # Read upcoming_earnings.csv — all event types (法說會 + 財報公告)
    upcoming_ir = []
    csv_path = repo / "upcoming_earnings.csv"
    if csv_path.exists():
        with open(csv_path, encoding="utf-8-sig") as fh:
            for row in _csv.DictReader(fh):
                upcoming_ir.append(row)

    def _expected_quarter(date_str: str):
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

    # Build merged rows: one row per CSV event (with optional ingested data),
    # plus any ingested entries that have no matching CSV event.
    from datetime import date as _date, timedelta
    today     = _date.today()
    two_weeks = today + timedelta(weeks=4)

    merged = []
    matched_keys = set()

    for ev in upcoming_ir:
        ev_name  = ev.get("事件名稱", "")
        ev_class = ev.get("類別", "")
        date     = ev.get("開始日期", "")
        link1    = ev.get("Link1", "")
        m = re.search(r'[（(](\d{4})[）)]', ev_name)
        sid = m.group(1) if m else None

        # Only 法說會 events are matched to ingested audio/PDF data
        exp_year, exp_q = _expected_quarter(date)
        ingested = None
        if ev_class == "法說會" and sid and exp_year:
            key = (sid, exp_year, exp_q)
            for r in rows:
                if (r["stock_id"], r["year"], r["quarter"]) == key:
                    ingested = r
                    matched_keys.add(key)
                    break

        # Normalise company name: prefer KNOWN_TW_STOCKS, else parse from event name
        if sid:
            _, chi = KNOWN_TW_STOCKS.get(sid, ("", ""))
            if not chi:
                # e.g. "鴻海(2317) 法說會" → "鴻海"
                chi = re.sub(r'[（(]\d{4}[）)].*', '', ev_name).strip()
            display_name = f"{sid} {chi}"
        else:
            # Clean duplicate tickers e.g. "台積電(TSM)(TSM) 財報" → "台積電(TSM) 財報"
            display_name = re.sub(r'\((\w+)\)\(\1\)', r'(\1)', ev_name)

        if ingested:
            name   = display_name
            qstr   = f"{ingested['year']} Q{ingested['quarter']}"
            dur    = f"{ingested['audio_min']:.1f} min" if ingested["audio_min"] is not None else "無"
            audio  = f"[{dur}]({ingested['audio_path']})" if ingested["audio_path"] else dur
            pdf_cn = f"[中]({ingested['pdf_cn']})" if ingested["pdf_cn"] else "—"
            pdf_en = f"[EN]({ingested['pdf_en']})" if ingested["pdf_en"] else "—"
        else:
            # CSV-only row (not yet ingested): only include if within next 2 weeks
            try:
                ev_date = _date.fromisoformat(date)
                if not (today <= ev_date <= two_weeks):
                    continue
            except (ValueError, TypeError):
                continue
            name   = display_name
            qstr   = "—"
            audio  = "—"
            pdf_cn = "—"
            pdf_en = "—"

        merged.append({
            "name": name, "quarter": qstr, "date": date,
            "audio": audio, "pdf_cn": pdf_cn, "pdf_en": pdf_en,
            "mops": f"[↗]({link1})" if link1 else "",
        })

    # Add ingested entries with no CSV event (older quarters, etc.)
    for r in rows:
        key = (r["stock_id"], r["year"], r["quarter"])
        if key in matched_keys:
            continue
        _, chi = KNOWN_TW_STOCKS.get(r["stock_id"], (r["stock_id"], r["stock_id"]))
        dur    = f"{r['audio_min']:.1f} min" if r["audio_min"] is not None else "無"
        audio  = f"[{dur}]({r['audio_path']})" if r["audio_path"] else dur
        pdf_cn = f"[中]({r['pdf_cn']})" if r["pdf_cn"] else "—"
        pdf_en = f"[EN]({r['pdf_en']})" if r["pdf_en"] else "—"
        merged.append({
            "name":    f"{r['stock_id']} {chi}",
            "quarter": f"{r['year']} Q{r['quarter']}",
            "date":    "",
            "audio":   audio,
            "pdf_cn":  pdf_cn,
            "pdf_en":  pdf_en,
            "mops":    "",
        })

    # Sort by date descending (newest first); entries without date sink to the bottom
    merged.sort(key=lambda x: (x["date"] != "", x["date"]), reverse=True)

    # Build README
    lines = [
        "# InvestorConference",
        "",
        "台股法人說明會（法說會）音檔與投資人關係資料收錄庫。",
        "",
        "## 法說會一覽",
        "",
        "| 公司 | 季度 | 法說日期 | 音檔 | IR (TW) | IR (EN) | MOPS |",
        "|:-----|:----:|:--------:|-----:|:-------:|:-------:|:----:|",
    ]
    for m in merged:
        lines.append(
            f"| {m['name']} | {m['quarter']} | {m['date']} "
            f"| {m['audio']} | {m['pdf_cn']} | {m['pdf_en']} | {m['mops']} |"
        )

    lines.append("")

    readme_path = repo / "README.md"
    readme_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[README] ✓ Updated: {readme_path}")


# ── InvestorConference Commit/Push ───────────────────────────────────────────

def commit_push_files(stock_id: str, year: str, quarter: str,
                      audio_path: Path, pdf_paths: list = None) -> str | None:
    """
    Move the downloaded audio (and optional PDFs) into InvestorConference/<stock_id>/,
    commit (git-lfs for .m4a), push, then remove local whisper-sandbox copies.

    Returns the new audio path inside InvestorConference, or None on failure.
    """
    repo = INVESTOR_CONFERENCE_REPO
    if not repo.exists():
        print(f"[git] InvestorConference repo not found at {repo}")
        return None

    target_dir = repo / stock_id
    target_dir.mkdir(exist_ok=True)

    def git(*args):
        result = subprocess.run(
            ["git", "-C", str(repo)] + list(args),
            capture_output=True, encoding="utf-8", errors="replace",
        )
        if result.returncode != 0 and result.stderr:
            print(f"[git] {' '.join(args)}: {result.stderr.strip()}")
        return result.returncode == 0

    # Move audio
    target_audio = target_dir / audio_path.name
    shutil.move(str(audio_path), str(target_audio))
    print(f"[git] Moved → {target_audio}")
    git("add", str(target_audio.relative_to(repo)))

    # Move PDFs
    for pdf in (pdf_paths or []):
        target_pdf = target_dir / pdf.name
        shutil.move(str(pdf), str(target_pdf))
        print(f"[git] Moved → {target_pdf}")
        git("add", str(target_pdf.relative_to(repo)))

    # Regenerate README.md and stage it
    update_readme()
    git("add", "README.md")

    extras = f" + {len(pdf_paths)} PDF(s)" if pdf_paths else ""
    msg = (f"feat: add {stock_id} {year} Q{quarter} earnings call audio{extras}\n\n"
           f"Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>")
    if not git("commit", "-m", msg):
        print(f"[git] commit failed")
        return str(target_audio)

    print(f"[git] Committed. Pushing (LFS upload may take a moment) ...")
    if git("push", "origin", "main"):
        print(f"[git] ✓ Pushed to InvestorConference/{stock_id}/")
    else:
        print(f"[git] push failed — committed locally, push manually.")

    return str(target_audio)


# ── Main Ingestion Function ───────────────────────────────────────────────────

def ingest_earnings_audio(stock_id: str, year: str, quarter: str,
                          auto_push: bool = False) -> str | None:
    """
    Main entry point. Pipeline per market:

    Taiwan:
      1. Company IR site → webcast-eqs.com login → Playwright HLS intercept → yt-dlp
      2. MOPS (公開資訊觀測站) → irconference MP4 or company-linked YouTube URL → yt-dlp

    US:
      1. Known IR portal → company-linked YouTube ID → yt-dlp

    If auto_push=True: on success, moves audio to InvestorConference repo,
    commits via git-lfs, pushes, and removes local copy.
    """
    save_dir = Path(__file__).parent / "tmp"
    save_dir.mkdir(exist_ok=True)

    market    = detect_market(stock_id)
    eng_name, chi_name = get_company_name(stock_id)

    print(f"=== Smart Ingestion v5.0 ===")
    print(f"Stock  : {stock_id} ({eng_name} / {chi_name})")
    print(f"Market : {market}")
    print(f"Target : {year} Q{quarter}")
    print(f"Push   : {'yes → InvestorConference' if auto_push else 'no (local only)'}")
    print()

    output_path = save_dir / f"{stock_id}_{year}_q{quarter}.m4a"
    _conf_date: list = [None]   # mutable cell so inner functions can write it

    def verify_audio_length(path: Path, min_minutes: float = 45.0) -> bool:
        """Verify audio is at least min_minutes long using ffprobe."""
        try:
            r = subprocess.run(
                ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                 "-of", "csv=p=0", str(path)],
                capture_output=True, encoding="utf-8", errors="replace", timeout=15,
            )
            duration_sec = float(r.stdout.strip())
            minutes = duration_sec / 60
            print(f"[Verify] Audio length: {minutes:.1f} min", end="")
            if minutes < min_minutes:
                print(f" ✗ TOO SHORT (expected ≥{min_minutes:.0f} min) — rejecting")
                path.unlink(missing_ok=True)
                return False
            print(f" ✓")
            return True
        except Exception as e:
            print(f"[Verify] ffprobe failed: {e} — skipping length check")
            return True  # don't reject if ffprobe unavailable

    def done() -> str:
        """Called after every successful audio download — also downloads PDFs."""
        print(f"\n✓ SUCCESS: {output_path}")
        if not verify_audio_length(output_path):
            return None
        pdf_paths = download_pdfs(stock_id, year, quarter, save_dir)
        # MOPS PDFs — use conf_date discovered during audio scraping
        if _conf_date[0]:
            mops_pdfs = download_mops_pdfs(
                stock_id, _conf_date[0], year, quarter, save_dir)
            pdf_paths = pdf_paths + [p for p in mops_pdfs if p not in pdf_paths]
        if auto_push:
            pushed = commit_push_files(stock_id, year, quarter, output_path, pdf_paths)
            return pushed or str(output_path)
        return str(output_path)

    if output_path.exists():
        print(f"[Cache] Already downloaded: {output_path}")
        # Still resolve conf_date for MOPS PDF lookup
        if detect_market(stock_id) == "TW":
            direct_ir_url = KNOWN_TW_DIRECT_IR.get(stock_id)
            if direct_ir_url:
                _, conf_date = scrape_tw_direct_ir(stock_id, direct_ir_url, year, quarter)
                _conf_date[0] = conf_date
            elif KNOWN_TW_PLAYWRIGHT_IR.get(stock_id):
                pw_ir_url = KNOWN_TW_PLAYWRIGHT_IR[stock_id]
                _, conf_date = scrape_playwright_direct_ir(stock_id, pw_ir_url, year, quarter)
                _conf_date[0] = conf_date
        return done()

    target_url = None

    # ── Taiwan Pipeline ───────────────────────────────────────────────────────
    if market == "TW":

        # Step 0a: Company direct IR site with hosted MP4 (simple requests, e.g. STI Liferay)
        direct_ir_url = KNOWN_TW_DIRECT_IR.get(stock_id)
        if direct_ir_url:
            mp4_url, conf_date = scrape_tw_direct_ir(stock_id, direct_ir_url, year, quarter)
            if mp4_url:
                _conf_date[0] = conf_date   # store for MOPS PDF lookup in done()
                print(f"\n[Direct-IR] Downloading: {mp4_url[:80]}...")
                if download_audio(mp4_url, output_path, no_check_cert=True):
                    return done()
                print(f"[Direct-IR] yt-dlp failed. Falling back...")

        # Step 0b: JS-rendered IR site (Playwright intercept, e.g. quantatw.com for 廣達)
        pw_ir_url = KNOWN_TW_PLAYWRIGHT_IR.get(stock_id)
        if pw_ir_url:
            mp4_url, conf_date = scrape_playwright_direct_ir(stock_id, pw_ir_url, year, quarter)
            if mp4_url:
                _conf_date[0] = conf_date
                print(f"\n[PW-IR] Downloading: {mp4_url[:80]}...")
                if download_audio(mp4_url, output_path, no_check_cert=True):
                    return done()
                print(f"[PW-IR] yt-dlp failed. Falling back...")

        # Step 1: Company IR site → webcast-eqs.com → Playwright HLS intercept
        ir_url = KNOWN_TW_IR.get(stock_id)
        if ir_url:
            webcast_url = scrape_tw_ir(stock_id, ir_url, year, quarter)
            if webcast_url:
                hls_url = extract_webcast_eqs_stream(webcast_url)
                if hls_url:
                    print(f"\n[HLS] Downloading: {hls_url}")
                    if download_audio(hls_url, output_path, no_check_cert=True):
                        return done()
                    print(f"[HLS] yt-dlp failed on HLS stream.")
                else:
                    print(f"[webcast-eqs] Could not extract HLS. Falling back...")

        # Step 2: MOPS via Playwright (intercepts ajax_t100sb07_1 XHR)
        mops_data = scrape_mops_playwright(stock_id, year, quarter)
        if mops_data.get("video_url"):
            print(f"\n[MOPS-PW] Downloading video: {mops_data['video_url']}")
            if download_audio(mops_data["video_url"], output_path, no_check_cert=True):
                # Extract conf_date from irconference URL filename
                m = re.search(r'_(\d{8})_', mops_data["video_url"])
                if m:
                    _conf_date[0] = m.group(1)
                return done()
        elif mops_data.get("pdfs"):
            # No video but has PDFs — download them directly
            print(f"[MOPS-PW] No video, but found {len(mops_data['pdfs'])} PDF(s) — downloading.")
            for fn, pdf_url in mops_data["pdfs"]:
                # Infer lang suffix from filename (M=中文, E=英文)
                lang = "ir_en" if fn[len(stock_id)+8] == "E" else "ir"
                dest = save_dir / f"{stock_id}_{year}_q{quarter}_{lang}.pdf"
                if not dest.exists():
                    try:
                        r = requests.get(pdf_url, headers={"User-Agent": UA,
                            "Referer": "https://mopsov.twse.com.tw/"}, timeout=30, verify=False)
                        if r.status_code == 200 and r.content[:4] == b"%PDF":
                            dest.write_bytes(r.content)
                            print(f"[MOPS-PW] ✓ {dest.name} ({len(r.content)//1024}KB)")
                    except Exception as e:
                        print(f"[MOPS-PW] PDF download failed: {e}")
        else:
            # Fallback: original requests-based MOPS scraper
            mops_url = scrape_mops_tw(stock_id, year, quarter)
            if mops_url:
                target_url = mops_url

    # ── US Pipeline ───────────────────────────────────────────────────────────
    else:
        ir_url = KNOWN_US_IR.get(stock_id.upper())
        if ir_url:
            target_url = scrape_ir_site(ir_url, year, quarter)

    # ── Direct URL Download (MOPS / IR scraper result) ────────────────────────
    if target_url:
        print(f"\n[Download] {target_url}")
        if download_audio(target_url, output_path):
            return done()

    print(f"\n✗ FAILED: Could not find audio for {stock_id} {year} Q{quarter}")
    return None


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Smart Ingestion v5.0 — Earnings Call Audio Downloader"
    )
    parser.add_argument("stock_id", nargs="?", help="Stock ID (e.g. 2357, NVDA)")
    parser.add_argument("year",     nargs="?", help="Year (e.g. 2025)")
    parser.add_argument("quarter",  nargs="?", help="Quarter (1-4)")
    parser.add_argument(
        "--push", action="store_true",
        help="After download, commit + push to InvestorConference repo",
    )
    parser.add_argument(
        "--update-readme", action="store_true",
        help="Regenerate README.md from repo state + upcoming_earnings.csv, then exit",
    )
    args = parser.parse_args()

    if args.update_readme:
        update_readme()
    elif args.stock_id and args.year and args.quarter:
        ingest_earnings_audio(args.stock_id, args.year, args.quarter,
                              auto_push=args.push)
    else:
        parser.print_help()
