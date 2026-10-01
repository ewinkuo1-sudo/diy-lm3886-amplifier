# tools/ 腳本索引

更新：2026-10-01。腳本以 PCB 版號分家族（v03／v04／v05／v051），**現行是 V0.5.1**：放大板用 v05 家族建、電源板用 v051 家族建。舊家族保留，只為重現歷史板檔，不再修改。

原理圖側入口只有一支：

```sh
python3 tools/rebuild.py
```

`rebuild.py` 需要 KiCad 10 CLI 與 Poppler `pdftoppm`；它只重建**原理圖側**：畫兩份 KiCad 原理圖、跑 ERC、匯出 netlist／PDF／PNG、獨立核對網路，再重新產生 docs/02。任何驗證失敗即中止。**它不呼叫任何 pcb 腳本**；PCB、看圖資料、導讀圖、PDF 需另外手動執行。Windows 本機沒有 `pdftoppm`，照 rebuild.py 的步驟手動跑並用 PyMuPDF 轉 PNG（見 HANDOFF「環境注意」）。

## 原理圖與估算（由 rebuild.py 呼叫）

| 腳本 | 用途 |
|---|---|
| `build_schematic.py` | 產生放大板原理圖 `electrical/lm3886-v01.kicad_sch`（純標準庫） |
| `build_power_supply.py` | 產生次級電源原理圖 `electrical/internal-psu-v02.kicad_sch`；引用 build_schematic 的繪圖函式 |
| `build_control_board.py` | **2026-10-01 新增，rebuild.py 尚未呼叫**：產生控制／保護板 `electrical/control-v01.kicad_sch`（UPC1237、G2R-1-E ×2、光耦靜音、TL431 旁通計時、7812 輔助電源）與市電板 `electrical/mains-v01.kicad_sch`（NTC、K_BYP、K_TRIG）。手動跑 `kicad-cli sch erc／export pdf／export netlist`，PyMuPDF 轉 PNG 到 `electrical/preview/` |
| `verify_electrical.py` | 以獨立電路規格核對 KiCad 匯出的放大板 netlist |
| `verify_power_supply.py` | 電源板拓樸、極性與線束核對 |
| `power_budget.py` | 理想 B 類功率／散熱估算，輸出 docs/02 |
| `mains_budget.py` | 市電變動、空載電壓、紋波估算，**只印到 stdout**，人工更新 docs/05 估算段（docs/06 已於 2026-09-21 併入 docs/05）；引用 power_budget。**前提仍是「22 V＋8% 調整率」，尚未改成 2026-10-01 實測值** |
| `control_budget.py` | 控制板估算：湧流／軟啟動、繼電器 DC 分斷、掉電時序、12 Vac 輔助電源、靜音、Z10 trigger；輸出 docs/14 §6（不由 rebuild.py 呼叫，手動執行） |

## PCB 現行 V0.5.1（需 KiCad Python 環境）

每個版本家族都是同一組角色：**layout（資料檔）→ build → DRC → verify → render**，再加六支 inspection 腳本。V0.5.1 只重畫電源板，放大板沿用 V0.5。

| 腳本 | 用途 |
|---|---|
| `pcb_layout_v05.py` | 放大板 D 90×90 位置與走線定義（**現行放大板**；底層整面接地） |
| `pcb_layout_v05_psu.py` | 電源板 V0.5 125×130 定義（歷史；v051 由它衍生） |
| `pcb_layout_v051_psu.py` | 電源板 V0.5.1 定義：V0.5 只覆寫 BR1／BR2 改 GBJ2510 直立上板與相關七條走線（**現行電源板**） |
| `build_pcb_v05.py` | 一次建放大板 D＋電源板 V0.5（沿用 v03 的 `build()` 與 v04 的 `add_zones()`；新增封裝 `BP_Axial_Vert_D20_P15`） |
| `build_pcb_v051.py` | 只建電源板 V0.5.1；新增封裝 `GBJ_Upright_P10_7.5_7.5`（`make_fp_oval` 長孔） |
| `verify_pcb_v05.py` | DRC 0、焊盤網路對照、放大板鋪銅單一連通區 → `pcb/validation-v05.json` |
| `verify_pcb_v051.py` | 同上（電源板）＋ GBJ 本體與 10 mm 散熱片包絡不撞件 → `pcb/validation-v051.json` |
| `render_pcb_v05.py` | 由 JSON 畫 `pcb/preview/*-v05*.png` 與 `system-layout-v05.png` |
| `render_pcb_v051.py` | 畫 `psu-layout-v051.png` 與 V0.5／V0.5.1 並排對照圖 |
| `build_pcb_inspection_v051.py` → `export_` → `frame_` → `render_` → `write_pcb_parts_audit_v051.py` → `verify_pcb_inspection_v051.py` | 看圖資料 `pcb/inspection-v051/`：導讀 SVG、暫定 VRML、預覽板、kicad-cli 分層與 3D 匯出、加註假設框、SVG→PNG（PyMuPDF）、零件核對表、來源綁定核對。中間產物（`3d/models/`、`*-preview.*`、`raw-*.png`）不入版控 |

