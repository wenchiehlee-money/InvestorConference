---
name: skill-company-investorconference-ingest
description: 投資人說明會/財報事件材料蒐集 Ingest 模組（支援台股與美股）；法說會抓音檔、IR、逐字稿，財報事件抓 Skills 財報結果、earnings release、financial tables、SEC filing，並避免對純財報事件產生 FIN/GT。
---

# InvestorConference Ingest 技能說明

本技能提供法說會影音、簡報、第三方逐字稿與 metadata 的材料蒐集與同步。Ingest 的責任是把可用原始材料放進 repo，研究級字幕校正與 GT 生成由 `skill-company-investorconference-digest` 負責。

## ⚙️ 核心功能
1. **智慧影音下載 (Smart Ingest)**：自動檢測美股/台股市場，解析 webcast 影音網址或透過 YouTube 尋找，並藉由 `yt-dlp` 下載音檔。
2. **材料蒐集與落檔**：保存音檔、IR PDF/Markdown、第三方逐字稿、Yahoo/AlphaSpread/AlphaMemo 等可用來源。若產生機器字幕，僅視為 `*_FIN.srt` 初稿。
3. **美股 earnings-call 材料支援**：對所有非台灣 ticker，依照季度解析結果蒐集 earnings release、prepared remarks、IR presentation、performance review/deck、financial tables、transcript PDF/HTML 與 SEC 10-Q/10-K/8-K；Yahoo/Google Finance/AlphaSpread 僅作 discovery 或 transcript 補充；其中 Google Finance/Quartr 若已用瀏覽器確認精確季度，且取得可重現的 presentation 或完整 earnings-call transcript，可作為 conference-material 的 I/M 證據，但仍不得填入 F/X，也不得冒充 FIN.srt 的 S。
4. **簡報 OCR 與文字層提取**：批次處理各公司 PDF 簡報，必要時透過 Mac-mini 高精度 OCR API 補齊圖表數值。
5. **README、Manifest 與音檔 metadata 自動同步**：維護 `audio_manifest.json`、`audio_durations.json`、`audio_metadata.json` 與 README.md 表格。

> [!IMPORTANT]
> Ingest 不負責產生或判定 `*_GT.srt`。GT 是 digest 前的研究資料校正成果，必須由 `skill-company-investorconference-digest` 使用 FIN、音檔、IR、Q&A、第三方逐字稿與前後期資料交叉生成或修正。

## 🎧 音檔 checksum / metadata 防呆規則

Ingest 必須把「音檔身份」與「音檔長度」分開管理：

| 檔案 | 角色 | 規則 |
| :--- | :--- | :--- |
| `audio_manifest.json` | stem -> release URL | SRT player 與 README 的音檔來源 |
| `audio_durations.json` | file path -> integer seconds | 只供 README/SRT player 顯示長度；不得用來判定音檔是否相同 |
| `audio_metadata.json` | stem -> checksum/size/duration/status | 音檔身份與 duplicate 判定的可稽核來源 |

每次新增或更新音檔時必須執行以下 gate：

1. 先對下載完成的本地音檔計算 `sha256`、`size_bytes` 與 ffprobe `duration_sec`。
2. 將 `sha256` 與 `audio_metadata.json`、本地音檔及 GitHub Release asset digest（若 API 提供）比對。音檔只存 GitHub Release asset，不進 Git 或 Git LFS。
3. 若 checksum 已存在於不同 stem，必須拒絕登錄或上傳，避免把舊季度音檔掛到新季度。
4. 若 release 中已存在疑似重複音檔，執行 audit 工具重建 metadata，並將錯誤季度標為 `status: duplicate`、`duplicate_of: <canonical_stem>`。
5. `audio_durations.json` 只能視為顯示用快取；即使 duration 不同，也不能覆蓋 checksum 結論。若 checksum 相同但 duration cache 不同，應以重新 ffprobe 的結果更新 duration。

建議稽核指令：

```bash
# 只稽核指定 stem，避免一次下載全部 release 音檔
python skills/skill-company-investorconference-ingest/scripts/audit_audio_metadata.py \
  --stems 2454_2025_q4 2454_2026_q1 \
  --cache-dir /tmp \
  --update-durations

# CI 或批次檢查可加 fail-on-duplicate
python skills/skill-company-investorconference-ingest/scripts/audit_audio_metadata.py --fail-on-duplicate
```

> [!CAUTION]
> 若 `audio_metadata.json` 顯示某 stem 為 `duplicate`，該季度的 FIN.srt 很可能也來自錯誤音檔。Ingest 不應關閉資料品質問題；digest skill 必須在 GT/digest 前把音訊錯配列為 Blocker/Major，直到正確音檔或足夠文字來源可支持保守 GT candidate。

### 公司 IR / MOPS 來源選擇與日期窗口檢查

Ingest 不得只信任 MOPS 查詢結果的第一個影音檔。部分公司或 MOPS 查詢會回傳該公司最新法說影音，即使目標是前一季度。


### MOPS 文件類型邊界

本 repo 會接觸兩種不同的 MOPS 相關文件，必須在命名與 README 說明中區分：

| 類型 | 來源/入口 | README row | 目前落檔/連結 | 用途 | 不可做的事 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| MOPS 法說會附件 | `t100sb07_1` 法說會/受邀法說公告附件，常見檔名 `{stock}{YYYYMMDD}{M/E}001.pdf` | `法說會` / `受邀法說` | `data/{stock}/{stock}_{year}_q{quarter}_ir.pdf`、`_ir_en.pdf` | 法說會簡報、presentation deck、營運/財務結果簡報；可支援 digest 與 GT 校正 | 不得稱為「財報」或用來滿足 `財報` row 的 statutory financial report 缺口 |
| MOPS repo 財報文件 | `../MOPS` 或 `wenchiehlee-investment/MOPS/downloads/...`，常見檔名 `{YYYYQQ}_{stock}_AI1.pdf`、`AIA.pdf` | `財報` | README 外部連結或後續落檔為 report/financial statement 類材料 | 財報事件的一級財務文件、GoodInfo 尚未更新時的財務數字來源 | 不得用來滿足 `法說會` row 的音檔/法說會附件缺口；除非同一來源明確也是法說會簡報 |

