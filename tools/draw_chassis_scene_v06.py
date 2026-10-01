# -*- coding: utf-8 -*-
"""弘宙 102 機箱內部 3D 配置圖（V0.6）：兩側內置散熱器、後排放大板 L／電源板／放大板 R、前排變壓器、
左前控制板 CTRL、右前市電板 MAINS。CTRL／MAINS 用 kicad-cli 匯出的 STL（含 KiCad 函式庫 3D 模型），
沒有模型的零件（繼電器、電解、端子、NTC、電阻）照板檔 JSON 補方塊／圓柱；放大板與電源板是 V0.6 目標外形的示意
（板子尚未畫），大件零件位置照 V0.5 配置縮放。單位 mm：x 向右（寬 393）、y 由後到前（深 273）、z 向上（高 100）。
用 pyvista（VTK）離屏算圖；另輸出 glTF 給 Blender。需要 `py -3.13`（pyvista、Pillow）。

用法：先 `kicad-cli pcb export stl --subst-models --include-pads -o <dir>/ctrl-layout-v06.stl pcb/ctrl-layout-v06.kicad_pcb`
（mains 同），再 `py -3.13 -X utf8 tools/draw_chassis_scene_v06.py <dir>`；輸出 docs/diagrams/chassis_102_v06_3d.png。
"""
from pathlib import Path
import json, math, sys
import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw, ImageFont
pv.OFF_SCREEN = True
R = Path(__file__).resolve().parents[1]
STL = Path(sys.argv[1]) if len(sys.argv) > 1 else R / 'pcb/preview/3d'
OUT = R / 'docs/diagrams'; OUT.mkdir(exist_ok=True)
W, D, H = 393, 273, 100                 # 內尺寸（估）
GAP, FIN, BASE, ICZ = 10, 30, 5, 10     # 側牆→空氣通道→鰭片→底板→IC
HS = GAP + FIN + BASE + ICZ             # 55
HSL, HS_Y0 = 150, 10
REAR = 15
AMP_W, AMP_D = 80, 90                   # 放大板 V0.6：離牆 80（板 y）× 沿牆 90（板 x）
PSU_W, PSU_D = 92, 120
Z0 = 8                                  # 銅柱高：板底離殼底
PCB_T = 1.6
COL = dict(pcb='#1f6b3a', pcb_edge='#2e8b57', cap='#1b2a4a', cap_blue='#2d4f8a', ic='#101010', hs='#3a3f45', fin='#4b5158',
           chassis='#b8bec6', floor='#8d949c', tr='#5a6068', tr_tape='#2a4d8f', disc='#9aa0a6', relay='#1a1a1a', term='#1d7a9a',
           ntc='#2f2f2f', res='#c9b58a', film='#b23a2a', film_y='#d8c25a', front='#c8ccd2')

pl = pv.Plotter(off_screen=True, window_size=(2200, 1500))
pl.set_background('#eef1f4')


# 2D 配置圖的座標（x 向右、y 向前、俯視後面板在上）是從正面看的左右；VTK 右手座標要把 x 鏡射才會一致。
MX = lambda x: W - x


def box(x0, y0, z0, x1, y1, z1, color, opacity=1.0, edges=False):
    x0, x1 = MX(x1), MX(x0)
    m = pv.Box(bounds=(x0, x1, y0, y1, z0, z1))
    pl.add_mesh(m, color=color, opacity=opacity, show_edges=edges, edge_color='#222222', smooth_shading=False)
    return m


def cyl(cx, cy, z0, r, h, color, opacity=1.0, axis=(0, 0, 1)):
    cx = MX(cx)
    m = pv.Cylinder(center=(cx, cy, z0 + h / 2) if axis == (0, 0, 1) else (cx, cy, z0), direction=axis, radius=r, height=h, resolution=64)
    pl.add_mesh(m, color=color, opacity=opacity, smooth_shading=True)
    return m


# ---------- 機殼：底板、三面牆（半透明）、前面板 ----------
box(-2, -2, -3, W + 2, D + 2, 0, COL['floor'])
for (x0, y0, x1, y1) in ((-2, -2, 0, D), (W, -2, W + 2, D), (-2, -2, W + 2, 0)):
    box(x0, y0, 0, x1, y1, H, COL['chassis'], opacity=0.25)
box(-2, D, 0, W + 2, D + 10, H + 15, COL['front'], opacity=0.12)           # 鋁擠前面板（示意，幾乎透明以免擋住內部）
# 後面板接頭（示意）：RCA ×2、喇叭端子 ×4、AC 尾插
for x in (95, 298):
    cyl(x, -1, 70, 4.5, 8, '#c0392b', axis=(0, 1, 0))
for x in (70, 85, 308, 323):
    cyl(x, -1, 40, 4, 10, '#333333', axis=(0, 1, 0))
box(180, -2, 30, 213, 2, 55, '#222222')

