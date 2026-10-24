# -*- coding: utf-8 -*-
"""3D 列印機殼第一版（mechanical/chassis-print-v01）的建置腳本：
1. 用 OpenSCAD 把 chassis_print_v01.scad 的每一件匯成 STL（mechanical/chassis-print-v01/stl/）
2. 用 pyvista 算圖：方案 A／B 對照、掀蓋等角、俯視配置、爆炸圖、後視（docs/diagrams/chassis_print_v01_*.png）
3. 算每件體積與列印耗材估計（mechanical/chassis-print-v01/parts.json）
用法：py -3.13 -X utf8 tools/chassis_print_v01.py [--no-export]
OpenSCAD 2021.01 在 Program Files（不在 PATH）；pyvista／Pillow 只在 Python 3.13。
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json, subprocess, sys
import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw, ImageFont

pv.OFF_SCREEN = True
R = Path(__file__).resolve().parents[1]
MECH = R / 'mechanical/chassis-print-v01'
SCAD = MECH / 'chassis_print_v01.scad'
STL = MECH / 'stl'; STL.mkdir(exist_ok=True)
OUT = R / 'docs/diagrams'; OUT.mkdir(exist_ok=True)
OPENSCAD = Path(r'C:\Program Files\OpenSCAD\openscad.com')
FONT = r'C:\Windows\Fonts\msjh.ttc'

W, D, H, T = 290, 280, 78, 4

# 零件：名稱 → (群組, 顏色)。群組：print＝列印件、alu＝鋁板、hs＝散熱片、int＝機內零件
PRINT = '#d9d4c8'; ALU = '#b4bac2'; HS = '#2b2f34'
PARTS = {
    'side_rear_R': ('print', PRINT), 'side_front_R': ('print', PRINT), 'side_rear_L': ('print', PRINT), 'side_front_L': ('print', PRINT),
    'rear_panel': ('print', PRINT), 'front_panel': ('print', PRINT), 'feet': ('print', '#8c8780'),
    'plate_bottom': ('alu', ALU), 'plate_top': ('alu', ALU),
    **{f'tile_bottom_{k}': ('tileA', PRINT if k % 2 == 0 else '#cfc9bb') for k in range(4)},
    **{f'tile_top_{k}': ('tileA', PRINT if k % 2 == 0 else '#cfc9bb') for k in range(4)},
    'heatsink_R': ('hs', HS), 'heatsink_L': ('hs', HS),
    'amp_R': ('int', '#1f6b3a'), 'amp_L': ('int', '#1f6b3a'), 'psu': ('int', '#1f6b3a'), 'ctrl': ('int', '#1f6b3a'), 'mains': ('int', '#1f6b3a'),
    'transformer': ('int', '#5a6068'), 'connectors': ('int', '#444444'),
}
PRINT_SINGLE = ['side_rear_R', 'side_front_R', 'rear_panel', 'front_panel', 'foot']   # 列印件清單用（左右對稱件只算一次再乘 2）


def export(name):
    out = STL / f'{name}.stl'
    cmd = [str(OPENSCAD), '-o', str(out), '--export-format', 'binstl', '-D', f'part="{name}"', str(SCAD)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not out.exists():
        raise SystemExit(f'OpenSCAD 匯出失敗 {name}:\n{r.stderr[-800:]}')
    return name


def export_all():
    names = list(PARTS) + ['foot']
    with ThreadPoolExecutor(max_workers=6) as ex:
        for n in ex.map(export, names):
            print('  stl', n)


def load(name):
    return pv.read(str(STL / f'{name}.stl'))


def scene(opt='B', lid=True, internals=True, explode=0.0, bg='#eef1f4', size=(1800, 1300)):
    """回傳 Plotter。explode>0 時各件沿自己的方向拉開 explode 倍距離。"""
    pl = pv.Plotter(off_screen=True, window_size=size)
    pl.set_background(bg)
    shift = {
        'plate_top': (0, 0, 70), 'tile_top_0': (0, 0, 70), 'tile_top_1': (0, 0, 70), 'tile_top_2': (0, 0, 70), 'tile_top_3': (0, 0, 70),
        'plate_bottom': (0, 0, -40), 'tile_bottom_0': (0, 0, -40), 'tile_bottom_1': (0, 0, -40), 'tile_bottom_2': (0, 0, -40), 'tile_bottom_3': (0, 0, -40),
        'feet': (0, 0, -70), 'front_panel': (0, 70, 0), 'rear_panel': (0, -70, 0),
        'side_rear_R': (-50, -25, 0), 'side_front_R': (-50, 25, 0), 'side_rear_L': (50, -25, 0), 'side_front_L': (50, 25, 0),
        'heatsink_R': (-130, 0, 0), 'heatsink_L': (130, 0, 0),
    }
    for name, (grp, col) in PARTS.items():
        if grp == 'alu' and opt != 'B': continue
        if grp == 'tileA' and opt != 'A': continue
        if grp == 'int' and not internals: continue
        if not lid and name in ('plate_top', 'tile_top_0', 'tile_top_1', 'tile_top_2', 'tile_top_3'): continue
        m = load(name)
        if explode and name in shift:
            m = m.translate(np.array(shift[name]) * explode, inplace=False)
        kw = dict(color=col, smooth_shading=False)
        if grp == 'alu': kw.update(pbr=True, metallic=0.6, roughness=0.45)
        if grp == 'hs': kw.update(pbr=True, metallic=0.3, roughness=0.7)
        pl.add_mesh(m, **kw)
    pl.enable_anti_aliasing('ssaa')
    return pl


def shot(pl, cam, fname, parallel=False):
    pl.camera_position = cam
    if parallel:
        pl.enable_parallel_projection()
    pl.camera.zoom(1.0)
    img = pl.screenshot(return_img=True)
    pl.close()
    im = Image.fromarray(img)
    im.save(OUT / fname)
    return im


def label(im, text, size=42, fill='#1d2320', bg=(238, 241, 244)):
    """在圖上方加一條標題帶（不壓到圖）；字太長就縮小到塞得下。"""
    while size > 20 and ImageFont.truetype(FONT, size).getlength(text) > im.width - 40:
        size -= 2
    band = int(size * 1.9)
    out = Image.new('RGB', (im.width, im.height + band), bg)
    out.paste(im, (0, band))
    ImageDraw.Draw(out).text((20, band * 0.25), text, font=ImageFont.truetype(FONT, size), fill=fill)
    return out


def crop_margin(im, pad=30, bg=(238, 241, 244)):
    arr = np.asarray(im.convert('RGB')).astype(int)
    mask = np.abs(arr - np.array(bg)).sum(axis=2) > 24
    ys, xs = np.where(mask)
    if len(xs) == 0: return im
    return im.crop((max(xs.min() - pad, 0), max(ys.min() - pad, 0), min(xs.max() + pad, im.width), min(ys.max() + pad, im.height)))


def hstack(ims, gap=40, bg=(238, 241, 244)):
    h = max(i.height for i in ims)
    w = sum(i.width for i in ims) + gap * (len(ims) - 1)
    out = Image.new('RGB', (w, h), bg)
    x = 0
    for i in ims:
        out.paste(i, (x, (h - i.height) // 2)); x += i.width + gap
    return out


def vstack(ims, gap=40, bg=(238, 241, 244)):
    w = max(i.width for i in ims)
    h = sum(i.height for i in ims) + gap * (len(ims) - 1)
    out = Image.new('RGB', (w, h), bg)
    y = 0
    for i in ims:
        out.paste(i, ((w - i.width) // 2, y)); y += i.height + gap
    return out


ISO = [(W + 420, D + 460, 360), (W / 2, D / 2 - 10, 20), (0, 0, 1)]        # 從左前上方看（從正面看 +x 是左）
ISO_BACK = [(-420, -430, 330), (W / 2, D / 2 + 10, 20), (0, 0, 1)]         # 從右後上方看
TOP = [(W / 2, D / 2, 900), (W / 2, D / 2, 0), (0, -1, 0)]                 # 俯視，後面板在上
REAR = [(W / 2, -700, 45), (W / 2, 0, 35), (0, 0, 1)]


def render():
    # 1. 方案 A／B 對照（閉合、從左前上方）
    a = crop_margin(shot(scene('A'), ISO, 'tmp_a.png'))
    b = crop_margin(shot(scene('B'), ISO, 'tmp_b.png'))
    a = label(a, 'A　全列印：上下蓋各分 4 塊列印（有接縫、要加肋）')
    b = label(b, 'B　混合：上下蓋用 2 mm 鋁板，只列印四周框（建議）')
    hstack([a, b]).save(OUT / 'chassis_print_v01_options.png')
    # 2. 掀蓋等角＋俯視配置
    lid = crop_margin(shot(scene('B', lid=False), ISO, 'tmp_lid.png'))
    lid = label(lid, '掀開上蓋：散熱片當側牆、IC 直接鎖在散熱片底板上')
    top = crop_margin(shot(scene('B', lid=False), TOP, 'tmp_top.png', parallel=True))
    d = ImageDraw.Draw(top)
    f = ImageFont.truetype(FONT, 30)
    # 俯視圖是平行投影，像素↔mm 比例由影像寬度推：影像涵蓋 x 由 -37（鰭片外）到 W+37
    sx = top.width / (W + 2 * (T + 29) + 60)
    def put(x, y, s, col='#ffffff'):
        px = top.width - (x + T + 29 + 30) * sx; py = (y + T + 30) * sx
        d.text((px, py), s, font=f, fill=col, anchor='mm', stroke_width=3, stroke_fill='#1d2320')
    put(41, 65, '放大板 R\n80×90'); put(W - 41, 65, '放大板 L\n80×90'); put(145, 80, '電源板\n92×120')
    put(40, 210, '控制板\n70×120'); put(250, 220, '市電板\n70×100'); put(145, 210, '變壓器\nØ120×50', '#ffffff')
    put(-20, 100, '散熱片\n176×60×33'); put(W + 20, 100, '散熱片\n176×60×33')
    top = label(top, '俯視（後面板在上；從正面看，右聲道在右）')
    vstack([lid, top]).save(OUT / 'chassis_print_v01_layout.png')
    # 3. 爆炸圖＋後視
    ex = crop_margin(shot(scene('B', explode=1.0, internals=False), ISO, 'tmp_ex.png'))
    ex = label(ex, '爆炸圖（方案 B，不含機內零件）：6 件列印框＋5 機腳＋2 鋁板＋2 散熱片')
    rear = crop_margin(shot(scene('B'), REAR, 'tmp_rear.png', parallel=True))
    rear = label(rear, '後視：回折段放 XLR＋RCA，中央板放喇叭端子 ×4、IEC 電源座、trigger')
    vstack([ex, rear]).save(OUT / 'chassis_print_v01_exploded.png')
    for p in OUT.glob('tmp_*.png'): p.unlink()


def volumes():
    rows = {}
    for n in list(PARTS) + ['foot']:
        m = load(n)
        b = m.bounds
        rows[n] = dict(group=PARTS.get(n, ('print',))[0], volume_cm3=round(m.volume / 1000, 1),
                       size_mm=[round(b[1] - b[0], 1), round(b[3] - b[2], 1), round(b[5] - b[4], 1)])
    (MECH / 'parts.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
    return rows




def viewer(dest=None):
    """把 STL 以 base64 嵌進 viewer_template.html，產生可旋轉的 3D 網頁（output/，不入版控）。"""
    import base64
    meta = json.loads((MECH / 'parts.json').read_text(encoding='utf-8'))
    stl = {n: base64.b64encode((STL / f'{n}.stl').read_bytes()).decode() for n in PARTS}
    html = (MECH / 'viewer_template.html').read_text(encoding='utf-8')
    html = html.replace('__STL_JSON__', json.dumps(stl)).replace('__META_JSON__', json.dumps(meta, ensure_ascii=False))
    dest = Path(dest) if dest else R / 'output/chassis_print_v01_viewer.html'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding='utf-8')
    print('viewer', dest, round(dest.stat().st_size / 1e6, 2), 'MB')


if __name__ == '__main__':
    if '--no-export' not in sys.argv:
        export_all()
    rows = volumes()
    for n, r in rows.items():
        print(f"{n:16s} {r['group']:6s} {r['volume_cm3']:8.1f} cm³  {r['size_mm']}")
    if '--no-render' not in sys.argv:
        render()
    viewer(sys.argv[sys.argv.index('--viewer') + 1] if '--viewer' in sys.argv else None)
    print('done')