對非台灣股票，`F/X` 也代表官方財務結果材料，不限於 MOPS：`F` 是公司 IR 的 earnings-release / financial-results PDF、SEC 8-K Exhibit 99.1 或 SEC/公司 financial-tables PDF；`X` 是同一份來源的 Markdown 轉檔。若官方只提供 HTML/web page 而沒有 PDF，仍可將官方頁面保存為可追溯的 Markdown sidecar，並同時填 `F/X`；不得因缺少 PDF 自動標成 `-`。HTML 轉 MD 時必須保留官方 URL、公司、季度、公告日期與來源類型。這些是財報材料，不能與 `I/M`（IR presentation PDF/MD）混用；第三方 transcript 不得填入 `F/X`。

Broadcom 等 IR CDN 可能對 Python `requests` 回傳 HTTP 403，但同一個公開 PDF 可由 `curl` 取得。下載器只對 403 啟用 `curl` fallback，並強制檢查 `%PDF-` magic bytes；HTML challenge 或錯誤頁會被拒絕。Broadcom earnings 還必須檢查官方 Events & Presentations archive：有日期的 `Company Presentation`（例如 `20260902 Broadcom_Company_Overview.pdf`）才可作該季 `I`，earnings-release PDF 才是 `F`，兩者不可混用。

Micron 的季度頁會把正式材料分在不同官方入口：`Q3 Earnings Deck` 是 `I`、同季 earnings-release PDF 是 `F`、prepared remarks 是補充逐字稿；下載器應以季度頁/事件頁提供的 canonical `micron.gcs-web.com` URL 為準，不要保留會回 404 的舊 `investors.micron.com/node/...` 別名。

GlobalFoundries 的季度結果頁同時列出 earnings release、earnings presentation 與 Form 6-K；季度 `earnings release` PDF 才是 `F`，`earnings presentation` PDF 才是 `I`。兩個 PDF 必須分別轉成 `*_report_en.md` 與 `*_ir_en.md`，不可用同一份 PDF 同時填兩種旗標。

Marvell 的季度頁會同時提供 `Earnings Release PDF`、`Financial and Business Results PDF` 與 `Additional Earnings Information PDF`。`Earnings Release PDF` 應標準化為 `*_report_en.pdf/md`，作為 `F/X`；營運簡報則維持 `*_performance_review.pdf/md`，作為 `I/M`。不能因為其他財務 PDF 已存在就跳過 earnings-release PDF。

HP Inc. 的 earnings event page 會明確分開 `Results Press Release` 與 `Results Presentation`。前者標準化為 `*_report_en.pdf/md`（`F/X`），後者標準化為 `*_ir_en.pdf/md`（`I/M`）；兩個連結都必須以同一個 fiscal-quarter event page 驗證，不能只抓最新一份文件。

NVIDIA 的季度頁會把 `Quarterly Presentation` 與書面 `CFO Commentary` 分開提供；兩者都是公司官方 PDF。季度簡報標準化為 `*_ir_en.pdf/md`（`I/M`），CFO Commentary 或 earnings-release PDF 標準化為 `*_report_en.pdf/md`（`F/X`）。SEC 8-K HTML/第三方 transcript 只能作 provenance 或補充來源，不能單獨填 `F/X`。

Qualcomm 的 historical financial results 頁會分開提供 `Earnings Release` 與 `Earnings Presentation` PDF；同一 fiscal quarter 的 release 應標準化為 `*_report_en.pdf/md`（`F/X`），presentation 應標準化為 `*_ir_en.pdf/md`（`I/M`）。例如 FY2026 Q3（公告 2026-07-29）對應 calendar 2026 Q2，不能誤歸到 calendar Q3。

TSMC 的 ADR ticker `TSM` 與台股 ticker `2330` 指向同一家公司，但 matrix 仍須為非台灣 `TSM` 保存自己的可追溯材料。TSMC Q2 2026 官方 Quarterly Results 頁的 `Financial Statements` 應標準化為 `TSM_2026_q2_report_en.pdf/md`（`F/X`），`Presentation Material` 應標準化為 `TSM_2026_q2_ir_en.pdf/md`（`I/M`）；Transcript 只能作補充來源，不可取代這兩個 PDF。

因此，像 `2382_2026_q2_ir.pdf` / `_ir_en.pdf` 這類從 `238220260813M001.pdf` / `E001.pdf` 取得的檔案，應描述為「MOPS 法說會附件 / investor-conference presentation deck」。即使內容包含 Q2 財務結果，也不是 MOPS repo 的財報文件。相反地，README `財報` row 連到 `wenchiehlee-investment/MOPS/downloads/.../202602_2382_AI1.pdf` 這類檔案時，才是財報事件材料。

### 來源層級與衝突處理

Ingest 必須把來源分成兩層，且不得讓二級來源覆蓋一級來源的季度、日期、檔案類型或公司正式材料判定。

| 層級 | 來源 | 可用用途 | 限制 |
| :--- | :--- | :--- | :--- |
| 一級來源 | 公司 IR 官網、公司正式 replay/webcast、公司正式 PDF、MOPS/TWSE 官方公告、SEC filing（美股） | 決定季度、日期、檔案類型、是否為正式公司材料；落檔與 README metadata 的主依據 | 若一級來源彼此衝突，必須保留衝突紀錄並降信心，不得靜默覆蓋 |
| 二級來源 | Google Finance earnings tab / Quartr、FinmoConf、AlphaSpread、Yahoo Finance transcript、AlphaMemo、第三方法說會索引或摘要平台 | 發現資料、補逐字稿、補 speaker/Q&A、交叉驗證、產生候選來源清單；其中已用瀏覽器確認精確季度的 Quartr presentation 或完整 transcript 可作 conference-material `I/M` | 不得覆蓋一級來源的季度/日期/檔案類型；Quartr `I/M` 仍不得宣稱為公司官方來源，也不得填入 `F/X` 或 `S` |

#### Google Finance earnings tab secondary fallback

若公司 IR、官方 webcast/replay 與 MOPS/TWSE 都沒有取得音檔，Ingest 可把 Google Finance earnings tab 當作二級 discovery fallback，例如 `https://www.google.com/finance/beta/quote/2382:TPE?tab=earnings`（台股，固定 `:TPE` 後綴）或 `https://www.google.com/finance/beta/quote/AVGO:NASDAQ?tab=earnings`（美股，交易所後綴依 ticker 而異）。這個來源常由 Quartr 提供文件、逐字稿或 HLS replay audio，可補足 README 中暫列 `無` 的音檔缺口。