# ---------- 散熱器 150×90×30：鰭片朝牆、底板朝板 ----------
for side in (0, 1):
    xw = 0 if side == 0 else W
    sgn = 1 if side == 0 else -1
    f0 = xw + sgn * GAP; f1 = f0 + sgn * FIN; b1 = f1 + sgn * BASE
    box(min(f1, b1), HS_Y0, 3, max(f1, b1), HS_Y0 + HSL, 3 + 90, COL['hs'])            # 底板 5 厚
    for k in range(10):
        yy = HS_Y0 + 2 + k * (HSL - 4 - 1.5) / 9
        box(min(f0, f1), yy, 3, max(f0, f1), yy + 1.5, 3 + 90, COL['fin'])          # 10 片鰭
# ---------- 放大板 ×2 與電源板：V0.6 真板（kicad-cli STL ＋ JSON 補零件），見下方 place_board ----------
# ---------- 變壓器 Ø120×50 ＋ 壓碟 ----------
tx, ty = W / 2, REAR + PSU_D + 5 + 60
cyl(tx, ty, 0, 60, 50, COL['tr'])
cyl(tx, ty, 10, 60.5, 30, COL['tr_tape'])
cyl(tx, ty, 50, 50, 3, COL['disc'])
cyl(tx, ty, 53, 4, 14, '#777777')

# ---------- CTRL／MAINS：KiCad STL ＋ 補零件 ----------
HEIGHT = {'Relay_G2RL-1-E': 15.7, 'Terminal2_P5.08': 12, 'Terminal3_P5.08': 12, 'Header2_P2.54': 6, 'CP_D12.5_P5': 25, 'CP_D5_P2': 11,
          'CP_D6.3_P2.5': 11, 'CP_D35_P10': 50, 'BP_Axial_Vert_D20_P15': 42, 'Film_P5': 6.5, 'Film_P15': 15, 'R_P7.5': 2.5, 'R_2W_P20': 5,
          'AirCoil_P20': 14, 'Fuse5x20_P25': 10, 'GBJ_Upright_P10_7.5_7.5': 20, 'NTC_D22_P10': 22}
COLOR = {'Relay_G2RL-1-E': COL['relay'], 'Terminal2_P5.08': COL['term'], 'Terminal3_P5.08': COL['term'], 'Header2_P2.54': COL['ic'],
         'CP_D12.5_P5': COL['cap'], 'CP_D5_P2': COL['cap'], 'CP_D6.3_P2.5': COL['cap'], 'CP_D35_P10': COL['cap'], 'BP_Axial_Vert_D20_P15': COL['cap_blue'],
         'Film_P5': COL['film'], 'Film_P15': COL['film_y'], 'R_P7.5': COL['res'], 'R_2W_P20': COL['res'], 'AirCoil_P20': '#8a5a2b',
         'Fuse5x20_P25': '#555555', 'GBJ_Upright_P10_7.5_7.5': COL['ic'], 'NTC_D22_P10': COL['ntc']}


def place_board(name, origin, rot):
    """Put a KiCad board into the chassis. Board coords (bx, by) -> chassis (x, y) = origin + R(rot)*(bx, by), rot in degrees,
    a proper rotation (same handedness), so every board is the real, component-side-up PCB. kicad-cli STL has
    X = bx, Y = -by, board top at z = 0. The scene then mirrors x (MX) like every other object."""
    m = pv.read(str(STL / f'{name}.stl'))
    m = m.transform(np.array([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], float), inplace=False)   # Y = +by
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    T = np.array([[c, -sn, 0, origin[0]], [sn, c, 0, origin[1]], [0, 0, 1, Z0 + PCB_T], [0, 0, 0, 1]], float)
    M = np.array([[-1, 0, 0, W], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], float)          # scene x-mirror (MX)
    m = m.transform(M @ T, inplace=False)
    m = m.compute_normals(auto_orient_normals=True, inplace=False)
    pl.add_mesh(m, color=COL['pcb_edge'], smooth_shading=True)
    data = json.loads((R / 'pcb' / f'{name}.json').read_text(encoding='utf-8'))
    def to_chassis(bx, by): return (origin[0] + c * bx - sn * by, origin[1] + sn * bx + c * by)
    for part in data['parts']:
        fp = part['footprint']
        if fp not in HEIGHT: continue
        bx0, by0, bx1, by1 = part['body']; a = math.radians(part['angle'])
        pts = [to_chassis(part['x'] + x * math.cos(a) + y * math.sin(a), part['y'] - x * math.sin(a) + y * math.cos(a))
               for x, y in ((bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1))]
        xs = [q[0] for q in pts]; ys = [q[1] for q in pts]; zt = Z0 + PCB_T
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        if fp.startswith('CP_') or fp.startswith('BP_'):
            cyl(cx, cy, zt, (max(xs) - min(xs)) / 2, HEIGHT[fp], COLOR[fp])
        elif fp == 'NTC_D22_P10':
            box(cx - 11, cy - 2.5, zt + 2, cx + 11, cy + 2.5, zt + 24, COLOR[fp])
        elif fp == 'GBJ_Upright_P10_7.5_7.5':
            box(min(xs), min(ys), zt, max(xs), max(ys), zt + HEIGHT[fp], COLOR[fp])
            # 10 mm heatsink on the metal-back side (+by for rotation 180 on the PSU)
            hx0, hy0 = to_chassis(part['x'] - 27.5, part['y'] + 2); hx1, hy1 = to_chassis(part['x'] + 2.5, part['y'] + 12)
            box(min(hx0, hx1), min(hy0, hy1), zt, max(hx0, hx1), max(hy0, hy1), zt + 30, COL['hs'])
        else:
            box(min(xs), min(ys), zt, max(xs), max(ys), zt + HEIGHT[fp], COLOR[fp])


