# GOOGL Alphabet Inc. 2026 Q2 法說會與財報重點萃取

| 欄位 | 內容 |
| :--- | :--- |
| 股票代碼 | GOOGL / GOOG |
| 公司 | Alphabet Inc. |
| 季度 | 2026 Q2；期間截至 2026-06-30；公告日 2026-07-22 |
| 分析模式 | repo-only；official SEC release + secondary call transcript |
| 市場模板 | US mega-cap technology / advertising / cloud |
| 產業模板 | Internet platform、cloud、AI infrastructure |
| Correlation Mode | tw_readthrough |
| 市場預期來源 | Yahoo.Finance consensus history (repo-synced)，最近 cutoff 2026-06-14：revenue US$116.678B、EPS US$2.870 |
| 資料來源 | `data/GOOGL/GOOGL_2026_q2_report_en.md`；`data/GOOGL/GOOGL_2026_q2_8k.md`；`data/GOOGL/GOOGL_2026_q2_google_finance_transcript.md`；`audio_metadata.json` |
| 字幕來源 | 無 GT/FIN；音檔 release metadata status=ok，但來源為 Google Finance/Quartr secondary replay |
| 資料品質 Issue | Major：官方 earnings call audio URL 已留存，但本 repo 沒有官方逐字稿；Q&A 內容來自 secondary transcript，重大財務數字以 SEC release 為準。 |
| 分析日期 | 2026-09-08 |

## 零、投資決策摘要

Alphabet 2026 Q2 是「營收明顯超過 repo 共識、Cloud/AI 動能加速，但 AI CapEx 與資本需求大幅升高」的季度。官方營收為 **US$119.796B**，高於 cutoff 前共識 US$116.678B，約 beat 2.7%；營業利益 US$40.770B、營益率 34%，均較去年同期改善。Google Cloud 營收 US$24.768B、年增 82%，Cloud 營益率升至 35.6%，是本季最大基本面催化劑。

EPS US$9.11 與淨利的跳升主要由 US$97.983B 其他收益支撐，官方指出主要是 equity securities 未實現收益，不能視為本業 run-rate。更值得放進模型的是 Search +17%、YouTube ads +13%、Cloud +82%、Cloud backlog US$514B，以及公司把全年 CapEx 指引由 US$180B–190B 上調至 **US$195B–205B**。

投資判斷偏正面但不是無條件 bullish：AI 需求與 backlog 支持 2027 年收入能見度；短期則需承受第三方 capacity bridging 對 Cloud margin 的壓力、折舊與 data-center operating costs 上升，以及 CapEx 對 Q2 free cash flow 造成 **US$5.9B 負值**。管理層 Q&A 的重要增額資訊是 TPU system revenue 今年仍只占既有協議小部分，多數收入預計在 2027 年認列。

## 一、法說會一句話重點

1. 最大正面 surprise：營收 beat repo 共識約 2.7%，且 Cloud 82% 成長、backlog US$514B 顯示 AI infrastructure demand 仍強。
2. 最大負面 surprise：CapEx 指引上修至 US$195B–205B，Q2 FCF 為負，短期折舊、能源與第三方 capacity 將壓抑利潤率。
3. Q&A 增額資訊：TPU system sales 的大部分收入預計在 2027 年認列；Q3 會使用第三方 capacity 作為內部產能建置前的橋接。
4. 最可能改變模型的變數：Cloud backlog 轉收入速度、TPU revenue ramp、外部 capacity 成本，以及 Search AI monetization 是否維持增長。

## 二、財務表現與 Surprise Matrix

| 項目 | 2026 Q2 實績 | 2025 Q2 | YoY | Repo 共識/前值 | 結果判定 | 模型影響 |
| :--- | ---: | ---: | ---: | ---: | :--- | :--- |
| 營收 | US$119.796B | US$96.428B | +24% | US$116.678B | Beat，約 +2.7% | 上修當期基礎 |
| 營業利益 | US$40.770B | US$31.271B | +30% | NA | 正面 | 營益槓桿改善 |
| 營益率 | 34% | 32% | +2ppt | NA | 正面 | 但第三方 capacity 可能造成短期壓力 |
| 歸屬普通股股東淨利 | US$112.107B | US$28.196B | +298% | NA | 不可直接年化 | Equity gain 主導 |
| 稀釋 EPS | US$9.11 | US$2.31 | +294% | US$2.870 | 表面大幅 beat | 非本業收益造成不可持續性 |
| 營業現金流 | US$39.1B | NA | NA | NA | 強 | 支撐 CapEx，但仍不足以抵銷投資支出 |
| Free cash flow | -US$5.9B | NA | NA | NA | 負面 | AI infrastructure 投資壓力 |
| CapEx | US$44.9B | NA | NA | FY26 US$195B–205B | 上修投資強度 | 長期供給與短期報酬率的交換 |

