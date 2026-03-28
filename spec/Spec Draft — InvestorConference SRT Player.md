# Spec Draft — InvestorConference SRT Player

> Status: Draft
> Date: 2026-03-28

---

## 概述

**核心目的**：快速理解法說會脈絡，讀懂公司高管的思維與溝通方式。

純 client-side 靜態 web app（TypeScript + Vite），部署於 **GitHub Pages**（`wenchiehlee-money/InvestorConference`）。無需伺服器——所有資產（音訊、SRT、PDF）直接從 public repo 以 `raw.githubusercontent.com` 取得，檔案列表由 **GitHub Git Trees API** 建立。

---

## 整體佈局與導覽

兩個核心頁面，**list → detail** 導覽（桌面與手機一致）：

```
┌──────────────────────────────────────────────────────┐
│                File Manager（列表頁）                  │
│                                                      │
│  [ 全部 ]  [ 法說會 ]  [ GTC 大會 ]  [ Podcast ]      │ ← Filter Bar
│  [ 公司分組 ]  [ 法說日期 ]  [ 列表 ]  [ 🔍 搜尋 ]    │ ← View 切換
│                                     [ 排序 ▼ ]       │
│                                                      │
│  ▼ 廣達 2382                                          │
│       2025 Q3   [GT] [Gen]  📄×2   01:08:23          │
│       2025 Q2   [GT]        📄×1   01:02:44          │
│  ▶ 台達電 2308  （收合）                               │
│  ▶ 英業達 2356  （收合）                               │
└──────────────────────────────────────────────────────┘
                     點擊列 ↓  /  back button ↑
┌──────────────────────────────────────────────────────┐
│                SRT Player（詳細頁）                    │
│                                                      │
│  ← 返回                                               │
│  廣達 2382  ·  2025 Q3 法說會  ·  2026-03-20          │
│  電腦、伺服器、筆電代工，AI 伺服器為主要成長動能         │ ← 主要業務
│                                                      │
│  相關文件：                                            │
│  📄 2382_2025_q3_presentation.pdf  ↗                 │
│  📄 2382_2025_q3_report.pdf  ↗                       │
│  ──────────────────────────────────────────          │
│    [01:23]  已過的字幕行                              │ ← 暗色
│    [01:35]  已過的字幕行                              │
│    [01:48]  已過的字幕行                              │
│    [02:01]  已過的字幕行                              │
│  ▶ [02:14]  我們今年~~底~~的毛利率維持在穩定水位        │ ← highlight bar（第5行）
│    [02:28]  未到的字幕行                              │ ← 略暗
│    [02:41]  未到的字幕行                              │
│    [02:55]  未到的字幕行                              │
│    [03:08]  未到的字幕行                              │
│    [03:21]  未到的字幕行                              │
│  ──────────────────────────────────────────          │
│  [ ▶ Play ]  [ ■ Stop ]  [ 1x ▼ ]                   │ ← 控制列
└──────────────────────────────────────────────────────┘
```

導覽規則：
- 點擊 File Manager 的列 → 進入 SRT Player 詳細頁
- 瀏覽器 back button → 回到列表頁**並恢復上次 scroll 位置**
- 實作：`history.pushState` / `popstate` + `sessionStorage` 記錄 scroll position
- 桌面 + 手機皆支援（響應式）

---

## File Manager

### 資料來源

**音訊 / SRT / PDF 檔案列表**：GitHub Git Trees API（一次取全部，無需 token）

```
GET https://api.github.com/repos/wenchiehlee-money/InvestorConference/git/trees/main?recursive=1
```

Client 端過濾 `.m4a` / `.mp3` / `.wav` / `_turboscribe.srt` / `.srt` / `.pdf`，從路徑解析欄位。

**音訊時長**：從 `audio_durations.json`（repo 根目錄）讀取，單一 request 取得全部：

```json
{
  "2382/2382_2025_q3.wav": 3720,
  "2308/2308_2025_q4.mp3": 3716,
  "2357/2357_2025_q4.m4a": 3587
}
```

- 支援 `.m4a` / `.mp3` / `.wav` 三種格式
- key：相對路徑；value：秒數（整數）
- `ingest.py` 在新增音訊時自動更新此檔案

**公司資訊**（依市場別）：

