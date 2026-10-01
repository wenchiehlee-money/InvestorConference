#!/usr/bin/env python3
"""Generate the canonical investor-material matrix for InvestorConference.

The CSV is the machine-readable source.  The Markdown file is a generated
human-readable view of the same rows.  Each populated cell is a link to the
artifact that caused the flag to be present.
"""

import csv
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
MOPS_ROOT = ROOT.parent / "MOPS"
CSV_OUTPUT = ROOT / "data" / "investor_material_matrix.csv"
MD_OUTPUT = ROOT / "docs" / "investor_material_matrix.md"
FIELDS = ("A", "S", "G", "I", "M", "F", "X", "D")
IC_BLOB = "https://github.com/wenchiehlee-money/InvestorConference/blob/main/"
IC_RELEASE = "https://github.com/wenchiehlee-money/InvestorConference/releases/download/audio-files/"
MOPS_BLOB = "https://github.com/wenchiehlee-investment/MOPS/blob/main/"

# Fiscal-year starts used to map non-Taiwan source keys to the calendar
# quarter convention used by Taiwan stocks.  The mapping is intentionally
# calendar-quarter based (the same convention as the shared fiscal-quarter
# resolver), while the original matrix still preserves source keys.
NON_TW_FISCAL_START_MONTH = {
    "AAPL": 10,
    "ARM": 4,
    "AVGO": 11,
    "DELL": 2,
    "HPE": 11,
    "HPQ": 11,
    "MRVL": 2,
    "MSFT": 7,
    "MU": 9,
    "NVDA": 2,
    "QCOM": 10,
    "SNDK": 7,
    "0992HK": 4,
}

# A few source keys were created before the fiscal-quarter resolver was
# deployed, or use an issuer-specific announcement cycle.  These are the
# verified calendar-period identities for the current material set.
# Explicitly verified official-source gaps.  A linked `-` means the issuer
# page was checked for that quarter and no qualifying document was published;
# it is a status marker, not a populated material cell.
# User-directed pause list: existing unknown (`?`) statuses for these
# companies are intentionally paused and must not be treated as active work.
PAUSED_STOCKS = {"6902", "7722", "7705", "6123", "6720", "4114", "7708", "7737", "7736", "6918", "9914", "7732", "7712", "6997", "6442", "3653", "5274", "5274O", "6962", "7713", "2353", "7749", "6751", "6506", "6850", "3158"}
PAUSED_PENDING_TO_MARK = {"2353"}

OFFICIAL_UNAVAILABLE = {
    # Alphabet's official Q1 2026 webcast is available and is registered as A;
    # the issuer transcript is a PDF, not the pipeline's FIN.srt artifact.
    ("GOOGL", 2026, 1): {
        "S": "https://s206.q4cdn.com/479360582/files/doc_events/2026/Apr/29/2026_Q1_Earnings_Transcript.pdf",
    },
    # SMIC's official 2026 financial-summary page lists the Q2 webcast
    # announcement and earnings release, but no separate presentation.
    ("0981HK", 2026, 2): {
        "I": "https://www.smics.com/en/site/company_financialSummary?year=2026",
        "M": "https://www.smics.com/en/site/company_financialSummary?year=2026",
    },
    ("MSFT", 2026, 4): {
        "I": "https://www.microsoft.com/en-us/investor/earnings/fy-2026-q4/press-release-webcast",
        "M": "https://www.microsoft.com/en-us/investor/earnings/fy-2026-q4/press-release-webcast",
    },
}