共識來源為 repo-synced Yahoo.Finance history 最近一筆 `forecast_asof_date <= 2026-07-22` 的 2026-06-14 row；該檔只支援 revenue/EPS 比較。官方 release/8-K 為 unaudited 一級來源，優先於 secondary transcript。

## 三、獲利、EPS 品質與現金流

Q2 營業利益年增 30%，但淨利跳升主要不是本業。Other income/expense 為 **US$97.983B**，去年同期為 US$2.662B，官方說明主要來自 equity securities portfolio 的未實現收益。因此 EPS US$9.11 的市場 headline 很強，卻不應直接套用到 forward P/E 或下一季 EPS run-rate。

營業現金流 US$39.1B，但 CapEx US$44.9B，使季度 FCF 為負 US$5.9B；TTM FCF 仍為 US$53.3B。公司期末現金與有價證券 US$242.5B，其中 marketable equity securities US$87.1B；長期債務 US$98.2B。資產負債表有能力支撐投資，但資本效率與折舊回收速度會成為估值核心。

## 四、Segment / platform 表現

| Segment | Q2 2026 revenue | YoY | Q2 operating income | Q2 operating margin | 判讀 |
| :--- | ---: | ---: | ---: | ---: | :--- |
| Google Services | US$94.540B | +15% | US$39.544B | 41.8% | Search、YouTube、訂閱共同支撐 |
| Google Search & other | US$63.271B | +17% | — | — | AI features 尚未破壞廣告成長 |
| YouTube ads | US$11.055B | +13% | — | — | Brand/direct response 均有貢獻 |
| Google Cloud | US$24.768B | +82% | US$8.814B | 35.6% | AI infrastructure/solutions 加速 |
| Other Bets | US$0.382B | +2% | -US$1.799B | NM | 仍是損失來源 |

Cloud backlog 增至 **US$514B**，公司表示超過 50% 預期在未來 24 個月認列；但 backlog 主要是 GCP 合約，TPU system sales 只占其中一部分，不能把 US$514B 全部當成近期營收。Cloud Q2 已開始認列 TPU system sales，公司預期既有協議今年只認列小部分，2027 年才是主要認列期。

## 五、AI 成長動能與管理層承諾

管理層表示 Gemini API 約每分鐘處理 220 億 tokens、Gemini app 月活約 9.5 億；約 90% Fortune 100 使用 Gemini Enterprise。這些是管理層 operational metrics，對產品滲透有方向性價值，但不是可直接換算營收的合約數字。Cloud backlog、客戶使用量、Google Marketplace 交易與 TPU delivery 才是更接近收入模型的驗證點。

| 動能 | 目前階段 | 對模型影響 | 主要風險 |
| :--- | :--- | :--- | :--- |
| Gemini Enterprise / AI solutions | 採用擴張、收入已反映於 Cloud | 支持 Cloud revenue / backlog | usage 未完全等於高毛利收入 |
| TPU system sales | 初始交付、Q2 開始認列 | 2027 revenue opportunity | 供應、交付、客戶 acceptance |
| AI Search / AI Mode | 大規模使用與廣告測試 | 支持 Search query/ads monetization | inference cost 與廣告格式變現 |
| Third-party capacity | Q3 橋接策略 | 保護 Cloud revenue growth | 短期 Cloud margin 壓力 |

## KPI 衛生檢查

| KPI | 定義/口徑 | 本季 | 可否直接與 GAAP 對比 | 模型注意事項 |
| :--- | :--- | ---: | :---: | :--- |
| Google Cloud backlog | 公司管理層揭露的 Cloud 合約 backlog | US$514B | 否，非當季收入 | 多數為 GCP 合約，超過 50% 預計 24 個月內認列；TPU system sales 只占一部分 |
| Free cash flow | 營業現金流減 CapEx | -US$5.9B | 否，non-GAAP | 公司定義與 GAAP CFO/CapEx 分開看，Q2 受 AI infrastructure 投資壓力 |
| Constant-currency revenue | 排除匯率與 hedge effect 的管理層補充口徑 | +23% YoY | 否，non-GAAP | 官方 GAAP revenue growth 為 +24%，不可混用 |
| Non-GAAP EPS | 排除 restructuring、amortization、tax 等調整 | US$9.11 headline 為 GAAP；non-GAAP 需依 release reconciliation | 否 | EPS 異常主要受 equity securities unrealized gain 影響，必須與 GAAP net income 一起看 |


## 六、財測與 CapEx guidance delta

