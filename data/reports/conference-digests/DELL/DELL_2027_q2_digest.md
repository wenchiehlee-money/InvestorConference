# DELL 2027 Q2 Conference Digest

| 欄位 | 內容 |
| :--- | :--- |
| 股票代碼 | DELL |
| 季度 | 2027 Q2 / Dell FY2027 Q2 |
| 分析模式 | repo_only |
| 市場模板 | US |
| 產業模板 | hardware / AI server / enterprise infrastructure |
| Correlation Mode | tw_readthrough |
| 市場預期來源 | repo-only，未取得市場共識 |
| 資料來源 | `DELL_2027_q2_report_en.md`, `DELL_2027_q2_financial_tables.md`, `DELL_2027_q2_performance_review.md`, `DELL_2027_q2_transcript.md`, `DELL_2027_q2_GT.srt`, `DELL_2026_q1_digest.md` |
| 字幕來源 | GT candidate: `Review-Level=conservative_from_FIN`, `Audio-Checked=none`; GT 由 Dell 官方 transcript 依 59.9 min 音檔長度切分，時間戳為近似值 |
| 資料品質 Issue | `lint_sources.py DELL 2027 q2`: ERROR 0 / WARN 0 / INFO 1；INFO 為 GT candidate，非完整人工音訊校正版 |
| 分析日期 | 2026-09-02 |

## 零、投資決策摘要

| 項目 | 結論 |
| :--- | :--- |
| 核心預期差 | repo-only 下無外部共識；相對公司前次口徑，最大正向差異是 FY27 revenue guide 由 $167B 上修至 $192B、AI-optimized servers guide 由約 $60B 上修至 $74B（來源: report Page 1-2；prior digest）。 |
| 財測變化 | Q3 FY27 revenue guide $49.0B、non-GAAP EPS $6.50；FY27 revenue $192.0B、non-GAAP EPS $25.50、AI server revenue $74.0B（來源: report Page 2; transcript Page 282-294）。 |
| Q&A 增額資訊 | 法人追問集中在傳統 server/storage 是否可持續、AI backlog 品質、margin 結構、供應限制與價格/通膨；管理層明確補充需求仍高於供給，限制包含 DRAM、NAND、CPU、disk drives、ABF substrate、T-glass、optical、CDU/power racks 等（來源: transcript Q&A Page 740-770）。 |
| 管理層可信度 | 偏正面。上季 raised guide 後本季繼續上修，且 orders/backlog/revenue 同步量化；但 GT 未完整聽校、10-Q 未進 repo，現金流與融資應收調整需保守解讀。 |
| 可能上修項目 | FY27 revenue、AI server revenue、ISG operating income、non-GAAP EPS、storage revenue、台系 AI server/電源/散熱供應鏈 sentiment。 |
| 可能下修項目 | Raw FCF conversion、inventory/working-capital days、AI supply-chain delivery timing；若零組件通膨無法轉嫁，gross margin 也可能被壓縮。 |
| 股價反應條件 | 正面條件是 $95B backlog 能轉 revenue 並維持 ISG margin；負面條件是供應限制延長、AI server mix 壓低 cash conversion，或 adjusted FCF 與 raw FCF 差距擴大。 |
| 分析信心 | 中。公司文件、官方 transcript、GT candidate 足以做研究 digest；但無外部共識與完整音訊聽校。 |

## 一、法說會一句話重點

1. Dell Q2 FY27 revenue 達 $47.0B、YoY +58%，non-GAAP EPS $7.04、YoY +203%，並把 FY27 revenue guide 上修 $25B 至 $192B（來源: report Page 1-2）。
2. AI server 是核心 surprise：Q2 orders $60.9B、revenue $16.4B、ending backlog $95B，過去 12 個月 AI orders 超過 $130B（來源: report Page 1; transcript Page 63-101）。
3. Margin 並未被 AI mix 明顯稀釋：non-GAAP gross margin rate 21.1%，高於去年同期 18.7%；ISG operating margin 15.0%，高於去年同期 8.8%（來源: report Page 3/6）。
4. 最大風險在 supply/working capital：公司明說需求超過供給；Q2 raw FCF $986M、YoY -47%，但 adjusted FCF $8.149B、YoY +224%，主要差異來自 financing receivables adjustment（來源: report Page 3/8; transcript Page 740-770）。

## 二、財務表現與 Surprise Matrix