| 市場 | 來源 CSV | 對照鍵 | 使用欄位 |
|------|---------|-------|---------|
| 台灣上市公司 | `raw_companyinfo.csv`（sync 自 `wenchiehlee-investment/Python-Actions.GoodInfo.CompanyInfo`）| `代號` | `名稱`、`主要業務`、`產業別`、`*概念` |
| 美國上市公司 | `raw_conceptstock_company_metadata.csv`（sync 自 `wenchiehlee-investment/ConceptStocks`）| `Ticker` | `公司名稱`、`產品區段` |

對照邏輯：路徑頂層資料夾為**數字** → TW 市場；為**英文 ticker** → US 市場。

**法說日期**：`upcoming_earnings.csv`（sync 自 `wenchiehlee-investment/InvestorEvents`）

對照邏輯：從路徑取 Stock ID，在 `upcoming_earnings.csv` 找 `類別=法說會` 且 `事件名稱` 含該 ID 的列，取 `開始日期`。

> **待辦**：以下三個 sync workflow 尚未建立：
> - `.github/workflows/sync-companyinfo.yml`（`raw_companyinfo.csv`）
> - `.github/workflows/sync-conceptstocks.yml`（`raw_conceptstock_company_metadata.csv`）
> - `.github/workflows/sync-investorevents.yml`（`upcoming_earnings.csv`）

### 音訊內容類型

| 類型 | 頂層資料夾 | 範例 |
|------|----------|------|
| 法說會 | 數字股票代號（e.g. `2382/`）| 現有資料，維持現狀 |
| GTC 大會 | `GTC/` | GTC 2025 Keynote |
| Podcast | `Podcast/` | 游庭皓的財經皓角 |

### 列表欄位

| 欄位 | 說明 |
|------|------|
| 類型 | 法說會 / GTC 大會 / Podcast |
| Stock ID | 從路徑解析（e.g. `2382`）|
| 名稱 | 公司名稱或節目名稱（從公司資訊 CSV 對照）|
| Period | 從檔名解析（e.g. `2025 Q3`）|
| 法說日期 | 從 `upcoming_earnings.csv` 對照（法說會類型才有）|
| Duration | 從 `audio_durations.json` 讀取（單一 request 取得全部）|
| GT SRT | `{stem}_turboscribe.srt` 存在 → 綠色 badge「GT」|
| Gen SRT | `{stem}.srt` 存在 → 藍色 badge「Gen」|
| PDF | 同目錄 `.pdf` 數量（e.g. 📄×2）|

### Filter Bar

```
[ 全部 ]  [ 法說會 ]  [ GTC 大會 ]  [ Podcast ]
```

全文搜尋時：**掃描範圍**跨所有類型；**顯示範圍**依 Filter Bar 選取過濾。

### View 切換

```
[ 公司分組 ]  [ 法說日期 ]  [ 列表 ]  [ 🔍 搜尋 ]     [ 排序 ▼ ]
```

| View | 說明 | 適合場景 |
|------|------|---------|
| **公司分組** | 同公司歷季聚在一起，可展開/收合 | 深入研究某公司、看歷史脈絡 |
| **法說日期分組** | 依法說會舉辦日期分組，同日多家公司並列 | 追最新法說、橫向比較同期公司 |
| **平鋪列表** | 無分組，純可排序表格 | 快速依特定欄位排序 |
| **全文搜尋** | 跨所有 SRT 關鍵字搜尋，progressive 顯示結果 | 找特定主題的高管發言 |

排序：
- 點擊欄位標題（column header）
- 右上角排序 dropdown（e.g. 日期新→舊 / 股票代號 / 類型）

### 列互動規則

- **點擊列** → 進入 SRT Player 詳細頁
- **無 SRT**（GT 與 Gen 皆無）→ 整行呈灰色、無法點擊
- **有 GT + Gen** → Diff Mode（見 SRT Player 章節）

---

## 全文搜尋 View

### 搜尋框

```
┌──────────────────────────────────────────┐
│  🔍  搜尋逐字稿關鍵字...                  │
└──────────────────────────────────────────┘
搜尋中… 已掃描 12 / 34 份
```

- debounce ~300ms 觸發
- 逐一 fetch 每份 SRT，找到結果**即時插入列表**（progressive）
- 掃完後依當前 View 模式重新排序/分組
- 狀態列：`找到 27 筆結果（依 Filter Bar 顯示 15 筆）`
- 多關鍵字：空格分隔，AND 邏輯

