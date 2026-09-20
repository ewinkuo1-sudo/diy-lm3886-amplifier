# 方案 C V0.3 電路導讀圖

更新：2026-09-17。六張 PNG 已取代 2026-09-13 舊圖，對齊目前兩份 V0.3 KiCad 原理圖與 PCB V0.3 的回流說明。原理圖、PCB、元件值與採購狀態未在本次更動；沒有新增硬體量測或重跑 ERC／DRC。舊圖可由 Git 歷史取回。

| 圖片 | 內容 |
|---|---|
| [完整電路總覽](lm3886_complete.png) | 單聲道訊號與回授、共用電源、靜音及保護邊界 |
| [輸入級與回授](lm3886_input_stage.png) | R1/C1/R6/R2、R4 回授與串聯 R3/C2 |
| [IC → 輸出級](lm3886_ic_to_output.png) | Zobel、L1∥R7、假負載及回授取樣點 |
| [電源級 → IC](lm3886_power_to_ic.png) | 雙橋四電容、極性、線束、去耦與靜音 |
| [放大板色塊導讀](lm3886_sch_annotated.png) | 現行雙聲道原理圖的向量底圖與功能分區 |
| [電源板色塊導讀](lm3886_psu_sch_annotated.png) | 現行次級原理圖的向量底圖與功能分區 |

![完整電路總覽](lm3886_complete.png)

## 與舊圖不同之處

- 供電改為兩組**獨立 22Vac** 各接全橋，BR1 負端與 BR2 正端在 DC 側形成 GND；AC 次級不另行互接。不是舊總覽圖的單橋／中心抽頭架構。
- C201–C204 各 10,000µF／63V，每軌兩顆並聯為 20,000µF；負軌電解正端接 GND。
- 元件編號依 KiCad：輸入串阻 R6=1kΩ、輸入洩放 R1=1MΩ、偏壓 R2=22kΩ。R4=20kΩ 從 IC 輸出取樣；R3=1kΩ 與 C2=47µF 無極性電容**串聯**到地。
- R5 與 C5 串聯構成 Zobel；L1 與 R7 並聯後串入輸出。兩者不是喇叭 DC 保護。
- C8 的正端接 GND，負端接 pin 8；pin 8 經 R8、RUN 跳線接 VEE。負軌 C6 正端也接 GND。
- 約 ±30V 與 30–40W／8Ω 是規劃／探索範圍；沒有固定軌電壓或連續功率保證。35.8V／軌只是高市電空載假設。
- 保留「僅變壓器與 IC 已訂待到貨」；整流橋、四顆主電容和其他料件仍待購。12Vac 控制、一次側及喇叭保護尚待設計。

## 來源與核對

電路以 [放大板](../../electrical/lm3886-v01.kicad_sch)、[次級電源](../../electrical/internal-psu-v02.kicad_sch) 及各自生成器為準。色塊底圖直接從 `electrical/preview/` 的現行向量 PDF 轉出，沒有重新猜畫原理圖。框線只標示功能區域；圖框中的原始日期與舊檔名保留。原 PDF 中「no PCB」為 9/16 快照註記，目前已有工程草稿 PCB，狀態見 [PCB V0.3](../../pcb/README-v03.md)。

接地回流說明來自 [PCB V0.3 審查](../../pcb/review-v03.md)。訊號、回授、局部去耦與負載的 GND 屬於同一電氣網路，實體回流需分路規劃；示意圖不替代實際 PCB 走線。供電估算與採購狀態見 [現行計畫](../archive/09-採購後修訂計畫.md)。

本次逐張檢查 PNG 可讀性、元件值、回授串聯關係、雙橋極性與線束腳位；以現行 netlist 的既有網路檢查規格交叉核對。這是文件同步，不代表新的電氣驗證或製造核准。

## 重建

可編輯原稿位於 [svg/](svg/)，SHA-256 來源清單在 [sources.json](sources.json)。需要 Python 3、PyMuPDF，以及 Node.js、sharp；中文字型預設 Microsoft JhengHei，其他平台需 Noto Sans CJK TC。

```sh
python -m pip install pymupdf
# sharp 可安裝於外部工具環境，並以 NODE_PATH 指向其 node_modules。
python tools/build_diagrams.py
node tools/render_diagrams.cjs
```

若改動電路，先依專案流程重建 KiCad 原理圖、netlist、PDF 與電氣檢查，再同步 `tools/build_diagrams.py` 的導讀內容，重建六張圖並逐張檢視。來源雜湊提供版本追溯，不會自動推導或驗證手繪導讀的電路正確性。