### Google Finance browser requirement (verified)

Google Finance earnings data is rendered and historical rows are lazy-loaded; a static `curl`/`requests` response is not sufficient to conclude that audio or a transcript is absent. The maintained browser order is:

1. Use Playwright first. Launch Chromium with `--no-sandbox`; if the repository-managed Playwright browser is unavailable, use an installed `chromium`, `chromium-browser`, or `google-chrome` executable via `executable_path`.
2. Use Selenium only as a documented fallback when Playwright cannot start or the target page is incompatible; do not switch between tools silently. Record the tool, browser executable, URL, and failure reason in the ingest log.
3. Install/repair the runtime before classifying a source as unavailable: `pip install playwright` and `python -m playwright install chromium`, or use the verified system Chromium path.
4. For a historical quarter, render the page, locate the exact `Previous reports` quarter row, open its `Documents and forms` control, and verify the quarter label before accepting any PDF, media manifest, or transcript. The page's main panel may remain on the newest quarter.
5. Google Finance/Quartr remains a secondary source for provenance, but a quarter-confirmed Quartr presentation or complete earnings-call transcript may populate conference-material `I/M`. It must retain the Google Finance page URL, captured Quartr URL, exact quarter label, and source type. It still cannot populate `F/X` or `S`; official financial-report provenance remains required for `F/X`, and FIN.srt remains required for `S`.

A browser failure, missing Playwright runtime, or a page that only shows the newest quarter must be recorded as `not verified`; it must not be converted to the matrix `-` indicator.

> [!NOTE]
> 美股 ticker 沒有像台股 `:TPE` 這種固定後綴，需要逐一在 `ingest.py` 的 `KNOWN_US_GOOGLE_FINANCE_EXCHANGE` 登記 `{ticker: exchange}`（例如 `AVGO: NASDAQ`、`HPE: NYSE`）才會啟用；未登記的 ticker，`scrape_google_finance_earnings_audio()` / `fetch_google_finance_transcript()` 會直接回傳空結果，不會猜測交易所或假造候選網址。新增一個美股 ticker 前，必須先手動打開該頁面確認交易所後綴正確、且頁面能顯示目標 `Fiscal Q{N} {Year}` 文字，才可登記。已驗證：AVGO FY2026 Q3、HPE FY2026 Q3（2026-09-04 ingest）。

使用條件：

1. 只在一級來源已檢查後使用；不得跳過公司 IR、官方 replay 或 MOPS/TWSE。
2. 必須用 Playwright/Chromium render earnings tab，不能只用靜態 HTML 判定沒有資料。
3. 頁面必須明確顯示目標 `Fiscal Q{N} {Year}` 或等價季度文字；若仍是 `Waiting for the earnings call` 且未攔截到 media manifest，不得產生音檔。
4. 僅接受可重現的 Quartr media manifest 或音檔 URL，例如 `files.quartr.com/.../master.m3u8` 或 `/streams/YYYY-MM-DD/.../playlists.m3u8`；不得用 segment、chunk、`part_*.ts` 或中間實作 URL。
5. 若 URL 含會議日期（例如 `/streams/2026-07-30/...`），日期必須落在目標季度的法說會窗口。
6. 下載後仍要通過 checksum、duration、duplicate gate；成功時 `audio_metadata.json` 必須記錄 `source: google_finance_quartr`、Google Finance page `source_url`、實際 `captured_media_url` 與 secondary-source note。
7. Google/Quartr 可補音檔、逐字稿與 conference-material I/M；README 的季度、日期與事件類型仍以一級來源為準。Quartr transcript/presentation 不得填入 F/X，也不得改寫 S；必須在 sidecar 保存 secondary-source provenance。
8. Quartr `master.m3u8` 是完整長篇 HLS 會議串流；即使 playlist 與 segments 可正常 HTTP 200，也可能超過短下載 timeout。實作對 Quartr HLS 使用最長 600 秒的 ffmpeg/yt-dlp timeout；timeout 只代表本次下載未完成，不得標記為 `not_published` 或誤判為需要註冊。

### ffmpeg runtime prerequisite

The ingestion skill must reuse the `ffmpeg` already provided by the runtime; it must not install packages during a local ingestion run. Before starting audio extraction, verify `command -v ffmpeg` and fail with a clear prerequisite error if it is absent. GitHub Actions may install `ffmpeg` only when the ephemeral runner does not already provide it (`command -v ffmpeg || apt-get install ...`).

**逐字稿（transcript）**：同一個 earnings tab 頁面通常也內嵌 Quartr 提供的完整逐字稿（含講者姓名/職稱與時間戳記，從開場到 Q&A 到 operator 結束語）。`fetch_google_finance_transcript(stock_id, year, quarter, stem, save_dir)` 會捲動該頁面觸發逐字稿區塊 lazy-load、以同一個 `Fiscal Q{N} {Year}` 文字比對確認季度，再存成 `{stem}_google_finance_transcript.md`（清除 UI 雜訊如 `music_history`/`Listen from here`，保留講者標題與時間戳）。若頁面明確確認目標季度，這個完整 Quartr transcript 可作 conference-material 的 I/M（I 與 M 可連到同一個 transcript artifact），但不能作 F/X 或 FIN.srt 的 S；sidecar 必須記錄 Google Finance page、captured Quartr URL 與季度文字。`ingest_earnings_audio()` 的 `done()` 已將它接在 AlphaSpread/Yahoo transcript 之後、都沒有結果時自動嘗試一次。

若一級與二級來源衝突，例如第三方索引把公司官方 `2026 Q2` 法說會標成 `2026Q3`：

1. README、manifest、metadata 必須以一級來源為準。
2. 二級來源只可記錄為 discovery/reference URL。
3. 在 `audio_metadata.json`、sidecar metadata、issue draft 或 ingest log 中記錄 mismatch，包含來源 URL、二級來源標籤、官方判定與處理結果。
4. 不得因二級來源存在而跳過官方頁面、官方 PDF、官方 replay 或 MOPS/TWSE 的核對。

來源優先順序：

