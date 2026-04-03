# Ingest TODO

- [ ] Fix `scrape_playwright_direct_ir(...)` so an already-intercepted video URL is returned even if `Page.goto(..., wait_until="networkidle")` times out.
- [ ] Reduce Playwright reliance on `networkidle` for OTT replay pages that keep long-lived media/network activity open.
- [ ] Make `2454 2025 Q3` ingest succeed end-to-end by reusing the intercepted replay stream instead of falling through after timeout.
- [ ] Make `2330 2025 Q3` ingest succeed end-to-end by reusing the intercepted replay stream instead of falling through after timeout.
- [ ] Investigate why `2330 2025 Q2` replay page `v=2393` currently yields `No video URLs found` and add extraction logic that works for that page.
- [ ] Update `.github/workflows/ingest.yml` so the workflow fails when no audio file is produced or committed, instead of reporting a false success when `push=true`.
- [ ] Support PDF-only ingest success by committing downloaded PDFs even when no audio is available.
- [ ] Verify whether `2454` PDF-only cases should be considered a successful ingest outcome or a partial ingest outcome.
- [ ] Add a post-run verification step that checks the target files actually exist in the repo after `--push`.
- [ ] Re-run and verify these cases after fixes: `2330 2025 Q2`, `2330 2025 Q3`, `2454 2025 Q3`.
