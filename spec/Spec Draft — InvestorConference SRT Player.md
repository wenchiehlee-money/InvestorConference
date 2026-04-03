# Spec Draft — InvestorConference SRT Player

> Status: Implementation-aligned draft
> Updated: 2026-04-03

---

## 概述

InvestorConference SRT Player 是一個純 client-side 靜態 web app，使用 TypeScript + Vite 建置，部署到 GitHub Pages。它的目標是把 repo 內既有的音訊、字幕與 PDF 整理成可瀏覽、可搜尋、可播放的介面。

目前產品已經有兩個主要視圖：
- File Manager：列表、公司分組、法說日期分組、全文搜尋
- Player Detail：播放音訊、檢視字幕、開啟 PDF、切換 Diff 模式

這份 spec 以目前程式碼為準，未實作項目另外列在「Refinement 提案」，不再和已上線行為混寫。

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

注意：舊 draft 提到 `_turboscribe.srt`。目前程式碼不是這樣判定，實作依據是 `_GT.srt`。

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
- 有字幕才可點進 player；無字幕列會加上 `no-srt` 樣式並禁用 checkbox
- checkbox 目前只有 UI，尚未接任何批次動作
- PDF 在列表頁只特別顯示 `ir` 與 `ir_en` 兩種 label
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

- 點擊可用 row 會 `history.pushState(..., '', '#player')`
- 返回時依 `popstate` 重建 File Manager
- `sessionStorage['fm-scroll']` 用來恢復列表滾動位置

目前沒有獨立 route parameter，也沒有直接 deep-link 到特定 entry 的能力。

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

### 與舊 draft 不一致處

以下功能目前尚未實作：
- 多關鍵字 AND 邏輯
- 前後文裁切約 20 字
- 顯示 cue timestamp 並點進後直接定位到該 cue
- 搜尋完成後依 view 再分組排序

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

### 字幕載入與主軸

- GT 與 Gen 會並行 fetch
- 若 GT 存在，GT 是主軸
- 若 GT 不存在，改用 Gen
- 若兩者都不存在，顯示 `尚無字幕檔。`

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

### 與舊 draft 不一致處

以下敘述不精確：
- 不是字詞 tooltip 展開 UI，而是原生 `title` tooltip
- 不是保證「點擊差異標記」才看得到替代文字，hover 即可看到 title
- Diff 演算法目前是 LCS；spec 不應再寫成 `LCS / Myers`

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

---

## 目前已知落差

以下是舊 draft 與現況的主要落差，應視為 backlog，不應描述成已完成：
- Filter Bar 不是 pill button，而是類型下拉選單
- 沒有排序 dropdown，也沒有欄位排序
- 沒有固定 10 行字幕窗與第 5 行 highlight bar
- 沒有搜尋結果 timestamp 定位
- 沒有多關鍵字 AND 搜尋
- 沒有 richer diff tooltip/popover UI
- 沒有真正的 list → detail 深連結模型
- 列表中的 checkbox 尚未有實際功能

---

## Refinement 提案

### 方向一：先把 spec 分層

建議把 spec 拆成兩層，避免之後再失真：
- `Current Behavior`: 只記錄程式碼已存在的功能
- `Planned Refinements`: 只記錄想做但未做的項目，附優先級與驗收條件

這份檔案現在已接近這種結構，後續應維持。

### 方向二：把 roadmap 拆成 3 個小里程碑

#### Milestone 1: 搜尋與導覽補齊

目標：讓全文搜尋真正可作研究入口。

建議內容：
- 搜尋結果改成 cue-level 而非 raw line-level
- 顯示 timestamp、badge、前後文片段
- 點擊結果時把 cue id 放進 route state 或 query/hash
- player 初始化時自動定位並高亮目標 cue

這是目前產品價值最高、也最直接補齊 spec 落差的一段。

#### Milestone 2: Player 可讀性升級

目標：讓 detail view 更像「閱讀器」而不是單純字幕列表。

建議內容：
- 視窗化顯示當前 cue 附近固定數量的行
- 建立視覺中心線，而不是只用 `scrollIntoView(nearest)`
- active / past / future cue 狀態分層更明確
- 補上 keyboard controls

如果真的要保留「第 5 行 bar」這個概念，應在這個階段做，而不是先寫進 spec 當已完成。

#### Milestone 3: File Manager 決策工具化

目標：讓列表頁從「可看」變成「可篩、可比較、可下一步處理」。

建議內容：
- 補真正的排序模型
- 決定 checkbox 的用途；若無用途就拿掉
- 列表頁 PDF 顯示從 `ir/ir_en` 擴充到通用 label 呈現
- 補 deep-link entry route，避免只靠 `#player`

### 方向三：定義驗收基準

之後每個 refinement 建議都附最小驗收條件，例如：
- 搜尋任一關鍵字後，3 秒內出現第一批結果
- 點擊搜尋結果後，自動播放並定位到對應 cue ±1 秒內
- 返回列表後，scroll 恢復誤差不超過一個 viewport
- GT / Gen diff 關閉後，字幕內容與主軸 SRT 完全一致

這會比現在的敘述型 spec 更能約束實作。
