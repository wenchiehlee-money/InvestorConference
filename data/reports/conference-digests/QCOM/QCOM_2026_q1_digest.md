# QCOM 2026 Q1 Conference Digest

| 欄位 | 內容 |
| :--- | :--- |
| 股票代碼 | QCOM |
| 季度 | 2026 Q1 / Qualcomm FY2026 Q2 call |
| 分析模式 | repo_only + limited external cross-check |
| 市場模板 | US |
| 產業模板 | fabless semiconductor / smartphone AP / auto / IoT / data center AI |
| Correlation Mode | tw_readthrough |
| 市場預期來源 | repo-only；未取得完整市場共識。外部新聞提及 FactSet consensus，但未落檔為正式 expectation source。 |
| 資料來源 | `QCOM_2026_q1_GT.srt`, `QCOM_2026_q1_FIN.srt`, previous `QCOM_2025_q4_ir.md`, external cross-check snippets from WSJ / MarketWatch / AndroidCentral / BusinessInsider |
| 字幕來源 | GT candidate: `Review-Level=conservative_from_FIN`, `Audio-Checked=none` |
| 資料品質 Issue | `lint_sources.py QCOM 2026 q1`: WARN，缺 QCOM 2026 Q1 company report/tables/performance review；本 digest 不應視為完整財務 digest。 |

External cross-check URLs（僅補充，不取代公司正式文件）:

| Source | URL | 用途 |
| :--- | :--- | :--- |
| WSJ | https://www.wsj.com/business/earnings/qualcomm-second-quarter-sales-rise-on-automotive-internet-of-things-growth-fef711dd | Q2 results, Q3 guidance, hyperscaler context |
| MarketWatch | https://www.marketwatch.com/story/why-qualcomms-stock-is-soaring-even-in-the-face-of-a-weak-outlook-560f4546 | FactSet consensus snippets and stock reaction context |
| AndroidCentral | https://www.androidcentral.com/phones/qualcomm/qualcomm-fy-q2-2026-earnings | Segment/guidance context |
| BusinessInsider | https://www.businessinsider.com/qualcomm-earnings-qcom-stock-chip-deal-hyperscaler-ai-datacenter-2026-4 | Hyperscaler Q&A context |

## 零、投資決策摘要

| 項目 | 結論 |
| :--- | :--- |
| 核心預期差 | repo-only 無正式共識；FIN 顯示 Q2 revenue $10.6B、non-GAAP EPS $2.65，EPS at high end of guidance；但 Q3 guide $9.2B-$10.0B / non-GAAP EPS $2.10-$2.30，近端 handset/memory 壓力偏負面（來源: GT 02:15, 17:02）。 |
| 財測變化 | Q3 guidance 反映 China Android / memory constraint；管理層同時釋出 data center custom silicon leading hyperscaler shipment expected in December quarter（來源: GT 17:02, 18:36）。 |
| Q&A 增額資訊 | Q&A 聚焦 data center hyperscaler、China handset bottoming、memory duration、QTL sensitivity、Apple revenue、automotive ADAS content；最重要新增資訊是 hyperscaler engagement 多次被追問但客戶未揭露（來源: GT 19:50-44:41）。 |
| 管理層可信度 | 中低到中：對數字與 guidance 直接，但對 hyperscaler 客戶身份與 data center revenue timing 保留；缺官方 release/tables 落檔，財務硬數字需補文件驗證。 |
| 可能上修項目 | Data center AI/custom silicon optionality、automotive revenue run-rate/content、IoT growth。 |
| 可能下修項目 | QCT handset revenue、China Android units、near-term QTL/handset assumptions、non-GAAP EPS for Q3。 |
| 股價反應條件 | 正面條件是 hyperscaler program 轉為可量化 revenue；負面條件是 memory constraints 延續到 2027 或 China handset rebound 未發生。 |
| 分析信心 | 低-中。Call transcript 可用，但缺公司正式 Q2 FY26 release/tables/performance review。 |

## 一、法說會一句話重點

