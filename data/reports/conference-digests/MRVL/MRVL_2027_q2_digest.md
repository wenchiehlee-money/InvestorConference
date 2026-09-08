# MRVL Marvell Technology FY2027 Q2 法說會 Digest

| 欄位 | 內容 |
|---|---|
| 股票代碼 | MRVL |
| 公司 | Marvell Technology, Inc. |
| 季度 | FY2027 Q2（季末 2026-08-01，公告/法說會 2026-08-27） |
| 分析模式 | US earnings digest；官方 earnings release + financial/business results PDF + additional earnings PDF；repo-only |
| 資料來源 | `data/MRVL/MRVL_2027_q2_report_en.md`, `data/MRVL/MRVL_2027_q2_performance_review.md`, `data/MRVL/MRVL_2027_q2_financial_tables.md`, `data/MRVL/MRVL_2027_q2_sources.json` |
| 市場預期來源 | repo-only；未取得 FactSet/Yahoo sell-side consensus，核心預期差以公司前次 outlook、Q2 實績與本季 guidance delta 判讀 |
| 字幕來源 | NA；官方 webcast exists，但本地未取得 audio/FIN/GT，Q&A-only 分析受限 |
| 資料品質 Issue | README 原列為 FY2025 Q2，已依 Marvell 官方資料校正為 FY2027 Q2；缺本地 audio/transcript/GT，因此不做逐題 Q&A 壓力統計 |
| 分析日期 | 2026-09-06 |

## 零、投資決策摘要

核心預期差：Marvell FY2027 Q2 最大重點是 AI data center 需求把營收、data center revenue 與 non-GAAP operating margin 同時推上新高。Q2 revenue 27.39 億美元，YoY +37%、QoQ +13%；data center revenue 21.72 億美元，占比 79%，YoY +46%、QoQ +18%。Non-GAAP EPS 0.94 美元、YoY +40%、QoQ +18%，non-GAAP operating margin 36.6%，YoY +180 bps、QoQ +160 bps。來源：financial results Page 8/9/15/16。

財測明確上修：Q3 revenue guide 31.50 億美元 +/-5%，約 QoQ +15%、YoY >50%；FY2027 revenue outlook 上修至約 120 億美元、YoY 約 +45%，高於前次 115 億美元；FY2028 revenue outlook 上修至約 180 億美元、YoY 約 +50%，較前次高約 15 億美元。這是本季最重要的正面 surprise。來源：financial results Page 8/21。

投資判斷偏正面但需注意毛利率 mix 壓力。AI data center 的 custom silicon、connectivity、optical DSP、51.2T switching 與 XPU attach 都在加速，但 Q3 non-GAAP gross margin guide 57.5%~58.5%，低於 Q2 的 58.9%，顯示 custom/AI ramp 與供應鏈成本可能稀釋毛利率。若 FY2028 revenue 180 億美元路徑兌現，MRVL 會被市場更強烈地視為 AI infrastructure silicon platform；反之，最大風險是 custom ramp timing、hyperscaler 集中度與 gross margin 下滑。來源：financial results Page 18/21。

## 一、Surprise Matrix

| 項目 | 本季實績 | QoQ | YoY | 前次公司財測/承諾 | 判讀 |
|---|---:|---:|---:|---|---|
| Revenue | 27.39 億美元 | +13% | +37% | 高於上季 guide midpoint 3,900 萬美元 | 正面，創 Q2 record。來源：official release / financial results Page 8 |
| Data center revenue | 21.72 億美元 | +18% | +46% | 主要成長引擎 | 強正面，占比 79%。來源：financial results Page 8/18 |
| Communications & other | 5.68 億美元 | -3% | +10% | 非核心成長線 | 中性，Q3 預期低雙位數至中雙位數下滑。來源：financial results Page 19 |
| GAAP EPS | 0.33 美元 | +725% | +50% | NA | 正面，但含 purchase accounting/acquisition effects。來源：financial results Page 15 |
| Non-GAAP EPS | 0.94 美元 | +18% | +40% | NA | 正面，營運槓桿明確。來源：financial results Page 16 |
| Non-GAAP GM | 58.9% | 持平 | -50 bps | 略高於 guidance midpoint | 中性偏正，但 Q3 guide 下滑。來源：financial results Page 12/21 |
| Non-GAAP operating margin | 36.6% | +160 bps | +180 bps | NA | 正面，AI revenue 放大帶來槓桿。來源：financial results Page 13/16 |
| Operating cash flow | 6.06 億美元 | -5% | +31% | NA | 正面但受 supplier capacity prepayments 影響。來源：financial results Page 14 |

