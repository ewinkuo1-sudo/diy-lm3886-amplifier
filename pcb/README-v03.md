# PCB B 方案 V0.3：去耦與載流修訂

**2026-09-18 選料更新：**已登記使用者預計下單清單；47µF／470µF 各保留兩款候選，尚未決定。全部未購，詳見 [目前候選與封裝影響](../docs/10-預計下單清單.md)。既有 PCB／3D 外框尚未依此換料。

2026-09-17。保留兩片 100 × 90 mm 單聲道板＋一片 160 × 120 mm 共用電源板。LM3886T 與變壓器仍在寄送中；本版依現有假設完成下一輪布局改善、銅箔損耗估算及原生檢查，**仍是工程草稿，不可直接送廠**。

![PCB V0.3](preview/system-layout-v03.png)

| 項目 | 單聲道板 ×2 | 電源板 ×1 |
|---|---|---|
| 可編輯 PCB | [mono-layout-v03.kicad_pcb](mono-layout-v03.kicad_pcb) | [psu-layout-v03.kicad_pcb](psu-layout-v03.kicad_pcb) |
| 專案規則 | [KiCad 專案](mono-layout-v03.kicad_pro) | [KiCad 專案](psu-layout-v03.kicad_pro) |
| 圖面 | [PNG](preview/mono-layout-v03.png)／[原生 SVG](preview/mono-v03-native.svg) | [PNG](preview/psu-layout-v03.png)／[原生 SVG](preview/psu-v03-native.svg) |
| 封裝假設 | [清單](mono-layout-v03-footprints.csv) | [清單](psu-layout-v03-footprints.csv) |
| 原生 DRC | [0 違規、0 未連通](mono-v03-drc.json) | [0 違規、0 未連通](psu-v03-drc.json) |

**2026-09-19 絲印組裝標記（僅封裝庫與生成器，板檔未重建）：**`DraftV03.pretty` 的 `CP_D12.5_P5`／`CP_D8_P3.5`／`CP_D35_P10` 加上「+」記號（pad 1 側）與負極粗條（pad 2 側）；`LM3886T_UNVERIFIED` 加上 pad 1 標記「1」、散熱片側粗線與「TAB = V- HEATSINK」字樣。極性依 `tools/pcb_layout_v03.py` 走線核對：七顆電解（C6／C7／C8／C201–C204）pad 1 皆接較正節點。幾何集中在 [tools/silk_marks_v03.py](../tools/silk_marks_v03.py)，`build_pcb_v03.py` 重建時會自動寫入。**兩份 `.kicad_pcb`、預覽圖與 DRC 雜湊未變**（本機無 KiCad），下次在 KiCad 環境執行「重建」段落的指令後才會出現在板面。C8 極性依 mute 拓樸推定（pin 8 經 R8 拉向 V−，故 GND 側為正），到料後請再核對。

**2026-09-18 新增：**[正反面／組裝／3D 圖](inspection-v03/README.md)、[零件與封裝核對表](inspection-v03/parts-audit.md)。本輪僅新增看圖資料及模型預覽板，原 PCB 保持不變。

詳細結果：[本輪審查與計算假設](review-v03.md)、[銅箔計算表](current-budget-v03.md)、[完整計算資料](current-budget-v03.json)、[驗證摘要](validation-v03.json)、[原生 DRC 檔案綁定](drc-provenance-v03.json)。

本輪改善：

- C3/C4 的地端就近回到 IC 地腳；幾何回地長度分別由 102.94／126.16 mm 降至 24.15／33.15 mm。
- 主輸出改走底層，保留頂層 7.14 mm 的 IC 輸出取樣線；正電源移除兩個主電流換層導通孔。
- 放大板主電流段加寬，電源板 AC／DC 主幹改為 4.0 mm。以 40W／8Ω、名義 1 oz／25°C 為計算情境，IC 至 L1 的銅箔電阻約由 20.93 降至 9.25 mΩ。
- 估算電流、電阻、峰值壓降及發熱功率；充電電流採明確標示的占空比敏感度模型，沒有把它當量測或保證上界。
- 修正重建會還原規則的問題。**V0.2 舊文字的 0.3 mm 說法已更正**；本版固定 0.3 mm 並核對 DRC 前後設定。

KiCad 10.0.6：54＋35 個焊盤網路與原理圖相符，兩板 0 違規、0 未連通；放大板 100 段走線／3 孔，電源板 59 段／0 孔。分路接地幾何檢查及 4 個計算／規則回歸測試通過，已檢視兩板 PNG 與原生 SVG。DRC 與中心線幾何不代表高頻穩定、載流溫升或實際製造條件已驗證。

## 重建

需要 KiCad 10 CLI、能匯入 `pcbnew` 的 Python、繪圖用 Pillow。生成器在 `tools/pcb_layout_v03.py` 定義位置與走線，舊 V0.1／V0.2 原始板檔完整保留。原理圖、數值與舊 PDF 未修改，沒有重跑 ERC。

```sh
kicad-cli sch export netlist --format kicadxml -o electrical/netlist.xml electrical/lm3886-v01.kicad_sch
kicad-cli sch export netlist --format kicadxml -o electrical/psu-netlist.xml electrical/internal-psu-v02.kicad_sch
python3 tools/build_pcb_v03.py
python3 tools/run_pcb_drc_v03.py --cli kicad-cli
python3 tools/verify_pcb_v03.py
python3 tools/analyze_pcb_v03.py
python3 tools/test_pcb_analysis_v03.py
python3 tools/render_pcb_v03.py
kicad-cli pcb export svg --layers F.Cu,B.Cu,F.SilkS,Edge.Cuts --mode-single --fit-page-to-board --exclude-drawing-sheet -o pcb/preview/mono-v03-native.svg pcb/mono-layout-v03.kicad_pcb
kicad-cli pcb export svg --layers F.Cu,B.Cu,F.SilkS,Edge.Cuts --mode-single --fit-page-to-board --exclude-drawing-sheet -o pcb/preview/psu-v03-native.svg pcb/psu-layout-v03.kicad_pcb
```

繪圖 Python 可以與 KiCad Python 分開；非 macOS／Windows 環境以 `LM3886_FONT` 指向中文字型。改過 PCB、規則或走線 JSON 後需重新執行原生 DRC，否則雜湊驗證會拒絕舊報告。腳距／封裝、銅厚、孔壁鍍層、接頭、散熱器、板外線束及整機保護仍待選型／到貨核對，沒有 Gerber。