DRC 不再有專用腳本（v03 的 `run_pcb_drc_v03.py` 之後直接用 `kicad-cli pcb drc`），完整指令順序見 HANDOFF「V0.5.1 重建流程」。

## PCB V0.6（現行五板，2026-10-01 深夜～10-02 凌晨；需 KiCad Python 環境與 `py -3.13`）

| 腳本 | 用途 |
|---|---|
| `pcb_layout_v06.py` | 放大板 90×80（U1 用函式庫 TO-220-11，背板貼板邊 y=0）與電源板 92×120 的位置與走線定義；檔頭列出與 V0.5／V0.5.1 的差異 |
| `build_pcb_v06.py` | 一次建放大板＋電源板；借 `build_pcb_v06_ctrl.import_std` 複製 TO-220-11 封裝成 `LM3886T_TO220-11`（3D 模型保留），GBJ 封裝來自 `build_pcb_v051` |
| `verify_pcb_v06.py` | DRC 0 錯誤、焊盤網路對照、焊盤在板內、放大板鋪銅單一連通區、U1 背板在板邊、GBJ 本體與 10 mm 散熱片包絡（+y 側）不撞件、列出未上板的 snubber 零件 → `pcb/validation-v06.json` |
| `render_pcb_v06.py` | `pcb/preview/mono-layout-v06.png`、`psu-layout-v06.png`、五板同比例 `system-layout-v06.png` |
| `pcb_layout_v06_ctrl.py` | CTRL 70×120 與 MAINS 70×100 的位置與走線定義（檔頭有樓層圖；CTRL 底層 GND 鋪銅、+12V 走底層 x=50 兩個過孔；MAINS 市電側 x≥32、低壓側 x≤24） |
| `build_pcb_v06_ctrl.py` | 一次建兩板。`import_std()` 把 KiCad 函式庫封裝（G2RL-1-E、SIP-8、DIP-4、TO-92 wide、TO-220、DO-41、DO-35）複製進 `pcb/DraftV03.pretty` 並把焊盤編號改成原理圖腳名；另做 `NTC_D22_P10`、`CP_D5_P2`、`CP_D6.3_P2.5` 暫定外框。跑完 `git checkout -- pcb/DraftV03.pretty` 只還原既有檔（新封裝檔要保留） |
| `verify_pcb_v06_ctrl.py` | DRC 0 錯誤、焊盤網路對照、焊盤在板內、CTRL 鋪銅單一連通區、**MAINS 市電網路與低壓網路銅箔最小距離 ≥6.4 mm** → `pcb/validation-v06-ctrl.json` |
| `render_pcb_v06_ctrl.py` | 畫 `pcb/preview/ctrl-mains-layout-v06.png`（兩板並排，頂視） |
| `draw_chassis_scene_v06.py` | 弘宙 102 機箱內部 3D（pyvista／VTK 離屏算圖）：吃 `kicad-cli pcb export stl --subst-models --include-pads` 匯出的五塊板 STL（`place_board(name, origin, rot)` 以純旋轉放進機殼，右聲道放大板＝左板轉 180°），沒有模型的零件照板檔 JSON 補方塊／圓柱；散熱器、變壓器為估算尺寸 → `docs/diagrams/chassis_102_v06_3d.png`（另輸出 .gltf 給 Blender，不入版控） |