## 二、業務與成長動能

| 業務/主題 | 本季訊號 | 模型含意 |
|---|---|---|
| Data center | Revenue 21.72 億美元、YoY +46%、QoQ +18%；Q3 預期 QoQ >20%、YoY 約 +75%；來源：financial results Page 18 | AI infra 是主要成長與估值 driver，且 Q3 會再加速 |
| Optical / connectivity | 800G optical DSP demand 強，1.6T ramping rapidly；scale-out switching FY27 預期 more than double | 對高速網通、光通訊 DSP、switch silicon 與供應鏈為正向 |
| Custom silicon | 與 Tier 1 hyperscaler 擴大 commercial agreement，涵蓋 TPU ecosystem attach programs；FY2028 custom business 預期 YoY >2x | Custom ASIC/XPU attach 從敘事轉成明確 growth pillar |
| AI infrastructure platform | Marvell 覆蓋 site-to-site、rack-to-rack、XPU-to-XPU、chiplets/HBM/package 連接 | 投資重點不只是單一 ASIC，而是 data movement across AI infrastructure |
| Communications & other | Q3 預期 QoQ/YoY 低雙位數至中雙位數下滑，Q4 預期 sequential recovery；來源：financial results Page 19 | 非 AI 業務短期拖累，但公司預期 FY27 年增接近 10% target |

## 三、財測變化與模型影響

Marvell 本季最明確的模型上修是 revenue trajectory。FY2027 revenue outlook 從 115 億美元上修到約 120 億美元，FY2028 從約 165 億美元隱含水準上修到約 180 億美元。若套用 Q2 non-GAAP operating margin 36.6%，高營收基礎會讓 EPS 彈性放大；但 Q3 gross margin guide 57.5%~58.5% 表示 revenue mix 與 ramp cost 仍需保守。來源：financial results Page 8/16/21。

| 模型欄位 | 方向 | 理由 |
|---|---|---|
| FY2027 revenue | 上修 | 公司明確上修至約 120 億美元，YoY 約 +45%。來源：financial results Page 8 |
| FY2028 revenue | 上修 | 公司明確上修至約 180 億美元，YoY 約 +50%，較前次高約 15 億美元。來源：financial results Page 8 |
| Data center revenue | 上修 | FY2027 data center growth outlook 從約 +50% 上修至約 +60%。來源：financial results Page 8 |
| Custom silicon revenue | 上修 | FY2028 custom business 預期 YoY >2x。 |
| Gross margin | 小幅下修/保守 | Q3 non-GAAP GM guide 57.5%~58.5%，低於 Q2 58.9%。來源：financial results Page 21 |
| OpEx | 上修 | Q3 non-GAAP OpEx guide 約 6.55 億美元，高於 Q2 6.11 億美元。來源：financial results Page 21 |

## 四、台灣供應鏈讀-through

MRVL 的訊號對台灣 AI supply chain 偏正面，尤其是先進製程、先進封裝、ABF/高速板材、光通訊與高速互連相關供應鏈。不過本 digest 沒有取得 Q&A，因此無法確認特定代工/封裝/系統廠客戶或 allocation。

