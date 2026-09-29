# -*- coding: utf-8 -*-
"""BZ4312A2 俯視配置 A：左＝V0.5 三板、右＝V0.5.2 兩塊合板。板尺寸讀 pcb/*.json。單位 mm，x 0..330、y 0..297。
輸出 docs/diagrams/chassis_bz4312a2_v052_fit.png。需要 Pillow 與微軟正黑體。"""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
R = Path(__file__).resolve().parents[1]
F = lambda s, b=False: ImageFont.truetype("C:/Windows/Fonts/msjhbd.ttc" if b else "C:/Windows/Fonts/msjh.ttc", s)
W, D, S = 330, 297, 2.5
img = Image.new("RGB", (2300, 1560), "white"); d = ImageDraw.Draw(img)
DARK, BLUE, RED, GREEN, GRAY, AMBER = "#1F242B", "#1F5C7A", "#B33A28", "#2E6B4F", "#6B7480", "#B5730D"
size = lambda name: json.loads((R / "pcb" / f"{name}.json").read_text(encoding="utf-8"))["size"]

def frame(ox, oy, title):
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
    return P

def amp_boards(P, ad, aw, tag):
    for x0, name in ((0, "放大板 L"), (W - aw, "放大板 R")):
        d.rectangle([*P(x0, 25), *P(x0 + aw, 25 + ad)], fill="#E9F3EE", outline=GREEN, width=3)
        ic_x = x0 if x0 == 0 else W - 2
        d.rectangle([*P(ic_x, 45), *P(ic_x + 2, 65)], fill=DARK)
        d.text(P(x0 + 5, 30), name + tag, font=F(22, True), fill=GREEN)
        d.text(P(x0 + 5, 56), f"{aw}×{ad}", font=F(20), fill=GREEN)

def gap(P, x0, y0, x1, y1, text):
    d.rectangle([*P(x0, y0), *P(x1, y1)], fill="#FFF3D6", outline=AMBER, width=1)
    d.text(P((x0 + x1) / 2, (y0 + y1) / 2), text, font=F(18, True), fill=AMBER, anchor="mm")

def transformer(P, x, y):
    d.ellipse([*P(x - 60, y), *P(x + 60, y + 120)], fill="#E7EFF4", outline=BLUE, width=3)
    d.ellipse([*P(x - 20, y + 40), *P(x + 20, y + 80)], fill="white", outline=BLUE, width=2)
    d.text(P(x, y + 100), "變壓器 Ø120", font=F(22, True), fill=BLUE, anchor="ma")

def notes(ox, oy, verdict, vcolor, lines):
    d.rectangle([ox, oy + D * S + 50, ox + 50 * S * 2 + W * S, oy + D * S + 110], fill=vcolor[1], outline=vcolor[0], width=2)
    d.text((ox + 15, oy + D * S + 62), verdict, font=F(24, True), fill=vcolor[0])
    for i, t in enumerate(lines):
        d.text((ox, oy + D * S + 130 + i * 32), t, font=F(20), fill=DARK)

a5, p5, a52 = size("mono-layout-v05d"), size("psu-layout-v05"), size("mono-layout-v052")
d.text((50, 30), "同一個機殼 BZ4312A2（內 330 寬 × 297 深 × 112 高，俯視等比例）：V0.5 三板 vs V0.5.2 兩塊合板", font=F(34, True), fill=DARK)

# ---- left: V0.5 ----
P = frame(50, 150, f"左：V0.5 三板（放大板 {a5[0]}×{a5[1]}、電源板 {p5[0]}×{p5[1]}）")
ad, aw = a5; amp_boards(P, ad, aw, "")
cw, cd = 120, 105; cx0 = (W - cw) / 2
d.rectangle([*P(cx0, 30), *P(cx0 + cw, 30 + cd)], fill="#F3F5F7", outline=DARK, width=3)
d.text(P(cx0 + 5, 35), "控制板預留", font=F(22, True), fill=DARK); d.text(P(cx0 + 5, 61), f"{cw}×{cd}（尺寸未定）", font=F(18), fill=GRAY)
row_y = 25 + ad + 30; tx = 80; transformer(P, tx, row_y)
px0 = tx + 80; pw, pd = p5
d.rectangle([*P(px0, row_y), *P(px0 + pw, row_y + pd)], fill="#FBEDE9", outline=RED, width=3)
d.text(P(px0 + 5, row_y + 5), f"電源板 {pw}×{pd}", font=F(22, True), fill=RED)
d.text(P(px0 + 5, row_y + 32), "橋堆 ×2 鎖機殼在旁", font=F(18), fill=GRAY)
gap(P, px0 + pw, row_y, W, row_y + pd, f"前排寬餘 {W - px0 - pw}")
rd = max(120, pd); gap(P, 0, row_y + rd, W, D, f"深度餘裕 {D - row_y - rd}")
d.line([*P(0, 25 + ad), *P(W, 25 + ad)], fill=GRAY, width=1); d.text(P(aw / 2, 25 + ad + 15), "間隔 30", font=F(18), fill=GRAY, anchor="mm")
notes(50, 150, f"現行。深度餘 {D - row_y - rd}、前排寬餘 {W - px0 - pw}；控制板在兩片放大板之間。", (GREEN, "#E9F3EE"),
      [f"寬：{aw} + {W - 2 * aw} + {aw} = {W}。", f"深：25 + {ad} + 30 + {rd} = {25 + ad + 30 + rd}。",
       "電源板→放大板每聲道 3 條 DC 線約 20–30 cm；橋堆→電源板 4 條 Faston。", "一個 GND 匯流點在電源板，兩聲道共用。"])

