# PCB V0.3（B 方案）

**兩片 100×90 mm 單聲道放大板＋一片 160×120 mm 共用電源板。**（2026-09-24 放大板已改為 **115×90 mm** 並重建，DRC 0 違規、0 未連通。）

> ⚠️ **工程草稿，不可送製。** 兩板在 KiCad 10.0.6 下 0 DRC 違規、0 未連通，54＋35 焊盤網路與原理圖相符；但封裝是暫定外框與假設高度，溫升、散熱、機構與線束都沒驗證，**沒有 Gerber**。DRC 與中心線幾何不代表高頻穩定、載流溫升或製造條件已驗證。

![PCB V0.3](preview/system-layout-v03.png)

| 項目 | 單聲道板 ×2 | 電源板 ×1 |
|---|---|---|
| 可編輯 PCB | [mono-layout-v03.kicad_pcb](mono-layout-v03.kicad_pcb) | [psu-layout-v03.kicad_pcb](psu-layout-v03.kicad_pcb) |
| 專案規則 | [KiCad 專案](mono-layout-v03.kicad_pro) | [KiCad 專案](psu-layout-v03.kicad_pro) |
| 圖面 | [PNG](preview/mono-layout-v03.png)／[原生 SVG](preview/mono-v03-native.svg) | [PNG](preview/psu-layout-v03.png)／[原生 SVG](preview/psu-v03-native.svg) |
| 封裝假設 | [清單](mono-layout-v03-footprints.csv) | [清單](psu-layout-v03-footprints.csv) |
| 原生 DRC | [0 違規、0 未連通](mono-v03-drc.json) | [0 違規、0 未連通](psu-v03-drc.json) |

其他資料：[銅箔計算表](current-budget-v03.md)／[完整計算資料與輸入雜湊](current-budget-v03.json)、[驗證摘要](validation-v03.json)、[DRC 檔案綁定](drc-provenance-v03.json)、[正反面／組裝／3D 看圖資料](inspection-v03/README.md)、[零件與封裝核對表](inspection-v03/parts-audit.md)、[左右聲道對照](mono-channel-mapping.csv)。

V0.1／V0.2 板檔、封裝庫與舊腳本已於 2026-09-21 刪除，從 Git 歷史（`41b217c`）取回；僅保留 `archive/v02/*-layout-v02.json` 供 `analyze_pcb_v03.py` 做 V0.2→V0.3 對照。

## 審查結論（2026-09-17，以 V0.2 `d39b623` 為比較基準）

**改了什麼：** C3/C4 的高頻回地改在 IC 附近接至 U1.7，再由獨立局部去耦地線回匯流區，輸入／回授仍走自己的低電平支路；主輸出改走 B.Cu，R4 取樣仍由 U1.3 單獨走 F.Cu；放大板主電流段加寬（主幹 3.0 mm），電源板 AC／DC 主幹由 2.0／3.0 加寬至 4.0 mm；**移除正電源上的兩個換層導通孔**，剩下 3 孔只用於靜音與 Zobel 地線，不在主供電或喇叭電流路徑上；固定生成後的專案規則並加入 DRC 前後設定核對與檔案雜湊綁定。沒有改增益、元件值或電路網路。

| 量化結果 | V0.2 | V0.3 |
|---|---:|---:|
| C3 地端→U1.7 中心線路徑 | 102.94 mm | 24.15 mm |
| C4 地端→U1.7 中心線路徑 | 126.16 mm | 33.15 mm |
| C3→U1.1 電源線＋回地線總長 | 110.55 mm | 32.76 mm |
| C4→U1.4 電源線＋回地線總長 | 147.18 mm | 50.17 mm |
| U1.3→L1.1 走線電阻（1 oz／25°C） | 20.93 mΩ | 9.25 mΩ |
| 正電源 J5→U1.5 走線電阻 | 33.41 mΩ | 22.98 mΩ |
| 負電源 J5→U1.4 走線電阻 | 30.33 mΩ | 26.77 mΩ |

