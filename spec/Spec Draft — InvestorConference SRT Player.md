# Spec Draft — InvestorConference SRT Player

> Status: Implementation-aligned draft with approved product-direction updates
> Updated: 2026-04-03

---

## 概述

InvestorConference SRT Player 是一個純 client-side 靜態 web app，使用 TypeScript + Vite 建置，部署到 GitHub Pages。它的目標是把 repo 內既有的音訊、字幕與 PDF 整理成可瀏覽、可搜尋、可播放的介面。

目前產品已經有三個主要視圖：
- File Manager：列表、公司分組、法說日期分組、全文搜尋
- Player Detail：播放音訊、檢視字幕、切換 Diff 模式、查看相關 PDF
- PDF Viewer：在站內檢視 PDF，而不是只把 PDF 當成下載檔案

這份 spec 以目前程式碼為準。已實作功能寫在前段，未實作功能統一整理在「尚未實作（Backlog）」區塊，避免和現況描述混淆。PDF Viewer 屬於已確認的產品方向，但目前尚未實作，細節列在 backlog。

---

## 部署與資產來源

### 部署

- Repo：`wenchiehlee-money/InvestorConference`
- GitHub Pages 由 [deploy-web.yml](/app/projects/InvestorConference/.github/workflows/deploy-web.yml) 建置與部署
- Vite base path：`/InvestorConference/`
- Build output：`web/dist`

### 資產來源

- 檔案索引：GitHub Git Trees API
  - `https://api.github.com/repos/wenchiehlee-money/InvestorConference/git/trees/main?recursive=1`
- 一般文字檔與 PDF：`raw.githubusercontent.com`
- 音訊檔：`media.githubusercontent.com`
  - 目前程式碼明確把音訊與其他靜態檔分流，因為音訊可能走 Git LFS

### 補充資料

- `audio_durations.json`：音訊秒數
- `raw_companyinfo.csv`：台股公司名稱與主要業務
- `raw_conceptstock_company_metadata.csv`：美股公司名稱與產品區段
- `upcoming_earnings.csv`：法說日期

CSV 若不存在或讀取失敗，目前 loader 會回傳空陣列，不阻斷整體頁面載入。

---

## 路徑與資料模型

### 內容類型判定

目前 parser 支援三類內容：
- 法說會：頂層資料夾為數字股號，例如 `2382/2382_2025_q3.mp3`
- GTC 大會：頂層資料夾 `GTC/`
- Podcast：頂層資料夾 `Podcast/`

### 檔名規則

法說會：
- 音訊：`{stockId}/{stockId}_{year}_q{quarter}.mp3|m4a|wav`
- 字幕：`{stockId}/{stockId}_{year}_q{quarter}.srt` 或 `{stockId}_{year}_q{quarter}_GT.srt`
- PDF：`{stockId}/{stockId}_{year}_q{quarter}_{label}.pdf`

GTC / Podcast：
- 音訊：`{folder}/{stem}.mp3|m4a|wav`
- 字幕：`{folder}/{stem}.srt` 或 `{stem}_GT.srt`
- PDF：`{folder}/{stem}_{label}.pdf`

### SRT badge 規則

- `GT`：檔名包含 `_GT.srt`
- `Gen`：一般 `.srt`

注意：舊 draft 曾提到 `_turboscribe.srt`。目前程式碼不是這樣判定，實作依據是 `_GT.srt`。

### AudioEntry 欄位

前端最終組裝出的 entry 包含：
- `id`
- `contentType`
- `companyName`
- `businessDesc`
- `quarterLabel`
- `irDate`
- `audioUrl?`
- `durationSec?`
- `srts[]`
- `pdfs[]`

法說日期是從 `upcoming_earnings.csv` 的 `事件名稱` 中解析 `{stock/ticker}_{year}_q{quarter}` 後對應 `開始日期`。

---

## File Manager

### 已實作功能

頁面載入後，會先抓全部資料，再 render File Manager。上方工具列目前包含：
- 快速搜尋框：搜尋股號或公司名
- 類型下拉選單：`全類型 / 法說會 / GTC 大會 / Podcast`
- View tabs：`列表 / 公司分組 / 法說日期 / 搜尋`

### 列表 View

目前主列表欄位是：
- AI 討論
- 股名
- 日期
- 時長
- 中文簡報
- 英文簡報

行為說明：
- 有音訊或字幕即可點進 player；只有同時缺少音訊與字幕時，列才會加上 `no-srt` 樣式並禁用 checkbox
- checkbox 目前只有 UI，尚未接任何批次動作
- 目前列表頁只特別顯示 `ir` 與 `ir_en` 兩種 label
- 目前 PDF link 仍是直接開啟檔案；產品方向將改為「點擊後進入站內 PDF Viewer」
- 日期欄優先顯示 `irDate`，若沒有才退回 `quarterLabel`