### 搜尋結果格式

```
廣達 2382  ·  2025 Q3  ·  [02:14]
  資本支出方面，我們預計今年【毛利率】將維持在穩定水位...
────────────────────────────────────
台達電 2308  ·  2025 Q4  ·  [18:32]
  受惠 AI 伺服器需求，【毛利率】有望持續改善...
```

- 關鍵字前後各 ~20 字上下文
- 關鍵字以 highlight 標示
- 點擊結果 → 導覽到 SRT Player 詳細頁，bar 定位到該行

---

## SRT Player

### 詳細頁結構

1. **頁首**：公司名稱 + Stock ID + Period + 法說日期
2. **背景 context**：`主要業務`（TW）或 `產品區段`（US）
3. **PDF 連結區**：同目錄 `.pdf` 清單，點擊開新分頁
4. **字幕視窗**：10 行，highlight bar 固定第 5 行
5. **控制列**：Play/Pause、Stop、播放速度

### 控制列

| 控制項 | 行為 |
|--------|------|
| Play / Pause | 切換播放／暫停（同一按鈕）|
| Stop | 停止並將音訊歸零 |
| 播放速度 | 0.75x / 1x / 1.25x / 1.5x / 2x（`<audio>.playbackRate`）|

### 字幕視窗

- 固定顯示 **10 行**
- **Bar 固定在第 5 行**，字幕隨時間向上 scroll

| 行狀態 | 呈現 |
|--------|------|
| 已過 | 暗色 |
| 當前 | 全亮 + highlight bar |
| 未到 | 略暗 |

每行格式：`[mm:ss]  字幕文字`

### Diff Mode（GT + Gen 皆存在時）

- 以 **GT SRT 為主軸**顯示
- 與 Gen SRT 有差異的字詞加上**橘色底線**標記
- 點擊差異標記 → tooltip 展開顯示 Gen 版本文字
- 無差異的行正常顯示，不干擾閱讀
- 僅有一種 SRT 時，正常顯示，無 diff

```
▶ [02:14]  我們今年~~底~~的毛利率維持在穩定水位
                  ^^^
           （tooltip）GT: 的  ·  Gen: 底
```

### 點擊字幕行

- 點擊任意行 → 音訊跳到該行 `start` timestamp
- 播放中 → 繼續播放（從新位置）
- 暫停中 → 自動開始播放
- Bar 立即移動到該行並置中

---

## 技術架構

| 項目 | 選擇 |
|------|------|
| 語言 | TypeScript |
| 建置 | Vite |
| 部署 | GitHub Pages（`docs/` 目錄）|
| 音訊 | `<audio>` + `timeupdate` 事件（~250ms 精度）|
| SRT 解析 | 自製 regex parser（無外部 library）|
| Diff 演算法 | 自製 LCS / Myers diff（字詞級別，無外部 library）|
| 動畫 | CSS `@keyframes`（scroll + highlight）|
| 導覽 | `history.pushState` / `popstate` + `sessionStorage`（scroll 位置）|
| 資料來源 | GitHub Git Trees API + `raw.githubusercontent.com` |

---

## 待辦 / 待確認

| # | 項目 | 狀態 |
|---|------|------|
| Q3 | Duration 來源：`audio_durations.json`（ingest 時自動更新，單一 request）| ✅ 已確認 |
| Q4 | 響應式：桌面 + 手機皆支援 | ✅ 已確認 |
| Q5 | SRT 合併：Diff Mode，GT 為主軸，差異橘色底線，點擊 tooltip 顯示 Gen | ✅ 已確認 |
| Q6 | 佈局：list→detail 導覽，桌面與手機一致 | ✅ 已確認 |
| Q7 | 路徑規則：數字=法說會，`GTC/`=GTC，`Podcast/`=Podcast | ✅ 已確認 |
| Q8 | Stage 音訊不進此 repo，無需過濾 | ✅ 已確認 |
| Q9 | 公司資訊：TW 用 `raw_companyinfo.csv`；US 用 `raw_conceptstock_company_metadata.csv` | ✅ 已確認，sync workflow 待建 |
| Q10 | 法說日期：`upcoming_earnings.csv`（`開始日期`）| ✅ 已確認，sync workflow 待建 |