1. 已知的 quarter-specific 官方公司 IR / seminar / replay URL。
2. 公司 IR seminar 頁中與目標季度名稱及會議日期一致的影音檔。
3. MOPS video/PDF，但必須通過會議日期窗口檢查。
4. 其他搜尋或 fallback。

日期窗口規則：

* `Q4` 法說會通常落在下一年度 `01` 至 `04` 月。
* `Q1` 法說會通常落在同年度 `04` 至 `06` 月。
* `Q2` 法說會通常落在同年度 `07` 至 `09` 月。
* `Q3` 法說會通常落在同年度 `10` 至 `12` 月。

若 MOPS 回傳影音或 PDF 檔名日期不在目標窗口，必須拒絕該 asset，不得下載、不得更新 manifest，也不得產 FIN。若公司 IR 頁列出更精確的目標季度影音，應將其加入 quarter-specific direct source，讓後續 re-ingest 可重現。

若公司官方 IR 頁的 `VIDEO`、`影音`、`錄音` 或 replay 連結是短 HTML redirect、YouTube 短網址、Zucast/webcast player 或其他二段式播放器，ingest 必須跟隨該官方 redirect 並把最後可重現的 quarter-specific URL 寫入 direct source mapping；不得只依賴 `ytsearch` 或 MOPS fallback。若 redirect 只在 browser network 裡暴露 `.mp3`、`.m4a`、`.mp4` 或 HLS manifest，需用 Playwright/Chromium 擷取並驗證後落檔。

若官方 IR 頁只提供 YouTube 候選，title 必須明確符合目標年度與季度（例如 `Q2 2026`、`2Q 2026`、`2026Q2` 或中文 `2026年第二季`）。若 title 顯示同年度其他季度（例如目標 `2026 Q2` 卻是 `1Q 2026`），必須拒絕該候選；不得用「頁面第一支影片」或只匹配年度的 fallback 產生音檔。

驗證時不得用固定 45 或 60 分鐘作為正確音檔門檻；部分官方法說 replay 可能只有十幾分鐘。長度檢查只用來拒絕明顯空檔或截斷檔，正確性仍以官方來源、目標季度名稱、會議日期窗口與 checksum 去重為主。

### Playwright browser-download fallback

許多公司 IR 站、webcast 平台或新版官方頁面會使用 Cloudflare、JavaScript challenge、registration flow、動態連結或防 hotlink 機制。若 `curl`、`requests`、`yt-dlp` 或 MOPS fallback 取得的是 HTML challenge、登入頁、空檔或錯誤 content-type，不可直接判定材料不存在；必須改用 Playwright/Chromium 以真瀏覽器 context 下載。

使用規則：

1. 先以 Playwright 開啟一級來源頁面作為 `warmup-url`，取得 cookie、session 與動態頁面狀態。
2. 用同一個 browser context request 下載 PDF、音檔或 webcast material URL，並帶入官方頁 `Referer`。
3. 下載後必須驗證 HTTP status、`content-type`、檔案大小與 magic bytes，例如 PDF 必須以 `%PDF` 開頭，m4a/mp4 前段必須含 `ftyp`。
4. 若 browser download 成功，應以本地官方檔案更新 README；若只取得外部 registration form，不得產生音檔、FIN 或 GT。
5. 若需要提交姓名/email 才能取得 replay 或 webcast，必須先取得使用者明確同意與使用者提供的資料；不得使用假個資自動送出公司表單。
6. 使用者提供的姓名、email、公司、職稱等表單欄位必須存放在 ignored `.env` 或執行環境變數中；不得寫入 tracked script、README、metadata、issue、commit message 或 log artifact。執行前需用 `git check-ignore -v .env` 或等效方式確認不會被提交。
7. 若 Playwright 只能取得 PDF 但不能取得 audio/replay，仍應落檔 PDF/MD，並在 sidecar metadata 記錄 audio 缺口。
8. 若 webcast backend 只回傳 live playlist，但 playlist 回 404/403/HTML、player 已切到 `wordCardType=picture` 或結束圖、或 `/live` 端點沒有媒體內容，不得建立 `.m4a`、FIN 或 GT；必須在 sidecar 記錄已測試的 playlist、player fallback、HTTP status、content-type 與結論。
9. Live 結束後若使用者回報官方頁面更新，必須重新檢查一級來源的季度頁、歷史材料頁與 audio-webcast/replay 頁，而不只重查原 live channel。若官方頁新增 `watch?v=...`、`replay`、`線上會議視訊重播` 等入口，需用 headed/persistent Playwright 開啟 replay 頁並擷取 network 中實際 HLS/DASH/media URL；只有 manifest 與 segment 均為 HTTP 200 且 content-type 正確時，才可用 ffmpeg/yt-dlp 抽出音檔並更新 release asset、`audio_manifest.json`、`audio_metadata.json`、README 與 sidecar。

可重用下載工具：

```bash
python skills/skill-company-investorconference-ingest/scripts/download_with_playwright.py \
  --warmup-url https://investor.tsmc.com/chinese/quarterly-results/2026/q2 \
  --kind pdf \
  --download data/2330/2330_2026_q2_ir.pdf=https://.../2Q26%20Presentation%20%28C%29.pdf
```

> [!IMPORTANT]
> browser-download fallback 是 ingest 的一級材料取得流程，不是 digest 的推論流程。成功取得的檔案仍必須通過 checksum/magic-byte/content-type gate，並產生 Markdown sidecar 供 digest 使用。

#### chrome-devtools MCP browser inspection（僅限互動 session，非 daily-ingest.yml）

某些 IR 站（例如 Wistron/緯創）在 Akamai edge 層級直接擋掉 headless 環境（`requests`、無頭 Playwright）：連根網域都回 403 `Access Denied`（`errors.edgesuite.net`），不是單一頁面或爬蟲偽裝問題，`curl`/`requests`/headless Playwright 換 UA、locale、header 都無法繞過。

在互動式 Codex session 中處理 ingest 時，若 **mcp chrome devtools** 可用，應優先把它納入瀏覽器檢查流程：用它確認目前已開啟的頁面、觀察真實瀏覽器渲染狀態、檢查是否落在 Access Denied / registration / replay 頁、必要時跑 accessibility 或 Lighthouse snapshot 來驗證頁面可讀性。這對官方 IR 頁、webcast player、JavaScript redirect 與需要真瀏覽器 session 的下載線索特別有用。

