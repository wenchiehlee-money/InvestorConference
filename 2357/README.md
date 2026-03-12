# 2357 ASUS (華碩電腦) — Investor Conference Audio

Earnings call audio files for ASUS (TWSE: 2357), downloaded via `ingest_poc.py` from the official webcast-eqs.com HLS stream.

## Files

| File | Quarter | Size | Duration | Source |
|------|---------|------|----------|--------|
| `2357_2025_q4.m4a` | 2025 Q4 | 133 MB | ~60 min | webcast-eqs.com HLS |
| `2357_2025_q3.m4a` | 2025 Q3 | 119 MB | ~57 min | webcast-eqs.com HLS |
| `2357_2024_q4.m4a` | 2024 Q4 | 117 MB | ~56 min | webcast-eqs.com HLS |

## How to download more quarters

```bash
cd Mac-mini
python Whisper-API-Server/ingest_poc.py 2357 <year> <quarter>
# e.g.
python Whisper-API-Server/ingest_poc.py 2357 2024 3   # Q3 2024
python Whisper-API-Server/ingest_poc.py 2357 2024 2   # Q2 2024
```

Output is saved to `Whisper-API-Server/whisper-sandbox/` then move here.

## Official Source

- IR Page: https://www.asus.com/event/Investor/C/
- Webcast: https://www.webcast-eqs.com/asus{YY}q{Q}/tc
