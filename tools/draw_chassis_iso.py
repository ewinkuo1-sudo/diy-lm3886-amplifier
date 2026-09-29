# -*- coding: utf-8 -*-
"""BZ4312A2 內部空間等角立體示意（配置 A）。PIL 畫家演算法，座標 mm：x 左→右 0..330，y 後→前 0..297，z 高。"""
import math
from PIL import Image, ImageDraw, ImageFont
F = lambda s: ImageFont.truetype("C:/Windows/Fonts/msjhbd.ttc" if s >= 26 else "C:/Windows/Fonts/msjh.ttc", s)
W, D, H = 330, 297, 112
S = 2.35
C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))
OX, OY = 800, 330   # 畫布上 (0,0,0) 的位置

def P(x, y, z):
    return (OX + (x - y) * C30 * S, OY + (x + y) * S30 * S - z * S)

img = Image.new("RGB", (2300, 1500), "white"); d = ImageDraw.Draw(img)
DARK, BLUE, RED, GREEN, GRAY = "#1F242B", "#1F5C7A", "#B33A28", "#2E6B4F", "#6B7480"

def shade(hexc, k):
    r, g, b = int(hexc[1:3], 16), int(hexc[3:5], 16), int(hexc[5:7], 16)
    return "#%02x%02x%02x" % (int(r * k), int(g * k), int(b * k))

def box(x, y, z, w, dd, h, color, edge=DARK, lw=2, faces="all"):
    """可見面：頂 (z+h)、右 (x+w)、前 (y+dd)。"""
    X0, X1, Y0, Y1, Z0, Z1 = x, x + w, y, y + dd, z, z + h
    top = [P(X0, Y0, Z1), P(X1, Y0, Z1), P(X1, Y1, Z1), P(X0, Y1, Z1)]
    right = [P(X1, Y0, Z0), P(X1, Y1, Z0), P(X1, Y1, Z1), P(X1, Y0, Z1)]
    front = [P(X0, Y1, Z0), P(X1, Y1, Z0), P(X1, Y1, Z1), P(X0, Y1, Z1)]
    if faces == "wire":
        for poly in (top, right, front, [P(X0, Y0, Z0), P(X1, Y0, Z0), P(X1, Y1, Z0), P(X0, Y1, Z0)]):
            d.polygon(poly, outline=edge)
        return
    d.polygon(right, fill=shade(color, 0.72), outline=edge)
    d.polygon(front, fill=shade(color, 0.88), outline=edge)
    d.polygon(top, fill=color, outline=edge)

def cyl(cx, cy, z, r, h, color, edge=DARK, n=48, hole=0):
    ang = [math.radians(-45 + i * 180 / n) for i in range(n + 1)]   # 可見半圓（朝向觀看者 +x,+y）
    bot = [P(cx + r * math.cos(a), cy + r * math.sin(a), z) for a in ang]
    top = [P(cx + r * math.cos(a), cy + r * math.sin(a), z + h) for a in ang]
    d.polygon(bot + top[::-1], fill=shade(color, 0.8), outline=edge)
    full = [P(cx + r * math.cos(math.radians(t)), cy + r * math.sin(math.radians(t)), z + h) for t in range(0, 361, 6)]
    d.polygon(full, fill=color, outline=edge)
    if hole:
        hp = [P(cx + hole * math.cos(math.radians(t)), cy + hole * math.sin(math.radians(t)), z + h) for t in range(0, 361, 8)]
        d.polygon(hp, fill="white", outline=edge)

def label(x, y, z, text, color=DARK, size=20, dx=0, dy=0, anchor="la"):
    px, py = P(x, y, z); d.text((px + dx, py + dy), text, font=F(size), fill=color, anchor=anchor)

# ---------- 遠處：底板、後板、左側散熱器 ----------
box(0, 0, -3, W, D, 3, "#E3E6EA")                                   # 底板
box(0, -3, 0, W, 3, H, "#D5D9DE")                                    # 後板（薄）
box(-50, 0, 0, 50, D, H, "#C4C9CF")                                  # 左散熱器本體
for k in range(8):                                                   # 左側鰭片（朝外）
    box(-50 - 12, 10 + k * 36, 0, 12, 4, H, "#B3B9C0", lw=1)

# ---------- 後面板端子（內凸帶 25） ----------
for x in (35, 295):
    box(x - 8, 0, 40, 16, 25, 16, "#C94F3D")                          # 喇叭端子 ×2 側
for x in (85, 245):
    box(x - 10, 0, 50, 20, 25, 20, "#7C8794")                         # XLR
for x in (120, 210):
    box(x - 6, 0, 52, 12, 25, 12, "#7C8794")                          # RCA
box(150, 0, 15, 30, 30, 30, "#2B3038")                               # 電源尾插（帶保險絲）
box(163, 0, 62, 4, 20, 10, "#7C8794")                                # 切換開關

# ---------- 內部物件（依 x+y 由遠到近排序） ----------
objs = []
def add(key, fn): objs.append((key, fn))

# 放大板 L（貼左牆）：板 90×115 @ y 25..140
def amp(x0, wall_left):
    def draw():
        box(x0, 25, 8, 90, 115, 1.6, "#3E8A6A")
        box(x0 + 30, 40, 9.6, 12, 12, 16, "#4E7F6A"); box(x0 + 30, 60, 9.6, 12, 12, 16, "#4E7F6A")   # 470µF
        box(x0 + 50, 45, 9.6, 21, 20, 20, "#6C8F7E")                                             # C2 臥式
        box(x0 + 58, 95, 9.6, 20, 14, 14, "#8A9C93")                                             # 電感
        box(x0 + 70, 120, 9.6, 12, 10, 12, "#3E8A6A")                                            # 端子
        if wall_left:
            box(0, 65, 18, 3, 30, 30, "#A5ADB5"); box(0, 65, 18, 22, 30, 3, "#A5ADB5")           # L 型鋁角
            box(3, 70, 21, 20, 20, 4.5, "#2B2B2B")                                               # IC 躺平
        else:
            box(W - 3, 65, 18, 3, 30, 30, "#A5ADB5"); box(W - 22, 65, 18, 22, 30, 3, "#A5ADB5")
            box(W - 23, 70, 21, 20, 20, 4.5, "#2B2B2B")
    return draw
