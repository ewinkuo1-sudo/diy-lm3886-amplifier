# -*- coding: utf-8 -*-
"""3D 列印機殼 v0.2（mechanical/chassis-print-v02，Bambu Lab H2D）的建置腳本：
1. OpenSCAD 匯出每件 STL
2. 體積、重量、H2D 平台放不放得下 → parts.json
3. 碰撞檢查（trimesh＋manifold3d 布林交集）→ clash.json
4. pyvista 出圖（docs/diagrams/chassis_print_v02_*.png）
5. 3D 網頁（output/chassis_print_v02_viewer.html，不入版控）
用法：py -3.13 -X utf8 tools/chassis_print_v02.py [--no-export] [--no-render]
需要：OpenSCAD 2021.01（Program Files）、py -3.13 的 pyvista／Pillow／trimesh／manifold3d。
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json, subprocess, sys, itertools
import numpy as np
import pyvista as pv
import trimesh
from PIL import Image, ImageDraw, ImageFont

pv.OFF_SCREEN = True
R = Path(__file__).resolve().parents[1]
MECH = R / 'mechanical/chassis-print-v02'
SCAD = MECH / 'chassis_print_v02.scad'
STL = MECH / 'stl'; STL.mkdir(exist_ok=True)
OUT = R / 'docs/diagrams'; OUT.mkdir(exist_ok=True)
OPENSCAD = Path(r'C:\Program Files\OpenSCAD\openscad.com')
FONT = r'C:\Windows\Fonts\msjh.ttc'
W, D, H, T, FT, LT = 290, 280, 78, 4, 3, 3
H2D = (325, 320, 325)          # 單噴頭列印範圍（官方規格）
DENS = 1.07                     # ASA g/cm³

PRINT = '#d9d4c8'; HS = '#2b2f34'; PCB = '#1f6b3a'
PARTS = {   # 名稱: (群組, 顏色)
    'tub': ('print', PRINT), 'lid': ('print', '#e4dfd3'), 'mains_cover': ('print', '#c9533b'), 'feet': ('print', '#8c8780'),
    'heatsink_R': ('hs', HS), 'heatsink_L': ('hs', HS),
    'amp_R': ('int', PCB), 'amp_L': ('int', PCB), 'psu': ('int', PCB), 'softstart': ('int', '#2a5d8f'), 'protect': ('int', '#2a5d8f'),
    'transformer': ('int', '#5a6068'), 'connectors': ('int', '#444444'),
}
EXTRA = ['foot', 'foot_center']
PRINT_LIST = [('tub', 1), ('lid', 1), ('mains_cover', 1), ('foot', 4), ('foot_center', 1)]


def export(name):
    out = STL / f'{name}.stl'
    r = subprocess.run([str(OPENSCAD), '-o', str(out), '--export-format', 'binstl', '-D', f'part="{name}"', str(SCAD)],
                       capture_output=True, text=True)
    if r.returncode != 0 or not out.exists():
        raise SystemExit(f'OpenSCAD 匯出失敗 {name}:\n{r.stderr[-800:]}')
    return name


def export_all():
    with ThreadPoolExecutor(max_workers=6) as ex:
        for n in ex.map(export, list(PARTS) + EXTRA):
            print('  stl', n)


def load(name):
    return pv.read(str(STL / f'{name}.stl'))


def volumes():
    rows = {}
    for n in list(PARTS) + EXTRA:
        m = trimesh.load(STL / f'{n}.stl')
        ext = m.extents
        rows[n] = dict(group=PARTS.get(n, ('print',))[0], volume_cm3=round(m.volume / 1000, 1),
                       size_mm=[round(float(v), 1) for v in ext], watertight=bool(m.is_watertight))
    # 列印件能不能放進 H2D：最長兩邊排序後比平台（允許在平台上轉 90°）
    for n, qty in PRINT_LIST:
        sx, sy, sz = rows[n]['size_mm']
        a, b = sorted([sx, sy], reverse=True)
        rows[n]['qty'] = qty
        rows[n]['fits_H2D'] = bool(a <= max(H2D[:2]) and b <= min(H2D[:2]) and sz <= H2D[2])
        rows[n]['mass_g_solid'] = round(rows[n]['volume_cm3'] * DENS * qty)
    (MECH / 'parts.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
    return rows


def clash():
    """機內零件 vs 外殼（底殼＋上蓋＋護罩＋散熱片），以及機內零件彼此。交集體積 >1 mm³ 才算撞。"""
    m = {n: trimesh.load(STL / f'{n}.stl') for n in PARTS if n != 'feet'}
    shell = ['tub', 'lid', 'mains_cover', 'heatsink_R', 'heatsink_L']
    inside = ['amp_R', 'amp_L', 'psu', 'softstart', 'protect', 'transformer', 'connectors']
    res = []
    pairs = [(a, b) for a in inside for b in shell] + list(itertools.combinations(inside, 2)) + [('heatsink_R', 'tub'), ('heatsink_L', 'tub')]
    for a, b in pairs:
        lo = np.maximum(m[a].bounds[0], m[b].bounds[0]); hi = np.minimum(m[a].bounds[1], m[b].bounds[1])
        if np.any(hi <= lo):
            continue
        try:
            x = trimesh.boolean.intersection([m[a], m[b]], engine='manifold')
            v = float(x.volume) if x is not None and len(x.faces) else 0.0
        except Exception as e:
            v = -1.0
        if v > 1 or v < 0:
            bb = x.bounds.round(1).tolist() if v > 0 else None
            res.append(dict(a=a, b=b, volume_mm3=round(v, 1), bounds=bb))
    (MECH / 'clash.json').write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
    return res


# ---------------- 出圖 ----------------
def scene(lid=True, internals=True, explode=0.0, hide=(), size=(1800, 1300), clip_y=None, bg='#eef1f4'):
    pl = pv.Plotter(off_screen=True, window_size=size)
    pl.set_background(bg)
    shift = {'lid': (0, 0, 90), 'feet': (0, 0, -60), 'mains_cover': (0, 0, 70), 'heatsink_R': (-110, 0, 0), 'heatsink_L': (110, 0, 0)}
    for name, (grp, col) in PARTS.items():
        if name in hide: continue
        if grp == 'int' and not internals: continue
        if not lid and name == 'lid': continue
        mm = load(name)
        if explode and name in shift:
            mm = mm.translate(np.array(shift[name]) * explode, inplace=False)
        if clip_y is not None:
            mm = mm.clip(normal=(0, 1, 0), origin=(0, clip_y, 0), invert=False)
            if mm.n_points == 0: continue
        kw = dict(color=col, smooth_shading=False)
        if grp == 'hs': kw.update(pbr=True, metallic=0.3, roughness=0.7)
        pl.add_mesh(mm, **kw)
    pl.enable_anti_aliasing('ssaa')
    return pl


def shot(pl, cam, parallel=False):
    pl.camera_position = cam
    if parallel: pl.enable_parallel_projection()
    img = pl.screenshot(return_img=True); pl.close()
    return Image.fromarray(img)


def label(im, text, size=40, bg=(238, 241, 244)):
    while size > 20 and ImageFont.truetype(FONT, size).getlength(text) > im.width - 40: size -= 2
    band = int(size * 1.9)
    out = Image.new('RGB', (im.width, im.height + band), bg); out.paste(im, (0, band))
    ImageDraw.Draw(out).text((20, band * 0.25), text, font=ImageFont.truetype(FONT, size), fill='#1d2320')
    return out


def crop(im, pad=30, bg=(238, 241, 244)):
    a = np.asarray(im.convert('RGB')).astype(int)
    ys, xs = np.where(np.abs(a - np.array(bg)).sum(axis=2) > 24)
    if len(xs) == 0: return im
    return im.crop((max(xs.min() - pad, 0), max(ys.min() - pad, 0), min(xs.max() + pad, im.width), min(ys.max() + pad, im.height)))


def stack(ims, horiz, gap=40, bg=(238, 241, 244)):
    if horiz:
        out = Image.new('RGB', (sum(i.width for i in ims) + gap * (len(ims) - 1), max(i.height for i in ims)), bg); x = 0
        for i in ims: out.paste(i, (x, (out.height - i.height) // 2)); x += i.width + gap
    else:
        out = Image.new('RGB', (max(i.width for i in ims), sum(i.height for i in ims) + gap * (len(ims) - 1)), bg); y = 0
        for i in ims: out.paste(i, ((out.width - i.width) // 2, y)); y += i.height + gap
    return out


ISO = [(W + 420, D + 460, 360), (W / 2, D / 2 - 10, 20), (0, 0, 1)]
ISO_BACK = [(-430, -440, 340), (W / 2, D / 2 + 10, 20), (0, 0, 1)]
TOP = [(W / 2, D / 2, 900), (W / 2, D / 2, 0), (0, -1, 0)]
REAR = [(W / 2, -700, 45), (W / 2, 0, 35), (0, 0, 1)]
SEC = [(W / 2, -600, 40), (W / 2, 94, 35), (0, 0, 1)]


def render():
    a = label(crop(shot(scene(), ISO)), '組好：底殼一體＋上蓋一片，散熱片當左右側牆')
    b = label(crop(shot(scene(lid=False), ISO)), '掀開上蓋：前排變壓器、軟啟動板（紅色護罩）、保護板')
    stack([a, b], True).save(OUT / 'chassis_print_v02_overview.png')

    top = crop(shot(scene(lid=False, hide=('mains_cover',)), TOP, parallel=True))
    d = ImageDraw.Draw(top); f = ImageFont.truetype(FONT, 28)
    ext = W + 2 * (T + 28)              # 俯視影像的 x 範圍：含兩側鰭片
    sx = (top.width - 60) / ext
    def put(x, y, s):
        px = top.width - 30 - (x + T + 28) * sx; py = 30 + (y + T) * sx
        d.text((px, py), s, font=f, fill='#ffffff', anchor='mm', stroke_width=3, stroke_fill='#1d2320', align='center')
    put(42, 100, '放大板 R\n80×90'); put(W - 42, 88, '放大板 L\n80×90'); put(145, 80, '電源板\n92×120')
    put(254, 201, '保護板\n52×31'); put(39, 217, '軟啟動板\n95×58'); put(145, 210, '變壓器\nØ120')
    top = label(top, '俯視（後牆在上；從正面看右聲道在右）—— 兩片現成板取代自製 CTRL／MAINS 板')
    top.save(OUT / 'chassis_print_v02_layout.png')

    ex = label(crop(shot(scene(explode=1.0, internals=False), ISO)), '爆炸圖：列印件只有底殼、上蓋、市電護罩、5 顆機腳')
    rear = label(crop(shot(scene(), REAR, parallel=True)), '後視：XLR＋RCA（兩側）、喇叭端子 ×4、IEC 電源座')
    stack([ex, rear], False).save(OUT / 'chassis_print_v02_exploded.png')

    section_fig()


def section_fig():
    """真正的截面（trimesh 切平面→填色多邊形）：右聲道 IC 中心與銅柱兩刀。"""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    font_manager.fontManager.addfont(FONT)
    plt.rcParams['font.family'] = font_manager.FontProperties(fname=FONT).get_name()
    plt.rcParams['axes.unicode_minus'] = False
    names = ['tub', 'lid', 'heatsink_R', 'amp_R', 'psu', 'feet']
    m = {n: trimesh.load(STL / f'{n}.stl') for n in names}
    cuts = [(94, 'y=94：IC 中心'), (59, 'y=59：靠牆銅柱')]
    fig, axs = plt.subplots(1, 2, figsize=(14, 6.2), dpi=130)
    for ax, (y0, title) in zip(axs, cuts):
        for n in names:
            sec = m[n].section(plane_origin=[0, y0, 0], plane_normal=[0, 1, 0])
            if sec is None: continue
            to2d = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, y0], [0, 0, 0, 1]], float)
            pl2, _ = sec.to_planar(to_2D=to2d, check=False)
            for poly in pl2.polygons_full:
                xs, zs = poly.exterior.xy
                ax.fill(xs, zs, color=PARTS[n][1], ec='#1d2320', lw=0.4)
                for hole in poly.interiors:
                    hx, hz = hole.xy; ax.fill(hx, hz, color='#ffffff', ec='#1d2320', lw=0.4)
        ax.set_xlim(-40, 105); ax.set_ylim(-14, 86); ax.set_aspect('equal')
        ax.set_title(title, fontsize=13); ax.set_xlabel('x (mm)，0＝右內牆'); ax.set_ylabel('z (mm)，0＝底板上表面')
        ax.grid(alpha=0.25)
    axs[0].text(-14, 34, '散熱片\n（機外）', ha='center', va='center', fontsize=10, color='white')
    axs[0].annotate('IC', (3.2, 30), (30, 62), fontsize=11, arrowprops=dict(arrowstyle='->'))
    axs[0].annotate('窗口（45° 尖頂免支撐）', (2, 55), (35, 75), fontsize=10, arrowprops=dict(arrowstyle='->'))
    axs[1].annotate('板邊槽', (2.5, 11), (25, 30), fontsize=10, arrowprops=dict(arrowstyle='->'))
    axs[1].annotate('長孔 M3 由下鎖銅柱', (5.5, -3), (25, -11), fontsize=10, arrowprops=dict(arrowstyle='->'))
    fig.suptitle('右聲道截面（從機後往前看；左邊是機外鰭片）', fontsize=15)
    fig.tight_layout()
    fig.savefig(OUT / 'chassis_print_v02_section.png', facecolor='#eef1f4')
    plt.close(fig)


def bed_fit():
    """H2D 平台（325×320）上擺底殼與上蓋的俯視示意。"""
    rows = json.loads((MECH / 'parts.json').read_text(encoding='utf-8'))
    s = 2.0; pad = 60
    ims = []
    for n, title in (('tub', '底殼'), ('lid', '上蓋（翻面印）')):
        im = Image.new('RGB', (int(H2D[0] * s) + 2 * pad, int(H2D[1] * s) + 2 * pad + 70), (238, 241, 244))
        d = ImageDraw.Draw(im); f = ImageFont.truetype(FONT, 30); fs = ImageFont.truetype(FONT, 24)
        x0, y0 = pad, pad + 70
        d.rectangle([x0, y0, x0 + H2D[0] * s, y0 + H2D[1] * s], outline='#5a6068', width=3, fill='#f8f9fa')
        px, py, pz = rows[n]['size_mm']
        ox = x0 + (H2D[0] - px) / 2 * s; oy = y0 + (H2D[1] - py) / 2 * s
        d.rounded_rectangle([ox, oy, ox + px * s, oy + py * s], radius=12, outline='#1d2320', width=3, fill='#d9d4c8')
        d.text((x0, 15), f'{title} {px:.0f}×{py:.0f}×{pz:.0f} mm', font=f, fill='#1d2320')
        d.text((x0 + H2D[0] * s / 2, y0 + H2D[1] * s / 2), f'四周餘裕\n左右 {(H2D[0] - px) / 2:.0f}、前後 {(H2D[1] - py) / 2:.0f} mm',
               font=fs, fill='#1d2320', anchor='mm', align='center')
        d.text((x0 + H2D[0] * s, y0 + H2D[1] * s + 8), 'H2D 單噴頭 325×320', font=fs, fill='#5a6068', anchor='ra')
        ims.append(im)
    stack(ims, True).save(OUT / 'chassis_print_v02_bedfit.png')


def viewer(dest=None):
    import base64
    meta = json.loads((MECH / 'parts.json').read_text(encoding='utf-8'))
    stl = {n: base64.b64encode((STL / f'{n}.stl').read_bytes()).decode() for n in PARTS}
    html = (MECH / 'viewer_template.html').read_text(encoding='utf-8')
    stiff = json.loads((MECH / 'stiffness.json').read_text(encoding='utf-8')) if (MECH / 'stiffness.json').exists() else {}
    html = (html.replace('__STL_JSON__', json.dumps(stl)).replace('__META_JSON__', json.dumps(meta, ensure_ascii=False))
                .replace('__STIFF_JSON__', json.dumps(stiff, ensure_ascii=False)))
    dest = Path(dest) if dest else R / 'output/chassis_print_v02_viewer.html'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding='utf-8')
    print('viewer', dest, round(dest.stat().st_size / 1e6, 2), 'MB')


if __name__ == '__main__':
    if '--no-export' not in sys.argv:
        export_all()
    rows = volumes()
    for n, r in rows.items():
        print(f"{n:12s} {r['group']:6s} {r['volume_cm3']:7.1f} cm³ {r['size_mm']} wt={r['watertight']} {'fits' if r.get('fits_H2D') else ''}")
    cl = clash()
    print('clash:', cl if cl else 'none')
    if '--no-render' not in sys.argv:
        render(); bed_fit()
    if (MECH / 'viewer_template.html').exists():
        viewer(sys.argv[sys.argv.index('--viewer') + 1] if '--viewer' in sys.argv else None)
    print('done')
