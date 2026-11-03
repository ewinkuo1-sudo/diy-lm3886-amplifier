"""舊 SHENG-LIN 鐵殼配置 v0.1（2026-11-03）

沿用 3D 列印殼 v0.2 的零件 STL（mechanical/chassis-print-v02/stl），只搬位置：
- 散熱片 176×33×60 改放殼內兩側，立在底板上，鰭片朝側牆、留 GAP 空氣道，底板朝放大板。
- 放大板 V0.6.1 IC 貼散熱片底板；8 mm 母母銅柱＋上下尼龍華司（鐵殼接 PE，背面 GND 鋪銅離孔 1.85 mm）。
- 電源板、變壓器放中間；保護板右後、軟啟動板右前（同 v0.2 的走線邏輯）。

座標同 v0.2：x=0 是從正面看的右側內牆，y=0 是後牆內面、往前增加，z=0 是底板上表面。
**內寬／內深是估的**（使用者 10/18 量外部約 420×340、內高 85）；改 WI／DI 後重跑即可。

用法：py -3.13 -X utf8 tools/chassis_iron_v01.py
"""
from pathlib import Path
import json
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
STL = ROOT / 'mechanical' / 'chassis-print-v02' / 'stl'
OUT = ROOT / 'docs' / 'diagrams'
JOUT = ROOT / 'mechanical' / 'chassis-iron-v01'
JOUT.mkdir(parents=True, exist_ok=True)

# ---- 鐵殼內部（估）----
WI, DI, HI = 410.0, 320.0, 85.0   # 內高 85 使用者已量；寬、深由外部 420×340 估
GAP = 8.0                         # 鰭片尖到側牆的空氣道
HS_T, HS_L, HS_H = 33.0, 176.0, 60.0
HS_Y0 = 6.0                       # 散熱片後端離後牆
WASH = 1.0                        # 尼龍華司厚（估）
STANDOFF = 8.0

# v0.2 參考位置：散熱片底板內面 x=1（右）／289（左），散熱片底 z=4，放大板底 z=10
dx_R = (GAP + HS_T) - 1.0              # 右側整組往內移
dx_L = (WI - GAP - HS_T) - 289.0       # 左側整組
dz_hs = -4.0                           # 散熱片直接立在底板上（L 型角鐵固定）
dz_amp = (STANDOFF + WASH) - 10.0      # 放大板底 = 銅柱＋華司
CX = WI / 2

PLACE = {
    # name: (dx, dy, dz)
    'heatsink_R': (dx_R, 0, dz_hs),
    'heatsink_L': (dx_L, 0, dz_hs),
    'amp_R': (dx_R, 0, dz_amp),
    'amp_L': (dx_L, 0, dz_amp),
    'psu': (CX - 145.0, 0, STANDOFF + WASH - 10.0),
    'transformer': (CX - 145.0, 10.0, 3.0 - 13.0),      # 3 mm 橡膠墊直接坐底板，往前 10
    'protect': (dx_R, 0, 0),                              # 右後，放大板 R 正後方
    'softstart': (8.0, 10.0, 0),                          # 右前，靠牆；散熱片後面
}
COLORS = {
    'heatsink_R': '#5b6470', 'heatsink_L': '#5b6470', 'amp_R': '#2e7d4f', 'amp_L': '#2e7d4f',
    'psu': '#1f5fa8', 'transformer': '#b8742a', 'protect': '#7b4fa8', 'softstart': '#c0392b',
}
LABEL = {
    'heatsink_R': '散熱片 R\n176×33×60', 'heatsink_L': '散熱片 L\n176×33×60',
    'amp_R': '放大板 R\n90×80', 'amp_L': '放大板 L\n90×80', 'psu': '電源板\n92×120',
    'transformer': '變壓器\nØ120', 'protect': '保護板\n52×31', 'softstart': '軟啟動板\n95×58',
}


def load():
    parts = {}
    for n, (dx, dy, dz) in PLACE.items():
        m = trimesh.load(STL / f'{n}.stl')
        m.apply_translation([dx, dy, dz])
        parts[n] = m
    return parts