若一般工具無法取得材料，且 chrome-devtools MCP 暴露了可操作頁面、DOM snapshot、script evaluation 或 network inspection 類工具，則可把該真實、已通過瀏覽器驗證的 session 作為最後一層 fallback：

1. 先呼叫可用的 `mcp__chrome_devtools` 工具（例如 `list_pages`，若存在則用 page/open/snapshot/click/evaluate/network 相關工具）確認瀏覽器 session 與目標一級來源頁面狀態；若成功載入非 Access Denied 頁，代表該瀏覽器 session 可能已通過 bot 防護。
2. 用可用的 DOM snapshot、page inspection 或 click 工具找出目標音檔/PDF 連結（`data-title`、年份 tab、分頁按鈕等需要時操作 DOM 找出正確季度）。
3. 若工具支援在頁面 context 內執行 script 或讀取 network，才可用該能力 `fetch()` 目標 URL、擷取實際 media/PDF URL，並把大檔案寫到 scratchpad 或本地暫存，避免把 base64 大內容塞進對話 context。
4. 本地用 Python/ffmpeg 把 base64 解碼、必要時轉檔（例如 mp3 不能塞進 `.m4a`/MP4 容器,要嘛保留 `.mp3` 副檔名,要嘛重新編碼),再放到 `tmp/{stock_id}_{year}_q{quarter}.{ext}`。
5. 呼叫 `ingest.py <stock_id> <year> <quarter> --push`（若目標路徑與 `tmp/{stem}.m4a` 快取命中會跳過重新下載),或直接 `import ingest; ingest.commit_push_files(...)` 走完 checksum/上傳/README/commit 流程。

> [!IMPORTANT]
> 這是**人工協助的一次性補齊流程**，不是可自動化的 pipeline 步驟。`daily-ingest.yml` 在 GitHub Actions headless runner 上執行，沒有 chrome-devtools MCP 可用，Akamai 擋下的來源在排程裡仍會持續失敗——需要使用者在互動 session 中手動觸發這個 escalation。

### 錯誤/重複音檔的 re-ingest 前置清理

若發現某季度 release audio 與另一季度 checksum 相同，或 FIN 開頭明確屬於其他季度，必須先清掉錯誤狀態再重新 ingest。不可在錯誤 release asset 仍存在時直接重跑 ingest，否則 README、SRT player、Mac-mini FIN 可能繼續吃到舊音檔。

清理順序：

1. 用 GitHub release asset digest 確認重複關係，記錄錯誤 stem、canonical stem、sha256、size。
2. 刪除錯誤季度的 GitHub release audio asset；只刪錯誤 stem，不刪 canonical stem。
3. 移除錯誤 stem 在 `audio_manifest.json` 的 URL。
4. 移除錯誤 stem 在 `audio_durations.json` 的顯示快取。
5. 移除或改正 `audio_metadata.json` 中錯誤 stem；若保留稽核紀錄，必須標 `status: duplicate` 與 `duplicate_of`，不得標 `ok`。
6. 刪除由錯誤音檔產生的 `{stem}_FIN.srt`；若 `{stem}_GT.srt` 是依錯 FIN 生成，也必須刪除。
7. 更新 README，讓錯誤季度的音檔、FIN、GT 欄位回到缺失狀態。
8. commit 清理狀態後，再重新執行 `ingest.py <stock_id> <year> <quarter> --push`。
9. re-ingest 成功後，立刻跑 targeted audit：

```bash
python skills/skill-company-investorconference-ingest/scripts/audit_audio_metadata.py \
  --stems <wrong_stem> <canonical_or_adjacent_stem> \
  --cache-dir /tmp \
  --update-durations \
  --fail-on-duplicate
```

驗收條件：

* 新音檔 sha256 不得等於任何不同 stem。
* `audio_manifest.json` URL 必須指向新 release asset。
* `audio_metadata.json` 的 stem 必須有 `sha256`、`size_bytes`、`duration_sec`、`status: ok`。
* Mac-mini FIN 只能在音檔通過 checksum gate 後生成。


## 財報事件材料蒐集規則

當 README `類型` 為 `財報` 時，Ingest 不得把該事件當成法說會處理；除非同一事件另有正式 earnings call / webcast replay，否則不得產生音檔、FIN.srt 或 GT.srt。財報事件的責任是取得「結果」與可稽核財務文件，供 digest 做 earnings-result 分析。

財報事件優先材料：

| 材料 | 建議檔名 | 用途 |
| :--- | :--- | :--- |
| Skills 財報結果 | `{ID}_{Year}_q{N}_skills_result.md` / `.json` | 已整理的財報實績、共識 beat/miss、重點摘要；若可得應優先落檔 |
| Earnings release / report | `{ID}_{Year}_q{N}_report_en.pdf/md` 或 `_report.md` | 公司正式財務結果第一來源 |
| Financial tables | `{ID}_{Year}_q{N}_financial_tables.pdf/md` | GAAP/non-GAAP、現金流、資產負債表、reconciliation |
| Supplemental / performance deck | `{ID}_{Year}_q{N}_performance_review.pdf/md` 或 `_ir_en.md` | segment、guidance、KPI 補充 |
| SEC filing | `{ID}_{Year}_q{N}_10q.md` 或 metadata link | 美股 10-Q/10-K 交叉驗證 |
| Consensus snapshot | repo-synced `data/Yahoo.Finance/raw_yahoo_finance_consensus_history.csv` | revenue/EPS consensus cutoff 比較 |

Skills 使用規則：

1. Skills workflow 是財報結果輔助流程，不是公司一級來源；財務硬數字仍需以公司 release、financial tables 或 SEC filing 驗證。
2. 若 Skills workflow 與公司文件衝突，以公司文件為準，並在 sidecar/issue 記錄 mismatch。
3. 若 README 只有 Yahoo Finance financials 連結，應先嘗試用 Skills 財報流程取得該 ticker/季度財報結果，再補公司 IR/SEC 官方文件。
4. Skills workflow 回傳資料若含個別欄位來源、時間戳或更新時間，必須保存；若只有摘要，digest 信心不得標高於中。
5. 財報事件可產出 digest，但欄位應標為 `earnings_result_digest`；音檔、FIN、GT 維持 `-`，直到官方 call audio/transcript 存在。