CALENDAR_PERIOD_OVERRIDES = {
    # AAPL_2026_q1 is the issuer-labeled FY2026 Q2 release and belongs to
    # calendar Q1 2026 in the shared matrix.
    ("AAPL", 2026, 1): (2026, 1),
    # Apple FY2026 Q3 ended in June 2026 and belongs to calendar 2026 Q2.
    ("AAPL", 2026, 3): (2026, 2),
    # Dell FY2026 Q1 ended 2025-05-02 (calendar 2025 Q2).
    ("DELL", 2026, 1): (2025, 2),
    # Dell FY2027 Q1 ended 2026-05-01 (calendar 2026 Q2).
    ("DELL", 2027, 1): (2026, 2),
    ("DELL", 2027, 2): (2026, 3),
    ("ARM", 2027, 1): (2026, 2),
    ("AVGO", 2026, 2): (2026, 2),
    ("AVGO", 2026, 3): (2026, 3),
    ("HPE", 2026, 3): (2026, 3),
    # HPE FY2026 Q2 ended 2026-04-30 (calendar 2026 Q2).
    ("HPE", 2026, 2): (2026, 2),
    ("HPQ", 2026, 3): (2026, 3),
    # HPQ FY2026 Q2 was reported 2026-05-27 (calendar 2026 Q2).
    ("HPQ", 2026, 2): (2026, 2),
    # Marvell FY2027 Q1 was reported 2026-05-27 (calendar 2026 Q2).
    ("MRVL", 2027, 1): (2026, 2),
    ("MRVL", 2027, 2): (2026, 3),
    # Micron FY2026 quarters are reported on the following calendar periods.
    ("MU", 2026, 1): (2025, 4),
    ("MU", 2026, 2): (2026, 1),
    ("MU", 2026, 3): (2026, 2),
    ("MU", 2026, 4): (2026, 3),
    # NVIDIA FY2027 Q1 ended 2026-04-26 (calendar 2026 Q2).
    ("NVDA", 2027, 1): (2026, 2),
    ("NVDA", 2027, 2): (2026, 3),
    ("ORCL", 2026, 4): (2026, 2),
    ("QCOM", 2026, 1): (2026, 1),
    # Qualcomm FY2026 Q3 ended 2026-06-28, so it belongs to calendar 2026 Q2.
    ("QCOM", 2026, 3): (2026, 2),
    ("SNDK", 2026, 4): (2026, 2),
}


def norm(value):
    return re.sub(r"[^A-Z0-9]", "", value.upper())


def canonical_stock(value):
    """Use exchange-qualified symbols consistently for Hong Kong listings."""
    normalized = norm(value)
    if re.fullmatch(r"\d{4}HK", normalized):
        return f"{normalized[:4]}.HK"
    return value


