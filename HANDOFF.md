# 接班進度

更新：2026-10-01（整理版，取代 9 月累積的逐日段落；逐日細節一律看 [CHANGELOG.md](CHANGELOG.md)）。

使用者指定**內建供電、純後級，外接現有 DAC 與前級**。已確認 Eversolo DAC-Z10（DAC＋前級，RCA 2.5 Vrms／0 dBFS；XLR 5 Vrms）；音量由 Z10 控制，本機固定增益約 20 倍。目標喇叭 **Usher Be-718**（標稱 8 Ω、實測低中音 >6 Ω、約 85 dB），匹配估算在 [docs/01](docs/01-設計規格.md)「目標喇叭」節。

## 現況（2026-10-01）

- **電路**：放大板 `electrical/lm3886-v01` 與電源次級 `electrical/internal-psu-v02` 兩份 KiCad 原理圖是電路唯一來源（生成器 `tools/build_schematic.py`／`build_power_supply.py`），43＋15 元件，ERC 0 錯誤 0 警告。改電路 → 改生成器 → `python3 tools/rebuild.py`。**2026-10-01 深夜新增控制／保護板第一版**：`electrical/control-v01`（CTRL，46 件：UPC1237、7812 輔助電源、G2R-1-E ×2、光耦靜音 ×2、TL431 旁通計時）＋`electrical/mains-v01`（MAINS，11 件：SL22 10005 NTC、K_BYP G2R-1-E、K_TRIG G5LE-1），生成器 `tools/build_control_board.py`，ERC 0；**rebuild.py 尚未呼叫它**，手動跑 ERC／PDF／netlist。決定與偏離 docs/14 之處見 docs/14 開頭狀態列。**同夜 PCB 也畫了**：`pcb/ctrl-layout-v06`（70×120）與 `pcb/mains-layout-v06`（70×100），DRC 0 錯誤、`validation-v06-ctrl.json` 通過（含市電／低壓 ≥6.4 mm 檢查），工具 `tools/*_v06_ctrl.py`，見 pcb/README「PCB V0.6」。繼電器定為 G2RL-1-E ×4（低背，KiCad 有封裝）、橋改 1N4007 ×4、光耦 SFH617A-3。機箱 3D：`docs/diagrams/chassis_102_v06_3d.png`（`tools/draw_chassis_scene_v06.py`，pyvista）。
- **機殼與配置（2026-10-01 深夜改向）**：BZ4312A2 延到下一台；**改選弘宙 102**（型錄 d395×c290×e105，內估 393×273×100，賣家未確認），**散熱器內置**兩側：150 長×90 高×30 深黑色鋁擠 ×2（規格依 8 Ω 連續正弦 θSA ≤1.2 °C/W，估法 θSA≈1000/表面積 cm²），鰭片朝牆、底板朝板、上蓋底板開通風孔。配置：後排 放大板 L 80×90｜電源板 87×120｜放大板 R 80×90，變壓器前排中央，控制板 70×120 平放左側、市電板右側。**V0.6 三板尚未畫**（目標尺寸如上，對 103 也成立）。下單前問賣家：內寬實際值、上蓋通風孔、後面板是否空白。
- **PCB：現行為放大板／電源板 V0.6.1（2026-10-03 併入 main；`pcb/mono-layout-v061`、`psu-layout-v061`，與 V0.6 只差走線寬度，見 pcb/README「PCB V0.6.1」）＋ CTRL／MAINS V0.6**。**2026-10-08 放大板與電源板 V0.6.1 已送嘉立創試印（各 5 片、1 oz、US$12.87；送件檔 `pcb/fab-20261008/`；IC／C2／機殼內寬都未實量就送，到貨先乾插核對，見 CHANGELOG）**；CTRL／MAINS 仍是工程草稿，不可送製。V0.6 基礎：放大板 `pcb/mono-layout-v06` 90×80（U1 用 KiCad TO-220-11 直立封裝、背板貼板邊 y=0 直接鎖散熱器＝方案 B，型錄幾何）、電源板 `pcb/psu-layout-v06` 92×120（兩欄 381LX、GBJ 朝前、AC 朝變壓器、DC 朝放大板；snubber 預留位未上板）、CTRL 70×120、MAINS 70×100。四板 DRC 0 錯誤、`validation-v06.json`／`validation-v06-ctrl.json` 通過；圖 `pcb/preview/system-layout-v06.png`。**看圖資料（inspection-v06）未做。** V0.5.1、V0.5、V0.4、V0.3 均為歷史，檔案原樣保留。右聲道放大板＝左板轉 180°，RCA 端子落在前側。
- **機殼**：定案淘寶清風工作室 **BZ4312A2**（BRZHIFI，「無音量前＋平衡後」版，¥458，內 330×297×112，兩側散熱器 300×118×50，附保險絲尾插與電源開關）。**未下單**，只剩問賣家能否加開 12 V trigger 孔。配置 A（放大板貼後側牆、中間控制板、前排變壓器＋電源板）餘裕深 22／前排寬 45 mm，圖 `docs/diagrams/chassis_bz4312a2_v05_fit.png`。XLR 只當接頭：pin 2→DPDT→J1，pin 3 空接。
- **IC 固定**：使用者傾向方案 B（IC 搬到板邊直接鎖側牆散熱器，不用 L 型鋁角），**等三項實量才改板**。
- **採購**：已付 NT$4,821（變壓器、yosontw 40 件、LM3886T ×4 拆機品已到貨，T 封裝、NS 打標）。整機估 10.9k–16.2k，總覽在 [docs/00](docs/00-採購總表.md) §5。待買清單與順序一律看 docs/00 §2／§3；本輪可買：GBJ2510 ×2＋小散熱片＋M3 件、保險絲（提案：一次側 T2.5A 有軟啟動／T3.15A 無、22 V 各 T5A、12 V T1.25A）、機殼、XLR 母座 ×2、DPDT 開關。
- **變壓器**：2026-10-01 已量空載——標籤 22 V 4.2 A×2＋12 V 1 A ≈ 197 VA；兩組 22 V 各 22.29 Vac（DCR 0.25／0.2 Ω，串接同相 44.6 V）；12 V 12.27 V；一次側約 2 Ω；市電 110 V。最壞軌電壓 **±33.5 V**，帶載推估連續 30–32 W／8 Ω。**未量：帶載電壓、繞組間絕緣（應 OL）、溫升。**
- **選型定案**：C2／C102＝ROE EGW 47 µF 無極性（V0.5 起站立封裝 `BP_Axial_Vert_D20_P15`，**腳距 15 是假設**）；C6／C7／C106／C107＝ROE EKE 470 µF／63 V；C8 `CP_D12.5_P5`；主電容 381LX A05 殼 Ø35×50 `CP_D35_P10`。

