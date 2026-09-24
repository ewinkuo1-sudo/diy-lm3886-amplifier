# 接班進度

更新：2026-09-24，原理圖與 PCB 已在本機 KiCad 10.0.6 重建（放大板 115×90、C2 躺式），DRC 0 違規；3D／導讀圖尚未重建（見「環境注意」）。逐日紀錄在 [CHANGELOG.md](CHANGELOG.md)。

使用者指定**內建供電、純後級，外接現有 DAC 與前級**。已確認 Eversolo DAC-Z10（DAC＋前級）及 RCA 介面；音量由 Z10 控制。本機採固定增益。

## 現況

- **電路**：放大板 `electrical/lm3886-v01` 與電源次級 `electrical/internal-psu-v02` 兩份可編輯 KiCad 原理圖為現行電路來源，43＋15 元件 BOM、ERC 均 0 錯誤 0 警告。生成器是唯一來源，改完要跑 `python3 tools/rebuild.py`。
- **PCB**：V0.3 為**工程草稿，不可送製**。兩片 **115×90 mm** 單聲道板（2026-09-24 由 100×90 加寬，C2 改躺式）＋一片 160×120 mm 電源板，KiCad 10.0.6 下 0 DRC 違規、0 未連通，54＋35 焊盤網路對照通過。封裝為暫定外框與假設高度，溫升、散熱、機構與線束都沒驗證。V0.1／V0.2 板檔與舊腳本已於 2026-09-21 刪除，需要時從 Git 歷史（`41b217c`）取回。
- **採購**：變壓器與 yosontw 40 件（電阻、WIMA、CDE、ROE）**2026-09-22 已到貨，未核對未量測**；LM3886T 拆機 IC 到貨未回報。量測順序見 docs/00 §1 與 docs/14 §8。整流橋、保險絲、電感、接頭、端子、絕緣散熱件、AC 入口、軟啟動、保護板、線材、假負載、機殼仍未購。現行採購狀態一律看 [docs/00-採購總表.md](docs/00-採購總表.md)。
- **選型定案**：C2／C102＝ROE EGW 47µF 臥式無極性；C6／C7／C106／C107＝ROE EKE 470µF／63V。

## 下一步

1. **到貨後量四款電解的實體尺寸**（2026-09-23 已量 381LX、EKE、EGW；361R 與 381LX 腳片寬厚未量）—— ROE EGW 47µF、ROE EKE 470µF、CDE 381LX、CDE 361R。ROE 兩款無公開型錄只能實測；CDE 兩款型錄值已寫進採購總表第 1 節，到貨對印字與量一次確認。**381LX 的 A052 料號不在現行 CDE 型錄**，實收可能是 Ø30 的 K 殼。
2. **改 `pcb/DraftV03.pretty/` 封裝** —— 型錄已確定的四項中，**三項已於 2026-09-22 改進封裝庫與生成器**（U1 鑽孔 1.1／焊盤 2.0、C8 改指派 `CP_D12.5_P5`、`CP_D35_P10` 鑽孔 2.5／焊盤 4.0 圓孔暫代槽孔）。**C2 已於 2026-09-23 改躺式 `BP_Axial_L40_D20_P50`、放大板加寬為 115×90、`CP_D12.5_P5` 鑽孔 1.0**（見 pcb/README）。**2026-09-24 已重建板檔並通過 DRC／驗證**；parts-audit 與 3D 預覽尚未重建。**BR1／BR2 已於 2026-09-24 定案：KBPC2510 鎖機殼、四條 Faston 線接到板上 `BridgeTerminal4_P5.08` 4 位端子**（電源板已重建、DRC 0）。逐項比對見採購總表 1.1。C201–C204 依實收殼徑改 snap-in 槽孔（腳片寬 ≤2.0／厚 0.8 mm，1.3 mm 圓孔不合）。改完在有 KiCad 的機器一次完成：`python3 tools/rebuild.py`（原理圖生成器已改 100V／0.6W／註記，會一併帶入 sch、PDF、BOM、validation.md）→ `build_pcb_v03.py` → `run_pcb_drc_v03.py` → `verify_pcb_v03.py` → `render_pcb_v03.py` → `build_diagrams.py`＋`render_diagrams.cjs`（兩張色塊圖底圖才會更新）。
3. **變壓器到貨後量各繞組電流與調整率** —— 用實際值定保險絲額定與整流橋規格，並更新 `tools/power_budget.py`、`tools/mains_budget.py` 的估算前提。
4. **主電容高度確定後才能定機殼** —— 目前推導的內部空間下限為寬 ≥300／深 ≥250／高 ≥90 mm（**以 100×90 放大板推導，放大板已加寬為 115×90，寬度要重算**），機殼未下單、熱阻未標、賣家未確認。
5. **V0.4 控制板**：需求在 [docs/13](docs/13-喇叭保護與啟停設計計畫.md)，設計草案在 [docs/14](docs/14-V0.4-控制與保護板設計草案.md)（2026-09-22 起）。變壓器到貨後照 14 §8 量五項寫回，再照 §7 選繼電器、定 R_s；之後才畫 CTRL 原理圖（新增 `tools/build_control_board.py`，比照兩份現有生成器）。UPC1237 模組到貨照 14 §9 驗證，不直接裝機。
5b. **PCB V0.4 三塊板已畫好**（2026-09-24）：放大板變體 C／D（`pcb/mono-layout-v04c.*`／`v04d.*`）與電源板（`pcb/psu-layout-v04.*`），各 DRC 0，見 pcb/README「PCB V0.4」節。**使用者 2026-09-24 選定 D 為主、C 保留**，D 的輸出主幹已改頂層。接下來：V0.4 的 current-budget／analyze 對照、3D 與導讀圖、系統並排圖（以 D 為放大板），並決定要不要把 V0.3 退為歷史版本。重建指令：`kicad-cli sch export netlist … electrical/netlist.xml` → KiCad 內建 python 跑 `tools/build_pcb_v04.py`（會同時建 C、D、電源板三板） → `kicad-cli pcb drc --format json --exit-code-violations -o pcb/mono-v04c-drc.json pcb/mono-layout-v04c.kicad_pcb` → `py -3.13 tools/verify_pcb_v04.py` → `tools/render_pcb_v04.py`；跑完 `git checkout -- pcb/DraftV03.pretty`（生成器只會重寫 UUID）。
6. Z10 RCA 規格已核對為 2.5Vrms／0dBFS；以假負載校正音量位置及削波點。一次側按 110V／60Hz 規劃，實際變壓器額定與調整率仍須核對。
7. 放大板先以限流實驗電源測試，內建電源獨立驗證後再整合；完成假負載／熱／失真量測後才接喇叭。

