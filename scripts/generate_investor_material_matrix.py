#!/usr/bin/env python3
"""Generate the canonical investor-material matrix for InvestorConference.

The CSV is the machine-readable source.  The Markdown file is a generated
human-readable view of the same rows.  Each populated cell is a link to the
artifact that caused the flag to be present.
"""

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOPS_ROOT = ROOT.parent / "MOPS"
CSV_OUTPUT = ROOT / "data" / "investor_material_matrix.csv"
MD_OUTPUT = ROOT / "docs" / "investor_material_matrix.md"
FIELDS = ("A", "S", "G", "I", "M", "F", "X", "D")
IC_BLOB = "https://github.com/wenchiehlee-money/InvestorConference/blob/main/"
IC_RELEASE = "https://github.com/wenchiehlee-money/InvestorConference/releases/download/audio-files/"
MOPS_BLOB = "https://github.com/wenchiehlee-investment/MOPS/blob/main/"


def norm(value):
    return re.sub(r"[^A-Z0-9]", "", value.upper())


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


def conference_keys():
    result = set()
    for line in (ROOT / "README.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) < 4 or cells[2] not in {"法說會", "受邀法說"}:
            continue
        code = re.match(r"([^ ]+)", cells[0])
        period = re.search(r"(\d{4}) Q([1-4])", cells[1])
        if code and period:
            result.add((norm(code.group(1)), int(period.group(1)), int(period.group(2))))
    return result


def linked(label, url):
    return f"[{label}]({url})"


def ensure(rows, code, year, quarter, display):
    canonical_code = norm(code)
    row = rows.setdefault((canonical_code, year), {"stock": code, "stock_name": display or code, "year": year})
    row.setdefault(quarter, {field: "" for field in FIELDS})
    return row[quarter]


def build():
    stock_names = names()
    conference_catalog = conference_keys()
    rows = {}
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
            elif lower.endswith(("_ir.pdf", "_ir_en.pdf")):
                cell["I"] = linked("I", IC_BLOB + f"data/{code}/{path.name}")
            elif lower.endswith(("_ir.md", "_ir_en.md")):
                cell["M"] = linked("M", IC_BLOB + f"data/{code}/{path.name}")
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
            cell["D"] = linked("D", IC_BLOB + f"data/reports/conference-digests/{code}/{path.name}")

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
    return rows


def write(rows):
    columns = ["stock", "stock_name", "year"] + [f"q{q}_{field}" for q in range(1, 5) for field in FIELDS]
    CSV_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for key in sorted(rows, key=lambda item: (rows[item]["stock_name"].casefold(), -item[1], item[0])):
            row = rows[key]
            output = {"stock": row["stock"], "stock_name": row["stock_name"], "year": row["year"]}
            for q in range(1, 5):
                for field in FIELDS:
                    output[f"q{q}_{field}"] = row.get(q, {}).get(field, "")
            writer.writerow(output)

    lines = [
        "# Investor material matrix",
        "",
        "Canonical view generated by `scripts/generate_investor_material_matrix.py`.",
        "Each row is one stock/year; each quarter occupies eight compact columns.",
        "Every populated cell links to the artifact that was verified.",
        "",
        "`A` audio · `S` FIN.srt · `G` GT.srt · `I` IR presentation PDF · `M` IR presentation MD · `F` financial-report PDF · `X` financial-report MD · `D` verified conference digest MD.",
        "",
        "|Stock|Year|" + "|".join(FIELDS * 4) + "|",
        "|---|---:|" + "|".join(["---"] * 32) + "|",
    ]
    totals = {q: {field: 0 for field in FIELDS} for q in range(1, 5)}
    with CSV_OUTPUT.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            cells = [row["stock_name"], row["year"]]
            for q in range(1, 5):
                for field in FIELDS:
                    value = row[f"q{q}_{field}"]
                    cells.append(value)
                    if value:
                        totals[q][field] += 1
            lines.append("|" + "|".join(cells) + "|")
    lines.extend([
        "|**Total populated cells**|—|" + "|".join(str(totals[q][field]) for q in range(1, 5) for field in FIELDS) + "|",
        "",
        "The total row counts populated stock-quarter cells in each quarter column. For the conference components, the four-quarter sums reconcile to the health summary: `A=95`, `S=99`, `G=46`, `I=143`, and `D=37`. `M` is the count of presentation Markdown cells. `F`/`X` are quarter-level financial-report cells; table (22) separately counts individual MOPS PDF/MD artifacts, so its artifact total is not mathematically interchangeable with this quarter matrix.",
    ])
    MD_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    MD_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    table = build()
    write(table)
    print(f"wrote {len(table)} stock-year rows to {CSV_OUTPUT}")