Repo 邊界與落檔規則：

* `InvestorConference` 保存 event-level evidence：某一個 `{Ticker}_{Year}_q{N}` 財報/法說事件的官方 release、financial tables、SEC filing 摘錄、webcast/transcript 與 digest 證據台帳。
* `../ConceptStocks`、`../Yahoo.Finance` 或其他資料倉庫保存 normalized company/market data、概念分類、共識時間序列或 discovery metadata；不得把這些資料當成本 repo 的一級財報文件。
* 若 `raw_event_upcoming_earnings.csv`、Yahoo 或 ConceptStocks 的季度標籤與公司 IR/SEC filing 衝突，季度與日期以公司 IR/SEC filing 為準，並在 ingest log 或 sidecar 記錄 mismatch。
* 已知 US calendar-year 公司財報公告需要用公告月份做 sanity check；未知 ticker 或特殊 FY 公司不得自動覆蓋 CSV/FY 標籤，需等公司 IR/SEC 確認。規則：1-3 月通常為前一年 Q4，4-6 月為當年 Q1，7-9 月為當年 Q2，10-12 月為當年 Q3；Apple、QCOM、Dell、NVIDIA 等特殊會計年度公司需保留 `QxFYyyyy` 標籤。
* 每個 official source snapshot 建議附 `{ID}_{Year}_q{N}_sources.json`，包含 `source_url`、`source_type`、`retrieved_at`、`accession`（若為 SEC）、`sha256` 與 `notes`。

## Official IR quarterly financials

For non-Taiwan competitors where provider data is incomplete, ingest official IR financial tables before downstream analysis. Run from `InvestorConference`:

```bash
python3 skills/skill-company-investorconference-ingest/scripts/fetch_official_ir_financials.py --provider all --replace-symbol
```

Output:

- `data/financials/raw_ir_quarterly_financials.csv`: normalized official quarterly rows.
- `data/{symbol}/{symbol}_official_ir_sources.json`: source URL, retrieval timestamp, SHA-256, and discovery links.

Provider status:

- `0992.HK` Lenovo: parses official key financial HTML table into quarterly rows.
- `005930.KS` Samsung: official earnings release discovery sidecar; PDF/table extraction still pending.
- `0981.HK` SMIC: official page discovery sidecar; table extraction still pending.

Downstream consumers should prefer this official CSV over `../ConceptStocks` provider rows when the same symbol and quarter both exist.

## 🇺🇸 美股材料蒐集規則

當 `stock_id` 為英文字母 ticker（如 `DELL`, `QCOM`, `GOOGL`）或 metadata 顯示為美股時，Ingest 仍只負責材料蒐集，不負責投資分析或 GT 判定。應盡量落檔或記錄以下來源：

| 材料 | 建議檔名 | 用途 |
| :--- | :--- | :--- |
| Earnings call audio | `{Ticker}_{Year}_q{N}.m4a` | FIN/GT 字幕時間軸來源 |
| FIN subtitle | `{Ticker}_{Year}_q{N}_FIN.srt` | 機器轉錄初稿 |
| Earnings release / report | `{Ticker}_{Year}_q{N}_report_en.pdf/md` | GAAP 財務數字第一來源 |
| Performance review / deck | `{Ticker}_{Year}_q{N}_performance_review.pdf/md` 或 `_ir_en` | 管理層簡報、guidance、segment 資訊 |
| Financial tables | `{Ticker}_{Year}_q{N}_financial_tables.pdf/md` | GAAP/non-GAAP reconciliation、現金流、資產負債表 |
| Google Finance/Quartr conference artifact | `{Ticker}_{Year}_q{N}_google_finance_transcript.md`、`_quartr_transcript.md` 或對應的 `_google_finance_presentation.pdf/md`、`_quartr_presentation.pdf/md` | 精確季度已驗證後可作 conference-material `I/M`；必須保存 Google Finance 頁面、Quartr URL、季度文字與來源類型 |
| Third-party transcript | `{Ticker}_{Year}_q{N}_yahoo_transcript.md` / `_alphaspread_transcript.md` | speaker、Q&A、英文術語校正補充；除非符合前述 Google Finance/Quartr 季度驗證規則，否則不可填 `I/M` |
| SEC filing link/file | `{Ticker}_{Year}_q{N}_10q.md` 或 metadata link | 10-Q/10-K 交叉驗證（若可得） |

> [!CAUTION]
> 一般美股第三方 transcript 只能作補充來源。Google Finance/Quartr 若已用瀏覽器確認精確季度，完整 transcript 或 presentation 可填 conference-material `I/M`，但仍不是 `F/X` 或 `S`；若與公司 IR、earnings release 或 SEC filing 衝突，digest 應以一級來源為準。

### 🇺🇸 美股 deterministic ingest workflow

美股資料通常比台股容易透過公司 IR 或 SEC 取得，但「容易找到」不等於「已完成 ingest」。每個 ticker/quarter 必須依下列順序執行；不得因為已經有 transcript、`sources.json` 或 digest 就宣告 `I/M/F/X` 完成。

#### 1. 先固定季度身份與 calendar period

1. 先呼叫 `skill-stock-fiscal-quarter-resolve`，以公告日期、公司財年起始月、SEC period-of-report 與公司頁面標籤確認 `fiscal_year/fiscal_quarter`。
2. 保留原始 fiscal key，例如 `NVDA_2027_q2`；另外計算 calendar period，例如 `2026 Q2`。不得把 calendar year 直接寫回來源檔名。
3. 若 metadata、Yahoo/ConceptStocks、公司 IR、SEC 的季度標籤衝突，以公司 IR/SEC 為準，並在 `{stem}_sources.json` 記錄 mismatch。
4. 同一 calendar quarter 的同日 `法說會` 與 `財報` 仍是兩個 event records；材料可以共用同一季度 key，但不能把事件列去重。

#### 2. 對每個季度執行官方 source ladder

