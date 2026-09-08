# HPQ HP Inc. FY2026 Q3 財報與法說會重點萃取

| 欄位 | 內容 |
| :--- | :--- |
| 股票代碼 | HPQ |
| 公司 | HP Inc. |
| 季度 | FY2026 Q3；期間截至 2026-07-31；公告日 2026-08-26 |
| 分析模式 | repo-only；official earnings-result digest |
| 市場模板 | US hardware / printing / services |
| 產業模板 | PC、印刷與耗材 |
| Correlation Mode | tw_readthrough |
| 市場預期來源 | Yahoo.Finance consensus history (repo-synced)，最近 cutoff 2026-06-14：revenue 約 US$14.34B、EPS 約 US$0.66；時間差使信心為中 |
| 資料來源 | `data/HPQ/HPQ_2026_q3_report_en.pdf`；`data/HPQ/HPQ_2026_q3_sources.json` |
| 字幕來源 | 無；官方 webcast/replay URL 已確認，但未下載本地音檔或 transcript |
| 資料品質 Issue | Major：官方結果 release 可用，但 call replay/transcript 尚未落檔；Q&A 與管理層回答品質無法驗證。 |
| 分析日期 | 2026-09-08 |

## 零、投資決策摘要

先釐清季度：2026-08-26 的 HPQ 事件是 **HP fiscal 2026 Q3**，不是 FY2026 Q1。官方 release 明確寫明 period ended July 31, 2026；README 與 CSV 的 Q1 標籤屬 upstream stale metadata，已修正。

Q3 FY26 營收 **US$15.7B**，年增 12.5%，高於 repo cutoff 共識約 US$14.34B；GAAP diluted EPS **US$0.71**、non-GAAP diluted EPS **US$0.83**，均高於公司先前 outlook 上緣（GAAP $0.47–$0.63；non-GAAP $0.61–$0.71）。公司同時上修 FY26 GAAP EPS 至 $2.52–$2.62、non-GAAP EPS 至 $3.19–$3.29，並上修 FCF 至 $3.0–$3.2B。

正面主要來自 Personal Systems 營收年增 18%、Commercial Personal Systems 年增 22%、AI PCs/工作站與較高 fulfillment。負面是 Personal Systems units 仍年減 16%，Printing 營收年減 2%、耗材年減 3%，且本季 EPS 含每股 $0.11 tariff refund，不能全數年化。

## 一、財務表現與 Surprise Matrix

| 項目 | Q3 FY26 | Q3 FY25 | YoY | 公司前次 outlook/Repo 共識 | 判讀 |
| :--- | ---: | ---: | ---: | ---: | :--- |
| 營收 | US$15.7B | US$13.9B | +12.5% | Repo 約 US$14.34B | 正面，約高於共識 9.5% |
| GAAP 營益率 | 5.7% | 5.1% | +0.6ppt | NA | 改善 |
| Non-GAAP 營益率 | 6.5% | 7.1% | -0.6ppt | NA | 調整後利潤率承壓 |
| GAAP 淨利 | US$0.66B | US$0.76B | -13% | NA | 受去年一次性稅務/訴訟利益比較基期影響 |
| GAAP diluted EPS | $0.71 | $0.80 | -11.3% | $0.47–$0.63 outlook | Beat 公司 outlook 上緣 |
| Non-GAAP diluted EPS | $0.83 | $0.75 | +10.7% | $0.61–$0.71 outlook | Beat 公司 outlook 上緣 |
| 營業現金流 | US$1.74B | US$1.66B | +4% | NA | 穩健 |
| Free cash flow | US$1.57B | US$1.47B | +7% | FY26 上修至 $3.0–$3.2B | 正面 |

官方 release 的 EPS 同時包含每股 $0.11 tariff refund；應拆分營運 EPS 與一次性/政策相關收益，避免把 $0.83 視為完全 recurring。

## 二、Segment 與營運 KPI

