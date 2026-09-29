# -*- coding: utf-8 -*-
"""BZ4312A2 俯視配置 A，左＝V0.4 三板、右＝V0.5 三板，板尺寸直接讀 pcb/*.json。單位 mm，x 左→右 0..330，y 後→前 0..297。
配置假設：後面板內凸帶 25、放大板 IC 邊貼散熱牆、排間隔 30、變壓器 Ø120 左右各留 20、控制板預留 120×105（docs/14 尺寸未定）。
輸出 docs/diagrams/chassis_bz4312a2_v05_fit.png。需要 Pillow 與微軟正黑體。"""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
R = Path(__file__).resolve().parents[1]
F = lambda s, b=False: ImageFont.truetype("C:/Windows/Fonts/msjhbd.ttc" if b else "C:/Windows/Fonts/msjh.ttc", s)
W, D = 330, 297
S = 2.5
img = Image.new("RGB", (2300, 1560), "white"); d = ImageDraw.Draw(img)
DARK, BLUE, RED, GREEN, GRAY, AMBER = "#1F242B", "#1F5C7A", "#B33A28", "#2E6B4F", "#6B7480", "#B5730D"
size = lambda name: json.loads((R / "pcb" / f"{name}.json").read_text(encoding="utf-8"))["size"]

def panel(ox, oy, title, amp, psu, ctrl, notes, verdict, vcolor):
    """amp=(沿牆, 垂直牆)；psu=(w, dep, 說明列)；ctrl=(w, dep)。放大板 JSON 的第一維是貼牆那一邊。"""
    P = lambda x, y: (ox + 50 * S + x * S, oy + y * S)
    d.text((ox, oy - 60), title, font=F(30, True), fill=DARK)
    for xw in (0, 50 * S + W * S):
        d.rectangle([ox + xw, oy, ox + xw + 50 * S, oy + D * S], fill="#C9CED4", outline=DARK, width=2)
        for k in range(10):
            yy = oy + 15 * S + k * 27 * S
            d.rectangle([ox + xw + (0 if xw else 38 * S), yy, ox + xw + (12 * S if xw else 50 * S), yy + 4 * S], fill="#B3B9C0")
    d.rectangle([*P(0, 0), *P(W, D)], outline=DARK, width=3)
    d.text((ox + 50 * S + W * S / 2, oy + D * S + 30), "前面板（10 mm，只有電源鈕）", font=F(18), fill=GRAY, anchor="ma")
    d.text((ox, oy + D * S + 8), "散熱器 300×118（左右各一）", font=F(18), fill=GRAY)
    d.rectangle([*P(0, 0), *P(W, 25)], fill="#FBEDE9", outline=RED, width=1)
    d.text(P(4, 5), "後面板內凸帶約 25：XLR / RCA / 切換開關 / 喇叭端子 / 電源尾插", font=F(18), fill=RED)
    ad, aw = amp          # ad 沿牆（深度方向），aw 垂直牆（寬度方向）
    for x0, name in ((0, "放大板 L"), (W - aw, "放大板 R")):
        d.rectangle([*P(x0, 25), *P(x0 + aw, 25 + ad)], fill="#E9F3EE", outline=GREEN, width=3)
        ic_x = x0 if x0 == 0 else W - 2
        d.rectangle([*P(ic_x, 45), *P(ic_x + 2, 65)], fill=DARK)
        d.text(P(x0 + 5, 30), name, font=F(22, True), fill=GREEN)
        d.text(P(x0 + 5, 56), f"{aw}×{ad}", font=F(20), fill=GREEN)
    cw, cd = ctrl
    cx0 = (W - cw) / 2
    d.rectangle([*P(cx0, 30), *P(cx0 + cw, 30 + cd)], fill="#F3F5F7", outline=DARK, width=3)
    d.text(P(cx0 + 5, 35), "控制板預留", font=F(22, True), fill=DARK)
    d.text(P(cx0 + 5, 61), f"{cw}×{cd}（尺寸未定）", font=F(18), fill=GRAY)
    d.text(P(cx0 + 5, 84), f"左右各離放大板 {int(cx0 - aw)}", font=F(18), fill=GRAY)
    pw, pd, plabel = psu
    row_y = 25 + ad + 30
    tx = 20 + 60
    d.ellipse([*P(tx - 60, row_y), *P(tx + 60, row_y + 120)], fill="#E7EFF4", outline=BLUE, width=3)
    d.ellipse([*P(tx - 20, row_y + 40), *P(tx + 20, row_y + 80)], fill="white", outline=BLUE, width=2)
    d.text(P(tx, row_y + 100), "變壓器 Ø120", font=F(22, True), fill=BLUE, anchor="ma")
    px0 = tx + 60 + 20
    d.rectangle([*P(px0, row_y), *P(px0 + pw, row_y + pd)], fill="#FBEDE9", outline=RED, width=3)
    d.text(P(px0 + 5, row_y + 5), f"電源板 {pw}×{pd}", font=F(22, True), fill=RED)
    for i, t in enumerate(plabel):
        d.text(P(px0 + 5, row_y + 32 + i * 24), t, font=F(18), fill=GRAY)
    def gap(x0, y0, x1, y1, text):
        d.rectangle([*P(x0, y0), *P(x1, y1)], fill="#FFF3D6", outline=AMBER, width=1)
        d.text(P((x0 + x1) / 2, (y0 + y1) / 2), text, font=F(18, True), fill=AMBER, anchor="mm")
    gap(px0 + pw, row_y, W, row_y + pd, f"前排寬餘 {W - px0 - pw}")
    gap(tx + 60, row_y, px0, row_y + pd, f"{px0 - tx - 60}")
    row_d = max(120, pd); dr = D - row_y - row_d
    d.rectangle([*P(0, row_y + row_d), *P(W, D)], fill="#FFF3D6", outline=AMBER, width=1)
    if dr >= 20: d.text(P(W / 2, row_y + row_d + dr / 2), f"深度餘裕 {dr}", font=F(18, True), fill=AMBER, anchor="mm")
    else: d.text(P(W / 2, D + 2), f"↑ 深度餘裕只有 {dr}", font=F(18, True), fill=AMBER, anchor="ma")
    d.line([*P(0, 25 + ad), *P(W, 25 + ad)], fill=GRAY, width=1)
    d.text(P(aw / 2, 25 + ad + 15), "間隔 30", font=F(18), fill=GRAY, anchor="mm")
    d.rectangle([ox, oy + D * S + 50, ox + 50 * S * 2 + W * S, oy + D * S + 110], fill=vcolor[1], outline=vcolor[0], width=2)
    d.text((ox + 15, oy + D * S + 62), verdict, font=F(24, True), fill=vcolor[0])
    for i, t in enumerate(notes):
        d.text((ox, oy + D * S + 130 + i * 32), t, font=F(20), fill=DARK)
    return dr, W - px0 - pw