| 順序 | 先查 | 可取得的材料 | 成功條件 |
| :--- | :--- | :--- | :--- |
| 1 | 公司 IR earnings/results page | earnings release、financial tables、prepared remarks、IR deck、replay | 頁面明確包含公司、季度與公告日期；保存 quarter-specific URL |
| 2 | 公司 IR PDF/HTML 直接連結 | `I/M` 或 `F/X` | 先分類文件，不可把 earnings release 當 presentation |
| 3 | SEC submissions/company filing index | 8-K Exhibit 99.1、10-Q、10-K、earnings release exhibit | 保存 accession、filing date、period of report、原始 URL；使用 SEC 官方內容作交叉驗證 |
| 4 | 官方 webcast/replay | audio、官方 transcript | 驗證季度文字與會議日期後才落檔 |
| 5 | Google Finance/Quartr、Yahoo、AlphaSpread | audio/transcript/discovery URL | 精確季度驗證後，Quartr presentation/transcript 可作 conference-material `I/M`；不得取代 `F/X`，也不得取代 `S` |

每一層都必須記錄「已查過但沒有目標季度材料」；不能只記錄成功下載的來源。若公司 IR 被 Cloudflare/Akamai 擋住，依本 skill 的 Playwright/chrome-devtools fallback 重試，不得直接標記 unavailable。

#### 3. 嚴格套用 `I/M/F/X` 分類

| Flag | 必須存在 | 不可用來替代 |
| :--- | :--- | :--- |
| `I` | 官方 IR presentation / investor deck PDF，例如 `*_ir_en.pdf`；或已用 Google Finance/Quartr 精確確認季度的 presentation/transcript artifact | earnings release、10-Q、一般未驗證 transcript |
| `M` | `I` 的同一份 PDF 轉成 Markdown，例如 `*_ir_en.md`；Quartr transcript-only artifact 可用同一份完整 MD 同時作 I/M | 未確認季度的 transcript、SEC HTML、financial-results MD |
| `F` | 官方 earnings release、financial-results、financial tables、SEC exhibit PDF，或已核實的官方 HTML/web page | 第三方 transcript、digest |
| `X` | `F` 的同一份官方來源保存/轉成 Markdown，例如 `*_report_en.md` 或 `*_financial_tables.md` | 第三方摘要、未核實 URL |

必要的配對規則：

- `I` 沒有 `M` 時，必須建立 `TODO: convert I PDF to MD`，不能因 PDF 可讀就補填 M。
- `M` 沒有同 stem 的 `I` 時，必須降級為 orphan MD，不能填 `M`。
- `X` 沒有同一季度/同一來源的 `F` 時，保留 `X` 但必須在 sources sidecar 標為 `pdf_missing`；matrix 不得假裝 F 存在。
- `F` PDF 轉檔含 `TODO:OCR` 時，F 可存在但 X 必須標為 incomplete，並建立 OCR TODO；不能把 partial MD 當成完整 X。官方 HTML/web page 轉成 MD 時沒有 PDF OCR 要求，但必須保留來源 URL 與完整可讀內容。
- `I/M` 與 `F/X` 必須分別記錄 source URL、source type、SHA-256；兩組檔案即使來自同一個 IR page，也不能互相滿足。

建議的落檔名稱：

```text
data/{TICKER}/{TICKER}_{FY}_{q}_ir_en.pdf
data/{TICKER}/{TICKER}_{FY}_{q}_ir_en.md
data/{TICKER}/{TICKER}_{FY}_{q}_report_en.pdf
data/{TICKER}/{TICKER}_{FY}_{q}_report_en.md
data/{TICKER}/{TICKER}_{FY}_{q}_financial_tables.pdf
data/{TICKER}/{TICKER}_{FY}_{q}_financial_tables.md
data/{TICKER}/{TICKER}_{FY}_{q}_10q.md
data/{TICKER}/{TICKER}_{FY}_{q}_sources.json
```

`10q.md`、`8k.md` 等 SEC snapshot 必須在 `sources.json` 指向 accession 與原始 SEC URL；若官方只發布 HTML，該 SEC HTML 可轉存為 `report_en.md`，並在 `sources.json` 明確標記 `source_type: official_sec_html`，此時 matrix 可填 `F/X`，不必虛構 PDF。

#### 4. 每季度完成 gate

對每個已到期或明確要求 ingest 的美股季度，執行以下 gate 並保存結果：

```text
[ ] fiscal quarter / calendar period resolved
[ ] official IR results page checked
[ ] SEC filing index checked when applicable
[ ] I: presentation PDF present or explicit not-published
[ ] M: presentation PDF converted, no TODO:OCR
[ ] F: official financial-results PDF present, or official HTML/web page captured
[ ] X: matching official financial-results Markdown present, with source URL and no unresolved extraction gap
[ ] unverified transcript/audio classified as supplemental; quarter-confirmed Quartr presentation/transcript may be used as I/M, never F/X or S
[ ] sources.json has URLs, source types, dates/accession, sha256, and missing-material notes
[ ] README and investor_material_matrix regenerated
```

若官方沒有發行某一類文件，寫入 `not_published`；若應有但尚未抓到，寫入 `TODO:ingest`；若 PDF 已抓到但轉檔/OCR 尚未完成，寫入 `TODO:OCR`。三者不可都用空白表示，否則無法區分「公司沒有」與「pipeline 漏抓」。

#### 5. 批次稽核與補抓順序

先處理最新 calendar quarter 中缺少 `F/X` 的公司，再處理只缺 `I/M` 的公司，最後才補 transcript/audio。建議每次以一家公司一個季度為單位，避免把同公司的不同 fiscal quarter 混在一起：

```bash
# 先列出官方來源與季度 mapping；不得直接以 transcript 當完成
python skills/skill-company-investorconference-ingest/scripts/fetch_official_ir_financials.py \
  --provider all --replace-symbol

# 完成指定季度後重建 matrix / README
python skills/skill-company-investorconference-ingest/scripts/ingest.py \
  <TICKER> <FISCAL_YEAR> <FISCAL_QUARTER> --update-readme

# 只補抓官方 PDF，避免在材料健康批次中重抓長篇音訊
python skills/skill-company-investorconference-ingest/scripts/ingest.py \
  <TICKER> <FISCAL_YEAR> <FISCAL_QUARTER> --materials-only
```

批次完成後，對每個非台股 ticker 輸出一行 `calendar_period`, `I`, `M`, `F`, `X`, `missing_reason`。沒有 `F` 的 `X`、只有未驗證 transcript 的季度，以及仍缺 I/M 的季度都必須進入 TODO/issue 清單；已用瀏覽器確認精確季度的 Quartr presentation/transcript 可列為 I/M，不應再被歸類為「資料不存在」。