1. 最大正面 surprise：Qualcomm 宣稱 data center custom silicon engagement 將在 December quarter 開始 initial shipments（來源: GT 18:36）。
2. 最大負面 surprise：Q3 revenue guide $9.2B-$10.0B，QCT handset revenue forecast about $4.9B，反映 memory dynamics（來源: GT 17:02, 17:26）。
3. 最重要 Q&A 增額資訊：法人多次追問 hyperscaler/data center，但管理層不揭露客戶，只稱 large/leading hyperscaler 與 multi-generation engagement（來源: GT 20:42, 29:17, 42:21）。
4. 最可能改變模型的變數：QCT China handset bottom timing、automotive ADAS ramp、data center revenue timing、QTL handset unit sensitivity。

## 二、財務表現與 Surprise Matrix

| 項目 | 本季實績 | QoQ | YoY | 前次公司財測 | 市場預期 | 結果判定 | 模型影響 |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- | :--- |
| Revenue | $10.6B | NA | NA | In guidance per management | NA | In-line/high confidence only after official docs | Q2 base okay；來源: GT 02:15, 14:03 |
| QCT revenue | $9.1B | NA | NA | In expectation | NA | NA | handset/auto/IoT mix; 來源: GT 02:26, 14:24 |
| QTL revenue | $1.4B | NA | NA | High end of guidance | NA | NA | licensing stable but handset unit risk; 來源: GT 02:35, 14:11 |
| EPS | non-GAAP $2.65 | NA | NA | high end of guidance | NA | positive vs own guide | Q2 EPS ok; Q3 guide lower; 來源: GT 02:15 |
| FCF | NA | NA | NA | NA | NA | NA | 缺 official tables |
| Inventory | NA | NA | NA | NA | NA | NA | 缺 official tables |

EPS 品質：FIN 指出 Q2 有 $5.7B non-cash GAAP tax benefit excluded from non-GAAP results（來源: GT 15:46-15:54）。因此 GAAP EPS/NI 不能直接外推；non-GAAP EPS 才能反映營運，但仍需 official reconciliation。

## 三、財測與未來展望

| 指標 | Guidance / Outlook | 判讀 |
| :--- | :--- | :--- |
| Q3 revenue | $9.2B-$10.0B | 近端轉弱；來源: GT 17:02 |
| Q3 non-GAAP EPS | $2.10-$2.30 | 低於 Q2 run-rate；來源: GT 17:02 |
| QCT revenue | $7.9B-$8.5B | Handset pressure; 來源: GT 17:18-17:33 |
| QCT handset revenue | 約 $4.9B | China OEM inventory/memory impact; 來源: GT 17:26-17:39 |
| QCT IoT | high single digit YoY growth | 相對穩健; 來源: GT 17:39-17:45 |
| QCT Automotive | 約 +50% YoY | strongest segment momentum; 來源: GT 17:45-17:57 |
| Data center | December quarter initial shipments to leading hyperscaler | 長期 optionality，但客戶/量未揭露; 來源: GT 18:36 |

## 四、成長動能與成熟度

| 成長動能 | 階段 | 時程 | 是否已貢獻營收 | 證據 | 主要不確定性 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Automotive Snapdragon Digital Chassis / ADAS | 營收放量 | FY26-FY27 | 是，Q2 annualized >$5B; Q3 +~50% YoY guide | GT 04:22, 17:45 | ADAS adoption/margin |
| IoT / edge AI | 營收放量 | FY26 | 是，Q2 IoT $1.7B, +9% YoY | GT 14:46 | demand breadth |
| Data center custom silicon | 客戶驗證到初期出貨 | December quarter | 尚未明確貢獻 | GT 18:36, Q&A | customer identity, revenue scale |
| China Android handset rebound | 庫存修正後復甦 | Q4 FY26 | 現階段承壓 | GT 16:37-17:00 | memory supply/pricing |

## 五、毛利率分析

