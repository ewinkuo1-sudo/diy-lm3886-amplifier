# PCB V0.3：正反面、組裝、3D 與零件核對

2026-09-18，依 GitHub `a71b2c4` 的現行電路與 PCB V0.3 製作。完成使用者選定的 A＋B＋C；**沒有改變原理圖、PCB 走線、元件值或採購狀態**。這是一套工程審查資料，尚不可送廠。

![PCB 立體預覽](3d/overview.png)

## A：正反面與組裝圖

兩片單聲道板完全相同，因此提供一套放大板圖與一套電源板圖。正、反面是同一電路在兩個銅層的實際走線；不代表兩套獨立電路。

| 圖面 | 單聲道板 ×2 | 電源板 ×1 |
|---|---|---|
| 正面銅箔 F.Cu | [PNG](drawings/mono-top.png)／[SVG](drawings/mono-top.svg) | [PNG](drawings/psu-top.png)／[SVG](drawings/psu-top.svg) |
| 背面銅箔 B.Cu | [PNG](drawings/mono-bottom.png)／[SVG](drawings/mono-bottom.svg) | [PNG](drawings/psu-bottom.png)／[SVG](drawings/psu-bottom.svg) |
| 正面組裝／極性圖 | [PNG](drawings/mono-assembly.png)／[SVG](drawings/mono-assembly.svg) | [PNG](drawings/psu-assembly.png)／[SVG](drawings/psu-assembly.svg) |
| 值、接頭用途、逐腳網路 | [對照表](drawings/mono-assembly-notes.md) | [對照表](drawings/psu-assembly-notes.md) |
| KiCad 原生銅箔匯出 | [正面](native/mono-top.svg)／[背面](native/mono-bottom.svg) | [正面](native/psu-top.svg)／[背面](native/psu-bottom.svg) |

**觀看方向：**正面圖從元件側看；背面銅箔圖相對正面左右鏡像，等於沿垂直軸把板子翻過來，板檔的 y 方向不變。背面圖中的元件編號只是對位註解，不表示元件裝在背面。原生背面 SVG 同樣使用 KiCad `--mirror`。沒有提供製板底片或保證 1:1 列印的加工圖。

組裝圖的 `1 +`／`2 -` 表示有極性電解的正負焊盤。C2 是無極性電容，不加正負標記。C6、C8、C203／C204 的**正端在 GND**，不能把所有 GND 一律當成電容負端。整流橋的 P／N 是功能名稱，實物腳位還未核對。

左右聲道實體板都使用 U1、R1、C1 等同一套絲印；右聲道對應 U2、R101、C101 等原理圖編號，見 [原理圖對照](../mono-channel-mapping.csv)。右聲道板上保留 L_* 網路名稱只是相同板檔的命名，不把左右輸出相接。

## B：PCB 3D 預覽

| 角度 | 單聲道板 | 電源板 |
|---|---|---|
| 斜視 | [PNG](3d/mono-isometric.png) | [PNG](3d/psu-isometric.png) |
| 正面 | [PNG](3d/mono-top.png) | [PNG](3d/psu-top.png) |
| 背面 | [PNG](3d/mono-bottom.png) | [PNG](3d/psu-bottom.png) |
| 可旋轉的 KiCad 預覽板 | [KiCad 專案](3d/mono-layout-v03-preview.kicad_pro)／[PCB](3d/mono-layout-v03-preview.kicad_pcb) | [KiCad 專案](3d/psu-layout-v03-preview.kicad_pro)／[PCB](3d/psu-layout-v03-preview.kicad_pcb) |

下載整個專案，使用 KiCad 開啟上表的 **preview 專案與 PCB**，再開啟「檢視 → 3D 檢視器」，即可旋轉與縮放。保留旁邊的 `models/` 資料夾；模型以 `${KIPRJMOD}/models/…` 相對路徑連結。GitHub 本身只預覽 PNG，不會直接操作 KiCad 檔案。

原 PCB 沒有修改；另產生的 preview 板只新增 3D 模型引用。共 15 種自建 VRML 外框覆蓋 22＋15 個元件位置。平面外框取自現有暫定封裝，**全部高度另採假設值**，詳見尺寸表；不是原廠 CAD，也不是保證能容納實物的最大外框。

模型沒有表達 IC 真正彎腳及背板、電感繞線、接頭插線口、螺絲工具空間、保險絲夾、散熱器或焊錫。小金屬柱僅協助看焊盤位置；不可拿來檢查真實引腳成形。板厚 1.6 mm 及四角固定孔仍是設計假設。3D 圖有助於討論配置，但不能據此宣稱無干涉或散熱合格。本輪沒有發行 STEP 加工模型、Gerber 或鑽孔製造包。

原生算繪的未加框 PNG 保存為 `3d/raw-*.png`，供來源追溯；分享時優先使用加上假設說明的上表圖面。3D 背面角度依 KiCad 的 bottom 視角；對照焊盤時請使用 A 的明確鏡像平面圖。

## C：零件與封裝核對

[完整核對表](parts-audit.md) 按板上編號列出元件值、暫定外形、假設高度、腳距、孔徑、採購狀態與選料優先順序。[JSON](parts-audit.json) 另含每個焊盤的本地座標與網路，便於後續更新。

只有變壓器與 LM3886T 已訂，最後紀錄仍為待到貨；本次沒有收到新的到料資訊。優先確定 IC、整流橋、大電容、接頭與保險絲座的實際料號，再修訂封裝。機殼及散熱器尚未納入本次模型。

## 檢查與來源

- [來源 SHA-256](sources.json)：原 PCB、專案與走線 JSON。
- [本輪核對結果](verification.json)：預覽板刪除模型節點後與原板語法樹一致；模型、尺寸與 89 焊盤位置／網路對照；全量檔案雜湊。
- [KiCad 匯出紀錄](native-export-log.json)：四份原生銅箔 SVG 與六張 3D 算繪。
- 既有 PCB V0.3 的 DRC／網路驗證見 [上層說明](../README-v03.md)。本輪沒有改走線，沒有新增 ERC／DRC 或實機測試；不把 3D 顯示當作電氣驗證。

原廠工具依據：[KiCad 10 PCB Editor／3D viewer](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html)；[KiCad VRML 單位說明](https://dev-docs.kicad.org/en/file-formats/legacy-pcb/index.html)。VRML 座標依 KiCad 的 0.1 inch 單位生成（1 單位＝2.54 mm）；不使用生成式圖片猜測電路。

## 重建

依序執行（Python 3、KiCad 10 CLI；PNG 工具另需 sharp 與 Pillow）：

```sh
python3 tools/build_pcb_inspection_v03.py
python3 tools/write_pcb_parts_audit_v03.py
node tools/render_pcb_inspection_v03.cjs
python3 tools/export_pcb_inspection_v03.py --cli kicad-cli
python3 tools/frame_pcb_inspection_v03.py
# 使用能匯入 pcbnew 的 KiCad Python：
python3 tools/verify_pcb_inspection_v03.py
```

中文圖片字型需 STHeiti 或對等 CJK 字型；Pillow 加框可透過 `LM3886_FONT` 指定字型檔。若電路或封裝改動，需先依主專案流程重建與檢查，再重製本套圖面；不得把本資料夾的 preview 板當成後續電路來源。