### 公司分組 View

- 以 `id` 分組
- 使用原生 `<details>` / `<summary>` 展開
- 群組標題顯示公司名加 business description
- 每個 session row 顯示季別、日期、字幕 badge、PDF link、時長

### 法說日期分組 View

- 以 `irDate` 分組
- 若沒有 `irDate`，退回 `quarterLabel`，再退回 `日期未知`
- 日期由新到舊排序

### 導覽

- **法說日期資料來源**：`raw_event_upcoming_earnings.csv`（sync 自 `wenchiehlee-investment/InvestorEvents`）
  - 對照邏輯：從路徑取 Stock ID，在 `raw_event_upcoming_earnings.csv` 找 `類別=法說會` 且 `事件名稱` 含該 ID 的列，取 `開始日期`。
- **導覽機制**：
  - 點擊可用 row 會 `history.pushState(..., '', '#player')`
  - 返回時依 `popstate` 重建 File Manager
  - `sessionStorage['fm-scroll']` 用來恢復列表滾動位置
- 目前沒有獨立 route parameter，也沒有直接 deep-link 到特定 entry 的能力。

### 列表欄位參考

| 欄位 | 說明 |
|------|------|
| 類型 | 法說會 / GTC 大會 / Podcast |
| Stock ID | 從路徑解析（e.g. `2382`）|
| 名稱 | 公司名稱或節目名稱（從公司資訊 CSV 對照）|
| Period | 從檔名解析（e.g. `2025 Q3`）|
| 法說日期 | 從 `raw_event_upcoming_earnings.csv` 對照（法說會類型才有）|
| Duration | 從 `audio_durations.json` 讀取（單一 request 取得全部）|
| GT SRT | `{stem}_turboscribe.srt` 存在 → 綠色 badge「GT」|
| Gen SRT | `{stem}.srt` 存在 → 藍色 badge「Gen」|
| PDF | 同目錄 `.pdf` 數量（e.g. 📄×2）|

### Filter Bar

目前頂部提供快速切換：
```
[ 全部 ]  [ 法說會 ]  [ GTC 大會 ]  [ Podcast ]
```
全文搜尋時：**掃描範圍**跨所有類型；**顯示範圍**依 Filter Bar 選取過濾。

### View 切換

目前提供四種 View：
- **列表**：無分組，純可排序表格。
- **公司分組**：同公司歷季聚在一起，可展開/收合。適合深入研究某公司。
- **法說日期分組**：依法說會舉辦日期分組，同日多家公司並列。適合追最新法說。
- **全文搜尋**：跨所有 SRT 關鍵字搜尋，progressive 顯示結果。

### 列互動規則

- **點擊列** → 進入 SRT Player 詳細頁
- **無 SRT 但有音訊** → 仍可進入 player，頁內顯示音訊控制與 PDF，字幕區顯示 `尚無字幕檔。`
- **無音訊且無 SRT** → 整行呈灰色且不可點擊
- **有 GT + Gen** → 預設開啟 Diff Mode（見 SRT Player 章節）

---

## 全文搜尋

### 目前行為

全文搜尋是獨立 view，不是頂部快速搜尋的延伸。

目前實作：
- 搜尋框輸入滿 2 字以上才會觸發
- debounce 約 300ms
- 只搜尋目前 filter 後可見 entries
- 逐一 fetch 每個 SRT 檔並即時更新結果
- 進度文字格式：`搜尋中 (completed/total)…`

### 搜尋匹配規則

目前不是語意搜尋，也不是 SRT cue-level 搜尋，而是：
- 把字幕檔當純文字讀入
- 用 `split('\n')` 拆行
- 找出包含查詢字串的文字行
- 最多顯示每個 SRT 前 5 行結果
- 以 `<mark>` 做簡單關鍵字 highlight

---

## Player Detail

### 已實作區塊

Player 頁面目前包含：
- 返回按鈕
- 標題列：公司名/代號、季度、法說日期
- business description
- PDF links
- Diff 模式切換 checkbox（僅在 GT + Gen 都存在時顯示）
- 字幕區
- 音訊控制列

### 音訊控制

若有音訊：
- `▶ 播放` / `⏸ 暫停`
- `■ 停止`：pause 並把 `currentTime` 設成 0
- 速度切換：`0.75x / 1x / 1.25x / 1.5x / 2x`
- 額外顯示目前播放時間

若無音訊：
- 顯示 `（無音訊檔）`

