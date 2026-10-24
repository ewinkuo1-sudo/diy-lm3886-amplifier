# -*- coding: utf-8 -*-
"""v0.2 配置選項俯視對照（2026-10-25 使用者問：電源座離電源板太近、變壓器能不能放到電源板的位置）。
只畫外形與關鍵間距，不是 3D 模型。輸出 docs/diagrams/chassis_print_v02_layout_options.png
用法：py -3.13 -X utf8 tools/chassis_v02_layout_options.py
"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle, Circle

R = Path(__file__).resolve().parents[1]
FONT = r'C:\Windows\Fonts\msjh.ttc'
font_manager.fontManager.addfont(FONT)
plt.rcParams['font.family'] = font_manager.FontProperties(fname=FONT).get_name()
plt.rcParams['axes.unicode_minus'] = False

W, T = 290, 4
C = dict(amp='#1f6b3a', psu='#1f6b3a', tr='#5a6068', mod='#2a5d8f', iec='#c9533b', hs='#2b2f34', wall='#d9d4c8')


def plan(ax, D, title, tr, psu, ss, notes, wires):
    # 從上往下看，後牆在上；x 照機殼座標（從機後看 x 向右），所以從正面看右聲道在畫面左邊
    ax.add_patch(Rectangle((-T, -T), W + 2 * T, D + 2 * T, fc=C['wall'], ec='#1d2320'))
    ax.add_patch(Rectangle((0, 0), W, D, fc='#f4f2ec', ec='none'))
    for x0 in (-T - 28, W + T):
        ax.add_patch(Rectangle((x0, 6), 28, 176, fc=C['hs'], ec='none'))
    ax.add_patch(Rectangle((1.5, 55), 80, 90, fc=C['amp'], alpha=.85)); ax.text(41.5, 100, '放大板 R', c='w', ha='center', va='center', fontsize=10)
    ax.add_patch(Rectangle((208.5, 43), 80, 90, fc=C['amp'], alpha=.85)); ax.text(248.5, 88, '放大板 L', c='w', ha='center', va='center', fontsize=10)
    ax.add_patch(Rectangle(psu[:2], psu[2], psu[3], fc=C['psu'], alpha=.6, ec='#1d2320'))
    ax.text(psu[0] + psu[2] / 2, psu[1] + psu[3] / 2, '電源板', c='w', ha='center', va='center', fontsize=10)
    ax.add_patch(Circle(tr, 60, fc=C['tr'], alpha=.9)); ax.text(*tr, '變壓器', c='w', ha='center', va='center', fontsize=10)
    ax.add_patch(Rectangle(ss[:2], ss[2], ss[3], fc=C['mod'], alpha=.85)); ax.text(ss[0] + ss[2] / 2, ss[1] + ss[3] / 2, '軟啟動', c='w', ha='center', va='center', fontsize=9)
    ax.add_patch(Rectangle((28, 23), 52, 31, fc=C['mod'], alpha=.85)); ax.text(54, 38.5, '保護板', c='w', ha='center', va='center', fontsize=9)
    ax.add_patch(Rectangle((W / 2 - 22, 0), 44, 30, fc=C['iec'], alpha=.9)); ax.text(W / 2, 15, '電源座', c='w', ha='center', va='center', fontsize=9)
    for (x0, y0, x1, y1, col) in wires:
        ax.annotate('', (x1, y1), (x0, y0), arrowprops=dict(arrowstyle='-', color=col, lw=2.2, alpha=.9))
    for (x, y, s) in notes:
        ax.text(x, y, s, fontsize=9.5, ha='center', va='center', bbox=dict(fc='#fff8d6', ec='#b4561c', lw=.8, pad=2))
    ax.set_xlim(W + 40, -40); ax.set_ylim(330, -40); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(title, fontsize=13)


fig, axs = plt.subplots(1, 3, figsize=(18, 8.4), dpi=120)
# 現況：D=280
plan(axs[0], 280, '現況（v0.2）：內深 280',
     tr=(145, 210), psu=(99, 20, 92, 120), ss=(10, 170, 58, 95),
     notes=[(145, -22, '電源座機身和電源板在平面上重疊 10 mm，\n只靠高度錯開；直流端子 J203/J204 就在它下面')],
     wires=[])
# 互換：變壓器到後中、電源板到前中
plan(axs[1], 280, 'A　你提的互換：變壓器後、電源板前',
     tr=(145, 105), psu=(85, 175, 120, 92), ss=(10, 170, 58, 95),
     notes=[(145, 182, '變壓器離兩片放大板\n各只有 3.5 mm'), (145, 300, '直流線從前面繞回放大板\n約 19 cm；開關會撞電源板')],
     wires=[(145, 220, 70, 100, '#b4561c'), (145, 220, 222, 88, '#b4561c')])
# 加深 25 mm
plan(axs[2], 305, 'B　建議：配置不變，機殼加深 25 mm（內深 305）',
     tr=(145, 235), psu=(99, 45, 92, 120), ss=(10, 195, 58, 95),
     notes=[(145, -22, '電源座背後空出 15 mm，\n直流端子不再壓在它下面'), (145, 318, '外形 298×313，H2D 轉 90° 放，\n四周餘裕 6–11 mm')],
     wires=[])
fig.text(0.5, 0.02, '俯視，後牆在上；從正面看右聲道在右邊。灰框＝牆，黑＝散熱片。只是外形示意，不是 3D 模型。', ha='center', fontsize=11, color='#5c6661')
fig.tight_layout(rect=(0, 0.04, 1, 1))
out = R / 'docs/diagrams/chassis_print_v02_layout_options.png'
fig.savefig(out, facecolor='#eef1f4')
print(out)
