---
source: https://raw.githubusercontent.com/wenchiehlee-money/InvestorConference/refs/heads/main/raw_column_definition_IC.md
destination: https://raw.githubusercontent.com/wenchiehlee-money/biztrends.TW/refs/heads/main/definitions/raw_column_definition_IC.md
---

# Raw CSV Column Definitions - InvestorConference Repo

---

## investor_conference_health_summary.csv (InvestorConference Ingestion Health Summary)
**No:** 80
**Source:** `data/reports/investor_conference_health_summary.csv`
**Purpose:** Summarize investor conference media ingestion metrics (PDFs, audio files, transcripts, srt files) to track ingestion coverage.

### Column Definitions:

| Column | Type | Description |
|--------|------|-------------|
| `process_timestamp` | timestamp | Time when health metrics were computed (Taipei Time). |
| `total_conferences` | int | Total number of conference events identified from directory filenames. |
| `has_pdf` | int | Total number of conference events that have at least one PDF presentation file downloaded. |
| `has_audio` | int | Total number of conference events that have audio tracks registered in `audio_manifest.json`. |
| `has_transcript` | int | Total number of conference events that have transcript markdown files. |
| `has_srt` | int | Total number of conference events that have srt subtitle files. |
| `fully_ingested` | int | Number of events fully ingested (contains PDF + Audio + either Transcript or SRT). |
| `pdf_only` | int | Number of events that only have PDF downloaded, but missing audio and transcripts. |
| `ingestion_rate_pct` | float | Percentage of conference events fully ingested (`fully_ingested / total_conferences * 100`). |
| `durations_registered_count` | int | Total number of conference events that have audio durations registered in `audio_durations.json`. |
| `ready_to_use_rate_pct` | float | Percentage of events with audio durations registered out of all identified events (`durations_registered_count / total_conferences * 100`). |
| `has_digest` | int | Number of conference events that have an analysis digest report (`data/reports/conference-digests/{stock_id}/{key}_digest.md`, produced by skill-conference-digest). |
| `digest_eligible` | int | Number of conference events eligible for digest analysis (has SRT subtitle or transcript). |
| `digest_rate_pct` | float | Digest coverage of analyzable events (`has_digest / digest_eligible * 100`). |
| `conf_md_complete` | int | Audio-conference events whose presentation PDFs are all converted to MD with full OCR (no `TODO:OCR` markers). |
| `conf_md_partial` | int | Audio-conference events whose presentation MDs exist but contain unconverted scanned pages (`<!-- TODO:OCR ... -->` markers from pdf_fallback). |
| `conf_md_missing` | int | Audio-conference events with at least one presentation PDF that has no corresponding MD file. |
| `conf_md_complete_rate_pct` | float | Presentation MD completeness over audio conferences that have PDFs (`conf_md_complete / (complete+partial+missing) * 100`). |
| `fully_ingested_md_warning` | int | Fully-ingested audio conferences whose presentation MD is partial or missing; shown as "Warning" (部分收錄) in downstream dashboards. |
| `checked_at` | timestamp | Execution time of the health checker (same as `process_timestamp`). |

---
