---
name: skill-mlx-api-client-whisper
description: 以 GitHub issue 觸發 Mac-mini 上的 whisper 轉錄 pipeline（skill-mlx-api-server-whisper），並輪詢結果是否已同步回本 repo。支援法說會音訊、YouTube 財經影片等多種來源。
---

# Mac-mini Whisper Pipeline 整合技能 (skill-mlx-api-client-whisper)

| 項目 | 內容 |
| :--- | :--- |
| 版本 | 1.0.2（詳見 `metadata.json`） |
| 來源 | https://github.com/wenchiehlee/InvestorConference |
| 登錄庫 | https://github.com/wenchiehlee/skills （`common/skill-mlx-api-client-whisper`） |
| 維護者 | wenchiehlee |
| 對應 Callee Skill | `common/skill-mlx-api-server-whisper`（Mac-mini 上實際執行 pipeline） |

## ⚠️ 與 `skill-mlx-api-client-ocr` 的關鍵差異

`skill-mlx-api-client-ocr` 是同步 HTTP client（`POST /ocr` 直接拿到 response）。**本技能不是**——whisper pipeline 耗時（單一 stem 完整跑完約 1–1.5 小時）且有狀態（多實驗轉錄 → postprocess → CER → git commit），因此改用**issue 驅動、非同步輪詢**的模式：

1. 本技能在**目標 repo**（跑 pipeline 的 Mac-mini repo）開一張帶 `generate-FIN` label 的 issue，附上 YAML metadata
2. Mac-mini 上的 self-hosted runner（`run-pipeline.yml`）監聽到 label 後接手執行
3. 執行完成後，Mac-mini 只會把 `FIN.srt` sync 回**本 repo**（你呼叫此技能所在的 repo）；`GT.srt` 由本 repo 維護，Mac-mini 的 GroundTrue 只是 cache
4. 呼叫方（例如排程或下一次執行）呼叫 `check_fin_status` / `close_if_done` 確認完成並關閉 issue

## 📦 技能結構說明

```text
skill-mlx-api-client-whisper/
├── SKILL.md
├── metadata.json
├── self_update.py
└── scripts/
    └── whisper_issue_client.py   # WhisperIssueClient：開/查/關 issue 的核心邏輯
```

## ⚙️ 前置環境配置

### 1. 安裝依賴
```bash
pip install requests python-dotenv
```

### 2. 設定環境變數（`.env`）
```env
WHISPER_TARGET_REPO=ZhongZheng782/Mac-mini          # 跑 pipeline 的 repo
WHISPER_SOURCE_REPO=wenchiehlee-money/YoutubeAudio.Fetch   # 本 repo（音訊/GT 的家）
WHISPER_SOURCE_TYPE=youtube                          # investor_conference | youtube
REPO_FILE_SYNC_ZHONGZHENG782_MONEY=<PAT，僅需 WHISPER_TARGET_REPO 的 Issues: Read and write>
```

> 變數名沿用既有 `tools/manage_missing_fin_issues.py` 與 Mac-mini Actions secrets 的命名慣例（`REPO_FILE_SYNC_<...>`）。這個 PAT **只需要對 `WHISPER_TARGET_REPO`（例如 `ZhongZheng782/Mac-mini`）開 Issues: Read and write**——不需要 Contents 權限，也不需要對本 repo（`WHISPER_SOURCE_REPO`）本身有任何權限，因為 `check_fin_status()` 只檢查本地檔案是否已被 `git pull` 同步下來，不透過 API 查詢。若沒有 `REPO_FILE_SYNC_*` 變數，會 fallback 讀取通用的 `GH_TOKEN`。

> `WHISPER_SOURCE_TYPE=investor_conference` 時 stem 需符合 `{stock_id}_{year}_q{quarter}`；`youtube` 時需符合 `{channel}_{video_id}`（video_id 固定 11 碼）。詳見 `skill-mlx-api-server-whisper` SKILL.md 的 stem 規則表。

## 🚀 使用方式

### 方式 A：批次同步整個 manifest
維護一份 `{stem: audio_url}` 的 `audio_manifest.json`（跟 InvestorConference 既有格式相同），對每個 stem：FIN.srt 已存在就關掉對應 issue，不存在且沒有 open issue 就開一張：
```bash
python scripts/whisper_issue_client.py sync audio_manifest.json
```