流程：`kicad-cli sch export netlist`（四份原理圖）→ KiCad python `build_pcb_v06.py`、`build_pcb_v06_ctrl.py` → `kicad-cli pcb drc --format json --severity-all --exit-code-violations`（四板）→ `py -3.13 verify_pcb_v06.py`、`verify_pcb_v06_ctrl.py` → `render_pcb_v06.py`、`render_pcb_v06_ctrl.py` → `kicad-cli pcb export stl` ×4 → `draw_chassis_scene_v06.py <stl 目錄>`。跑完 `git checkout -- pcb/DraftV03.pretty` 還原既有封裝的 UUID（新封裝檔保留）。

## 歷史家族（保留，不再改）

| 家族 | 板 | 腳本 |
|---|---|---|
| **v03**（2026-09-17～24） | 放大板 115×90＋電源板 160×120 | `pcb_layout_v03.py`、`build_pcb_v03.py`（其他版本的 `build()` 都來自這支）、`run_pcb_drc_v03.py`（雜湊綁定 DRC）、`verify_pcb_v03.py`、`render_pcb_v03.py`（其他版本的畫圖函式來源）、`silk_marks_v03.py`（封裝極性絲印）、`analyze_pcb_v03.py`＋`test_pcb_analysis_v03.py`（載流對照 V0.2→V0.3，讀 `pcb/archive/v02/*.json`，**之後版本沒再做**）、`*_inspection_v03.py` 五支＋`render_pcb_inspection_v03.cjs`（需 sharp） |
| **v04**（2026-09-24） | 放大板 C（星型改良）／D（整面接地）115×90＋電源板 160×120 | `pcb_layout_v04.py`（含 AMP_C／AMP_D）、`pcb_layout_v04_psu.py`、`build_pcb_v04.py`（一次建三板；`add_zones()` 鋪銅）、`verify_pcb_v04.py`、`render_pcb_v04.py`、`*_inspection_v04.py` 六支（SVG→PNG 改用 PyMuPDF） |
| **v05**（2026-09-29） | 放大板 D 90×90（現行）＋電源板 125×130（歷史） | 見上表 |

## 機殼、導讀圖與 PDF

| 腳本 | 用途 |
|---|---|
| `draw_chassis_fit_v05.py` | BZ4312A2 俯視配置 A，左 V0.4／右 V0.5 三板，板尺寸讀 `pcb/*.json` → `docs/diagrams/chassis_bz4312a2_v05_fit.png` |
| `draw_chassis_iso.py` | BZ4312A2 內部等角立體示意（配置 A）→ `chassis_bz4312a2_3d.png`（PIL） |
| `build_diagram_full_v04.py` | 單聲道完整接線圖 `docs/diagrams/svg/lm3886_full_v04.svg`（每條線畫出、無網路標籤；電路到 V0.5.1 未變，仍適用） |
| `build_diagrams.py` | 其餘五張導讀 SVG（色塊圖需 PyMuPDF 讀 KiCad PDF） |
| `render_diagrams.py` | SVG→PNG（PyMuPDF，Windows 用這支） |
| `render_diagrams.cjs` | SVG→PNG（Node＋sharp；mac 用） |
| `build_project_pdf.py` | 產生 `output/pdf/*.pdf`（需 reportlab、pypdf、CJK 字型；非 Windows 設 `LM3886_FONT`）。`output/` 不入版控 |

## 已刪除的歷史腳本

V0.1（`*_draft.py`）與 V0.2（`*_v02.py`）腳本已於 2026-09-21 刪除，需要時從 Git 歷史（`41b217c`）取回。`pcb/archive/v02/mono-layout-v02.json`、`psu-layout-v02.json` **刻意保留**，因為 `analyze_pcb_v03.py` 要讀它們做對照。

**檔名裡的 v01／v02 是 PCB 版號；`electrical/` 的 lm3886-v01、internal-psu-v02 是現行原理圖，別混淆。**