| 項目 | 前次/已知 | 本次 | 變化 | 模型解讀 |
| :--- | ---: | ---: | :--- | :--- |
| FY26 CapEx | US$180B–190B | US$195B–205B | 上修 US$15B | 需求強但折舊/FCF壓力更大 |
| Q3 FX | Q2 有約 1ppt tailwind | Q3 slight headwind | 轉弱 | Search/YouTube revenue 有換匯逆風 |
| Q3 Cloud capacity | 內部 capacity constraints | 增加 third-party capacity | 新增成本 | 支持收入、短期壓 margin |
| 2027 TPU revenue | — | 多數協議收入預計 2027 認列 | 延後至中期 | 今年 revenue contribution 不宜高估 |

公司沒有提供完整季度 revenue/EPS guidance 區間；因此本報告不把 FY26 revenue 或 EPS 做假想 forecast。前次 CapEx 區間與本次上修由官方 call remarks/secondary transcript記錄，正式 earnings release 也揭露 FY26 CapEx 相關 outlook 內容。

## 七、Q&A 壓力地圖

Q&A 內容取自 Google Finance/Quartr secondary transcript；沒有官方逐字稿，因此問答引用僅作增額資訊，重大數字回到官方 release。可辨識的法人壓力集中在 CapEx/ROIC、TPU 外售與收入認列、Cloud capacity/margin、Search/YouTube monetization。

| 主題 | 問題/追問 | 管理層回答品質 | 模型重要性 |
| :--- | :--- | :--- | :---: |
| CapEx / ROIC | 供給受限下如何決定 2027 投資規模與回報 | 部分回答：重申需求超過供給與長期回報框架，未給 ROIC 數字 | 高 |
| TPU revenue recognition | TPU 協議何時反映收入、margin 如何 | 有效但有限：今年小部分、主要 2027；未拆 revenue/margin | 高 |
| Cloud capacity | 第三方 capacity 是否代表廣泛短缺、成本如何 | 部分回答：承認短期成本高、長期合約回報 attractive | 高 |
| Search/YouTube monetization | AI Search 是否增加 query 與廣告變現 | 有效但多為定性與產品案例 | 中高 |
| YouTube growth | CTV、Demand Gen、Shorts、shopping formats | 有效但未提供完整量化 revenue bridge | 中 |

未取得官方 transcript 的資料品質限制使回答品質判定為中低信心；不可把 secondary transcript 的管理層表述視為 SEC filing 硬數據。

## 八、前次財測、承諾與措辭追蹤

| 承諾/展望 | 本季狀態 | 判斷 |
| :--- | :--- | :--- |
| AI investment 支撐 Cloud/AI demand | Cloud +82%、backlog US$514B | 財務結果支持，信心高 |
| TPU system sales 開始形成收入 | Q2 開始小量認列 | 已開始，但主要收入延至 2027 |
| 擴大 capacity 以支援需求 | Q3 使用第三方 capacity 作橋接 | 執行中；成本影響待觀察 |
| CapEx 支持長期 AI growth | FY26 CapEx 上修至 US$195B–205B | 投資承諾更強，FCF 代價也更高 |

## 九、風險與追蹤項目

1. **CapEx/FCF 風險**：FY26 CapEx 上修且 Q2 FCF 已為負，需追蹤 Cloud revenue 增長是否能覆蓋折舊、能源與第三方 capacity。
2. **Cloud margin 風險**：管理層明確表示 Q3 third-party capacity 將造成 modest margin pressure。
3. **TPU 認列風險**：backlog 不等於當期收入，主要 TPU revenue 延至 2027，需追蹤交付與 customer acceptance。
4. **業外 EPS 風險**：equity securities unrealized gain 使 Q2 EPS 異常高，不能用 headline EPS 判斷本業。
5. **廣告變現風險**：AI Search query growth 正面，但新的 AI response inference cost、廣告格式與 click economics仍待驗證。

## 十、加權紅黃綠燈評分

| 項目 | 權重 | 分數 | 燈號 | 信心 | 原因 |
| :--- | ---: | ---: | :---: | :---: | :--- |
| 營收/廣告 | 20% | +2 | 綠 | 高 | Revenue beat、Search +17%、YouTube +13% |
| Cloud/AI demand | 20% | +2 | 綠 | 高 | Cloud +82%、backlog US$514B |
| 獲利率 | 15% | +1 | 綠 | 高 | Operating margin 34%，但成本持續上升 |
| EPS 品質 | 10% | 0 | 黃 | 高 | Equity gain 使 headline EPS 不可持續 |
| 現金流/CapEx | 15% | -1 | 黃 | 高 | Q2 FCF -US$5.9B、CapEx guidance 上修 |
| 資產負債表 | 10% | +1 | 綠 | 高 | US$242.5B cash/securities，長債 US$98.2B |
| 管理層可信度 | 5% | +1 | 黃 | 中低 | guidance 明確，但 Q&A 為 secondary transcript |
| 供給/執行風險 | 5% | 0 | 黃 | 中 | supply constraint 與 third-party bridging 並存 |
| **加權總分** | **100%** | **+1.15** | **綠（附 CapEx 風險）** | **中高** | 基本面強，資本強度與可持續性需折價 |