| 影響因素 | 方向 | 估計影響 | 是否持續 | 證據 |
| :--- | :---: | ---: | :--- | :--- |
| Handset memory constraints | 負面 | 未量化 | 1-3季以上 | GT 16:08-17:39 |
| Automotive ADAS/module content | 正面 | 未量化 | 中長期 | GT 40:08-41:14 |
| Data center custom silicon | 正面但不確定 | 未量化 | 長期 | GT 18:36, 42:21 |
| QTL handset units | 負面 | 未量化 | 近端 | GT 30:11-31:04 |

## 六、CapEx、現金流與 KPI 衛生

KPI 衛生：本季多數 KPI 來自 transcript 而非 official tables，包含 QCT/QTL revenues、QCT EBT margin、non-GAAP EPS、Q3 guidance、automotive annualized revenue、data center initial shipment timing。缺 official release/tables 是 major data-quality issue。

CapEx/FCF：資料不足，標示 NA；不可從 FIN 推估。

## 六.1 美股對台股供應鏈/市場 Read-through

| Taiwan Stock | Company | Link Type | Relationship to US Company | Evidence | Impact Direction | Confidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2330 | 台積電 | Supply-chain exposure | Qualcomm fabless SoC/foundry ecosystem exposure | Qualcomm QCT/product cycle; no direct-quarter sourcing in repo | Mixed: handset weak, data center optionality positive | Medium |
| 2454 | 聯發科 | Competitive / sentiment | Smartphone AP competition and Android demand cycle | Qualcomm China Android handset pressure | Mixed/negative for handset cycle, relative-share unknown | Medium |
| 3034 | 聯詠 | End-market correlation | Smartphone/display driver end-market exposure | China Android handset inventory pressure | Negative near term | Low-Medium |
| 2379 | 瑞昱 | End-market correlation | Connectivity/PC/consumer semiconductor cycle | IoT/edge AI and handset commentary | Mixed | Low |
| 2317 | 鴻海 | Supply-chain exposure | Smartphone and electronics assembly cycle | China handset / AI device cycle | Mixed | Low-Medium |

不可把上述候選解讀為 Qualcomm 直接供應商。尤其 `Direct supply` 需要另有公司文件或可靠來源。

## 七、策略重點

策略重點是從 handset AP/licensing 擴大到 automotive、IoT、PC、data center AI。最具估值影響的是 data center hyperscaler engagement，但目前仍屬「客戶驗證/初期出貨」而非可量化 revenue driver。

## 八、風險

| 風險 | 來源 | 發生機率 | 財務衝擊 | 時間範圍 | 領先指標 | 是否已反映 |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| Memory supply/pricing hurting handset OEMs | 管理層 | 高 | 高 | 1-4季 | China QCT Android shipments | 已反映在 Q3 guide |
| Data center hype without near-term revenue | Q&A | 中 | 中 | 2-6季 | customer disclosure, shipment volume | 部分反映 |
| QTL unit sensitivity | Q&A | 中 | 中 | 1-3季 | global handset units | 部分反映 |
| Apple revenue decline | Q&A | 中 | 中 | FY27 | Apple modem transition/model assumptions | 部分反映 |

## 九、Q&A 壓力地圖

| 指標 | 結果 |
| :--- | ---: |
| 法人問題總數 | 約 10-12 |
| 追問次數 | 多 |
| 涉及財測問題數 | 高 |
| 涉及毛利率問題數 | 中 |
| 涉及需求/訂單問題數 | 高 |
| 明確回答比例 | 中 |
| 部分回答比例 | 中高 |
| 迴避/非回答比例 | 中，主要在 hyperscaler 客戶身份 |
| Q&A-only 新資訊數 | 至少 5 |

| 排名 | 主題 | 被問次數 | 是否追問 | 管理層回答品質 | 股價重要性 |
| ---: | :--- | ---: | :---: | :--- | :---: |
| 1 | Data center hyperscaler | 4 | 是 | 重新框架/部分回答 | 高 |
| 2 | China handset bottoming | 3 | 是 | 有效回答 | 高 |
| 3 | Memory duration | 2 | 是 | 部分回答 | 高 |
| 4 | QTL second-half sensitivity | 1 | 是 | 有效回答 | 中 |
| 5 | Automotive ADAS revenue/margin | 1 | 是 | 有效回答 | 中 |

