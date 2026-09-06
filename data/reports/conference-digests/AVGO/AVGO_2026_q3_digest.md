# AVGO 2026 Q3 Conference Digest

| 欄位 | 內容 |
| :--- | :--- |
| 股票代碼 | AVGO |
| 季度 | FY2026 Q3 |
| 分析模式 | repo_only |
| 市場模板 | US |
| 產業模板 | AI semiconductor / custom XPU / networking / infrastructure software |
| Correlation Mode | tw_readthrough |
| 市場預期來源 | Google Finance transcript insights；revenue consensus $29.36B、non-GAAP EPS consensus $3.24；Q4 revenue consensus $35.03B 僅作輔助 |
| 資料來源 | `AVGO_2026_q3_report_en.md`, `AVGO_2026_q3_google_finance_transcript.md`, `AVGO_2026_q3_GT.srt` |
| 字幕來源 | GT candidate: `Review-Level=conservative_from_FIN`, `Audio-Checked=none`；重大數字以 SEC 8-K Exhibit 99.1 report 為準 |
| 資料品質 Issue | `lint_sources.py AVGO 2026 q3`: ERROR 0 / WARN 0 / INFO 1；INFO 為 GT candidate，非完整人工音訊校正版 |
| 分析日期 | 2026-09-06 |

## 零、投資決策摘要

| 項目 | 結論 |
| :--- | :--- |
| 核心預期差 | Q3 revenue $29.591B 與 non-GAAP EPS $3.32 高於 Google transcript insights consensus $29.36B / $3.24；真正 surprise 是 AI semiconductor 2027/2028 長線 guide：FY2027 約 $115B、FY2028 約 $230B（來源: report Page 1; transcript 14:26-17:46）。 |
| 財測變化 | Q4 revenue guide $34.8B、AI semiconductor revenue $21.7B、non-GAAP operating income 約 66% of revenue；FY2026 AI revenue $58B，高於前次 $56B；FY2027/2028 AI revenue 分別約 $115B/$230B（來源: report Page 1-2; transcript 5:20-17:46）。 |
| Q&A 增額資訊 | 供應不是單一 HBM 問題，還包含 land/power/shell、leading-edge silicon、substrates、HBM、system memory；Singapore substrate capacity FY2027 開始部署，optical/EML/CW/VCSEL 產能也擴張（來源: transcript Q&A 27:14-29:32, 51:12-56:13）。 |
| 管理層可信度 | 偏正面但高波動。公司給出極大量化的 multi-year AI revenue outlook，並承認 demand exceeds secured supply；但 Q4 revenue 對 consensus 可能只是小幅不足，且 XPU 客戶集中與 financing/backstop exposure 是主要折價點。 |
| 可能上修項目 | AI semiconductor revenue、Semiconductor Solutions revenue、operating income、FY2027/FY2028 EPS trajectory、HBM/CoWoS/advanced packaging/optical supply chain read-through。 |
| 可能下修項目 | Gross margin rate、CapEx、customer concentration discount、XPV/residual value guarantee risk。 |
| 股價反應條件 | 正面條件是 FY2027 $115B / FY2028 $230B AI revenue 被市場採信並轉為 EPS；負面條件是 Q4 guide 未高於高期待、gross margin 壓縮、或供應/financing 風險放大。 |
| 分析信心 | 中高。AVGO 有 SEC 8-K report MD 與 transcript；GT 為 candidate。 |

## 一、法說會一句話重點

1. 最大正面 surprise：AI semiconductor revenue $16.7B、YoY +221%、QoQ +54%，FY2027/FY2028 AI revenue outlook 分別給到約 $115B/$230B（來源: report Page 1; transcript 14:26）。
2. 最大負面 surprise：AI XPU mix 增加使 Q4 consolidated gross margin guide 約 73%，低於去年 78%；市場可能聚焦 margin compression（來源: transcript 24:28）。
3. 最重要 Q&A 增額資訊：管理層表示 $115B/$230B 是基於 secured supply 與資料中心 readiness 的保守 outlook，demand 可更高，但受 land/power/shell、substrate、HBM 等限制（來源: transcript 27:14-28:16, 51:12-52:27）。
4. 最可能改變模型的變數：custom XPU revenue ramp、AI networking attach、gross margin dilution、CapEx/financing exposure。

## 二、財務表現與 Surprise Matrix