| 讀-through | 可能受惠環節 | 注意事項 |
|---|---|---|
| Custom silicon / XPU attach 擴張 | 先進製程、先進封裝、HBM 周邊封裝、測試 | 公司未揭露供應商與節點，不能直接指名單一供應商貢獻 |
| 800G/1.6T optical DSP 與 scale-out switching | 光通訊、交換器、SerDes、PCB/CCL | 需求明確，但毛利率可能受 ramp/mix 影響 |
| AI data center revenue 加速 | 伺服器、交換器、電源/散熱與高速互連供應鏈 | 讀-through 是方向性，不等於 MRVL 訂單直接流向台廠 |

## 五、風險

1. Q3 gross margin guide 57.5%~58.5%，較 Q2 non-GAAP 58.9% 低，custom/AI ramp 可能帶來 mix 或成本壓力。來源：financial results Page 21。
2. FY2028 revenue 180 億美元高度仰賴 AI data center 與 custom silicon ramp，若 hyperscaler 專案時程延後，估值敘事會受壓。來源：financial results Page 8。
3. Data center 占比已達 79%，業務集中度提高；若 AI capex 或 specific customer program 調整，波動會放大。來源：financial results Page 9。
4. Communications & other Q3 預期下滑，非 AI 業務仍不穩定。
5. 本次無本地 audio/transcript/GT，Q&A-only 資訊缺口大，管理層對毛利率、客戶集中、supply constraint 的口頭說法未能納入逐題分析。

## 六、證據台帳

| 證據 | 證據類型 | 信心 | 是否有矛盾 | 用法 |
|---|---|---|---|---|
| Q2 revenue 27.39 億美元、YoY +37%、QoQ +13% | 來源：官方 earnings release / financial results PDF | 高 | 無 | Surprise Matrix |
| Data center revenue 21.72 億美元、YoY +46%、QoQ +18%、占比 79% | 來源：官方 financial results PDF | 高 | 無 | 成長動能 |
| Non-GAAP EPS 0.94 美元、non-GAAP OP margin 36.6% | 來源：官方 financial results PDF | 高 | 無 | EPS 品質 |
| Q3 revenue guide 31.50 億美元 +/-5%、non-GAAP EPS 1.10 +/-0.05 | 來源：官方 release / financial results PDF | 高 | 無 | 財測 |
| FY2027 revenue outlook 約 120 億美元、FY2028 約 180 億美元 | 來源：官方 financial results PDF | 高 | 無 | 模型上修 |
| 官方 webcast URL 存在但未取得本地音檔 | 官方 financial results page / webcast HTML | 中高 | 無 | 資料品質註記 |


## 七、Q&A 壓力地圖與管理層可信度

| 法人追問熱點 | 追問次數 | 回答品質 | Q&A-only 增額資訊 | 風險含意 |
|---|---:|---|---|---|
| Custom silicon / TPU ecosystem attach | NA | NA | 無本地 audio/transcript/GT，僅能使用官方簡報揭露 | 客戶與專案集中度無法由 Q&A 驗證 |
| Gross margin mix pressure | NA | NA | Q3 non-GAAP GM guide 57.5%~58.5%，但缺口頭解釋；來源：financial results Page 21 | revenue 上修可能部分被 margin 稀釋抵銷 |
| 800G/1.6T optical 與 switching ramp | NA | NA | 官方簡報揭露需求強與 FY27 more than double | 供應鏈 read-through 需等後續 Q&A 或訂單佐證 |
| FY2028 revenue 180 億美元路徑 | NA | NA | 公司簡報量化上修，但沒有逐題問答可看假設細節；來源：financial results Page 8 | 若 ramp timing 延後，估值會快速修正 |

管理層可信度評為中高：本季正面在於公司用官方 PDF 清楚量化 FY2027/FY2028 revenue outlook、Q3 guide、data center revenue 與 custom business growth，揭露品質高；折扣在於本地未取得 Q&A，無法驗證法人追問下對客戶集中、供應鏈、毛利率與 project timing 的回答品質。

## 八、前次財測承諾措辭追蹤