def check(parts):
    rep = {'inner_mm': [WI, DI, HI], 'assumed': ['內寬 410、內深 320 由外部估，未量'], 'parts': {}, 'clash': [], 'margins': {}}
    for n, m in parts.items():
        b = m.bounds
        rep['parts'][n] = [[round(float(v), 1) for v in b[0]], [round(float(v), 1) for v in b[1]]]
        if b[0][0] < -0.01 or b[1][0] > WI + 0.01 or b[0][1] < -0.01 or b[1][1] > DI + 0.01 or b[1][2] > HI:
            rep['clash'].append(f'{n} 超出殼內')
    # 兩兩包絡盒重疊（粗檢）
    names = list(parts)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if {a, b} in ({'amp_R', 'heatsink_R'}, {'amp_L', 'heatsink_L'}):
                continue  # IC 背板本來就貼散熱片
            A, B = parts[a].bounds, parts[b].bounds
            if np.all(A[0] < B[1] - 0.01) and np.all(B[0] < A[1] - 0.01):
                try:  # 包絡盒重疊才做布林交集
                    v = trimesh.boolean.intersection([parts[a], parts[b]], engine='manifold').volume
                except Exception:
                    v = -1
                if v != 0 and abs(v) > 1:
                    rep['clash'].append(f'{a} × {b}（{v:.0f} mm³）')
    zmax = max(m.bounds[1][2] for m in parts.values())
    rep['margins']['上蓋餘裕'] = round(HI - float(zmax), 1)
    rep['margins']['最高件'] = max(parts, key=lambda k: parts[k].bounds[1][2])
    t = parts['transformer'].bounds
    rep['margins']['變壓器到前板'] = round(DI - float(t[1][1]), 1)
    p = parts['psu'].bounds
    rep['margins']['電源板到放大板R'] = round(float(p[0][0] - parts['amp_R'].bounds[1][0]), 1)
    rep['margins']['電源板到放大板L'] = round(float(parts['amp_L'].bounds[0][0] - p[1][0]), 1)
    rep['margins']['電源板到變壓器(y)'] = round(float(t[0][1] - p[1][1]), 1)
    s = parts['softstart'].bounds
    rep['margins']['軟啟動板到變壓器(x)'] = round(float(t[0][0] - s[1][0]), 1)
    (JOUT / 'layout.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding='utf8')
    return rep


def fig_top_section(parts, rep):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Polygon
    plt.rcParams['font.family'] = ['Microsoft JhengHei']

    fig = plt.figure(figsize=(16, 9.6), dpi=130, facecolor='#eef1f4')
    ax = fig.add_axes([0.03, 0.06, 0.58, 0.86])
    # 俯視：從正面看，右側內牆 x=0 畫在圖右 → 圖上橫座標用 WI-x；前板在下
    def P(x, y):
        return WI - x, y
    ax.add_patch(Rectangle((0, 0), WI, DI, fc='#fafbfc', ec='#333', lw=2.2))
    ax.text(WI / 2, -10, '後板（RCA／喇叭端子／要自開 IEC 孔）', ha='center', va='top', fontsize=11)
    ax.text(WI / 2, DI + 14, '前板（舊面板，孔多；只用電源開關）', ha='center', va='bottom', fontsize=11)
    for n, m in parts.items():
        b = m.bounds
        if n == 'transformer':
            c = P((b[0][0] + b[1][0]) / 2, (b[0][1] + b[1][1]) / 2)
            ax.add_patch(plt.Circle(c, (b[1][0] - b[0][0]) / 2, fc=COLORS[n], ec='k', alpha=.85))
            ax.text(*c, LABEL[n], ha='center', va='center', color='w', fontsize=11, weight='bold')
            continue
        x0, y0 = P(b[1][0], b[0][1])
        w, h = b[1][0] - b[0][0], b[1][1] - b[0][1]
        ax.add_patch(Rectangle((x0, y0), w, h, fc=COLORS[n], ec='k', alpha=.85))
        ax.text(x0 + w / 2, y0 + h / 2, LABEL[n], ha='center', va='center', color='w', fontsize=9.5, weight='bold')
    # 空氣道
    for xa in (0, WI - GAP):
        ax.add_patch(Rectangle((xa, HS_Y0), GAP, HS_L, fc='#cfe8ff', ec='none'))
    ax.annotate('空氣道 8', xy=(WI - GAP / 2, HS_Y0 + HS_L + 2), xytext=(WI - 150, HS_Y0 + HS_L + 22),
                fontsize=9, arrowprops=dict(arrowstyle='->', lw=.8))
    # 尺寸
    ax.annotate('', xy=(0, -26), xytext=(WI, -26), arrowprops=dict(arrowstyle='<->', lw=1))
    ax.text(WI / 2, -30, f'內寬 {WI:.0f}（估）', ha='center', va='top', fontsize=10)
    ax.annotate('', xy=(-14, 0), xytext=(-14, DI), arrowprops=dict(arrowstyle='<->', lw=1))
    ax.text(-18, DI / 2, f'內深 {DI:.0f}（估）', ha='right', va='center', rotation=90, fontsize=10)
    ax.text(WI + 6, 30, '右', fontsize=12, va='center')
    ax.text(-6 - 14, 30, '左', fontsize=12, va='center', ha='right')
    ax.set_xlim(-45, WI + 25); ax.set_ylim(DI + 36, -50)
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('舊鐵殼配置 v0.1 俯視（前板在下，從正面看）', fontsize=15, loc='left')

    # 截面：過放大板 R 的 IC（y=94）從正面看右半
    ax2 = fig.add_axes([0.64, 0.50, 0.34, 0.40])
    ycut = HS_Y0 + HS_L / 2
    for n in ('heatsink_R', 'amp_R', 'psu', 'transformer'):
        try:
            sec = parts[n].section(plane_origin=[0, ycut, 0], plane_normal=[0, 1, 0])
        except Exception:
            sec = None
        if sec is None:
            continue
        for e in sec.discrete:
            ax2.fill(WI - e[:, 0], e[:, 2], fc=COLORS[n], ec='k', lw=.4, alpha=.85)
        ax2.plot([WI - 175, WI], [0, 0], color='#333', lw=2); ax2.plot([WI, WI], [0, HI], color='#333', lw=2)
    ax2.plot([WI - 175, WI], [HI, HI], color='#333', lw=2, ls='--')
    ax2.text(WI - 172, HI - 3, '上蓋', fontsize=9, va='top')
    ax2.text(WI - GAP / 2, 30, '空\n氣\n道', fontsize=8, ha='center', va='center')
    ax2.set_xlim(WI - 175, WI + 5); ax2.set_ylim(-5, HI + 5)
    ax2.set_aspect('equal')
    ax2.set_title(f'截面（過 IC，y={ycut:.0f}），右半', fontsize=12, loc='left')
    ax2.tick_params(labelsize=8)

    m = rep['margins']
    txt = (
        f"上蓋餘裕：{m['上蓋餘裕']} mm（最高件 {m['最高件']}）\n"
        f"變壓器到前板：{m['變壓器到前板']} mm\n"
        f"電源板到放大板 R／L：{m['電源板到放大板R']}／{m['電源板到放大板L']} mm\n"
        f"電源板到變壓器：{m['電源板到變壓器(y)']} mm\n"
        f"軟啟動板到變壓器：{m['軟啟動板到變壓器(x)']} mm\n"
        f"碰撞：{'無' if not rep['clash'] else '、'.join(rep['clash'])}\n\n"
        "散熱片立在底板上，用 L 型角鐵鎖底板\n"
        "放大板：8 mm 母母銅柱＋上下尼龍華司\n"
        "散熱片、機殼都接 PE；IC 墊雲母＋絕緣粒\n"
        "上蓋在散熱片正上方要有通風孔（未確認）"
    )
    fig.text(0.645, 0.05, txt, fontsize=10.5, va='bottom', linespacing=1.5)
    fig.savefig(OUT / 'chassis_iron_v01_layout.png', facecolor=fig.get_facecolor())
    plt.close(fig)


def fig_3d(parts):
    import pyvista as pv
    pl = pv.Plotter(off_screen=True, window_size=(1800, 1200))
    pl.set_background('#eef1f4')
    t = 1.0
    shell = [
        pv.Box((0 - t, WI + t, -t, 0, -t, HI)),              # 後板
        pv.Box((-t, 0, -t, DI + t, -t, HI)),                 # 右側
        pv.Box((WI, WI + t, -t, DI + t, -t, HI)),            # 左側
        pv.Box((-t, WI + t, -t, DI + t, -t, 0)),             # 底板
    ]
    for s in shell:
        pl.add_mesh(s, color='#9aa3ad', opacity=0.35)
    pl.add_mesh(pv.Box((-t, WI + t, DI, DI + 6, -t, HI)), color='#c9a227', opacity=0.12)  # 前飾板
    for n, m in parts.items():
        pl.add_mesh(pv.wrap(m), color=COLORS[n], smooth_shading=True)
    pl.camera_position = [(WI * 1.25, DI * 1.9, 330), (WI / 2, DI / 2, 20), (0, 0, 1)]
    pl.enable_parallel_projection() if False else None
    pl.screenshot(str(OUT / 'chassis_iron_v01_3d.png'))
    pl.close()


if __name__ == '__main__':
    parts = load()
    rep = check(parts)
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    fig_top_section(parts, rep)
    fig_3d(parts)
    print('ok')