| 項目 | 本季實績 | QoQ | YoY | 前次公司財測 | 市場預期 | 結果判定 | 模型影響 |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- | :--- |
| Revenue | $46.971B | +7% vs Q1 $43.842B | +58% | Q2 guide $44.0B-$45.0B | NA | 正向超越公司財測 | FY27 revenue base 上修；來源: report Page 1/3; prior digest |
| AI server revenue | $16.401B | +2% vs Q1 $16.1B | +100% | FY27 guide 約 $60B | NA | 正向 | FY27 AI server guide 上修至 $74B；來源: report Page 1/3 |
| AI orders/backlog | orders $60.9B / backlog $95B | backlog +85% vs Q1 $51.3B | NA | NA | NA | 強正向 | Revenue visibility 上升；來源: report Page 1; prior digest |
| ISG revenue | $31.782B | NA | +89% | NA | NA | 正向 | ISG operating income 上修；來源: report Page 3 |
| ISG operating margin | 15.0% | NA | +6.2ppt | NA | NA | 正向 | AI mix 下仍有 scale leverage；來源: report Page 3 |
| CSG revenue | $15.034B | NA | +20% | NA | NA | 正向 | Commercial PC refresh 支撐；來源: report Page 3 |
| Non-GAAP EPS | $7.04 | +45% vs Q1 $4.86 | +203% | Q2 midpoint $4.80 | NA | 強正向 | FY27 EPS guide 上修至 $25.50；來源: report Page 1-3; prior digest |
| Raw FCF | $986M | NA | -47% | NA | NA | 負向品質項 | Cash conversion 需折價；來源: report Page 3/8 |
| Adjusted FCF | $8.149B | +157% vs Q1 $3.165B | +224% | NA | NA | 正向但需調整 | 融資應收 add-back 拉高；來源: report Page 3/8 |

EPS 品質：EPS 成長主要來自 revenue scale、ISG margin、OpEx leverage 與 share count 下降；non-GAAP reconciliation 仍包含 stock-based compensation、amortization、tax 與投資公允價值調整，需用 GAAP operating income 與 raw FCF 交叉檢查（來源: report Page 3/11）。

## 三、財測與未來展望

| 指標 | 前次 / 參考 | 本次 Guidance | 變化 | 判讀 |
| :--- | :--- | :--- | :--- | :--- |
| Q3 FY27 revenue | NA | $49.0B ± $0.5B | NA | 第二季強度延續；來源: report Page 2 |
| Q3 FY27 non-GAAP EPS | NA | $6.50 ± $0.10 | NA | EPS 維持高檔；來源: report Page 2 |
| FY27 revenue | $167.0B midpoint | $192.0B ± $2.0B | +$25.0B | 最大正式上修；來源: report Page 2; prior digest |
| FY27 AI server revenue | 約 $60B | $74.0B | +$14.0B | AI server demand/backlog 轉換速度高於前次；來源: report Page 2 |
| FY27 GAAP EPS | $17.31 midpoint | $24.37 midpoint | +$7.06 | Operating leverage 與收入規模重估；來源: report Page 2 |
| FY27 non-GAAP EPS | $17.90 midpoint | $25.50 midpoint | +$7.60 | EPS base reset；來源: report Page 2 |

## 四、成長動能與成熟度

| 成長動能 | 階段 | 時程 | 是否已貢獻營收 | 證據 | 主要不確定性 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| AI-optimized servers | 大量放量 | FY27 | 是，Q2 revenue $16.4B | report Page 1/3; transcript Page 100-104 | supply allocation、customer concentration、margin |
| Traditional servers/networking | 週期更新放量 | FY27 | 是，revenue $10.531B、YoY +122% | report Page 3; transcript Page 217-219 | 是否為 pull-forward 或持續 refresh |
| Dell IP storage | 回復成長/市佔提升 | FY27 | 是，storage $4.850B、YoY +26% | report Page 3; transcript Page 66-68 | NAND 通膨、enterprise IT budget |
| Commercial CSG | 成熟但回升 | FY27 | 是，commercial $13.192B、YoY +22% | report Page 3 | PC refresh 是否延續 |
| AI services / deployment | 附加價值 | FY27-FY28 | 部分貢獻 | transcript Page 112-185 | 未獨立揭露 revenue/margin |

## 五、毛利率分析