### 方式 B：作為模組整合進自己的排程腳本
```python
from scripts.whisper_issue_client import WhisperIssueClient

client = WhisperIssueClient()   # 讀 .env 裡的 WHISPER_* 變數
client.open_fin_request("some-channel_dQw4w9WgXcQ", audio_url="https://...")

# 之後排程輪詢：
if client.check_fin_status("some-channel_dQw4w9WgXcQ"):
    client.close_if_done("some-channel_dQw4w9WgXcQ")
```

### 方式 C：查詢單一 stem 狀態
```bash
python scripts/whisper_issue_client.py status some-channel_dQw4w9WgXcQ
```

## 🌐 語言提示（`language`）— issue metadata 欄位 vs. 實際生效位置

`investor_conference` source_type 下，`issue_body()` 會依 stem 解析出的 `stock_id` 自動附上 `language` 欄位：數字股號（台股）→ `zh`，英文字母 ticker（美股/國際股）→ `en`。若呼叫 `open_fin_request()` 或 `issue_body()` 時想覆寫自動判斷，可傳入 `language="en"` / `language="zh"` 明確指定。

> [!CAUTION]
> 這個 `language` 欄位目前**只出現在 issue body 裡供人閱讀，Mac-mini 端的 `run-pipeline.yml` 並不會讀取它**（`parse_issue_metadata()` 完全沒有解析 `language` key）。真正決定轉錄語言的是 **`ZhongZheng782/Mac-mini` repo 裡的 `mlx-api-server-whisper/company-configs/{TICKER}/whisper.yaml`**（`language: en` / `language: zh` 欄位）；該檔案不存在時，`run-pipeline.yml` 會透過 `2>/dev/null || echo "zh"` 悄悄退回 `zh`。
>
> 2026-09-05 實際發生：AVGO/HPE FY2026 Q3 第一次跑出的 `FIN.srt` 是 `Language: zh`，把英文法說會內容轉成語意錯誤的中文譯述（甚至把年份講錯），比對 `data/DELL/DELL_2027_q2_FIN.srt`、`data/NVDA/NVDA_2027_q2_FIN.srt` 才發現這兩者是因為早就有對應的 `company-configs/DELL/whisper.yaml`、`company-configs/NVDA/whisper.yaml`（`language: en`）才轉錄正確；AVGO/HPE 當時完全沒有這個目錄。
>
> **幫任何非台股（英文字母 ticker）新增 ingest 時，必須同時在 `ZhongZheng782/Mac-mini` repo 建立 `mlx-api-server-whisper/company-configs/{TICKER}/whisper.yaml`**（比照 `DELL`/`NVDA`/`QCOM` 既有格式：`company_name`、`stock_id`、`language: en`、`executives`、`products`、`terms`、`example_sentences`，內容需從已取得的官方逐字稿/新聞稿驗證，不得憑空杜撰），單靠 issue body 的 `language` 欄位不會生效。
>
> 若某張 `generate-FIN` issue 已經在補建 config 之前先跑過一次（因而產出錯誤語言的 `FIN.srt`），不要重開新 issue（`open_fin_request()` 對同標題的 open issue 是 no-op）；改為對同一張 issue 移除再加回 `generate-FIN` label 來重新觸發 `issues: types: [labeled]` 事件：
> ```bash
> gh issue edit <number> --repo ZhongZheng782/Mac-mini --remove-label generate-FIN
> gh issue edit <number> --repo ZhongZheng782/Mac-mini --add-label generate-FIN
> ```

## 🔁 GT 修正迴圈（`refine_fin_srt`）

若 GT.srt 在本 repo 被人工修正過，本 repo 是 GT owner；Mac-mini 不會把 cache GT 回推覆蓋本 repo。想讓 Mac-mini 重新拉最新 GT 並重跑 CER 評分（不需要重新轉錄），呼叫時指定 `task_type="refine_fin_srt"`：
```python
client.open_fin_request(stem, audio_url, task_type="refine_fin_srt")
```
GT 校正原則見 `skill-mlx-api-server-whisper` SKILL.md：語境相依的修正只留在 GT，不會自動被學習進 `company-configs` 的 corrections 字典。若本 repo 有 `data/**/*_GT.srt` 更新通知 workflow，可直接 dispatch Mac-mini `run-pipeline.yml`，並帶 `skip_transcribe=true`。

## 🔄 版本管理與更新
- 唯一可信來源為 skills 登錄庫中的 `common/skill-mlx-api-client-whisper`；各專案（InvestorConference、YoutubeAudio.Fetch）內的副本皆由登錄庫部署而來
- 版本採語意化版本，記錄於 `metadata.json`
- 檢查並更新到登錄庫最新版本：
  ```bash
  python self_update.py
  ```