a4, p4, a5, p5 = size("mono-layout-v04d"), size("psu-layout-v04"), size("mono-layout-v05d"), size("psu-layout-v05")
d.text((50, 30), "同一個機殼 BZ4312A2（內 330 寬 × 297 深 × 112 高，俯視等比例）：三板架構不變，V0.4 → V0.5 只改兩塊板的形狀", font=F(34, True), fill=DARK)
dr4, wr4 = panel(50, 150, f"左：V0.4 三板（放大板 {a4[0]}×{a4[1]}、電源板 {p4[0]}×{p4[1]}）",
      amp=(a4[0], a4[1]), psu=(p4[0], p4[1], ["四顆 Ø35×50 電容 2×2", "AC 端子區在左、輸出端子區在右"]), ctrl=(120, 105),
      notes=[f"寬：{a4[1]} + {W - 2 * a4[1]} + {a4[1]} = {W}，放大板兩邊貼牆剛好。",
             f"深：25 + {a4[0]} + 30 + 120 = {25 + a4[0] + 150}，前面只剩 {D - (25 + a4[0] + 150)} mm。",
             f"放大板 {a4[0]} 長是為了讓 EGW 47µF 躺著（腳距 50）。",
             f"電源板 {p4[0]} 寬是 AC 區與輸出區各佔一側夾著電容。"],
      verdict="塞得下，但深度只剩 7 mm、前排寬只剩 20＋10 mm，沒有走線與手指的空間。", vcolor=(RED, "#FBEDE9"))
dr5, wr5 = panel(1200, 150, f"右：V0.5 三板（放大板 {a5[0]}×{a5[1]}、電源板 {p5[0]}×{p5[1]}）",
      amp=(a5[0], a5[1]), psu=(p5[0], p5[1], ["電容 2×2 不變", "AC 區搬到上緣、輸出區搬到下緣", "snubber 預留位貼左右邊"]), ctrl=(120, 105),
      notes=[f"放大板：EGW 47µF 改站立，{a4[0]} → {a5[0]}，貼牆那邊短 {a4[0] - a5[0]}。",
             f"電源板：{p4[0]}×{p4[1]} → {p5[0]}×{p5[1]}，前排寬多出 {p4[0] - p5[0]}、深多 {p5[1] - p4[1]}。",
             f"深：25 + {a5[0]} + 30 + {max(120, p5[1])} = {25 + a5[0] + 30 + max(120, p5[1])}，前面剩 {D - (25 + a5[0] + 30 + max(120, p5[1]))} mm。",
             "兩板 KiCad 10.0.6 DRC 0 違規、0 未連通；IC 位置未動（方案 B 等實量）。"],
      verdict=f"同一個殼，深度餘 {D - (25 + a5[0] + 30 + max(120, p5[1]))}、前排寬餘 20＋{W - (20 + 120 + 20 + p5[0])}。", vcolor=(GREEN, "#E9F3EE"))
d.text((50, 1510), "尺寸來源：內部尺寸為淘寶商品頁 2026-09-29；板尺寸讀自 pcb/mono-layout-v04d.json、psu-layout-v04.json、mono-layout-v05d.json、psu-layout-v05.json。控制板 120×105 為預留值。tools/draw_chassis_fit_v05.py 產生。", font=F(18), fill=GRAY)
out = R / "docs/diagrams/chassis_bz4312a2_v05_fit.png"
img.save(out); print(out, "depth spare", dr4, "->", dr5, "front width spare", wr4, "->", wr5)