### PDF 區塊

產品方向：
- PDF 不應只是下載連結或單純開 raw 檔案
- 點擊 PDF 後，應進入站內 PDF Viewer
- PDF Viewer 與 Player Detail 應共享同一筆 entry context，避免使用者在 PDF 與字幕之間迷路

目前狀態：
- 目前程式碼仍是把 PDF 當外部連結處理

### 字幕載入與主軸

- GT 與 Gen 會並行 fetch
- 若 GT 存在，GT 是主軸
- 若 GT 不存在，改用 Gen
- 若兩者都不存在，顯示 `尚無字幕檔。`，但若 `audioUrl` 存在，音訊控制列與 PDF links 仍可正常使用

### 字幕顯示

目前不是固定 10 行視窗，也沒有 bar 固定第 5 行。實際行為是：
- 一次 render 全部 cue
- 每列格式為 `[mm:ss] + 文字`
- `timeupdate` 時找出當前 cue
- 對 active cue 加上 `cue-active`
- 以 `scrollIntoView({ behavior: 'smooth', block: 'nearest' })` 讓目前 cue 保持可見

### 點擊 cue

- 點擊任一 cue 會把 audio seek 到該 cue `startSec`
- 如果音訊原本暫停，會自動開始播放
- 目前沒有「點進搜尋結果直接定位某一 cue」的流程

---

## PDF Viewer

### 產品目標

PDF Viewer 是站內第三個主要視圖，用來取代目前「點 PDF 就直接開 raw 檔案」的行為。

核心原則：
- PDF 應在站內閱讀，不以下載為主要路徑
- 使用者從列表頁或 Player Detail 點擊 PDF，都應進入同一種 viewer 體驗
- Viewer 必須保留 entry context，例如公司名、季度、PDF label
- 使用者能明確返回上一層，而不必依賴瀏覽器下載頁或外部分頁

### 預期導覽

建議導覽規則：
- 從 File Manager 點擊 PDF pill：進入 PDF Viewer
- 從 Player Detail 點擊 PDF link：進入 PDF Viewer
- PDF Viewer 提供返回按鈕
- 返回後應回到前一個 app view，並保留原本 scroll / entry context

### 預期介面

PDF Viewer 建議包含：
- 返回按鈕
- entry title，例如公司名、股號、季度
- PDF 類型 label，例如 `ir`、`ir_en`、`qa`
- 主要閱讀區，使用 `iframe`、`object` 或 PDF.js 類似方案承載 PDF
- 基本操作列：上一頁、下一頁、頁碼、縮放、在新分頁開啟、下載

### 與現有 player 的關係

PDF Viewer 不應取代 Player Detail，而是和 Player Detail 並列：
- Player Detail 偏向音訊與字幕閱讀
- PDF Viewer 偏向簡報與附檔閱讀
- 後續可考慮在兩者之間保留快速切換入口

---

## Diff Mode

### 已實作行為

Diff Mode 只在 GT 與 Gen 同時存在時出現，而且預設為開啟。

目前行為：
- 以 GT cue 為主軸
- 以 cue `index` 對齊 Gen cue
- 文字 diff 是 whitespace token 為基礎的 LCS diff
- `gt` 差異片段用橘色底線樣式
- 如果後面緊接對應 `gen` 片段，會用 `title` 顯示 `Gen: ...`
- 單純新增的 Gen 片段會以 `[text]` 形式插入顯示

補充：
- 目前是原生 `title` tooltip，不是自訂 popover UI
- Diff 演算法目前是 LCS，不是 Myers

---

## 技術架構

| 項目 | 目前實作 |
|------|---------|
| 語言 | TypeScript |
| 建置 | Vite |
| 部署 | GitHub Pages，artifact 來自 `web/dist` |
| 路由 | `pushState` / `popstate` + hash `#player` |
| 音訊 | `HTMLAudioElement` + `timeupdate` |
| SRT 解析 | 自製 parser |
| Diff | 自製 word-level LCS diff |
| 資料來源 | Git Trees API + raw/media GitHub URLs |
| PDF 閱讀 | 目標為站內 viewer；目前尚未實作 |

---

## 尚未實作（Backlog）

- [ ] PDF Viewer
  功能：點擊 PDF 後進入站內 PDF Viewer，支援基本閱讀操作，而不是只開 raw 檔案
  目前狀態：目前列表頁與 Player Detail 都仍以外部 PDF link 處理
  建議優先級：高

- [ ] 全文搜尋升級
  功能：cue-level 搜尋結果、顯示 timestamp、顯示前後文、點擊後直接定位到對應 cue
  目前狀態：目前僅支援 line-level 關鍵字搜尋，顯示的是原始文字行，且不能直接把 player 定位到特定 cue
  建議優先級：高