README 先前把 MRVL 8/27 事件列為 FY2025 Q2，與官方 fiscal period 不一致；本次依官方 IR page 與 PDF 校正為 FY2027 Q2，quarter ended 2026-08-01。前次承諾基準以公司 prior outlook 為主：FY2027 revenue 前次約 115 億美元，本季上修至約 120 億美元；FY2028 outlook 較前次提高約 15 億美元至約 180 億美元。措辭上，管理層從一般 AI data center demand 進一步量化到 custom silicon franchise、TPU ecosystem attach、800G/1.6T optical DSP、51.2T switching 與 FY2028 custom business >2x。來源：financial results page / Page 8。

## 九、事件-模型-估值鏈條

| 事件 | 影響模型欄位 | 可能估值影響 | 需要追蹤的反證 |
|---|---|---|---|
| FY2027 revenue outlook 上修至約 120 億美元 | FY2027 revenue、EPS | 支撐近端 earnings revision | Q3 revenue 未達 31.50 億美元 midpoint |
| FY2028 revenue outlook 上修至約 180 億美元 | FY2028 revenue CAGR、terminal growth | 支撐 AI infrastructure silicon premium | custom/hyperscaler ramp 延後 |
| Data center revenue 占比 79% 且 Q3 預期再加速 | segment mix、gross profit dollars | 提高 AI exposure，可能推升估值倍數 | AI capex 或 optical/connectivity demand 降溫 |
| Q3 non-GAAP GM guide 57.5%~58.5% | gross margin、EPS | 對 revenue 上修形成部分抵銷 | GM 低於區間或 mix 持續惡化 |
| Communications & other Q3 下滑 | non-AI revenue | 降低整體業務分散度評價 | Q4 recovery 未出現 |

## 十、加權紅黃綠燈

| 權重 | 分數 | 燈號 | 判斷 |
|---:|---:|---|---|
| 財務實績 30% | 85 | 綠 | Q2 revenue、data center、non-GAAP EPS、OP margin 均強。來源：official PDF |
| 財測變化 25% | 88 | 綠 | FY2027/FY2028 revenue outlook 同步上修。來源：official PDF |
| 成長動能 20% | 86 | 綠 | Custom、connectivity、optical 與 switching ramp 明確。來源：official PDF |
| 毛利率/CapEx/FCF 風險 15% | 62 | 黃 | Q3 GM guide 下滑；OCF 受 supplier capacity prepayments 影響。來源：official PDF |
| Q&A 可驗證性 10% | 45 | 黃 | 缺 audio/transcript/GT，無逐題壓力地圖。來源：sources JSON |
| 加權總分 | 79 | 綠偏黃 | AI 上修明確，主要折扣是 margin 與資料缺口。 |

## 十一、KPI 衛生與 CapEx/FCF 風險

KPI 衛生：MRVL 本季使用 GAAP/non-GAAP revenue、gross margin、operating margin、EPS、operating cash flow，以及公司自定義 segment/end-market revenue。Non-GAAP 數字均來自官方 reconciliation PDF；segment revenue 依公司揭露，不能與 SEC line item 完全逐項調節，但可與總 revenue 方向一致。CapEx/FCF 風險：本 digest 未完整拆 10-Q capex 表，短期以 operating cash flow 6.06 億美元、supplier capacity prepayments、cash balance 39.33 億美元與 debt 49.63 億美元作為現金流/資本配置監控點。來源：financial results Page 14/17。

## 十二、結論

MRVL FY2027 Q2 是明確的 AI data center 上修事件：營收、data center、non-GAAP EPS 與 operating margin 都向上，且公司把 FY2027/FY2028 revenue outlook 同步上修。投資上最大的正面是 custom silicon 與 connectivity 進入更強的 FY2028 ramp；最大的折扣是毛利率 mix 壓力與缺 Q&A 的資訊缺口。README 的 fiscal label 應以官方 FY2027 Q2 為準。
