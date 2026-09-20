# tools/ 腳本索引

入口只有一支：

```sh
python3 tools/rebuild.py
```

`rebuild.py` 需要 KiCad 10 CLI 與 Poppler `pdftoppm`；它只重建**原理圖側**：畫兩份 KiCad 原理圖、跑 ERC、匯出 netlist／PDF／PNG、獨立核對網路，再重新產生 docs/02 與 docs/06 兩份估算文件。任何驗證失敗即中止。**它不呼叫任何 pcb 腳本**；PCB、導讀圖、PDF 需另外手動執行下列工具。

## 原理圖與估算（由 rebuild.py 呼叫）

| 腳本 | 用途 |
|---|---|
| `build_schematic.py` | 產生放大板原理圖 `electrical/lm3886-v01.kicad_sch`（純標準庫） |
| `build_power_supply.py` | 產生次級電源原理圖 `electrical/internal-psu-v02.kicad_sch`；引用 build_schematic 的繪圖函式 |
| `verify_electrical.py` | 以獨立電路規格核對 KiCad 匯出的放大板 netlist |
| `verify_power_supply.py` | 電源板拓樸、極性與線束核對 |
| `power_budget.py` | 理想 B 類功率／散熱估算，輸出 docs/02 |
| `mains_budget.py` | 市電變動、空載電壓、紋波估算，輸出 docs/06；引用 power_budget |

## PCB V0.3（現行；需 KiCad Python 環境）

| 腳本 | 用途 |
|---|---|
| `pcb_layout_v03.py` | B 方案 V0.3 位置與逐段走線定義（資料檔，不直接執行） |
| `build_pcb_v03.py` | 由 pcb_layout_v03 與 netlist 產生 `pcb/*-layout-v03.kicad_pcb`、JSON 與封裝表 |
| `run_pcb_drc_v03.py` | 固定規則下跑原生 DRC，並把報告雜湊綁到檔案 |
| `verify_pcb_v03.py` | 核對 DRC 結果、焊盤網路、放大板回地分組，寫 `pcb/validation-v03.json` |
| `render_pcb_v03.py` | 由 JSON 畫 `pcb/preview/*.png`（需 Pillow） |
| `analyze_pcb_v03.py` | 銅箔路徑電阻／壓降／損耗篩查，寫 `pcb/current-budget-v03.*` |
| `test_pcb_analysis_v03.py` | analyze_pcb_v03 的回歸測試（unittest） |

## PCB V0.3 看圖與零件核對（`pcb/inspection-v03/`）

| 腳本 | 用途 |
|---|---|
| `build_pcb_inspection_v03.py` | 產生導讀圖 SVG、暫定 VRML 模型、預覽板與組裝表 |
| `export_pcb_inspection_v03.py` | 用 kicad-cli 匯出原生分層 SVG 與 3D 渲染 |
| `frame_pcb_inspection_v03.py` | 3D 渲染加註假設說明框（需 Pillow） |
| `render_pcb_inspection_v03.cjs` | SVG 轉 PNG（Node，需 sharp） |
| `write_pcb_parts_audit_v03.py` | 產生 `parts-audit.json／md` |
| `verify_pcb_inspection_v03.py` | 核對預覽板、模型尺寸與來源綁定 |

## 導讀圖與 PDF

| 腳本 | 用途 |
|---|---|
| `build_diagrams.py` | 產生 `docs/diagrams/svg/*.svg`（色塊圖需 PyMuPDF） |
| `render_diagrams.cjs` | SVG 轉 PNG（Node） |
| `build_project_pdf.py` | 產生 `output/pdf/*.pdf`（需 reportlab、pypdf、CJK 字型；非 Windows 設 `LM3886_FONT`）。`output/` 為生成產物，不入版控 |

## archive/（歷史，勿用於現行版本）

V0.1（`*_draft.py`）與 V0.2（`*_v02.py`）的產生／繪圖／驗證腳本。輸出已改指向 `pcb/archive/v01/`、`pcb/archive/v02/`，只為重現歷史板檔。**檔名裡的 v01／v02 是 PCB 版號；`electrical/` 的 lm3886-v01、internal-psu-v02 是現行原理圖，別混淆。**