# amplifier L: IC edge (by = 0) against the left heatsink base, board x along the wall with the RCA end (bx = 85) at the rear
place_board('mono-layout-v06', (HS, REAR + AMP_D), -90)            # (bx,by) -> (HS + by, REAR + AMP_D - bx)
# amplifier R: the SAME board turned so its IC edge faces the right heatsink; its RCA end therefore lands at the front
place_board('mono-layout-v06', (W - HS, REAR), 90)                 # (bx,by) -> (W - HS - by, REAR + bx)
# PSU: DC outputs (by = 0) toward the rear / amplifier boards, AC side toward the transformer
place_board('psu-layout-v06', ((W - PSU_W) / 2, REAR), 0)
CTRL_X0, CTRL_Y0 = HS, REAR + PSU_D + 5
MAINS_X0, MAINS_Y0 = W - HS - 70, REAR + PSU_D + 5
place_board('ctrl-layout-v06', (CTRL_X0, CTRL_Y0), 0)
place_board('mains-layout-v06', (MAINS_X0, MAINS_Y0), 0)

# ---------- 標籤（ASCII，VTK 字型）----------
labels = {'AMP L (90x80)': (HS + 40, REAR + 45, 50), 'AMP R (90x80)': (W - HS - 40, REAR + 45, 50), 'PSU (92x120)': (W / 2, REAR + 60, 75),
          'T1 toroid D120': (tx, ty, 75), 'CTRL (70x120)': (CTRL_X0 + 35, CTRL_Y0 + 60, 40), 'MAINS (70x100)': (MAINS_X0 + 35, MAINS_Y0 + 50, 40),
          'HEATSINK 150x90x30': (HS / 2, HS_Y0 + 75, 100), 'HEATSINK 150x90x30 ': (W - HS / 2, HS_Y0 + 75, 100)}
pts = pv.PolyData(np.array([(MX(x), y, z) for x, y, z in labels.values()], float))
pl.add_point_labels(pts, list(labels.keys()), font_size=22, text_color='#111111', point_size=1, shape_opacity=0.75, shape_color='white', always_visible=True)

# ---------- 兩個視角 ----------
pl.camera_position = [(W + 360, D + 540, 520), (W / 2, D / 2, 10), (0, 0, 1)]   # 從正面左前上方看進去
pl.reset_camera(); pl.camera.zoom(1.12)
iso = pl.screenshot(return_img=True)
pl.camera_position = [(W / 2, D / 2, 1200), (W / 2, D / 2, 0), (0, -1, 0)]   # 俯視：後面板在上
pl.reset_camera(); pl.camera.zoom(2.1)
top = pl.screenshot(return_img=True)
try:
    pl.export_gltf(str(OUT / 'chassis_102_v06_3d.gltf'))
except Exception as e:                                                       # glTF export is a bonus for Blender
    print('gltf export skipped:', e)
pl.close()

# ---------- 拼圖＋中文標題（PIL） ----------
F = lambda s, b=False: ImageFont.truetype('C:/Windows/Fonts/msjhbd.ttc' if b else 'C:/Windows/Fonts/msjh.ttc', s)
iso_im = Image.fromarray(iso); top_im = Image.fromarray(top)
top_im = top_im.resize((int(top_im.width * 0.46), int(top_im.height * 0.46)))
canvas = Image.new('RGB', (iso_im.width, iso_im.height + 260), 'white')
canvas.paste(iso_im, (0, 170)); canvas.paste(top_im, (iso_im.width - top_im.width - 30, 190))
d = ImageDraw.Draw(canvas)
d.text((40, 30), f'弘宙 102 機箱內部 3D 配置（V0.6 五板）：內尺寸估 {W}×{D}×{H}，散熱器內置兩側，變壓器前排', font=F(40, True), fill='#1F242B')
d.text((40, 90), '五塊板都是 V0.6 KiCad 板檔匯出的 3D（函式庫模型：IC、繼電器、二極體、TO 封裝；電解、端子、NTC、GBJ 等暫定封裝以方塊／圓柱補）。右聲道放大板與左聲道同一塊板轉向，RCA 端因此在前。', font=F(20), fill='#6B7480')
d.text((40, 122), '上蓋拿掉、側牆半透明。右上小圖＝俯視。所有尺寸為估算／目標值，無任何實測。tools/draw_chassis_scene_v06.py（pyvista）產生；同名 .gltf 可用 Blender 開。', font=F(20), fill='#6B7480')
canvas.save(OUT / 'chassis_102_v06_3d.png'); print(OUT / 'chassis_102_v06_3d.png')
