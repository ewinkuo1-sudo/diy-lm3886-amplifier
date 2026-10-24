# -*- coding: utf-8 -*-
"""3D 列印機殼 v0.2 的剛性與強度估算（手算等級：格狀梁＋梁公式，不是有限元素）。

用法：py -3.13 -X utf8 tools/chassis_v02_stiffness.py
輸出：mechanical/chassis-print-v02/stiffness.json（給 docs/16 與 3D 網頁引用）

前提（改前提就改這裡）：
- 材料 Bambu ASA，Technical Data Sheet V2.0：E(XY)=2450±270 MPa、E(Z)=2120±260 MPa、HDT 92 °C@1.8 MPa；
  抗拉強度 V2.0 寫 XY 52／Z 35 MPa，舊版與第三方寫 XY 37／Z 31，這裡取舊版的低值。
- 列印件不是 100% 實心、層間有缺陷：設計模數＝0.8×E(XY)；剪力模數＝E/2.7。
- 容許應力：短時（搬運、壓重）＝Z 向強度／3＝10.3 MPa；長期（站著放、螺絲夾緊）＝4 MPa；
  靠散熱片 60–75 °C 的熱區，長期容許再打 0.75 折＝3 MPa。
- 容許撓度：長期與壓重 跨距／300；搬運（短時、彈性回復）跨距／150。
- 搬運動態係數 2。
- 底板與上蓋用格狀梁（tools/grillage.py）：肋＋分到的平板翼緣當梁，牆邊當簡支（保守）；
  同時列出牆邊固定的結果當下限，真實值在兩者之間。
- 重量：散熱片照外形算（鋁 2.70 g/cm³），變壓器沒秤過、取 200 VA 環形常見值 2.2 kg（範圍 1.8–2.6），
  電容／板子／線材是估的，外殼用 STL 體積×1.07 g/cm³（實心估，偏重）。
"""
from pathlib import Path
import json, math, sys
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import grillage as G

R = Path(__file__).resolve().parents[1]
MECH = R / 'mechanical/chassis-print-v02'
g = 9.81

E_XY, E_Z = 2450.0, 2120.0
E_D = 0.8 * E_XY
G_D = E_D / 2.7
S_XY, S_Z = 37.0, 31.0
ALLOW_SHORT = S_Z / 3
ALLOW_LONG = 4.0
ALLOW_HOT = 0.75 * ALLOW_LONG

# 幾何（和 chassis_print_v02.scad 一致）
W, D, H, T, FT, LT = 290, 280, 78, 4, 3, 3
RIBH, RIBH2, RIBW, RIBP = 6, 10, 2.4, 40
ZONE = (72, 225, 145)              # 加高區 x0、x1、y≥
LRIBH, LRIBP = 12, 40
TX, TY, TD = W / 2, 210, 120

# 重量
hs_vol = (176 * 60 * 5 + 23 * 1.5 * 28 * 60) / 1000
pj = json.loads((MECH / 'parts.json').read_text(encoding='utf-8'))
shell_cm3 = sum(pj[n]['volume_cm3'] for n in ('tub', 'lid', 'mains_cover', 'feet'))
mass = {
    '變壓器（未秤，200 VA 環形常見值）': 2.2,
    '散熱片 ×2（外形估算）': 2 * hs_vol * 2.70 / 1000,
    '電源板（4×10000 µF/63 V＋橋）': 0.40,
    '放大板 ×2': 0.20,
    '軟啟動板＋保護板': 0.17,
    '端子、線材、螺絲': 0.35,
    '列印外殼（STL 體積×1.07，實心估）': shell_cm3 * 1.07 / 1000,
}
M_TOT = sum(mass.values())
M_TR = mass['變壓器（未秤，200 VA 環形常見值）']


def grid(p, Wd, Dd):
    xs = [0.0] + [float(x) for x in range(p, int(Wd), p) if Wd - x > 5] + [float(Wd)]
    ys = [0.0] + [float(y) for y in range(p, int(Dd), p) if Dd - y > 5] + [float(Dd)]
    return np.array(xs), np.array(ys)