這些是**銅箔中心線的幾何與電阻指標**，不是完整換流迴路、電感或阻抗值，**不能換算成失真改善比例或不振盪保證**。計算條件：±30V、每聲道 40W／8Ω 正弦（40W 是走線尺寸計算點，不是額定）、每軌 85mA 靜態電流、`R = ρΣ(L/W)/t × [1+α(T−25)]`（ρ=17×10⁻⁶ Ω·mm，α=0.0039/°C）、名義 1 oz／2 oz 銅厚 0.0348／0.0696 mm，並以 25°C／85°C 作敏感度比較——**85°C 是輸入值，不是算出來的溫度**。孔壁、焊點、接頭、線材與元件電阻未併入。依據 [TI LM3886 datasheet pp.20–22](https://www.ti.com/lit/ds/symlink/lm3886.pdf) 與 [TI Analog Engineer's Pocket Reference](https://www.ti.com/seclit/eb/slyw038c/slyw038c.pdf)。

**整流充電只有情境、沒有預測。** 變壓器繞組電阻、漏感、空載電壓、橋壓降與電容 ESR 都未知，採矩形脈衝敏感度模型 `Ipeak=Idc/d`、`Irms=Idc/√d`：d=15% 時每軌平均 2.183A、RMS 5.637A、峰值 14.554A；d=35% 時 RMS 3.690A、峰值 6.238A。**這不是實測預測也不是保證上界**，到貨後波形可能超出。保險絲到橋的 50 mm AC 銅箔加寬到 4.0 mm 後，15% 情境下發熱由 0.388 降至 0.194 W，所以本輪優先加寬 AC 線而不只加寬 DC 輸出。

**本輪算的是發熱功率 W，不是溫升 °C**；實際溫升還取決於成品銅厚、板材、鄰近發熱零件、機殼溫度與通風。沒有使用 [IPC-2152](https://www.ipc.org/TOC/IPC-2152.pdf) 完整圖表，不宣稱符合該標準。

**規則重設問題的更正：** V0.2 生成器的 `SaveBoard` 會重建同名 `.kicad_pro` 把人工設定還原，已發布的 V0.2 實際是 Default 網路類別 0.2 mm，不是舊文字宣稱的 0.3 mm。V0.3 在所有 PCB 儲存後才寫入規則，`run_pcb_drc_v03.py` 於執行前後檢查 0.30 mm 間距、0.35 mm 線寬、0.50 mm 板邊距、0.20 mm 導通孔環寬、0.15 mm 絲印間距，並綁定 DRC／PCB／專案／走線 JSON 的 SHA-256。

**2026-09-19 絲印組裝標記（僅改封裝庫與生成器，板檔未重建）：** `DraftV03.pretty` 的 `CP_D12.5_P5`／`CP_D8_P3.5`／`CP_D35_P10` 加上「+」記號與負極粗條，`LM3886T_UNVERIFIED` 加上 pad 1 標記與「TAB = V- HEATSINK」字樣。幾何集中在 [tools/silk_marks_v03.py](../tools/silk_marks_v03.py)，重建時自動寫入；**兩份 `.kicad_pcb`、預覽圖與 DRC 雜湊未變**，要在 KiCad 環境跑完下方指令才會出現在板面。C8 極性依 mute 拓樸推定，到料後再核對。

**2026-09-23 依實量改（2026-09-24 已重建）：** ROE EGW 47µF 實量軸向 40×Ø20、腳徑約 0.8–1.0 → 新增 `BP_Axial_L40_D20_P50`（腳距 50、鑽孔 1.2、焊盤 2.6、外框 40×21），C2 躺式直放於 (70.5,80) 轉 90°，C2.2 在上方距 R3.1 約 12 mm、C2.1 在下方以 1.0 mm B.Cu 回 SG；放大板 100→**115×90**，R8／C8／JP1 右移至新增區（R8 100,48／C8 103,66 轉 180／JP1 110,52），R2 接地改繞 (76,26)(76,43) 避開 C2.2，靜音供電 VEE 改走 F.Cu 沿 y=76 避開 C2.1 接地線。`CP_D12.5_P5` 鑽孔 0.9→1.0（EKE、361R 腳徑 0.8）。**2026-09-24 KiCad 重建結果：** 首輪 DRC 抓到 C2 與 R1 零件保留區重疊（C2 由 x=72 移到 70.5 解決），以及 9/19 絲印那輪留下的兩個警告（U1「TAB」字高 0.7→0.8、U1 位號移到 (60,3) 不再壓字）；`verify_pcb_v03.py` 抓到 C2 訊號地與靜音回流在 (72,56) 相碰（同為 GND，DRC 不報，但違反「分路只在 STAR 匯合」），靜音回流改為 C8.1→F.Cu→`via_mute_ret` (62,71)→B.Cu→STAR。修正後兩板 0 違規、0 未連通、回地分組通過。走線寬度與訊號完整性仍只是工程假設。

**2026-09-22 依型錄改封裝庫與生成器（板檔未重建，比照 9/19 絲印那輪）：** `LM3886T_UNVERIFIED` 鑽孔 0.9→1.1、焊盤 1.65→2.0（TI 腳寬 0.97）；`CP_D35_P10` 鑽孔 1.3→2.5、焊盤 3→4（snap-in 腳片 2.0×0.8，圓孔暫代槽孔，腳距 10 待到貨確認）；`pcb_layout_v03.py` C8 改 `CP_D12.5_P5`（CDE 361R EG 殼 Ø12.5×20、腳距 5.0；位置 74,63 不動，與 R8／JP1 淨空已按座標核過）。C2 `BP_D10_P5` 立式→臥式等 ROE EGW 實測。**兩份 `.kicad_pcb`、預覽圖、DRC 雜湊未變**；重建後 U1 焊盤變大，要重看 pin 間走線間距。預覽圖標題已改為「方案 C PCB V0.3（布局 B）」，B 只是布局代號，不是電路方案。

**還不能定案，依序要核對：** ①LM3886T 實際腳距／彎腳／散熱片位置，再縮短負軌去耦與 470µF 回路（負電源近 IC 的 0.8 mm 段是目前最窄處）②變壓器 VA／繞組電流、整流橋與電容的實際料號與尺寸 ③板廠成品銅厚、孔壁最小鍍層、接頭與保險絲座額定 ④板外線束、機殼接地與整機保護 ⑤板級限流上電、假負載、示波器穩定性與熱量測。

## 重建

需要 KiCad 10 CLI、能匯入 `pcbnew` 的 Python、繪圖用 Pillow。位置與逐段走線定義在 `tools/pcb_layout_v03.py`。

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

繪圖 Python 可與 KiCad Python 分開；非 macOS／Windows 以 `LM3886_FONT` 指向中文字型。**改過 PCB、規則或走線 JSON 後必須重跑原生 DRC，否則雜湊驗證會拒絕舊報告。**
