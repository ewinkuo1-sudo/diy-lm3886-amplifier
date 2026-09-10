# V0.1 電路圖

![原理圖預覽](preview/lm3886-v01.png)

[下載 PDF](preview/lm3886-v01.pdf)。以 KiCad 10 開啟 [lm3886-v01.kicad_pro](lm3886-v01.kicad_pro)，即可編輯原理圖；自有符號庫已隨附。未指派 footprint，尚無 PCB。

左右各一套相同電路，RCA／電源／靜音間相同的網路名稱表示電氣相接。IC 1、5 兩腳共用正電源符號位置，2、6、11 是隱藏的 NC 腳；匯出 netlist 會分別核對。

本版 C2／C102 為無極性回授電容；C6／C106 負軌電解及 C8／C108 靜音電解的正端接 GND。輸出標記 TEST OUT，供假負載使用。

在專案根目錄執行 `python3 tools/rebuild.py` 會重建原理圖、ERC、netlist、BOM、PDF、PNG、功率報告與驗證紀錄。生成器會覆寫原理圖；手動修改後需先同步修改生成器，或明確改成以 KiCad 手動檔為主，避免覆蓋人工編輯。

[BOM](bom-draft.csv) · [驗證紀錄](validation.md) · [中文設計說明](../docs/01-design.md)