# ---- right: V0.5.2 ----
P = frame(1200, 150, f"右：V0.5.2 兩塊合板（每塊 {a52[0]}×{a52[1]}，放大＋該聲道濾波）")
ad, aw = a52; amp_boards(P, ad, aw, "＋濾波")
for x0 in (0, W - aw):
    d.line([*P(x0, 25 + 92), *P(x0 + aw, 25 + 92)], fill=GREEN, width=1)
    d.text(P(x0 + aw / 2, 25 + 92 + 20), "2×10,000µF＋DC 端子", font=F(16), fill=GRAY, anchor="mm")
gap(P, aw, 25, W - aw, 25 + ad, f"中間 {W - 2 * aw}")
for i in range(2):
    bx = (W - 29) / 2; by = 32 + i * 42
    d.rectangle([*P(bx, by), *P(bx + 29, by + 29)], fill="#D9DEE3", outline=DARK, width=2)
    d.text(P(bx + 14.5, by + 14.5), f"BR{i+1}", font=F(16, True), fill=DARK, anchor="mm")
d.text(P(W / 2, 98), "橋堆 ×2 鎖機殼底", font=F(14), fill=GRAY, anchor="ma")
d.text(P(W / 2, 105), "兩板 DC 端子正對它", font=F(14), fill=GRAY, anchor="ma")
row_y = 25 + ad + 30; tx = 80; transformer(P, tx, row_y)
cx0 = tx + 80
d.rectangle([*P(cx0, row_y), *P(cx0 + cw, row_y + cd)], fill="#F3F5F7", outline=DARK, width=3)
d.text(P(cx0 + 5, row_y + 5), "控制板", font=F(22, True), fill=DARK); d.text(P(cx0 + 5, row_y + 31), f"{cw}×{cd}（尺寸未定）", font=F(18), fill=GRAY)
gap(P, cx0 + cw, row_y, W, row_y + 120, f"前排寬餘 {W - cx0 - cw}")
gap(P, 0, row_y + 120, W, D, f"深度餘裕 {D - row_y - 120}")
d.line([*P(0, 25 + ad), *P(W, 25 + ad)], fill=GRAY, width=1); d.text(P(aw / 2, 25 + ad + 15), "間隔 30", font=F(18), fill=GRAY, anchor="mm")
notes(1200, 150, f"塞得下且更鬆：深度餘 {D - row_y - 120}、前排寬餘 {W - cx0 - cw}；控制板改到前排、橋堆進後排中間。", (BLUE, "#E7EFF4"),
      [f"寬：{aw} + {W - 2 * aw} + {aw} = {W}；後排中間 {W - 2 * aw} 放兩顆橋堆（29 方），控制板搬到前排變壓器旁。", f"深：25 + {ad} + 30 + 120 = {25 + ad + 30 + 120}。",
       "每板 4 條 DC 線自橋堆來（BR1+ BR1- BR2+ BR2-），約 5–10 cm；電源到 IC 只剩板上 5 cm 銅箔。",
       "每板一個 GND 匯流點，兩板的地要在機殼再匯一次；AC 保險絲離板（機殼保險絲座）。",
       "共用整流、各板濾波，不是真正雙單聲道（變壓器只有一組 2×22 Vac）。"])
d.text((50, 1510), "尺寸來源：內部尺寸為淘寶商品頁 2026-09-29；板尺寸讀自 pcb/mono-layout-v05d.json、psu-layout-v05.json、mono-layout-v052.json。控制板 120×105 為預留值。tools/draw_chassis_fit_v052.py 產生。", font=F(18), fill=GRAY)
out = R / "docs/diagrams/chassis_bz4312a2_v052_fit.png"; img.save(out); print(out)