## Audio storage boundary

Conference audio is stored only as a GitHub Release asset under the `audio-files`
release. It is never committed to Git, Git LFS, or Google Drive. Any legacy Google
Drive migration script is historical-only and must not be used by new ingestion.

## 📂 檔案清單
* `scripts/ingest.py`：主 Ingest 邏輯。
* `scripts/audio_utils.py`：本地音檔狀態與 manifest 讀寫。
* `scripts/audio_storage_bridge.py`：GitHub Releases 語音上傳與回退邏輯。
* `scripts/audit_audio_metadata.py`：重新下載 release 音檔、計算 checksum/duration、更新 `audio_metadata.json` 並標示 duplicate。
* `scripts/migrate_audio_to_gh_releases.py`：歷史 GDrive 資源移轉至 GitHub。
* `scripts/fetch_yahoo_transcript.py`：透過瀏覽器抓取 Yahoo Finance 逐字稿的獨立工具。
* `scripts/fetch_official_ir_financials.py`：抓取非台股官方 IR 財務表並輸出 `data/financials/raw_ir_quarterly_financials.csv`；目前 Lenovo 會產生 normalized quarterly rows，Samsung/SMIC 會產生 source discovery sidecar，後續再補 PDF/table parser。
* 台股 Ready 財報/法說事件若 GoodInfo 尚未更新，需先落公司官方 PDF，並用 `skills/skill-mac-mini-ocr/scripts/convert_ir_pdfs.py <stock>` 產生 `{stock}_{year}_q{n}_{press_release|financial_statements|ir}.md`。這些 official Markdown sidecars 是 downstream competitor/valuation table 的一級補值來源。
* `scripts/download_with_playwright.py`：以 Playwright/Chromium browser context 下載受 Cloudflare、JS challenge 或 hotlink 防護影響的官方 PDF/影音材料，並驗證 content-type 與 magic bytes。

## 🚀 使用方法
```bash
# 下載指定股票特定季度的音檔與可用材料；若有機器字幕，僅作為 FIN 初稿
python skills/skill-company-investorconference-ingest/scripts/ingest.py <stock_id> <year> <quarter> [--push]

# 更新 README 表格與持續更新
python skills/skill-company-investorconference-ingest/scripts/ingest.py --update-readme
```

### README event rows and health-counting boundary

README is both an event catalog and a material-status view. Keep these concepts separate:

1. A same-day `法說會` and `財報` are two rows and count as `1 + 1`; never deduplicate them because their dates match. The conference row tracks call/presentation/transcript materials, while the report row tracks the official financial-report material.
2. Future calendar rows with no assets are valid `planned/not_due` rows, not ingestion failures. They must be excluded from Healthy/Warning/Broken ingestion denominators until their due date or until material collection is explicitly requested.
3. Ingestion health denominators come from due/past event keys and artifact evidence, not from every README row. Keep conference-event and report-event denominators separate; `pdf_only` means standalone report events with no conference/audio/transcript signal, not every report paired with a conference.
4. If a consolidated report inventory is needed, calculate it separately as `conference-paired reports + standalone pdf-only reports` and label it as all reports. Do not overwrite the `pdf_only` health metric with that catalog count.

### README `--update-readme` 合併規則：法說會 vs 受邀法說 vs 財報

`raw_event_upcoming_earnings.csv`（同步自 `wenchiehlee-investment/InvestorEvents`，該 repo 即時爬 MOPS）對同一 `(股票, 年, 季)` 可能同時出現多筆非財報事件——例行季度法說會，以及公司另外受邀參加、與該季財報公布日相隔甚遠的投資論壇。`--update-readme` 用以下規則區分並合併已 ingest 的素材，避免把某一場的音檔/逐字稿/PDF 誤貼到另一場的日期上：

1. **例行 vs 受邀分類**：事件日期距「該季季底」超過 50 天（`INVITED_MEETING_THRESHOLD_DAYS`，同時定義於本 skill 的 `fetch_upcoming_earnings.py` 與 `ingest.py`），標為 `受邀法說`；否則為 `法說會`。
2. **素材認領需日期相近**：`ingest.py` 會用同一季 `財報` CSV 事件的日期，當作「已下載素材真正對應日期」的代理值（因為台股法說會與財報公布幾乎都是同日）。只有當 `法說會`/`受邀法說` CSV 事件日期與該財報日期相差 **14 天以內**（`NEARBY_CALL_DAYS`），才允許該 CSV 列直接繼承已 ingest 的音檔/FIN/GT/PDF；相差過遠則視為不同場次，不得認領既有素材。
3. **不得靜默壓制真正的法說會列**：即使同季已有一筆日期很遠的 `受邀法說` CSV 事件，只要已 ingest 的素材日期（財報日期）與該事件對不上，仍必須另外輸出一筆以財報日期為準、type 為 `法說會` 的列，讓真正的素材有正確歸屬。
4. 若 CSV 事件因此變成「無素材可認領」的未來事件，僅在其日期落在 `today` 起算 4 週內才顯示（CSV-only 佔位列，音檔/FIN/GT/PDF 皆為 `-`）；超出視窗則暫不顯示，待接近時自然出現。

> 反例：2301 光寶科 2026 Q2 的 07-31 例行法說會材料曾被誤貼到 CSV 另一筆 09-16「受邀法說」事件上（兩者相差 47 天，超過 14 天窗口），README 因而顯示「受邀法說 2026-09-16」卻附著 07-31 的音檔/簡報。修正後兩者會分開列出，且 09-16 那筆在超出 4 週視窗前不顯示。

```bash
# 稽核 release 音檔 checksum 與 duration
python skills/skill-company-investorconference-ingest/scripts/audit_audio_metadata.py --stems <stem...> --update-durations

# 使用 Playwright browser context 下載受保護官方材料
python skills/skill-company-investorconference-ingest/scripts/download_with_playwright.py \
  --warmup-url <official_page_url> \
  --kind pdf \
  --download <local_path.pdf>=<official_pdf_url>

# 批次轉換簡報 PDF 檔案
python skills/mac-mini-ocr/scripts/convert_ir_pdfs.py
```
