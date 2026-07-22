# Yahoo.Finance consensus history 同步機制

本目錄保存 `Yahoo.Finance` 倉庫產生的分析師共識歷史資料，供 `skill-investorconference-digest` 在 repo-only 模式下判斷 revenue / EPS 的市場預期差。

## 檔案

| 檔案 | 用途 |
| :--- | :--- |
| `data/Yahoo.Finance/raw_yahoo_finance_consensus_history.csv` | Yahoo Finance 分析師 EPS / revenue 共識時間序列 |
| `definitions/raw_yahoo_finance_consensus_history_definition.md` | 上述 CSV 的欄位定義 |

## 使用邊界

此資料足以支援：

* 當季 revenue consensus vs actual
* 當季 EPS consensus vs actual
* 下一季 revenue / EPS consensus 作為 guidance context

此資料不足以支援：

* 毛利率、營益率或 CapEx 共識
* segment / platform revenue 共識
* 法說前股價隱含期待
* 個別法人模型假設

## 同步來源

上游目標路徑為 `Yahoo.Finance/data/reports/raw_yahoo_finance_consensus_history.csv`。`Yahoo.Finance` 倉庫應透過 repo-file-sync 將下列檔案同步到本 repo：

* `data/reports/raw_yahoo_finance_consensus_history.csv` -> `data/Yahoo.Finance/raw_yahoo_finance_consensus_history.csv`
* `definitions/raw_yahoo_finance_consensus_history_definition.md` -> `definitions/raw_yahoo_finance_consensus_history_definition.md`

若上游同步尚未執行，可用 `biztrends.TW/data/Yahoo.Finance/raw_yahoo_finance_consensus_history.csv` 的已同步副本做一次性 bootstrap，但後續 source of truth 應回到 `Yahoo.Finance`。