尚未回答的重要問題：hyperscaler 名稱、data center shipment revenue magnitude、data center gross margin profile、memory constraint 是否延續到 FY27、China Android rebound 強度。

## 十、前次財測、承諾與措辭追蹤

| 類型 | 前次 | 本次 | 評估 |
| :--- | :--- | :--- | :--- |
| 正式財測達成 | 前季 repo 有 QCOM_2025_q4_ir.md，但本季 official release missing | Q2 revenue/EPS reported in FIN | 無法完整判斷 |
| 管理層承諾 | Memory constraints affected Q2 outlook | Q3 guidance still includes memory pressure | 承壓延續，偏負面 |
| 措辭變化 | 前季偏「near-term handsets impacted」 | 本季稱 China Android bottoming in fiscal Q3 | 從壓力轉為嘗試定位底部，需驗證 |

## 十一、加權紅黃綠燈評分

| 項目 | 權重 | 分數 | 燈號 | 信心 | 原因 |
| :--- | ---: | ---: | :---: | :---: | :--- |
| Revenue | 15% | 0 | 黃 | 低 | Q2 $10.6B，但缺 official tables |
| Guidance | 20% | -1 | 黃 | 中 | Q3 guide weak due to handset/memory |
| EPS quality | 10% | -1 | 黃 | 中 | GAAP tax benefit; non-GAAP needs reconciliation |
| Growth optionality | 15% | +1 | 綠 | 中 | data center/auto/IoT |
| Management credibility | 15% | 0 | 黃 | 中 | Direct on guide, evasive on hyperscaler identity |
| Risk | 15% | -1 | 黃 | 中 | memory/China handset/Apple/QTL |
| TW read-through | 10% | 0 | 黃 | 中 | mixed: handset negative, data center positive |
| 加權總分 | 100% | -0.25 | 黃 | 低-中 | 近端壓力與長期 optionality 並存 |

## 十二、股價影響分析：事件-模型-估值鏈條

| 事件 | 影響模型欄位 | 影響方向 | 時間範圍 | 可能估值影響 |
| :--- | :--- | :---: | :--- | :--- |
| Q3 revenue/EPS guide below Q2 run-rate | revenue, EPS | 下修 | 1季 | near-term estimate cut |
| China Android bottom in Q3, grow Q4 | QCT handset | 上修條件 | 1-2季 | recovery multiple support if verified |
| Leading hyperscaler initial shipment | data center revenue | 上修條件 | Dec quarter onward | multiple expansion if quantified |
| Automotive +~50% YoY Q3 guide | QCT auto | 上修 | 1-4季 | diversification premium |
| Memory pressure | handset revenue/margin | 下修 | 1-4季 | estimate risk |

## 十三、證據台帳

| 結論 | 原文引用 | 來源 | 位置 | 證據類型 | 信心 | 是否有矛盾 |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| Q2 revenue $10.6B, non-GAAP EPS $2.65 | delivered revenues / EPS high end | GT | 02:15, 14:03 | 管理層說法 | 中 | 缺 official table |
| Q3 revenue $9.2B-$10.0B, EPS $2.10-$2.30 | forecasting revenues / EPS | GT | 17:02 | 管理層財測 | 中 | 缺 official table |
| QCT handset $4.9B guide due to memory | handset revenues approx $4.9B | GT | 17:26-17:39 | 管理層財測 | 中 | 否 |
| Data center initial shipments in December quarter | initial shipments for custom silicon engagement | GT | 18:36 | Q&A/管理層說法 | 中 | 客戶未揭露 |
| GAAP tax benefit excluded from non-GAAP | $5.7B non-cash GAAP tax benefit | GT | 15:46-15:54 | 管理層說法 | 中 | 缺 official reconciliation |