封裝定案後另有待辦：J1／J2 極性標示、JP1（RUN）說明文字、全板零件值顯示。

## 未解決問題

- **一次側接線、軟啟動、控制輔助電源與喇叭 DC 保護尚未設計。** 電源圖只涵蓋隔離次級，**不是完整市電施工圖**。
- **沒有 SPICE 元件模擬、可製造 PCB（無 Gerber）、機構加工圖或任何實機量測。** 不得把理想計算或 ERC／DRC 通過當成電路穩定、安全或低失真的證明。
- LM3886T 為拆機品，數量與 /NOPB 版本待到貨核對。
- 變壓器賣場標示 200W，**不等同已驗證 VA**；各繞組電流與最大電壓未知。
- 每聲道 30～40W／8Ω 是探索範圍，不是額定；4Ω 與真實喇叭負載未驗證。
- 散熱器與介面材料未選料，≤0.4／≤0.3°C/W 只是估算條件。
- 機殼未選定，PE 接點、屏障、端子與線束尚未納入整機 BOM。
- 軟體檢查的詳細結果與限制見 [electrical/validation.md](electrical/validation.md)。

## 環境注意

- **（2026-09-23 更正）這台 Windows 其實裝有 KiCad 10.0.6**（`%LOCALAPPDATA%\Programs\KiCad\10.0\bin\` 的 `kicad-cli.exe` 與內建 `python.exe`，不在 PATH）。**2026-09-24 已用此機重建**，做法：另開 `core.autocrlf=false` 的 clone（工作樹 LF），`PATH` 加 KiCad bin，`PYTHONPATH` 指向一個讓 Python 文字寫檔一律 LF 的 `sitecustomize.py`；`build_pcb_v03.py`／`run_pcb_drc_v03.py` 已內建把 KiCad 寫出的 CRLF 轉 LF，雜湊路徑改用 `as_posix()`。本機無 `pdftoppm`，`rebuild.py` 會停；以 PyMuPDF 轉 PNG 代替並手動照 `rebuild.py` 步驟執行。以下為原說明：沒有 `kicad-cli` 時只能改文件與封裝庫（`.kicad_mod` 為純文字，可手改），**不要動 `.kicad_pcb`** —— V0.3 板檔、專案檔、DRC／驗證 JSON 之間有雜湊綁定，手改會讓驗證紀錄失效。
- **2026-09-24 生成器與原理圖／PCB 產物已一致**（`verify_electrical.py` 的期望值同步改為實購 100V／0.6W）。**仍不一致的**：`pcb/inspection-v03/`（3D、parts-audit）與 `docs/diagrams/` 仍是 100×90 舊板，需 sharp 才能重建。
- Windows 本機的 PyMuPDF、Pillow 只裝在 Python 3.13（`py -3.13 -X utf8 …`）；sharp 不在全域 npm，跑 `render_diagrams.cjs`／`render_pcb_inspection_v03.cjs` 前要 `npm install sharp` 到任意目錄並設 `NODE_PATH`。
- `tools/verify_pcb_v03.py` 需要 `electrical/netlist.xml`，該檔由 `kicad-cli` 匯出且不入版控；沒有 KiCad 的機器上它必定失敗，這不是程式錯誤。
- `tools/rebuild.py` 需要 Python 3、KiCad 10 CLI 與 Poppler 的 `pdftoppm`。`tools/build_project_pdf.py` 另需 reportlab、pypdf，非 Windows 環境要設 `LM3886_FONT` 指向 CJK TrueType 字型；產物在 `output/`，不入版控。
- 每次接手先檢查 Git 工作樹與遠端，保留其他協作者的修改，不強制覆寫遠端。

## 歷史紀錄

逐日進度、各版 PCB 與採購的完整歷史見 [CHANGELOG.md](CHANGELOG.md)。歷史採購附錄與舊版板檔已刪除，從 Git 歷史（`41b217c`）取回。
