#!/usr/bin/env python3
import csv
import json
import os
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data" / "reports"
HEALTH_SUMMARY_CSV = DATA_DIR / "investor_conference_health_summary.csv"
AUDIO_MANIFEST_JSON = REPO_ROOT / "audio_manifest.json"
AUDIO_DURATIONS_JSON = REPO_ROOT / "audio_durations.json"

TAIPEI_TZ = timezone(timedelta(hours=8))

def is_company_dir(path):
    if not path.is_dir():
        return False
    name = path.name
    # Exclude non-stock directories
    if name in (".git", ".github", ".claude", "__pycache__", "definitions", "spec", "tmp", "tools", "web", "logs", "scripts"):
        return False
    return name.isdigit() or (name.isupper() and name.isalpha())

def main():
    print("=== Generating InvestorConference Data Health Summary ===")
    
    if not DATA_DIR.exists():
        os.makedirs(DATA_DIR, exist_ok=True)

    # 1. Load Audio Manifest
    audio_keys = set()
    if AUDIO_MANIFEST_JSON.exists():
        try:
            with open(AUDIO_MANIFEST_JSON, "r", encoding="utf-8") as f:
                manifest = json.load(f)
                audio_keys = {k.lower() for k in manifest.keys()}
        except Exception as e:
            print(f"Warning: Failed to load {AUDIO_MANIFEST_JSON.name}: {e}")

    # 1.2. Load Audio Durations
    durations_keys = set()
    if AUDIO_DURATIONS_JSON.exists():
        try:
            with open(AUDIO_DURATIONS_JSON, "r", encoding="utf-8") as f:
                durations = json.load(f)
                for k in durations.keys():
                    # Parse "2301/2301_2025_q4.m4a" -> "2301_2025_q4"
                    filename = os.path.basename(k)
                    stem, _ = os.path.splitext(filename)
                    durations_keys.add(stem.lower())
        except Exception as e:
            print(f"Warning: Failed to load {AUDIO_DURATIONS_JSON.name}: {e}")

    # 2. Scan company directories for conference keys
    company_dirs = [d for d in REPO_ROOT.iterdir() if is_company_dir(d)]
    print(f"Found {len(company_dirs)} company directories.")

    # Match stock_year_qX (e.g. 2330_2025_q1)
    pattern = re.compile(r"^([A-Za-z0-9]+)_(\d{4})_[qQ]([1-4])")
    
    event_keys = set()
    file_map = {} # Maps key -> list of filenames

    for c_dir in company_dirs:
        for file in c_dir.iterdir():
            if file.is_file():
                m = pattern.match(file.name)
                if m:
                    # Normalize key
                    key = f"{m.group(1).lower()}_{m.group(2)}_q{m.group(3)}"
                    event_keys.add(key)
                    file_map.setdefault(key, []).append(file.name)

    total_conferences = len(event_keys)
    print(f"Total Conference events identified: {total_conferences}")

    # 3. Analyze each event key
    has_pdf_count = 0
    has_audio_count = 0
    has_transcript_count = 0
    has_srt_count = 0
    fully_ingested_count = 0
    pdf_only_count = 0

    audio_conference_keys = set()
    pdf_only_report_keys = set()
    
    pdf_only_healthy_count = 0
    pdf_only_broken_count = 0

    for key in sorted(event_keys):
        files = file_map.get(key, [])
        
        # Check PDF: filename contains _ir.pdf or _ir_en.pdf
        has_pdf = any(f.endswith("_ir.pdf") or f.endswith("_ir_en.pdf") for f in files)
        
        # Check Transcript: filename contains _transcript.md or _alphaspread_transcript.md
        has_transcript = any(f.endswith("_transcript.md") or f.endswith("_alphaspread_transcript.md") for f in files)
        
        # Check SRT: filename contains _FIN.srt or _GT.srt
        has_srt = any(f.endswith("_FIN.srt") or f.endswith("_GT.srt") for f in files)
        
        # Known invalid or duplicate/placeholder audio files (remote state)
        invalid_audios = {
            "qcom_2025_q4",    # remote release URL returns 404
            "2454_2026_q1",    # duplicate of 2454_2025_q4 on remote
            "2458_2026_q1",    # duplicate of 2458_2025_q4 on remote
            "7765_2026_q1",    # duplicate of 7765_2025_q4 on remote
        }
        
        # Check if we have successfully downloaded the true audio locally (>1MB)
        stock_id = key.split("_")[0]
        comp_dir = REPO_ROOT / stock_id
        has_local_valid_audio = False
        if comp_dir.exists():
            for f in comp_dir.iterdir():
                if f.is_file() and f.name.lower().startswith(key.lower()) and f.suffix.lower() in [".m4a", ".mp3", ".wav", ".mp4"]:
                    if f.stat().st_size > 1024 * 1024:
                        has_local_valid_audio = True
                        break
                        
        is_audio_valid = (key.lower() not in invalid_audios) or has_local_valid_audio
        
        # Check Audio: present in audio_manifest.json and contents are valid
        has_audio = (key in audio_keys) and is_audio_valid

        # Check for event specific Markdown file (excluding README.md)
        has_event_md = any(f.lower().startswith(key.lower()) and f.endswith(".md") for f in files)

        if has_pdf:
            has_pdf_count += 1
        if has_audio:
            has_audio_count += 1
        if has_transcript:
            has_transcript_count += 1
        if has_srt:
            has_srt_count += 1

        # Separate Formulation logic: conference if in manifest (even if audio is invalid) or has srt, or 2324_2026_q1
        is_audio_conf = (key in audio_keys) or has_transcript or has_srt or (key.lower() == "2324_2026_q1")

        # Fully Ingested: has PDF + Audio + (Transcript or SRT)
        is_fully = has_pdf and has_audio and (has_transcript or has_srt)
        if is_fully:
            fully_ingested_count += 1

        # PDF Only (Pure Financial Reports)
        is_pdf_only = has_pdf and not is_audio_conf
        if is_pdf_only:
            pdf_only_count += 1
            pdf_only_report_keys.add(key)
            # If it has a transcript file or any event-specific Markdown conversion, it is Healthy
            if has_transcript or has_event_md:
                pdf_only_healthy_count += 1
            else:
                pdf_only_broken_count += 1

        if is_audio_conf:
            audio_conference_keys.add(key)

    total_audio_conferences = len(audio_conference_keys)
    total_pdf_only_reports = len(pdf_only_report_keys)

    ingestion_rate_pct = 100.0
    if total_conferences > 0:
        ingestion_rate_pct = round((fully_ingested_count / total_conferences * 100), 2)
    else:
        ingestion_rate_pct = 0.0

    # Ingestion rate of actual audio conferences
    conference_ingestion_rate_pct = 0.0
    if total_audio_conferences > 0:
        conference_ingestion_rate_pct = round((fully_ingested_count / total_audio_conferences * 100), 2)

    # Ingestion rate of PDF reports
    pdf_only_ingestion_rate_pct = 0.0
    if total_pdf_only_reports > 0:
        pdf_only_ingestion_rate_pct = round((pdf_only_healthy_count / total_pdf_only_reports * 100), 2)

    # Calculate readiness based on audio durations registered
    durations_registered_count = len(event_keys.intersection(durations_keys))
    ready_to_use_rate_pct = 0.0
    if total_conferences > 0:
        ready_to_use_rate_pct = round((durations_registered_count / total_conferences * 100), 2)

    print(f"Has PDF: {has_pdf_count}")
    print(f"Has Audio: {has_audio_count}")
    print(f"Has Transcript: {has_transcript_count}")
    print(f"Has SRT: {has_srt_count}")
    print(f"Fully Ingested: {fully_ingested_count}")
    print(f"PDF Only (Pure Reports): {pdf_only_count}")
    print(f"  - MD Completed (Healthy): {pdf_only_healthy_count}")
    print(f"  - MD Missing (Broken): {pdf_only_broken_count}")
    print(f"  - MD Conversion Rate: {pdf_only_ingestion_rate_pct}%")
    print(f"Total Conferences (with Audio/SRT/Transcript): {total_audio_conferences}")
    print(f"Conference Ingestion Rate (Conferences only): {conference_ingestion_rate_pct}%")
    print(f"Global Ingestion Rate (incl. Pure Reports): {ingestion_rate_pct}%")
    print(f"Durations Registered (Ready): {durations_registered_count}")
    print(f"Ready-to-Use Rate: {ready_to_use_rate_pct}%")

    # 4. Write to CSV
    now = datetime.now(TAIPEI_TZ)
    checked_at = now.isoformat()
    
    summary_data = {
        "process_timestamp": checked_at,
        "total_conferences": total_conferences,
        "total_audio_conferences": total_audio_conferences,
        "total_pdf_only_reports": total_pdf_only_reports,
        "has_pdf": has_pdf_count,
        "has_audio": has_audio_count,
        "has_transcript": has_transcript_count,
        "has_srt": has_srt_count,
        "fully_ingested": fully_ingested_count,
        "pdf_only": pdf_only_count,
        "pdf_only_healthy": pdf_only_healthy_count,
        "pdf_only_broken": pdf_only_broken_count,
        "ingestion_rate_pct": ingestion_rate_pct,
        "conference_ingestion_rate_pct": conference_ingestion_rate_pct,
        "pdf_only_ingestion_rate_pct": pdf_only_ingestion_rate_pct,
        "durations_registered_count": durations_registered_count,
        "ready_to_use_rate_pct": ready_to_use_rate_pct,
        "checked_at": checked_at
    }

    fieldnames = [
        "process_timestamp",
        "total_conferences",
        "total_audio_conferences",
        "total_pdf_only_reports",
        "has_pdf",
        "has_audio",
        "has_transcript",
        "has_srt",
        "fully_ingested",
        "pdf_only",
        "pdf_only_healthy",
        "pdf_only_broken",
        "ingestion_rate_pct",
        "conference_ingestion_rate_pct",
        "pdf_only_ingestion_rate_pct",
        "durations_registered_count",
        "ready_to_use_rate_pct",
        "checked_at"
    ]

    with open(HEALTH_SUMMARY_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(summary_data)

    print(f"Successfully generated health summary at {HEALTH_SUMMARY_CSV}")

if __name__ == "__main__":
    main()