## 下一步（依順序）

1. **核對 LM3886T 實物與 V0.6 放大板的 IC 幾何**：量①背板背面到奇數／偶數腳排的距離（板檔假設 9.58／4.5）②背板孔中心離腳根高度 ③背板厚度。差超過 0.5 mm 就改 `pcb_layout_v06.py` 的 U1 y 值（其他零件不動；`pcb_layout_v061.py` 匯入它所以會跟著變），重跑 `build_pcb_v061.py`→DRC→`verify_pcb_v061.py`→`render_pcb_v061.py`→`analyze_pcb_v061.py`。散熱器底板每聲道一個 M3 孔，高＝8（銅柱）＋1.6＋②。
2. **C2 站立腳距實量**：把 EGW 47 µF 實物彎腳量腳距，不是 15 就改 `BP_Axial_Vert_D20_P15` 並重建。
3. **變壓器帶載量測**：照 [docs/04](docs/04-上電與驗收.md) 與 [docs/14](docs/14-V0.4-控制與保護板設計草案.md) §8 量帶載電壓、絕緣、溫升；然後把 `tools/mains_budget.py` 的「22 V＋8% 調整率」前提改成實測值重跑，更新 docs/05 試算段。
4. **採購**：照 docs/00 §3 順序。機殼下單前問 trigger 孔；GBJ2510 到貨核腳距 10／7.5／7.5、本體 30×20×3.8、背面絕緣；原理圖 BR1／BR2 的封裝欄位還沒改成 `GBJ_Upright_P10_7.5_7.5`（板檔已是）。
5. **控制板（docs/13／14）**：原理圖與 PCB 第一版都已畫（見現況）。接下來：①使用者審圖；②買零件（G2RL-1-E 12VDC ×5、UPC1237 ×2、SL22 10005 ×1、SFH617A-3 ×2、TL431、BC327 ×2、7812、1N4007 ×9、1N4148 ×2、2200µF/25V 等）→ 到貨核對 G2RL 腳位（COM／NO）、SL22 腳距 10、小電解直徑；③把 `build_control_board.py` 接進 `rebuild.py`，補 `verify_control_board.py`（比照 verify_power_supply）；④docs/14 §6 用 22.4 J 重算、§3 時序表改成「解除靜音＝繼電器吸合」、§7 清單改 G2RL；⑤麵包板實測 UPC1237 在 12 V 供電下的門檻與延遲（型錄是 25–60 V）；⑥CTRL／MAINS 看圖資料（inspection）與絲印整理尚未做。
5b. **V0.6 放大板與電源板已畫（2026-10-02）**。剩：①賣家回 102 內寬後核對 55＋90＋（餘）＋92＋（餘）＋90＋55 ≤ 內寬；②`inspection-v06`（比照 v051 六支腳本衍生）；③~~current-budget 載流對照仍未做~~ → 2026-10-03 `analyze_pcb_v061.py` 已做 V0.6 vs V0.6.1；④決定右聲道 RCA 線走法（同板轉 180°，接頭在前）或另出鏡像放大板。
5c. **V0.6.1（走線加寬）已於 2026-10-03 併入 main 成為放大板／電源板現行版**。後續改放大板／電源板一律改 `pcb_layout_v06.py`（擺位）或 `pcb_layout_v061.py`（寬度）再跑 v061 流程；`inspection` 若要做請做 v061。訂板時另決定 1 oz 或 2 oz（2 oz 全部電阻減半）。機箱 3D 仍吃 V0.6 STL（外形相同）。
6. **工具對照**：V0.4／V0.5／V0.5.1 沒做 current-budget；V0.6→V0.6.1 已有 `analyze_pcb_v061.py`（模型同 v03）。
7. **測試順序**：放大板先用限流實驗電源；內建電源獨立驗證後再整合；假負載／熱／失真量完才接喇叭（docs/04）。