def names():
    result = {}
    stock_map = ROOT / "StockID_TWSE_TPEX.csv"
    if stock_map.exists():
        with stock_map.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.reader(handle):
                if len(row) >= 2 and row[0].strip() and row[1].strip():
                    result.setdefault(norm(row[0].strip()), row[1].strip())
    for line in (ROOT / "README.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if cells:
            match = re.match(r"([^ ]+)\s+(.+)", cells[0])
            if match:
                result[norm(match.group(1))] = match.group(2)
    result.setdefault("1587", "吉茂")
    result.setdefault("6699", "奇邑")
    return result


def taiwan_stock_ids():
    """Return the Taiwan stock universe used for market classification."""
    result = set()
    stock_map = ROOT / "StockID_TWSE_TPEX.csv"
    if stock_map.exists():
        with stock_map.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.reader(handle):
                if row and row[0].strip():
                    result.add(norm(row[0].strip()))
    return result


def readme_event_code(label, sources):
    """Extract the canonical ticker from an event label or source URL."""
    match = re.search(r"\((([A-Za-z]{1,6}|\d{4})\.[A-Za-z]{1,4})\)", label)
    if match:
        return norm(match.group(1))
    first = re.match(r"([^ ]+)", label)
    if first and (re.fullmatch(r"[A-Z0-9]{1,8}(?:\.[A-Z]{1,4})?", first.group(1))
                  or re.search(r"\d", first.group(1))):
        return norm(first.group(1))
    for source in sources:
        match = re.search(r"/quote/([^/]+)/financials", source)
        if match:
            return norm(match.group(1))
    return norm(first.group(1)) if first else ""


def readme_event_display(label, code):
    """Return the issuer name without its exact ticker or fiscal suffix."""
    display = re.sub(r"\s*\([^)]*\)", "", label)
    display = re.sub(r"\s+(?:FY)?\d{4} Q[1-4].*$", "", display)
    first = re.match(r"([^ ]+)", display)
    if first and norm(first.group(1)) == code:
        display = display[first.end():].strip()
    return display.strip()


def conference_keys():
    result = set()
    for line in (ROOT / "README.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) < 4 or cells[2] not in {"法說會", "受邀法說"}:
            continue
        period = re.search(r"(\d{4}) Q([1-4])", cells[1])
        source = re.findall(r"https?://[^)]+", cells[-1])
        code = readme_event_code(cells[0], source)
        if code and period:
            result.add((code, int(period.group(1)), int(period.group(2))))
    return result


def is_taiwan_code(code, taiwan_ids):
    normalized = norm(code)
    return (
        normalized in taiwan_ids
        or normalized.isdigit()
        or (len(normalized) == 5 and normalized[:4] in taiwan_ids)
    )


def calendar_period(code, year, quarter, taiwan_ids):
    key = (norm(code), year, quarter)
    if key in CALENDAR_PERIOD_OVERRIDES:
        return CALENDAR_PERIOD_OVERRIDES[key]
    normalized = norm(code)
    if is_taiwan_code(code, taiwan_ids) or normalized not in NON_TW_FISCAL_START_MONTH:
        return year, quarter
    # The fiscal label is the fiscal year ending year.  Calculate the
    # quarter end month explicitly; using only the fiscal start quarter
    # misclassifies companies whose year starts in February, September, or
    # November.
    start_month = NON_TW_FISCAL_START_MONTH[normalized]
    start_year = year if start_month == 1 else year - 1
    end_month_index = start_year * 12 + (start_month - 1) + quarter * 3 - 1
    calendar_year = end_month_index // 12
    calendar_month = end_month_index % 12 + 1
    calendar_quarter = (calendar_month - 1) // 3 + 1
    return calendar_year, calendar_quarter


def event_calendar():
    """Return README event rows keyed by canonical stock/year/quarter."""
    result = {}
    for line in (ROOT / "README.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) < 4 or cells[0] in {"公司", ":-----"}:
            continue
        period = re.search(r"(?:FY)?(\d{4}) Q([1-4])", cells[1])
        event_date = cells[3]
        source = re.findall(r"https?://[^)]+", cells[-1])
        if (not period or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", event_date)
                or cells[2] not in {"法說會", "受邀法說", "財報"}):
            continue
        code = readme_event_code(cells[0], source)
        if not code:
            continue
        key = (code, int(period.group(1)), int(period.group(2)))
        entry = result.setdefault(key, {
            "date": event_date,
            "types": set(),
            "url": source[0] if source else "",
            "display": readme_event_display(cells[0], code),
        })
        entry["types"].add(cells[2])
    return result


def linked(label, url):
    return f"[{label}]({url})"


def calendar_view(rows, taiwan_ids):
    """Return the non-Taiwan rows normalized to calendar periods."""
    result = {}
    for (code, source_year), row in rows.items():
        for source_quarter in range(1, 5):
            source_cell = row.get(source_quarter, {})
            if not any(source_cell.get(field) for field in FIELDS):
                continue
            year, quarter = calendar_period(code, source_year, source_quarter, taiwan_ids)
            if is_taiwan_code(code, taiwan_ids):
                continue
            key = (code, year)
            output = result.setdefault(
                key,
                {"stock": row["stock"], "stock_name": row["stock_name"], "year": year},
            )
            cell = output.setdefault(quarter, {field: "" for field in FIELDS})
            for field in FIELDS:
                value = source_cell.get(field, "")
                if not value:
                    continue
                existing = cell.get(field, "")
                is_status = value.startswith(("[☐]", "[?]", "[-]"))
                existing_is_status = existing.startswith(("[☐]", "[?]", "[-]"))
                if not existing or (not is_status and existing_is_status):
                    cell[field] = value

    # Materialize overdue calendar quarters even when the corresponding
    # fiscal source quarter is not present yet (for example, calendar Q1 can
    # be the prior fiscal year's Q4 for February-start issuers).
    today = datetime.now(ZoneInfo("Asia/Taipei")).date()
    deadlines = {1: (5, 31), 2: (8, 31), 3: (11, 30), 4: (5, 31)}
    for (code, year), row in list(result.items()):
        if is_taiwan_code(code, taiwan_ids):
            continue
        for quarter, (month, day) in deadlines.items():
            deadline_year = year if quarter < 4 else year + 1
            if datetime(deadline_year, month, day).date() > today:
                continue
            cell = row.setdefault(quarter, {field: "" for field in FIELDS})
            url = f"https://finance.yahoo.com/quote/{canonical_stock(code)}/financials/"
            for field in ("F", "X"):
                if not cell.get(field):
                    cell[field] = linked("☐", url)
            for field in ("A", "S", "I", "M"):
                if not cell.get(field):
                    cell[field] = linked("?", url)
    return result


def markdown_rows(rows, taiwan_ids):
    """Return the rows used by Markdown, with non-Taiwan periods normalized."""
    result = {}
    calendar_rows = calendar_view(rows, taiwan_ids)
    for key, row in rows.items():
        code = norm(row["stock"])
        if code in taiwan_ids or code.isdigit():
            result[key] = row
    result.update(calendar_rows)
    return result


def source_url(token, code):
    """Resolve a digest source token to the repository URL when possible."""
    token = token.strip()
    if token.startswith("http://") or token.startswith("https://"):
        return token
    if token.startswith("../MOPS/"):
        return MOPS_BLOB + token.removeprefix("../MOPS/")
    if token.startswith("data/"):
        return IC_BLOB + token
    if token == "audio_metadata.json":
        return IC_BLOB + token
    if "/" not in token:
        return IC_BLOB + f"data/{code}/{token}"
    return None


def ensure(rows, code, year, quarter, display):
    canonical_code = norm(code)
    row = rows.setdefault(
        (canonical_code, year),
        {"stock": canonical_stock(code), "stock_name": display or code, "year": year},
    )
    row.setdefault(quarter, {field: "" for field in FIELDS})
    return row[quarter]


def is_quartr_conference_md(path):
    """Return true for a quarter-confirmed Google Finance/Quartr MD artifact."""
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:5000].lower()
    except OSError:
        return False
    return "google finance" in head and "quartr" in head


def is_official_html_report_md(path):
    """Return true only for an MD sidecar that records an official source URL."""
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:4000].lower()
    except OSError:
        return False
    if "source:" not in head and "source_url" not in head:
        return False
    return any(domain in head for domain in (
        "sec.gov/archives/", "investor.", "investors.",
        "ir.", "company",
    ))


def build():
    stock_names = names()
    conference_catalog = conference_keys()
    calendar = event_calendar()
    for (code, _year, _quarter), event in calendar.items():
        existing = stock_names.get(code, "").strip()
        if event["display"] and (not existing or norm(existing) == code):
            stock_names[code] = event["display"]
    rows = {}
    digest_sources = []
    manifest = {}
    manifest_path = ROOT / "audio_manifest.json"
    if manifest_path.exists():
        for key, url in json.loads(manifest_path.read_text(encoding="utf-8")).items():
            match = re.match(r"^(.+?)_(\d{4})_[qQ]([1-4])$", key)
            if match:
                manifest[f"{norm(match.group(1))}_{match.group(2)}_q{match.group(3)}"] = url
    invalid_audio = {f"{norm(s)}_{y}_q{q}" for s, y, q in (("qcom", 2025, 4), ("2454", 2026, 1), ("7765", 2026, 1))}

    data_root = ROOT / "data"
    for company_dir in data_root.iterdir():
        if not company_dir.is_dir() or company_dir.name == "reports":
            continue
        code = company_dir.name
        display = stock_names.get(norm(code), code)
        for path in company_dir.iterdir():
            match = re.match(r"^([A-Za-z0-9]+)_(\d{4})_q([1-4])", path.name, re.I)
            if not match:
                continue
            year, quarter = int(match.group(2)), int(match.group(3))
            cell = ensure(rows, code, year, quarter, display)
            lower = path.name.lower()
            if lower.endswith("_fin.srt"):
                cell["S"] = linked("S", IC_BLOB + f"data/{code}/{path.name}")
            elif lower.endswith("_gt.srt"):
                cell["G"] = linked("G", IC_BLOB + f"data/{code}/{path.name}")
            elif lower.endswith(("_google_finance_presentation.pdf", "_quartr_presentation.pdf")):
                # A quarter-confirmed Quartr presentation is conference evidence.
                # It is secondary-source I only; it is never financial-report F.
                cell["I"] = linked("I", IC_BLOB + f"data/{code}/{path.name}")
            elif lower.endswith(("_ir.pdf", "_ir_en.pdf", "_performance_review.pdf")):
                cell["I"] = linked("I", IC_BLOB + f"data/{code}/{path.name}")
            elif lower.endswith(("_google_finance_presentation.md", "_quartr_presentation.md")):
                if is_quartr_conference_md(path):
                    cell["M"] = linked("M", IC_BLOB + f"data/{code}/{path.name}")
            elif lower.endswith(("_ir.md", "_ir_en.md", "_performance_review.md")):
                cell["M"] = linked("M", IC_BLOB + f"data/{code}/{path.name}")
            elif lower.endswith("_report_en.pdf") or lower.endswith("_financial_tables.pdf"):
                cell["F"] = linked("F", IC_BLOB + f"data/{code}/{path.name}")
            elif lower.endswith("_report_en.md") or lower.endswith("_financial_tables.md"):
                md_url = IC_BLOB + f"data/{code}/{path.name}"
                cell["X"] = linked("X", md_url)
                # Official HTML/SEC pages may be the only durable financial
                # artifact. In that case the same audited MD sidecar is both
                # the official financial source (F) and its Markdown form (X).
                if not cell.get("F") and is_official_html_report_md(path):
                    cell["F"] = linked("F", md_url)
            elif lower.endswith(("_google_finance_transcript.md", "_quartr_transcript.md")):
                # A browser-confirmed Quartr transcript is conference evidence.
                # Per policy it may populate I/M, but never F/X or FIN.srt S.
                if is_quartr_conference_md(path):
                    md_url = IC_BLOB + f"data/{code}/{path.name}"
                    cell["I"] = linked("I", md_url)
                    cell["M"] = linked("M", md_url)
            audio_key = f"{norm(code)}_{year}_q{quarter}"
            if (norm(code), year, quarter) in conference_catalog and audio_key in manifest and audio_key not in invalid_audio:
                cell["A"] = linked("A", manifest[audio_key])

    digest_root = ROOT / "data" / "reports" / "conference-digests"
    for company_dir in digest_root.iterdir() if digest_root.exists() else []:
        if not company_dir.is_dir():
            continue
        code = company_dir.name
        display = stock_names.get(norm(code), code)
        for path in company_dir.glob("*_digest.md"):
            match = re.match(r"^([A-Za-z0-9.]+)_(\d{4})_q([1-4])_digest", path.name, re.I)
            if not match or not path.read_text(encoding="utf-8", errors="replace").strip():
                continue
            event = (norm(code), int(match.group(2)), int(match.group(3)))
            row = rows.get((norm(code), event[1]))
            existing = row.get(event[2], {}) if row else {}
            if event not in conference_catalog and not any(existing.get(field) for field in ("A", "S", "G", "I", "M")):
                continue
            cell = ensure(rows, code, event[1], event[2], display)
            digest_url = IC_BLOB + f"data/reports/conference-digests/{code}/{path.name}"
            # The final D/D- label is assigned after MOPS F/X collection below.
            cell["D"] = linked("D-", digest_url)
            source_line = next(
                (line for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
                 if line.startswith("| 資料來源 |")),
                "",
            )
            tokens = re.findall(r"`([^`]+)`", source_line)
            sources = []
            for token in tokens:
                url = source_url(token, code)
                sources.append((token, url))
            digest_sources.append((norm(code), display, event[1], event[2], digest_url, sources))

    downloads = MOPS_ROOT / "downloads"
    if downloads.exists():
        for company_dir in downloads.iterdir():
            if not company_dir.is_dir():
                continue
            code = company_dir.name
            display = stock_names.get(norm(code), code)
            for path in company_dir.iterdir():
                match = re.match(r"^(\d{4})0([1-4])_[A-Za-z0-9]+_AI1\.(pdf|md)$", path.name, re.I)
                if match:
                    cell = ensure(rows, code, int(match.group(1)), int(match.group(2)), display)
                    field = "F" if match.group(3).lower() == "pdf" else "X"
                    cell[field] = linked(field, MOPS_BLOB + f"downloads/{code}/{path.name}")

    # Add explicit official-source gap markers only after all real files have
    # been collected.  A real file always wins over a stale gap declaration.
    for (code, year, quarter), fields in OFFICIAL_UNAVAILABLE.items():
        cell = rows.get((code, year), {}).get(quarter)
        if not cell:
            continue
        for field, url in fields.items():
            if not cell.get(field):
                cell[field] = linked("-", url)

    # The README calendar is a due-date source, not the completeness universe.
    # A missing calendar row must not be interpreted as proof that a material
    # was never published. Future calendar events remain empty; past-due rows
    # expose missing expected materials as linked checkboxes.
    today = datetime.now(ZoneInfo("Asia/Taipei")).date()
    taiwan_ids = taiwan_stock_ids()
    expected_by_type = {
        "法說會": ("A", "S", "I", "M"),
        "受邀法說": ("A", "S", "I", "M"),
        "財報": ("F", "X"),
    }
    for (code, year, quarter), event in calendar.items():
        row = rows.setdefault(
            (code, year),
            {"stock": canonical_stock(code), "stock_name": stock_names.get(code, event["display"]), "year": year},
        )
        cell = row.setdefault(quarter, {field: "" for field in FIELDS})
        if datetime.strptime(event["date"], "%Y-%m-%d").date() > today:
            continue
        for event_type in event["types"]:
            for field in expected_by_type[event_type]:
                if not event["url"]:
                    continue
                if cell.get(field, "").startswith("[?]") or not cell.get(field):
                    cell[field] = linked("☐", event["url"])

    # Taiwan statutory reports are expected every quarter.  The README calendar
    # is incomplete for some issuers, so materialize overdue F/X placeholders
    # from the statutory schedule even when no calendar event was listed.
    taiwan_report_url = lambda code: (
        f"https://mops.twse.com.tw/mops/web/t100sb07_1?step=1&firstin=1&co_id={code}"
    )
    quarter_deadlines = {
        1: (5, 31),
        2: (8, 31),
        3: (11, 30),
        4: (5, 31),
    }
    for (code, year), row in rows.items():
        if norm(code) not in taiwan_ids and not norm(code).isdigit():
            continue
        for quarter, (month, day) in quarter_deadlines.items():
            deadline_year = year if quarter < 4 else year + 1
            deadline = datetime(deadline_year, month, day).date()
            if deadline > today:
                continue
            cell = row.setdefault(quarter, {field: "" for field in FIELDS})
            url = taiwan_report_url(code)
            for field in ("F", "X"):
                if not cell.get(field):
                    cell[field] = linked("☐", url)

    # Non-Taiwan quarterly reports are also expected after fiscal-to-calendar
    # normalization.  For an overdue mapped quarter, F/X are pending until
    # ingested and conference applicability remains unknown (`?`) until the
    # issuer calendar or an artifact confirms a conference.
    calendar_deadlines = {
        1: (5, 31),
        2: (8, 31),
        3: (11, 30),
        4: (5, 31),
    }
    for (code, year), row in rows.items():
        normalized = norm(code)
        if is_taiwan_code(code, taiwan_ids):
            continue
        fallback_url = f"https://finance.yahoo.com/quote/{canonical_stock(code)}/financials/"
        for source_quarter in range(1, 5):
            calendar_year, calendar_quarter = calendar_period(
                code, year, source_quarter, taiwan_ids
            )
            month, day = calendar_deadlines[calendar_quarter]
            deadline_year = calendar_year if calendar_quarter < 4 else calendar_year + 1
            deadline = datetime(deadline_year, month, day).date()
            if deadline > today:
                continue
            cell = row.setdefault(source_quarter, {field: "" for field in FIELDS})
            url = next(
                (match.group(0) for value in cell.values()
                 if (match := re.search(r"https?://[^)]+", value or ""))),
                fallback_url,
            )
            for field in ("F", "X"):
                if not cell.get(field):
                    cell[field] = linked("☐", url)
            for field in ("A", "S", "I", "M"):
                if not cell.get(field):
                    cell[field] = linked("?", url)

    # For a quarter already represented by material, a missing calendar entry
    # is uncertainty, not proof of absence. F/X are expected for every known
    # financial quarter; missing conference coverage is marked `?` until the
    # event/material applicability is verified. A known conference due date
    # turns missing A/S/I/M into `☐` instead.
    for (code, year), row in rows.items():
        for quarter in range(1, 5):
            cell = row.get(quarter)
            if not cell:
                continue
            event = calendar.get((code, year, quarter))
            event_types = event["types"] if event else set()
            if event:
                due_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
                status_url = event["url"]
            else:
                calendar_year, calendar_quarter = calendar_period(code, year, quarter, taiwan_ids)
                month = calendar_quarter * 3
                next_month = datetime(calendar_year + 1, 1, 1) if month == 12 else datetime(calendar_year, month + 1, 1)
                due_date = (next_month - timedelta(days=1)).date()
                status_url = next((
                    match.group(0)
                    for value in cell.values()
                    if (match := re.search(r"https?://[^)]+", value or ""))
                ), "")
            if due_date > today or not status_url:
                continue
            financial_expected = ("F", "X")
            conference_expected = ("A", "S", "I", "M")
            for field in financial_expected:
                if not cell.get(field):
                    cell[field] = linked("☐", status_url)
            conference_due = any(event_type in {"法說會", "受邀法說"} for event_type in event_types)
            conference_status = "☐" if conference_due else "?"
            for field in conference_expected:
                if not cell.get(field):
                    cell[field] = linked(conference_status, status_url)

    # Convert only unknown markers for explicitly paused companies. Existing
    # artifacts, pending checkboxes, and official-unavailable markers remain.
    for row in rows.values():
        if norm(row["stock"]) not in PAUSED_STOCKS:
            continue
        for quarter in range(1, 5):
            for field in FIELDS:
                value = row.get(quarter, {}).get(field, "")
                if value.startswith("[?]") or (norm(row["stock"]) in PAUSED_PENDING_TO_MARK and value.startswith("[☐]")):
                    row[quarter][field] = re.sub(r"^\[(?:\?|☐)\]", "[🚫]", value)

    # Classify digest cells only after every source pass has populated A/S/I/M/F/X.
    # G is deliberately excluded because it is generated after digest review.
    # `[-](...)` is an official-unavailable marker, not a material.
    required_before_gt = ("A", "S", "I", "M", "F", "X")
    for row in rows.values():
        for quarter in range(1, 5):
            cell = row.get(quarter, {})
            digest = cell.get("D", "")
            if not digest:
                continue
            label = "D" if all(
                cell.get(field) and not cell.get(field, "").startswith(("[-]", "[☐]", "[?]", "[🚫]"))
                for field in required_before_gt
            ) else "D-"
            cell["D"] = re.sub(r"^\[(?:D|D-)\]", f"[{label}]", digest)
    return rows, digest_sources


def is_paused_financial_only(row):
    """Hide rows whose only statuses are paused markers and F/X reports."""
    values = [
        row.get(quarter, {}).get(field, "")
        for quarter in range(1, 5)
        for field in FIELDS
    ]
    labels = []
    for value in values:
        if not value:
            continue
        match = re.match(r"^\[([^]]+)\]", value)
        labels.append(match.group(1) if match else value)
    return bool(labels) and all(label in {"🚫", "F", "X", "☐"} for label in labels)


def write(rows, digest_sources):
    rows = {key: row for key, row in rows.items() if not is_paused_financial_only(row)}
    columns = ["stock", "stock_name", "year", "generated_at"] + [f"q{q}_{field}" for q in range(1, 5) for field in FIELDS]
    generated_dt = datetime.now(timezone.utc)
    generated_at = generated_dt.isoformat()
    updated_label = generated_dt.astimezone(ZoneInfo("Asia/Taipei")).strftime("Updated: %Y-%m-%d %H:%M CST")
    taiwan_ids = taiwan_stock_ids()
    CSV_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for key in sorted(
        rows,
        key=lambda item: (
                1 if (
                    norm(rows[item]["stock"]) in taiwan_ids
                    or rows[item]["stock"].isdigit()
                ) else 0,
                rows[item]["stock_name"].casefold(),
                -item[1],
                item[0],
            ),
        ):
            row = rows[key]
            output = {"stock": row["stock"], "stock_name": row["stock_name"], "year": row["year"], "generated_at": generated_at}
            for q in range(1, 5):
                for field in FIELDS:
                    output[f"q{q}_{field}"] = row.get(q, {}).get(field, "")
            writer.writerow(output)

    lines = [
        "# Investor material matrix",
        "",
        updated_label,
        "",
        "Canonical view generated by `scripts/generate_investor_material_matrix.py`.",
        "This Markdown view uses calendar years for every stock. Taiwan fiscal quarters already align with calendar quarters; non-Taiwan source fiscal quarters are normalized before display.",
        "The CSV retains source fiscal-year keys for provenance. Each row is one stock/calendar-year; each quarter occupies eight compact columns.",
        "Every populated cell links to a verified artifact or the calendar source supporting its status.",
        "",
        "`A` audio · `S` FIN.srt · `G` GT.srt · `I` IR presentation PDF · `M` IR presentation MD · `F` official financial-report source (PDF or official HTML) · `X` financial-report MD · `☐` due event/quarter reached and ingestion is pending · `?` event/material applicability is not yet verified · `🚫` explicitly paused by policy · `-` official source checked and no qualifying document was published · empty = period not yet due or material explicitly not applicable · `D` digest with all pre-G materials (`A/S/I/M/F/X`) · `D-` digest with one or more pre-G materials missing. Digest precedes GT generation, so missing `G` does not downgrade `D`.",
        "",
        "|Stock|Year|" + "|".join(FIELDS * 4) + "|",
        "|---|---:|" + "|".join(["---"] * 32) + "|",
    ]
    totals = {q: {field: 0 for field in FIELDS} for q in range(1, 5)}
    display_rows = markdown_rows(rows, taiwan_ids)
    for key in sorted(
        display_rows,
        key=lambda item: (
            1 if (
                norm(display_rows[item]["stock"]) in taiwan_ids
                or norm(display_rows[item]["stock"]).isdigit()
            ) else 0,
            display_rows[item]["stock_name"].casefold(),
            -item[1],
            item[0],
        ),
    ):
        row = display_rows[key]
        cells = [row["stock_name"], str(row["year"])]
        for q in range(1, 5):
            for field in FIELDS:
                value = row.get(q, {}).get(field, "")
                cells.append(value)
                if value and not value.startswith(("[-]", "[☐]", "[?]", "[🚫]")):
                    totals[q][field] += 1
        lines.append("|" + "|".join(cells) + "|")
    lines.extend([
        "|**Total populated cells**|—|" + "|".join(str(totals[q][field]) for q in range(1, 5) for field in FIELDS) + "|",
        "",
        "The total row counts populated stock-quarter cells in each quarter column. The `D` column contains either `D` or `D-`: `D` has all pre-G materials (`A/S/I/M/F/X`); `D-` still has one or more pre-G material gaps. `G` is generated after digest review. `F`/`X` are quarter-level financial-report cells; table (22) separately counts individual MOPS PDF/MD artifacts, so its artifact total is not mathematically interchangeable with this quarter matrix.",
        "",
        "## Digest source provenance",
        "",
        "This generated table records the source tokens explicitly listed in each digest's `資料來源` field. It is the provenance view for what the digest actually read; it is not an additional material flag column.",
        "",
        "|Stock|Year|Quarter|Digest|Sources explicitly listed by the digest|",
        "|---|---:|---:|---|---|",
    ])
    for code, display, year, quarter, digest_url, sources in sorted(
        digest_sources, key=lambda item: (item[1].casefold(), -item[2], item[3])
    ):
        source_cells = []
        for token, url in sources:
            label = Path(token).name or token
            source_cells.append(f"[{label}]({url})" if url else f"`{token}`")
        digest_value = rows.get((code, year), {}).get(quarter, {}).get("D", "[D]")
        digest_label = re.match(r"^\[([^]]+)\]", digest_value)
        label = digest_label.group(1) if digest_label else "D"
        calendar_year, calendar_quarter = calendar_period(code, year, quarter, taiwan_ids)
        lines.append(
            f"|{display}|{calendar_year}|Q{calendar_quarter}|[{label}]({digest_url})|" + "<br>".join(source_cells) + "|"
        )
    MD_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    MD_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    table, provenance = build()
    write(table, provenance)
    print(f"wrote {len(table)} stock-year rows and {len(provenance)} digest provenance rows to {CSV_OUTPUT}")