| Segment/KPI | Q3 FY26 | YoY | 判讀 |
| :--- | ---: | ---: | :--- |
| Personal Systems revenue | US$11.8B | +18% | Consumer +10%、Commercial +22% |
| Personal Systems operating margin | 4.6% | NA | 營收成長但 unit decline，需看 mix/ASP |
| Personal Systems total units | — | -16% | 成長來自價格、mix、commercial/AI PC，不是量增 |
| Printing revenue | US$3.9B | -2% | Consumer -2%、Commercial -1% |
| Printing operating margin | 18.1% | NA | 高於 PS，但收入仍收縮 |
| Supplies revenue | — | -3% | 耗材 recurring base 仍弱 |
| Printing total hardware units | — | -7% | 硬體量縮 |

管理層指出 premium products、WXP、Print、workstations、AI PCs 與 memory supply improvements 支持本季表現；這些是公司說法，未提供完整產品 ASP 或 AI PC unit bridge。

## 三、財測變化與模型影響

| 指引 | 本次 | 模型影響 |
| :--- | :--- | :--- |
| FY26 GAAP diluted EPS | $2.52–$2.62，含 $0.19 tariff refunds | 支持模型上修，但需剝離一次性收益 |
| FY26 non-GAAP diluted EPS | $3.19–$3.29，含 $0.19 tariff refunds | 支持 EPS estimate，上修幅度需與正常化 EPS 分開 |
| FY26 FCF | $3.0–$3.2B | 增加現金回饋/降債能力 |
| Q4 FY26 GAAP EPS | $0.74–$0.84，含 $0.08 tariff refunds | 提供下一季模型區間 |
| Q4 FY26 non-GAAP EPS | $0.69–$0.79，含 $0.08 tariff refunds | 需扣除 tariff refund 影響 |

## 四、獲利品質、現金流與資本配置

Q3 營業現金流 US$1.74B、FCF US$1.57B，扣除整合融資租賃淨投資 US$20M 與 PP&E/無形資產投資 US$187M。公司本季支付股利 US$274M，並回購約 1,220 萬股、使用現金 US$300M；期末 gross cash 約 US$4.2B。

EPS 品質有三個限制：GAAP 與 non-GAAP EPS 都含每股 $0.11 tariff refund；去年同期含一次性稅務與訴訟利益；Personal Systems unit decline 顯示營收成長部分依靠 mix、價格與 fulfillment，而非需求量全面擴張。

## 五、Q&A 壓力地圖與資料限制

**Q&A 增額資訊：** NA；官方 webcast/replay 尚未落檔，沒有可稽核的問答文字。


官方頁面提供 FY26 Q3 audio webcast/replay URL `https://www.hp.com/investor/2026Q3Webcast`，但本 repo 尚未下載 replay 或 transcript。因此法人問題總數、追問次數、memory supply 的量化追問與管理層回答品質均為 NA。這不代表沒有舉行 Q&A，只代表目前沒有可稽核的本地逐字資料。

## 六、前次財測、承諾與措辭追蹤

官方 release 可驗證本季 EPS 高於原 outlook，並上修 FY26 EPS 與 FCF guidance；沒有本地 call transcript，無法追蹤管理層 Q&A 措辭或承諾細節。

## 七、風險與追蹤項目

1. **PC unit risk**：Personal Systems revenue +18% 但 total units -16%，需追蹤 ASP/mix 是否能持續抵銷量縮。
2. **Printing secular decline**：Printing revenue -2%、supplies -3%、hardware units -7%，高毛利耗材 base 仍承壓。
3. **Tariff refund normalization**：FY26 guidance 含 $0.19 EPS tariff refunds，未來季度需剝離一次性影響。
4. **Memory/supply risk**：公司提到 memory supply 與 fulfillment 改善，但成本、供給與價格仍可能改變 gross margin。
5. **Cash return vs investment**：回購與股利持續，但需與 PC/AI innovation 投資及負債管理同步觀察。

## 八、KPI 衛生檢查

| KPI | 定義/口徑 | 本季 | 模型注意事項 |
| :--- | :--- | ---: | :--- |
| Personal Systems units | 公司揭露的出貨量變化 | -16% YoY | Revenue +18% 與 units -16% 必須拆 ASP/mix |
| Printing supplies | 耗材營收變化 | -3% YoY | recurring base 仍弱 |
| Non-GAAP EPS | 公司排除特定調整後 EPS | $0.83 | 仍含 $0.11 tariff refund，不能與 GAAP 混用 |
| Free cash flow | CFO 減 lease/PP&E/無形資產投資 | $1.57B | 公司定義的 non-GAAP 指標，需與 GAAP CFO 一起看 |