封裝定案後另有待辦：J1／J2 極性標示、JP1（RUN）說明文字、全板零件值顯示。

## 未解決問題

- **一次側接線、軟啟動、控制輔助電源與喇叭 DC 保護尚未設計。** 電源圖只涵蓋隔離次級，**不是完整市電施工圖**。
- **沒有 SPICE 模擬、Gerber、機構加工圖或任何實機量測。** ERC／DRC 通過不等於電路穩定、安全或低失真。
- 每聲道 30–40 W／8 Ω 是探索範圍不是額定；Be-718 低中音 >6 Ω、±36 V 連續 6 Ω 時散熱可能超溫，要實測；4 Ω 未驗。
- 機殼散熱器熱阻賣家未標（估 0.5 °C/W 級），介面材料（雲母＋絕緣粒＋導熱膏）已選未買；PE 接點、屏障、端子與線束尚未納入整機 BOM。
- GBJ2510 散熱片候選未找（鋁鰭片寬 ≤30、厚 ≤10、高 25–35、M3 孔，估 8–12 °C/W），`inspection-v051` 的 GBJ 高度 20 mm 是假設。
- 軟體檢查的詳細結果與限制見 [electrical/validation.md](electrical/validation.md)。

## 環境注意（這台 Windows）

- **KiCad 10.0.6 有裝但不在 PATH**：`%LOCALAPPDATA%\Programs\KiCad\10.0\bin\` 有 `kicad-cli.exe` 與內建 `python.exe`（可 import pcbnew）。沒有 `pdftoppm`，`rebuild.py` 會停在那一步，用 PyMuPDF 轉 PNG 代替並手動照 `rebuild.py` 的步驟跑。
- **行尾**：OneDrive 工作樹是 `autocrlf=true`（CRLF），repo 是 LF。重建板檔一律另開 `git clone -c core.autocrlf=false` 的工作樹（放 scratchpad），改完 commit → push → 回 OneDrive repo `git merge --ff-only`（OneDrive 的 main 是 checked-out，不能直接 push 進去）。雜湊綁定檔（`verification.json`、`sources.json`、`drc-provenance`）一律 LF 正規化後再算。
- **Python**：PyMuPDF、Pillow 只在 3.13，圖表腳本用 `py -3.13 -X utf8`。SVG→PNG 用 `tools/render_diagrams.py`（PyMuPDF），不需 sharp；PyMuPDF 不支援巢狀 `<svg viewBox>` 與 `clip-path`。
- `verify_pcb_v0x.py` 需要 `electrical/netlist.xml`／`psu-netlist.xml`，由 `kicad-cli sch export netlist` 匯出且不入版控；沒匯出就會失敗，不是程式錯誤。
- 板檔生成器會重寫 `pcb/DraftV03.pretty` 的 UUID，跑完要 `git checkout -- pcb/DraftV03.pretty`。
- `tools/build_project_pdf.py` 需 reportlab、pypdf，非 Windows 設 `LM3886_FONT`；產物在 `output/`，不入版控。
- 每次接手先檢查 Git 工作樹與遠端，保留其他協作者的修改，不強制覆寫遠端。

## V0.5.1 重建流程

```
# 在 LF 工作樹，PATH 已加 KiCad bin
kicad-cli sch export netlist -o electrical/netlist.xml     electrical/lm3886-v01.kicad_sch
kicad-cli sch export netlist -o electrical/psu-netlist.xml electrical/internal-psu-v02.kicad_sch
<KiCad python> tools/build_pcb_v051.py            # 只建電源板；放大板用 build_pcb_v05.py
kicad-cli pcb drc --format json --exit-code-violations -o pcb/psu-v051-drc.json pcb/psu-layout-v051.kicad_pcb
py -3.13 -X utf8 tools/verify_pcb_v051.py
py -3.13 -X utf8 tools/render_pcb_v051.py
# 看圖資料：build_ → export_ → frame_ → render_ → write_pcb_parts_audit_ → verify_pcb_inspection_v051.py
git checkout -- pcb/DraftV03.pretty
```

## 分支

- `main`：現行。GitHub `origin/main` 同步。
- `v052-layout`：**未採用**的 V0.5.2 合板候選（每聲道放大＋濾波 90×142，DRC 0），保留供日後參考，不併入。
- `origin/v04-layout`、`origin/v05-layout`、`origin/v051-psu-gbj`：都已併入 main，只剩遠端分支。

## 歷史紀錄

逐日進度、各版 PCB 與採購的完整歷史見 [CHANGELOG.md](CHANGELOG.md)。V0.1／V0.2 板檔與舊腳本已刪除，從 Git 歷史（`41b217c`）取回。