def section_fn(xs, ys, hfun, tf, Wd, Dd):
    xl, yl = list(xs), list(ys)
    def sec(x0, y0, x1, y1):
        if y0 == y1:
            j = yl.index(y0); b = (ys[min(j + 1, len(ys) - 1)] - ys[max(j - 1, 0)]) / 2; on = y0 not in (0, Dd)
        else:
            i = xl.index(x0); b = (xs[min(i + 1, len(xs) - 1)] - xs[max(i - 1, 0)]) / 2; on = x0 not in (0, Wd)
        return G.tsec(b, tf, 1 if on else 0, RIBW, hfun((x0 + x1) / 2, (y0 + y1) / 2))
    return sec


def floor_h(x, y):
    return RIBH2 if (y >= ZONE[2] and ZONE[0] <= x <= ZONE[1]) else RIBH


def row(name, stress, allow, defl, defl_allow, note, extra=None):
    d = dict(case=name, stress_MPa=round(stress, 2), allow_MPa=round(allow, 1), stress_ratio=round(stress / allow, 2),
             deflection_mm=round(defl, 2), deflection_allow_mm=round(defl_allow, 2),
             ok=bool(stress <= allow and defl <= defl_allow), note=note)
    if extra: d.update(extra)
    return d


cases = []

# ---- 底板：變壓器壓在底板上（中央機腳沒碰地，或整台被提起） ----
xs, ys = grid(RIBP, W, D)
sec = section_fn(xs, ys, floor_h, FT, W, D)
nodes = [(i, j) for i, x in enumerate(xs) for j, y in enumerate(ys)
         if math.hypot(x - TX, y - TY) <= TD / 2 + 2 and 0 < i < len(xs) - 1 and 0 < j < len(ys) - 1]
for P, label, allow, dlim, note in (
        (M_TR * g * 2, '搬運：變壓器重量壓底板（×2 衝擊）', ALLOW_SHORT, D / 150, '短時；中央機腳離地時變壓器只能靠底板'),
        (M_TR * g, '站著放：中央機腳沒碰到地（最壞）', ALLOW_LONG, D / 300, '長期；正常情況變壓器重量經中心螺栓直接到中央機腳，底板幾乎不受力')):
    loads = {n: P / len(nodes) for n in nodes}
    _, s_pin, d_pin = G.solve(xs, ys, E_D, G_D, sec, loads, False)
    _, s_fix, d_fix = G.solve(xs, ys, E_D, G_D, sec, loads, True)
    cases.append(row(label, s_pin, allow, d_pin, dlim, note + f'；牆邊固定時 σ={s_fix:.1f} MPa、δ={d_fix:.2f} mm',
                     dict(k_N_per_mm=round(P / d_pin), stress_fixed=round(s_fix, 2), deflection_fixed=round(d_fix, 2))))

# ---- 對照：v0.2 前的版本（全部 6 mm 肋、上蓋 6 mm 肋）——寫進文件說明為什麼要加高 ----
sec6 = section_fn(xs, ys, lambda x, y: RIBH, FT, W, D)
_, s6, d6 = G.solve(xs, ys, E_D, G_D, sec6, {n: M_TR * g * 2 / len(nodes) for n in nodes}, False)
baseline = dict(floor_rib6_carry=dict(stress_MPa=round(s6, 2), deflection_mm=round(d6, 2)))

# ---- 上蓋 ----
lx, ly = grid(LRIBP, W, D)
lsec = section_fn(lx, ly, lambda x, y: LRIBH, LT, W, D)
q = 10 * g / (W * D)
uni = {}
for i in range(1, len(lx) - 1):
    for j in range(1, len(ly) - 1):
        uni[(i, j)] = q * (lx[i + 1] - lx[i - 1]) / 2 * (ly[j + 1] - ly[j - 1]) / 2
ic, jc = int(np.argmin(abs(lx - W / 2))), int(np.argmin(abs(ly - D / 2)))
for loads, label in ((uni, '上蓋放 10 kg（均布）'), ({(ic, jc): 5 * g}, '上蓋中央手壓 5 kg（集中）')):
    _, sp, dp = G.solve(lx, ly, E_D, G_D, lsec, loads, False)
    _, sf, df = G.solve(lx, ly, E_D, G_D, lsec, loads, True)
    cases.append(row(label, sp, ALLOW_SHORT, dp, W / 300, f'8 顆螺絲＋定位框，介於簡支與固定之間；固定時 δ={df:.2f} mm',
                     dict(stress_fixed=round(sf, 2), deflection_fixed=round(df, 2))))