add((0 + 25), amp(0, True))
add((240 + 25), amp(240, False))

# 控制板預留 120×105 @ x105 y30
def ctrl():
    box(105, 30, 8, 120, 105, 1.6, "#AEB6C0")
    for x in (120, 150, 180): box(x, 60, 9.6, 20, 15, 15, "#C7CDD4")
add(105 + 30, ctrl)

# 變壓器 Ø120×50 @ (80,230)
def xfmr():
    cyl(80, 230, 3, 60, 50, "#A9C8DA", edge=BLUE, hole=20)
    box(76, 226, 53, 8, 8, 6, "#7C8794")
add(20 + 170, xfmr)

# 電源板 160×120 @ x160 y170，四顆 Ø35×50
def psu():
    box(160, 170, 8, 160, 120, 1.6, "#C2574A")
    box(165, 180, 9.6, 12, 30, 10, "#7C8794"); box(165, 215, 9.6, 12, 30, 10, "#7C8794")     # 保險絲座
    box(300, 185, 9.6, 8, 20, 12, "#3E8A6A"); box(300, 245, 9.6, 8, 20, 12, "#3E8A6A")     # 輸出端子
    box(170, 260, 9.6, 12, 20, 12, "#3E8A6A")                                              # AC 入線端子
    for cx, cy in ((205, 195), (205, 245), (255, 195), (255, 245)):
        cyl(cx, cy, 9.6, 17.5, 50, "#454A52", edge=DARK)
add(160 + 170, psu)

for _, fn in sorted(objs, key=lambda t: t[0]): fn()

# ---------- 近處：右側散熱器、前板（線框）、上蓋輪廓 ----------
box(W, 0, 0, 50, D, H, "#000000", edge="#9AA3AB", faces="wire")
for k in range(8): box(W + 50, 10 + k * 36, 0, 12, 4, H, "#000000", edge="#C4C9CF", faces="wire")
box(0, D, 0, W, 10, H, "#000000", edge="#9AA3AB", faces="wire")
lid = [P(0, 0, H), P(W, 0, H), P(W, D, H), P(0, D, H)]
for i in range(4):
    a, b = lid[i], lid[(i + 1) % 4]
    n = 24
    for k in range(0, n, 2):
        d.line((a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n,
                a[0] + (b[0] - a[0]) * (k + 1) / n, a[1] + (b[1] - a[1]) * (k + 1) / n), fill="#9AA3AB", width=2)

# ---------- 標註 ----------
d.text((40, 20), "BZ4312A2 內部空間等角示意（配置 A，上蓋掀開；內部 330 寬 × 297 深 × 112 高 mm）", font=F(34), fill=DARK)
d.text((40, 70), "右側散熱器與前面板以線框表示，方便看進去；元件外形與高度為假設值，不是原廠模型。", font=F(20), fill=GRAY)
label(W / 2, D + 10, -3, "寬 330", DARK, 22, dy=40, anchor="ma")
label(W + 55, D / 2, -3, "深 297", DARK, 22, dx=60, anchor="la")
label(W + 55, D + 10, H / 2, "高 112", DARK, 22, dx=70, anchor="la")
def tag(x, y, ztop, text, color, size=19, up=55, dx=0):
    a = P(x, y, ztop); b = P(x, y, ztop + up)
    d.line((a[0], a[1], b[0], b[1]), fill=color, width=2)
    d.ellipse((a[0]-4, a[1]-4, a[0]+4, a[1]+4), fill=color)
    d.text((b[0] + dx, b[1] - 6), text, font=F(size), fill=color, anchor="md")
tag(20, 90, 26, "放大板 L：IC 躺平＋L 型鋁角貼左牆", GREEN, up=70)
tag(310, 90, 26, "放大板 R（同左）", GREEN, up=45, dx=40)
tag(165, 80, 25, "控制板預留 120×105", "#3B4452", up=45)
tag(80, 230, 53, "變壓器 Ø120×50", BLUE, up=60)
tag(255, 245, 60, "電源板 160×120，四顆 Ø35×50 電容", RED, up=45, dx=60)
tag(150, 15, 45, "電源尾插（帶保險絲）", "#2B3038", up=50)
tag(35, 12, 56, "喇叭端子", "#C94F3D", up=40)
tag(85, 12, 70, "XLR", "#5C6675", up=30); tag(120, 12, 64, "RCA", "#5C6675", up=30, dx=20)
tag(163, 10, 72, "切換開關", "#5C6675", up=32, dx=30)
label(-25, D / 2, H + 4, "散熱器側牆 300×118", GRAY, 17, anchor="md")
label(W + 40, D - 30, H + 4, "右散熱器（線框）", GRAY, 17, anchor="md", dx=90)
d.text((40, 1420), "高度：銅柱 8＋板 1.6；主電容頂約 60、變壓器頂約 58、IC 躺平頂約 26；上蓋在 112（虛線）。前面板只有電源鈕。", font=F(20), fill=DARK)
d.text((40, 1455), "俯視版：docs/diagrams/chassis_bz4312a2_layout.png ・ 元件位置同配置 A。", font=F(18), fill=GRAY)
img.save("chassis_bz4312a2_3d.png"); print("ok")