| 影響因素 | 方向 | 估計影響 | 是否持續 | 證據 |
| :--- | :---: | ---: | :--- | :--- |
| Scale leverage | 正面 | ISG margin YoY +6.2ppt；Q&A 稱 Q2 scale 對 ISG margin 約 +400 bps | 中期 | report Page 3; transcript Page 874 |
| AI server mix | 風險但本季被 scale 抵銷 | 未單獨量化 | 中期 | report Page 3/6; transcript Page 881 |
| Storage/Dell IP mix | 正面 | FY27 guide 隱含 storage 增量約 $2.5B | 中期 | transcript Page 877 |
| Component inflation | 雙向 | 未量化 | 取決轉嫁能力 | transcript Page 819-833 |
| OpEx leverage | 正面 | non-GAAP OpEx 8.5% of revenue vs 去年 11.0% | 中期 | report Page 6 |

## 六、CapEx、現金流與 KPI 衛生

KPI 衛生：AI orders、AI server revenue、AI backlog、adjusted FCF、non-GAAP EPS 均為高重要 KPI。AI revenue/backlog 為公司揭露的營運 KPI，需追蹤口徑是否穩定；non-GAAP EPS、FCF、adjusted FCF 有 reconciliation，但 adjusted FCF 需要特別看 financing receivables add-back（來源: report Page 8/11）。

CapEx/FCF：Q2 operating cash flow $2.225B、raw FCF $986M、adjusted FCF $8.149B；差異主要來自 financing receivables adjustment $6.667B。這表示獲利表現很強，但不能只用 adjusted FCF 判斷現金轉換品質（來源: report Page 3/8）。

資產負債表：cash $11.569B、total assets $127.393B、total liabilities $128.820B、shareholders' deficit $1.427B（來源: report Page 7）。因股東權益為負，ROE 不具直觀意義；repo 內也缺完整 TTM net income/平均資產口徑，因此不做 ROE/ROA 年化估算。

## 六.1 美股對台股供應鏈/市場 Read-through

| Taiwan Stock | Company | Link Type | Relationship to Dell | Evidence | Impact Direction | Confidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2382 | 廣達 | End-market / ODM exposure | AI server、rack-scale infrastructure demand cycle read-through；非直接供應商宣稱 | Dell AI orders $60.9B、backlog $95B、FY27 AI server guide $74B | Positive if buildout converts to shipments | Medium |
| 3231 | 緯創 | End-market / ODM exposure | AI server demand cycle related | Same as above | Positive | Medium |
| 6669 | 緯穎 | End-market exposure | AI server/rack-scale demand sentiment | Same as above | Positive | Medium |
| 2356 | 英業達 | End-market / server exposure | Enterprise server refresh 與 AI server sentiment | Traditional server/networking +122%; AI guide raised | Positive | Low-Medium |
| 4938 | 和碩 | End-market / PC-server mix | CSG/commercial PC and server-related sentiment | Commercial CSG +22%; CSG +20% | Mild positive | Low |
| 2317 | 鴻海 | End-market exposure | AI infrastructure manufacturing sentiment | Dell AI server/backlog acceleration | Positive | Low-Medium |
| 2308 | 台達電 | Power exposure | AI server power/rack infrastructure demand read-through | Supply constraints include power racks/CDUs; AI backlog | Positive, but supply may cap timing | Medium |
| 3017 | 奇鋐 | Thermal exposure | Higher-density AI server thermal demand read-through | AI server revenue/backlog; power rack discussion | Positive | Low-Medium |
| 3324 | 雙鴻 | Thermal exposure | AI server thermal demand read-through | Same as above | Positive | Low-Medium |
| 3711 | 日月光投控 | Semiconductor cycle exposure | AI/leading-node component and enterprise hardware cycle sentiment | Supply constraints include leading-node components and substrates | Mixed positive demand, supply bottleneck risk | Low |

以上為市場 read-through，不等於 Dell 直接供應鏈認證；若要升級 confidence，需另查 Dell supplier/customer disclosure、台廠法說或可靠第三方供應鏈資料。

## 七、策略重點

Dell 的策略重點從「AI server story」進一步變成「AI infrastructure operating system」：AI server、PowerEdge、PowerScale/ObjectScale/Data Domain、deployment services、global supply chain 一起賣。Q2 的關鍵不是單一產品線成長，而是 AI server backlog 上升的同時，traditional servers/networking +122%、storage +26%、CSG +20%，顯示 demand 不只集中在一個客戶群或一個 SKU（來源: report Page 1/3; transcript Page 217-253）。