lsec6 = section_fn(lx, ly, lambda x, y: 6, LT, W, D)
_, s6p, d6p = G.solve(lx, ly, E_D, G_D, lsec6, {(ic, jc): 5 * g}, False)
baseline['lid_rib6_point5kg'] = dict(stress_MPa=round(s6p, 2), deflection_mm=round(d6p, 2))

# ---- 整台當梁（兩側抬起） ----
Pw = M_TOT * g * 2 / 2
Lw = W + 2 * T
Iw = T * (H + FT) ** 3 / 12
cases.append(row('搬運：兩側抬起，前後牆當梁（×2）', Pw * Lw / 8 * (H + FT) / 2 / Iw, ALLOW_SHORT,
                 5 * Pw * Lw ** 3 / (384 * E_D * Iw), Lw / 150, '只算牆，底板與上蓋翼板不計'))

# ---- 散熱片當把手 ----
F_hs = M_TOT * g * 2 / 2
bear = F_hs / (176 * 5)
tens = F_hs * 20 / (56 - 22) / 2
cases.append(row('拿散熱片當把手（×2）', max(bear, tens / (math.pi / 4 * (9 ** 2 - 3.4 ** 2))), ALLOW_SHORT, 0, 1,
                 f'垂直力壓在凹槽下緣 {bear:.2f} MPa；上排螺絲各受拉約 {tens:.0f} N'))

# ---- 散熱片螺絲長期夾緊（熱區） ----
pre = 300.0          # M3 鎖到「剛好緊」的預力估計
for area, lab in ((math.pi / 4 * (7 ** 2 - 3.4 ** 2), 'Ø7 一般華司'), (math.pi / 4 * (9 ** 2 - 3.4 ** 2), 'Ø9 大華司'),
                  (10 * 25, '直立鋁條 10×50×1.5（每端一條、蓋 2 顆）')):
    cases.append(row(f'散熱片螺絲長期夾緊：{lab}', pre / area, ALLOW_HOT, 0, 1, '熱區 60–75 °C；超過會慢慢壓陷鬆掉'))

# ---- 變壓器中心螺栓 ----
pre6 = 1500.0
ring = math.pi / 4 * (116 ** 2 - 100 ** 2) + math.pi / 4 * 22 ** 2 + 8 * RIBW * 38
cases.append(row('變壓器中心螺栓夾緊：底板承環（長期）', pre6 / ring, ALLOW_LONG, 0, 1, 'M6 手鎖中等，約 1500 N；橡膠墊攤開'))
cases.append(row('變壓器中心螺栓夾緊：中央機腳（長期）', pre6 / (math.pi / 4 * (32 ** 2 - 11.6 ** 2)), ALLOW_LONG, 0, 1, '機腳 Ø32、底下六角螺帽槽'))

out = dict(
    assumptions=dict(E_XY=E_XY, E_Z=E_Z, E_design=E_D, strength_XY=S_XY, strength_Z=S_Z,
                     allow_short=round(ALLOW_SHORT, 1), allow_long=ALLOW_LONG, allow_hot=ALLOW_HOT, dyn_factor=2,
                     source='Bambu ASA Technical Data Sheet V2.0（強度取舊版低值）', method='格狀梁（tools/grillage.py）＋梁公式'),
    mass_kg={k: round(v, 2) for k, v in mass.items()}, mass_total_kg=round(M_TOT, 2),
    baseline_before_fix=baseline, cases=cases)
(MECH / 'stiffness.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
print(f'總重 {M_TOT:.2f} kg')
for k, v in mass.items():
    print(f'  {k:30s} {v:5.2f}')
print('改前對照', baseline)
for c in cases:
    print(f"{'OK' if c['ok'] else 'NG'}  {c['case']:34s} σ={c['stress_MPa']:5.2f}/{c['allow_MPa']:4.1f}  δ={c['deflection_mm']:.2f}/{c['deflection_allow_mm']}")
