# Ingest TODO

## Current Status

- [x] `2454 2025 Q1` audio + PDF 已落地並推上 `main`
- [x] `2454 2025 Q2` audio + PDF 已落地並推上 `main`
- [x] `2454 2025 Q3` audio + PDF 已落地並推上 `main`
- [x] `2454 2025 Q4` audio + PDF 已落地並推上 `main`
- [x] `2454 2025 Q4` 產物已統一為 `.m4a`，不再保留舊 `.mp3`
- [x] `audio_durations.json` 已補上 `2454 2025 Q1~Q4 .m4a` 時長
- [x] Web player 現在允許「只有音訊、沒有 SRT」的 entry 進入 player；無字幕時仍可播放音訊與開啟 PDF
- [x] `2330 2025 Q1` audio + IR PDF + transcript PDF 已落地並推上 `main`
- [x] `2330 2025 Q2` audio + IR PDF + transcript PDF 已落地並推上 `main`
- [x] `2330 2025 Q3` audio + IR PDF + transcript PDF 已落地並推上 `main`
- [x] `2330 2025 Q4` audio + IR PDF + transcript PDF 已落地並推上 `main`
- [x] `2330 2025 Q4` 產物已統一為 `.m4a`，不再保留舊 `.mp3`
- [x] `audio_durations.json` 已補上 `2330 2025 Q1~Q4 .m4a` 時長

## Remaining TODO

- [ ] Fix `scrape_playwright_direct_ir(...)` so an already-intercepted video URL is returned even if `Page.goto(..., wait_until="networkidle")` times out.
- [ ] Update `.github/workflows/ingest.yml` so the workflow fails when no audio file is produced or committed, instead of reporting a false success when `push=true`.
- [ ] Support PDF-only ingest success by committing downloaded PDFs even when no audio is available.
- [ ] Verify whether PDF-only cases should be considered a successful ingest outcome or a partial ingest outcome.
- [ ] Add a post-run verification step that checks the target files actually exist in the repo after `--push`.