- [ ] 多關鍵字搜尋
  功能：支援空白分隔、多關鍵字 AND 邏輯
  目前狀態：目前只支援單一查詢字串的 includes 比對
  建議優先級：中

- [ ] Player 閱讀模式
  功能：固定行數字幕窗、視覺中心線、active/past/future 更清楚的閱讀層次
  目前狀態：目前是 render 全部 cue，並用 `scrollIntoView` 讓 active cue 保持可見
  建議優先級：高

- [ ] 深連結導覽
  功能：以 route / query / hash 精準表示 entry 與 cue 或 PDF 位置，可直接分享與回訪
  目前狀態：目前只有 `#player` 與 `history.pushState`，沒有 entry-level、cue-level 或 PDF viewer deep link
  建議優先級：中

- [ ] 排序模型
  功能：欄位排序與排序 dropdown
  目前狀態：目前只有固定排序與固定分組方式，沒有互動式排序能力
  建議優先級：中

- [ ] 列表頁 checkbox 決策
  功能：定義 checkbox 的實際用途，或移除該 UI
  目前狀態：目前 checkbox 只有視覺存在，沒有任何行為
  建議優先級：中

- [ ] 列表頁 PDF 呈現擴充
  功能：除 `ir` / `ir_en` 外，也能通用顯示其他 label，例如 `qa`
  目前狀態：目前列表頁只特別顯示 `ir` 與 `ir_en`
  建議優先級：低

- [ ] Diff UI 強化
  功能：更清楚的差異 tooltip / popover 呈現
  目前狀態：目前僅使用原生 `title` tooltip
  建議優先級：低

- [ ] 資料同步自動化（Workflow）
  以下三個 sync workflow 尚未建立：
  - `.github/workflows/sync-companyinfo.yml`（`raw_companyinfo.csv`）
  - `.github/workflows/sync-conceptstocks.yml`（`raw_conceptstock_company_metadata.csv`）
  - `.github/workflows/sync-investorevents.yml`（`raw_event_upcoming_earnings.csv`）

---

## Refinement 提案

### 方向一：依優先級實作 backlog

建議優先順序：
- 第一優先：PDF Viewer、全文搜尋升級、Player 閱讀模式
- 第二優先：深連結導覽、排序模型、checkbox 決策
- 第三優先：PDF label 呈現擴充、Diff UI 強化

### 方向二：把 roadmap 拆成 4 個小里程碑

#### Milestone 1: PDF 閱讀流

目標：讓 PDF 不再鎖定下載，而是站內閱讀內容。

建議內容：
- 建立 PDF Viewer 視圖
- 從列表頁與 Player Detail 都導向同一 viewer
- 加入返回按鈕、標題、label、基本閱讀控制
- 補上新分頁開啟與下載作為次要操作

#### Milestone 2: 搜尋與導覽補齊

目標：讓全文搜尋真正可作研究入口。

建議內容：
- 搜尋結果改成 cue-level 而非 raw line-level
- 顯示 timestamp、badge、前後文片段
- 點擊結果時把 cue id 放進 route state 或 query/hash
- player 初始化時自動定位並高亮目標 cue

#### Milestone 3: Player 可讀性升級

目標：讓 detail view 更像「閱讀器」而不是單純字幕列表。

建議內容：
- 視窗化顯示當前 cue 附近固定數量的行
- 建立視覺中心線，而不是只用 `scrollIntoView(nearest)`
- active / past / future cue 狀態分層更明確
- 補上 keyboard controls

#### Milestone 4: File Manager 決策工具化

目標：讓列表頁從「可看」變成「可篩、可比較、可下一步處理」。

建議內容：
- 補真正的排序模型
- 決定 checkbox 的用途；若無用途就拿掉
- 列表頁 PDF 顯示從 `ir/ir_en` 擴充到通用 label 呈現
- 補 deep-link entry route，避免只靠 `#player`

### 方向三：定義驗收基準

之後每個 refinement 建議都附最小驗收條件，例如：
- 點擊 PDF 後，1 秒內進入 viewer 並顯示第一頁或 loading state
- 從 PDF Viewer 返回後，能回到原本列表或 player context
- 搜尋任一關鍵字後，3 秒內出現第一批結果
- 點擊搜尋結果後，自動播放並定位到對應 cue ±1 秒內
- 返回列表後，scroll 恢復誤差不超過一個 viewport
- GT / Gen diff 關閉後，字幕內容與主軸 SRT 完全一致

這會比敘述型 spec 更能約束實作。