| 項目 | 本季實績 | QoQ | YoY | 前次公司財測 | 市場預期 | 結果判定 | 模型影響 |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- | :--- |
| Revenue | $29.591B | +33% | +86% | NA | $29.36B | Beat | FY2026/FY2027 revenue base 上修；來源: report Page 1/tables |
| Non-GAAP gross margin | 約 75% | -210 bps | NA | 74% guide | NA | Beat vs company guide | AI mix 稀釋但好於 guide；來源: transcript 18:16 |
| Non-GAAP operating income | $20.095B | +35% | +92% | NA | NA | 正面 | operating leverage 強；來源: report table |
| Non-GAAP EPS | $3.32 | NA | +96% | NA | $3.24 | Beat | EPS 上修；來源: report Page 1 |
| FCF | $13.665B | +33% | +95% | NA | NA | 正面 | FCF margin 46%；來源: report Page 1/tables |
| Inventory | $4.523B | +$2.253B vs FY start | NA | NA | NA | 需求/供應雙向 | 支持 semiconductor demand，也占用 working capital；來源: report balance sheet |

EPS 品質：GAAP EPS $2.68、non-GAAP EPS $3.32，差異主要來自 acquisition-related amortization、SBC、restructuring、debt extinguishment、tax adjustments。GAAP operating income $15.955B 與 FCF $13.665B 皆創高，表示 non-GAAP EPS 不是單靠調整項（來源: report tables）。

ROE/ROA：repo 內缺完整 FY2025 full-year net income，不足以按 SOP 計算 TTM net income；不以三季累計或單季年化替代。可觀察 Q3-end total assets $188.148B、stockholders' equity $99.690B，但 ROE/ROA 標示 NA（來源: report balance sheet）。

## 三、財測與未來展望

| 指標 | Guidance | 判讀 |
| :--- | :--- | :--- |
| Q4 FY2026 revenue | 約 $34.8B, +93% YoY | 高成長但略低於 transcript insights consensus $35.03B |
| Q4 AI semiconductor revenue | $21.7B, +236% YoY | AI revenue 再加速；來源: report Page 1 |
| Q4 non-GAAP operating income | 約 66% of revenue | GM 壓縮但 operating leverage 維持；來源: report Page 1-2 |
| FY2026 AI revenue | $58B, +186% | 高於前次 $56B；來源: transcript 5:20 |
| FY2027 AI revenue | 約 $115B | secured supply 可支撐 doubled AI revenue；來源: transcript 14:26 |
| FY2028 AI revenue | 約 $230B | line of sight 再 double；來源: transcript 14:26 |

## 四、成長動能與成熟度

| 成長動能 | 階段 | 時程 | 是否已貢獻營收 | 證據 | 主要不確定性 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Custom XPU / TPU | 營收放量 | FY2026-FY2028 | 是，AI semi $16.7B | transcript 2:06-14:26 | 客戶集中、供應 |
| AI networking / Tomahawk | 營收放量 | FY2026-FY2028 | 是 | AI networking +2.5x YoY | Ethernet adoption, capacity |
| Optical / EML / CW / VCSEL | 擴產 | FY2027-FY2028 | 是但未單獨揭露 | transcript 54:11-56:13 | CapEx return |
| Infrastructure software / VMware | 獲利貢獻 | FY2026 | 是，revenue $8.752B | report table | ARR growth sustainability |
| XPV Platform | 商業模式擴張 | FY2026-FY2028 | 間接 | transcript 21:46-23:00 | residual guarantees/off-balance-sheet risk |

## 五、毛利率分析

| 影響因素 | 方向 | 估計影響 | 是否持續 | 證據 |
| :--- | :---: | ---: | :--- | :--- |
| AI XPU mix / memory content | 負面 | Q4 GM guide 73% vs prior year 78% | 中期 | transcript 24:28 |
| Operating leverage | 正面 | non-GAAP OM 67.9%, +240 bps YoY | 中期 | transcript 18:16 |
| Infrastructure software mix | 正面 | software GM 94%, OM 84% | 中期 | transcript 19:25 |
| Substrate/HBM/optical constraints | 風險 | 未量化 | 中期 | transcript 51:12-56:13 |
| Higher AI revenue scale | 正面 | Q4 OM 約 66% | 中期 | report Page 1-2 |

## 六、CapEx 分析

Q3 CapEx $532M，FCF $13.665B，FCF margin 46%；Q4 CapEx guide $1.4B，原因是半導體產能投資。Q&A 補充 CapEx 用於 substrate、EML、CW、VCSEL、indium phosphide capacity，美國與新加坡工廠未來兩年會顯著擴張（來源: report Page 1/tables; transcript 25:37, 54:11-56:13）。CapEx/營收 Q3 約 1.8%，Q4 以 $34.8B revenue guide 計約 4.0%；CapEx/折舊因折舊口徑不完整，標示 NA。