## 九、加權紅黃綠燈評分

| 項目 | 權重 | 分數 | 燈號 | 信心 | 原因 |
| :--- | ---: | ---: | :---: | :---: | :--- |
| 營收 | 20% | +2 | 綠 | 高 | +12.5%，高於 repo consensus |
| Personal Systems | 20% | +1 | 綠 | 高 | Revenue +18%，但 units -16% |
| Printing | 15% | -1 | 黃 | 高 | Revenue/units/supplies 均下降 |
| EPS/指引 | 15% | +1 | 綠 | 高 | EPS 高於原 outlook，FY26 guidance 上修 |
| 現金流/FCF | 15% | +1 | 綠 | 高 | CFO +4%、FCF +7% |
| EPS 品質 | 10% | 0 | 黃 | 高 | tariff refund 與基期一次性項目 |
| Q&A 可驗證性 | 5% | -1 | 黃 | 低 | replay/transcript 未落檔 |
| **加權總分** | **100%** | **+0.85** | **綠（有一次性項目風險）** | **中高** | 結果強但 unit/printing 結構需追蹤 |

## 十、事件-模型-估值鏈條與台股 read-through

| 事件 | 模型欄位 | 方向 | 時間範圍 | 可能估值影響 |
| :--- | :--- | :---: | :--- | :--- |
| Personal Systems revenue +18% | PC revenue、ASP、mix | 正面 | 短中期 | 支持 revenue，但 units decline 限制可持續性 |
| FY26 EPS/FCF guidance 上修 | EPS、FCF、shareholder return | 正面 | FY26 | 支持 estimate revision |
| Printing revenue -2%、supplies -3% | Printing revenue、margin | 負面 | 中長期 | 估值需反映 secular decline |
| Memory supply/fulfillment 改善 | COGS、gross margin、shipments | 正面 | 短期 | 若延續可減少供應限制 |

| Taiwan Stock | Company | Link Type | Relationship | Evidence | Impact Direction | Confidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| 2382 | 廣達 | End-market correlation | PC/商用系統需求循環共同暴露 | HP official Q3 PC results；未證明直接供應 | Positive if commercial PC demand persists | Low |
| 3231 | 緯創 | End-market correlation | PC/AI server and enterprise hardware cycle | 共同終端需求，非 HP direct-supplier claim | Positive | Low |

## 十一、證據台帳

| 結論 | 來源 | 位置 | 證據類型 | 信心 | 是否有矛盾 |
| :--- | :--- | :--- | :--- | :---: | :---: |
| 8/26 event is Q3 FY26, not Q1 | Official HP release | `data/HPQ/HPQ_2026_q3_report_en.pdf`, p.1 | 硬數據 | 高 | 與原 CSV/README stale label 矛盾，已修正 |
| Revenue $15.7B, GAAP EPS $0.71, non-GAAP EPS $0.83 | Official HP release | 同上，p.1–2 | 硬數據 | 高 | 無 |
| Personal Systems +18%, units -16%; Printing -2%, supplies -3% | Official HP release | 同上，p.2 | 硬數據 | 高 | 無 |
| FY26 EPS and FCF guidance raised | Official HP release | 同上，p.3 | 公司指引 | 高 | 無 |
| Webcast/replay URL | HP Investor Relations | `data/HPQ/HPQ_2026_q3_sources.json` | 官方材料狀態 | 高 | 無 |

## 十二、結論與待補材料

HPQ 8/26 是 FY2026 Q3，核心結果偏正面但不是純量增長故事：營收與 EPS 高於公司原 outlook，Personal Systems 強、Printing 弱，且 PC units 下滑表示 mix/ASP/fulfillment 是主要驅動。FY26 EPS 與 FCF guidance 上修支持模型上修，但 tariff refunds 與去年一次性基期利益需要正常化。

待補材料是官方 webcast replay/transcript 與正式 10-Q；取得後應補 Q&A 壓力地圖、memory supply 的量化細節、AI PC mix、Commercial PS backlog 與管理層可信度評估。