## 十一、事件-模型-估值鏈條與台股 read-through

| 事件 | 模型欄位 | 方向 | 時間範圍 | 可能估值影響 |
| :--- | :--- | :---: | :--- | :--- |
| Cloud revenue +82%、backlog US$514B | Cloud revenue、2027 revenue | 正面 | 中期 | 提升 AI/cloud growth multiple 支撐 |
| FY26 CapEx 上修 | FCF、折舊、margin | 短期負面/中期正面 | 短中期 | 高成長需配合高資本回報才能維持 multiple |
| TPU revenue 主要延至 2027 | revenue timing、backlog conversion | 中性 | 中期 | 避免把今年收入估得過高 |
| Search +17%、YouTube +13% | ads revenue、ROAS | 正面 | 短中期 | 支持廣告平台估值 |

| Taiwan Stock | Company | Link Type | Relationship | Evidence | Impact Direction | Confidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| 2330 | 台積電 | End-market / supply-chain exposure | AI accelerator、Google TPU 與先進製程需求的共同暴露 | 本報告僅支持 Google TPU/AI infrastructure demand；未證明直接供應關係 | Positive if AI compute demand persists | Medium |
| 2382 | 廣達 | End-market / supply-chain exposure | Cloud/AI server infrastructure demand | 共同暴露於 AI server cycle；未證明直接供應關係 | Positive if hyperscaler CapEx converts to shipments | Low |
| 3231 | 緯創 | End-market / supply-chain exposure | Cloud/AI server infrastructure demand | 同上；非 Alphabet direct-supplier claim | Positive | Low |

## 十二、證據台帳

| 結論 | 來源 | 位置 | 證據類型 | 信心 | 是否有矛盾 |
| :--- | :--- | :--- | :--- | :---: | :---: |
| Revenue US$119.796B、operating income US$40.770B、EPS US$9.11 | SEC earnings release | `data/GOOGL/GOOGL_2026_q2_report_en.md`，Q2 highlights/table | 硬數據 | 高 | 無 |
| Search US$63.271B、YouTube ads US$11.055B、Cloud US$24.768B | SEC earnings release | 同上，Q2 supplemental information | 硬數據 | 高 | 無 |
| Cloud backlog US$514B、>50% within 24 months | official remarks as captured in secondary transcript | `data/GOOGL/GOOGL_2026_q2_google_finance_transcript.md`，約 20–23 分鐘段落 | 管理層說法/secondary | 中 |
| CapEx US$44.9B、Q2 FCF -US$5.9B、FY26 CapEx US$195B–205B | official earnings release and call remarks | release；transcript 約 21–24 分鐘段落 | 硬數據/管理層說法 | 高 | 無 |
| TPU revenue mostly in 2027、third-party capacity pressures margin | secondary transcript cross-check | transcript 約 24–28 分鐘段落 | Q&A 增額資訊 | 中低 | 官方 release 未完整呈現 |
| Revenue consensus US$116.678B、EPS consensus US$2.870 | repo-synced Yahoo consensus | `data/Yahoo.Finance/raw_yahoo_finance_consensus_history.csv`，2026-06-14 | 二級共識 | 中 | cutoff 距公告約 38 天 |

## 十三、結論與待補材料

Alphabet Q2 基本面強，尤其 Cloud/AI demand 已反映在收入、營業利益、backlog 與 Search/YouTube monetization；但估值與模型不應使用 Q2 US$9.11 EPS 作為正常化盈利。下一步應以 Cloud backlog conversion、TPU 2027 revenue、FY26 CapEx US$195B–205B 對 FCF/折舊的影響，以及 third-party capacity 對 Cloud margin 的壓力追蹤。

待補材料：

1. 以官方 audio replay 或官方 transcript 取代 secondary Google Finance/Quartr transcript，並補 GT/音訊核對。
2. 取得 Alphabet 2026 Q2 10-Q，核對 equity issuance、preferred stock、debt 與 segment disclosure。
3. 取得正式 investor presentation，補 AI infrastructure / Cloud backlog 的圖表與 customer concentration。
4. 更新截止 2026-07-22 的 consensus snapshot；目前 repo consensus cutoff 為 2026-06-14，信心受時間差限制。