## 六.1 美股對台股供應鏈/市場 Read-through

| Taiwan Stock | Company | Link Type | Relationship to AVGO | Evidence | Impact Direction | Confidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2330 | 台積電 | Supply-chain exposure | leading-edge wafers / custom AI ASIC ecosystem | Q&A cites leading-edge silicon supply | Positive demand, capacity bottleneck | Medium |
| 3711 | 日月光投控 | Supply-chain exposure | advanced packaging / test sentiment | advanced packaging, substrates cited | Positive | Low-Medium |
| 2449 | 京元電子 | Supply-chain exposure | AI ASIC testing sentiment | custom XPU volume ramp | Positive | Low-Medium |
| 2382 | 廣達 | End-market exposure | AI rack/server deployment ecosystem | customers deploy GW-scale AI infrastructure | Positive | Low-Medium |
| 3231 | 緯創 | End-market exposure | AI server/rack demand | same | Positive | Low-Medium |
| 6669 | 緯穎 | End-market exposure | hyperscale AI infrastructure | same | Positive | Medium |
| 2308 | 台達電 | Supply-chain exposure | power infrastructure for GW AI data centers | land/power/shell and system constraints | Positive | Medium |
| 3017 | 奇鋐 | Supply-chain exposure | AI thermal and liquid cooling demand | optical/networking/rack-scale AI | Positive | Low-Medium |
| 3324 | 雙鴻 | Supply-chain exposure | AI thermal demand | same | Positive | Low-Medium |

## 七、策略重點

Broadcom 把 AI 策略明確鎖定六個 frontier-model XPU customers，搭配 Ethernet switching、PCIe switching、optical DSP/EML/VCSEL/CW lasers、advanced packaging 與 XPV financing platform。這不是單純敘事：Q3 AI semiconductor revenue 已達 $16.7B，FY2027/2028 也給出 $115B/$230B 的量化軌跡（來源: transcript 3:13-17:46）。

## 八、風險

| 風險 | 來源 | 發生機率 | 財務衝擊 | 時間範圍 | 領先指標 | 是否已反映 |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| 客戶集中 | 管理層 | 高 | 高 | FY2026-FY2028 | six XPU customers, top customer mix | 部分反映 |
| Supply / deployment constraints | Q&A | 高 | 高 | FY2027-FY2028 | land/power/shell, wafers, substrates, HBM | 部分反映在 outlook |
| Gross margin dilution | 管理層 | 高 | 中 | Q4-FY2027 | GM guide, AI revenue mix | 已反映 |
| XPV financing / residual guarantees | Q&A | 中 | 中 | FY2027-FY2028 | 10-Q disclosure, tranche terms | 尚未充分反映 |
| CapEx execution | Q&A | 中 | 中 | FY2027 | Singapore substrate / optical capacity ramp | 部分反映 |

## 九、Q&A 壓力地圖

| 指標 | 結果 |
| :--- | ---: |
| 法人問題總數 | 約 8 |
| 追問次數 | 多數為一問一追問 |
| 涉及財測問題數 | 高 |
| 涉及毛利率問題數 | 中 |
| 涉及需求/訂單問題數 | 高 |
| 完整回答比例 | 中 |
| 有效回答比例 | 高 |
| 部分回答比例 | 中 |
| 重新框架比例 | 中 |
| 迴避/非回答比例 | 低 |
| Q&A-only 新資訊數 | 至少 6 |

| 排名 | 主題 | 被問次數 | 是否追問 | 管理層回答品質 | 股價重要性 |
| ---: | :--- | ---: | :---: | :--- | :---: |
| 1 | FY2027/FY2028 AI revenue outlook and supply | 3 | 是 | 有效回答 | 高 |
| 2 | XPU customer GW / content per GW | 2 | 是 | 有效回答 | 高 |
| 3 | Gross margin dilution | 1 | 是 | 完整回答 | 高 |
| 4 | Tomahawk / networking attach | 2 | 是 | 有效回答 | 高 |
| 5 | XPV/backstop exposure | 2 | 是 | 部分回答 | 中高 |
| 6 | CapEx / optical capacity | 1 | 是 | 有效回答 | 中 |

Q&A-only：$115B/$230B outlook 已考慮 secured supply 與 data center readiness；Singapore substrate capacity FY2027 開始；Tomahawk 6/Ultra deployment 已跨 XPU/GPU clusters；XPV future tranches 會逐案評估；content per GW 約 $20B-$30B（來源: transcript Q&A）。