## 八、風險

| 風險 | 來源 | 發生機率 | 財務衝擊 | 時間範圍 | 領先指標 | 是否已反映 |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| 供應限制延長 | Q&A | 高 | 高 | FY27 | DRAM/NAND/CPU/disk/ABF/optical lead time、backlog conversion | 部分反映在 guide，但也限制 upside |
| AI backlog 客戶集中度 | 分析推論 | 中 | 高 | 2-5季 | top customer mix、repeat buyers、cancellation commentary | 未充分揭露 |
| Raw FCF 與 adjusted FCF 差距 | 財報 | 中 | 中 | 1-4季 | financing receivables、AR、inventory | 需折價看待 |
| Server demand pull-forward | Q&A | 中 | 中 | 2-6季 | replacement cycle、pipeline、enterprise budget | 管理層偏否認，但仍需追蹤 |
| Component inflation | Q&A | 中 | 中 | 1-4季 | pricing/margin、NAND/DRAM cost | 部分可轉嫁但未量化 |
| 負股東權益與資本配置 | 財報 | 中 | 中 | 中期 | buyback、leverage ratio、interest cost | 管理層稱 core leverage 0.8x；仍需追蹤 |

## 九、Q&A 壓力地圖

| 指標 | 結果 |
| :--- | ---: |
| 法人問題總數 | 約 9 |
| 追問次數 | 多數為一問一追問 |
| 涉及財測問題數 | 高 |
| 涉及毛利率問題數 | 中高 |
| 涉及需求/訂單問題數 | 高 |
| 明確回答比例 | 中高 |
| 部分回答比例 | 中 |
| 迴避/非回答比例 | 低 |
| Q&A-only 新資訊數 | 至少 5 |

| 排名 | 主題 | 被問次數 | 是否追問 | 管理層回答品質 | 股價重要性 |
| ---: | :--- | ---: | :---: | :--- | :---: |
| 1 | Traditional server/storage 是否為真實需求或 pull-forward | 2 | 是 | 有效回答，補充 14G/17G/18G replacement 與 enterprise demand | 高 |
| 2 | AI orders/backlog 可持續性 | 2 | 是 | 有效回答，補充 pipeline 仍為 backlog 的 multiples | 高 |
| 3 | Margin 結構與 ISG leverage | 2 | 是 | 有效回答，量化 scale 對 margin 的貢獻 | 高 |
| 4 | Supply constraints | 1 | 是 | 有效回答，列出 DRAM/NAND/CPU/disk/ABF/optical/power racks | 高 |
| 5 | Financing receivables / adjusted FCF | 1 | 是 | 部分回答，強調 net income to adjusted FCF over 1x | 中 |
| 6 | Storage attach / AI data growth | 1 | 是 | 有效回答，但缺獨立 revenue/margin guidance | 中 |

Q&A-only 增額資訊：18G consolidation ratio 12-14 old servers per new 18G；customer ordering further in advance to secure supply；AI customer count over 6,500 with 3,300 added over last three quarters；supply constraints broader than memory；ISG scale benefit roughly +400 bps in Q2 and over +650 bps in full-year guide（來源: transcript Q&A Page 362-371, 515, 642-644, 740-770, 874）。

## 十、前次財測、承諾與措辭追蹤

| 類型 | 前次 | 本次 | 評估 |
| :--- | :--- | :--- | :--- |
| Q2 revenue guide | $44.0B-$45.0B midpoint $44.5B | Actual $46.971B | 超過公司財測，可信度加分；來源: prior digest; report Page 3 |
| FY27 revenue guide | $167.0B midpoint | $192.0B midpoint | 上修 $25B；來源: report Page 2 |
| FY27 AI server guide | 約 $60B | $74.0B | 上修 $14B；來源: report Page 2 |
| AI backlog | $51.3B exiting Q1 | $95B exiting Q2 | 大幅提升，visibility 增加；來源: prior digest; report Page 1 |
| 措辭變化 | Q1: demand outpacing supply | Q2: demand continues to outpace supply, not enough supply | 需求措辭維持強勢，供應約束更具體；來源: transcript Page 327, 740-770 |

## 十一、加權紅黃綠燈評分

