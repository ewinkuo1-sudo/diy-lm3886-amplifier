# 專案工作約定

- 先讀 README.md、HANDOFF.md，確認工作樹與遠端。
- 僅維護 LM3886 AB 類後級；TPA3255、Purifi 使用各自儲存庫。
- 使用者指定內建供電、外接 Eversolo DAC-Z10 的 RCA 前級輸出；音量由 Z10 控制。實驗電源只用於板級測試。
- 原廠參數要附來源與條件，區分元件規格、設計假設、計算、模擬及實測。
- 放大板／次級電源圖分別由 tools/build_schematic.py、tools/build_power_supply.py 產生；修改後執行 tools/rebuild.py 並檢視兩份預覽。
- 不以 ERC 取代電路審查，不把未驗證 footprint／PCB 當可製造版本。
- 更新 HANDOFF.md 與首頁的進度，保留其他協作者的修改，不強制覆寫遠端。