## 十、前次財測、承諾與措辭追蹤

| 承諾事項 | 首次提出時間 | 原定時程 | 本季進度 | 是否達成 | 評估 |
| :--- | :--- | :--- | :--- | :---: | :--- |
| FY2026 AI revenue $56B | 前次 guide | FY2026 | 上修至 $58B | 是 | 可信度加分 |
| Q4 operating margin discipline | 前次長期模型 | Q4 FY2026 | guide 約 66% | 進行中 | operating leverage 抵銷 GM 壓力 |
| VMware integration/software margin | VMware 後 | FY2026 | software OM 約 84% | 進行中 | 正面 |

| 主題 | 前次法說 | 本次法說 | 變化判讀 |
| :--- | :--- | :--- | :--- |
| AI demand | strong | exponential / demand exceeds outlook | 轉強 |
| Supply | constrained | secured enough for $115B/$230B but demand higher | 更量化 |
| Margin | AI mix dilutive | stop focusing on GM, focus OM | 管理層重新框架至 operating margin |

## 十一、加權紅黃綠燈評分

| 項目 | 權重 | 分數 | 燈號 | 信心 | 原因 |
| :--- | ---: | ---: | :---: | :---: | :--- |
| Revenue | 15% | +2 | 綠 | 高 | $29.591B, +86% YoY |
| 毛利率/核心獲利率 | 15% | +1 | 綠 | 中 | GM 壓縮但 OM 強 |
| EPS | 15% | +2 | 綠 | 高 | non-GAAP EPS beat |
| 財測 | 20% | +2 | 綠 | 中高 | Q4/FY2027/FY2028 AI trajectory very strong |
| 現金流 | 10% | +2 | 綠 | 高 | FCF $13.665B, 46% revenue |
| 資產負債表 | 5% | +1 | 綠 | 中 | cash $24B, debt paydown |
| 管理層可信度 | 10% | +1 | 綠 | 中 | 量化但客戶集中與 financing 未完全揭露 |
| 風險 | 5% | -1 | 黃 | 中 | supply/customer/financing risk |
| 訂單或需求能見度 | 5% | +2 | 綠 | 中 | secured supply + demand exceeds outlook |
| 加權總分 | 100% | +1.60 | 綠 | 中高 | AI 長線上修很強，GM/客戶集中是主要折價 |

## 十二、股價影響分析：事件-模型-估值鏈條

| 事件 | 影響模型欄位 | 影響方向 | 時間範圍 | 可能估值影響 |
| :--- | :--- | :---: | :--- | :--- |
| Q3 revenue/EPS beat | FY2026 revenue/EPS | 上修 | 短期 | 支撐 estimate revision |
| FY2027/FY2028 AI revenue outlook | AI semi revenue, EPS | 大幅上修 | 中長期 | AI multiple 支撐 |
| Q4 GM guide 73% | gross margin | 下修 | 短期 | multiple cap if GM focus |
| Operating margin 66% guide | operating income | 維持/上修 | 短中期 | 抵銷 GM 壓縮 |
| Substrate/HBM/land-power-shell constraints | shipment timing, CapEx | 雙向 | FY2027-FY2028 | visibility vs execution risk |
| XPV/backstop | contingent liabilities | 下修風險 | 中期 | balance-sheet risk premium |

## 十三、證據台帳

| 結論 | 原文引用 | 來源 | 位置 | 證據類型 | 信心 | 是否有矛盾 |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| Revenue $29.6B, +86% | Q3 financial results | report_en | Page 1/table | 硬數據 | 高 | 否 |
| AI semiconductor revenue $16.7B, +221% | CEO quote | report_en | Page 1 | 硬數據 | 高 | 否 |
| Non-GAAP EPS $3.32 | financial highlights | report_en | Page 1/table | 硬數據 | 高 | 否 |
| FCF $13.7B, 46% revenue | cash flow highlight | report_en | Page 1/table | 硬數據 | 高 | 否 |
| Q4 revenue $34.8B and OM 66% | business outlook | report_en | Page 2 | 管理層財測 | 高 | 否 |
| FY2027/FY2028 AI revenue $115B/$230B | AI revenue outlook | Google transcript / GT | 14:26-17:46 | 管理層財測 | 中 | 否 |
| Supply constraints include land/power/shell, silicon, substrates, HBM | Q&A response | Google transcript / GT | 51:12-52:27 | Q&A 增額資訊 | 中 | 否 |
| Singapore substrate and optical capacity expansion | CapEx Q&A | Google transcript / GT | 54:11-56:13 | Q&A 增額資訊 | 中 | 否 |