| 項目 | 權重 | 分數 | 燈號 | 信心 | 原因 |
| :--- | ---: | ---: | :---: | :---: | :--- |
| Revenue | 20% | +2 | 綠 | 高 | $46.971B、YoY +58%，高於前次公司 Q2 guide |
| Guidance | 20% | +2 | 綠 | 高 | FY27 revenue +$25B、AI server guide +$14B |
| Gross margin | 15% | +1 | 綠 | 中 | non-GAAP GM rate 21.1%，ISG margin 15.0%；但 AI mix/零組件仍是風險 |
| FCF/Balance sheet | 10% | 0 | 黃 | 中 | adjusted FCF 強，但 raw FCF YoY -47%、股東權益為負 |
| Management credibility | 15% | +1 | 綠 | 中 | 前次 Q2 guide 被超越，回答直接且量化 |
| Risk | 10% | -1 | 黃 | 中 | 供應限制非常廣，可能限制交付與現金轉換 |
| TW read-through | 10% | +1 | 綠 | 中 | AI server/電源/散熱供應鏈需求訊號強 |
| 加權總分 | 100% | +1.20 | 綠 | 中 | 正面 surprise 明顯，但現金流品質與 supply cap 需要折價 |

## 十二、股價影響分析：事件-模型-估值鏈條

| 事件 | 影響模型欄位 | 影響方向 | 時間範圍 | 可能估值影響 |
| :--- | :--- | :---: | :--- | :--- |
| FY27 revenue guide 上修至 $192B | Revenue, gross profit, EPS | 上修 | FY27 | EPS base reset，估值支撐 |
| FY27 AI server revenue guide 上修至 $74B | ISG revenue, backlog conversion | 上修 | FY27 | AI infrastructure exposure premium |
| AI backlog $95B | Revenue visibility | 上修 | 2-5季 | Visibility premium，但需看 cancellation/concentration |
| ISG operating margin 15.0% | Segment margin, EPS | 上修 | 1-4季 | 緩解 AI server low-margin 疑慮 |
| Raw FCF $986M vs adjusted FCF $8.149B | Cash conversion, balance sheet | 下修品質 | 1-4季 | 現金流折價，特別是融資應收增加時 |
| 供應限制擴大 | Revenue timing, inventory, margin | 雙向 | 1-4季 | 支撐需求強度，但壓抑交付與營運資金 |
| Storage +26% | Gross margin, attach | 上修 | 2-4季 | 改善 AI server mix 品質 |

## 十三、證據台帳

| 結論 | 原文引用 | 來源 | 位置 | 證據類型 | 信心 | 是否有矛盾 |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| Q2 revenue $47.0B、YoY +58% | record revenue / table | report_en | Page 1, Page 3 | 硬數據 | 高 | 否 |
| Non-GAAP EPS $7.04、YoY +203% | non-GAAP diluted EPS table | report_en | Page 1, Page 3 | 硬數據 | 高 | 否 |
| AI orders $60.9B、revenue $16.4B、backlog $95B | booked / recognized / backlog | report_en, transcript | Page 1, transcript Page 100-104 | 硬數據 + 管理層說法 | 高 | 否 |
| FY27 revenue guide $192B、AI server guide $74B | Full-Year Guidance table | report_en | Page 2 | 管理層財測 | 高 | 否 |
| ISG revenue $31.782B、margin 15.0% | segment table | report_en | Page 3 | 硬數據 | 高 | 否 |
| Q2 raw FCF $986M、adjusted FCF $8.149B | cash flow / reconciliation | report_en | Page 3, Page 8 | 硬數據 | 高 | 否 |
| Demand outpaces supply and constraints are broad | DRAM/NAND/CPU/disk/ABF/optical/CDU/power racks | transcript | Q&A Page 740-770 | Q&A 增額資訊 | 中 | 否 |
| 18G consolidation ratio 12-14 old servers per new 18G | server consolidation statement | transcript | Q&A Page 362-371 | Q&A 增額資訊 | 中 | 否 |
| Scale drove ISG margin improvement | just over 400 basis points / full-year over 650 bps | transcript | Q&A Page 874 | Q&A 增額資訊 | 中 | 否 |
| 台股 read-through 偏正面 | AI server guide/backlog acceleration | report_en/transcript | Page 1-2, Q&A | 分析推論 | 中 | 無直接供應商證據，已標示限制 |
