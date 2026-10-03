"""Copper-path screen, V0.6 vs V0.6.1 (amplifier + PSU). Same model and limits as analyze_pcb_v03: centreline
geometry only, R = rho * sum(L/W) / t, no pads, solder, vias, connectors, wires, ESR, inductance or thermal rise.
Writes pcb/current-budget-v061.json and prints the Markdown table used in pcb/README.
Run: py -3.13 -X utf8 tools/analyze_pcb_v061.py
"""
from pathlib import Path
import json, math, hashlib, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_pcb_v03 as A
ROOT = Path(__file__).resolve().parents[1]
FILES = {('mono', '06'): 'pcb/mono-layout-v06.json', ('psu', '06'): 'pcb/psu-layout-v06.json',
         ('mono', '061'): 'pcb/mono-layout-v061.json', ('psu', '061'): 'pcb/psu-layout-v061.json'}
data = {k: json.loads((ROOT / f).read_text(encoding='utf-8')) for k, f in FILES.items()}

# Sizing case as analyze_pcb_v03: +-30 V, 40 W / 8 ohm sine per channel (sizing point, not a rating), Iq 85 mA,
# both channels in phase on the shared PSU, rectifier charge pulses as rectangular 15 % duty.
out_rms = math.sqrt(40 / 8); out_peak = out_rms * math.sqrt(2); iq = .085
rail_rms = math.sqrt(out_peak**2 / 4 + 2 * iq * out_peak / math.pi + iq**2); rail_avg = out_peak / math.pi + iq
charge_avg = 2 * rail_avg; duty = .15
CURRENTS = {'output': (out_rms, out_peak), 'rail1': (rail_rms, out_peak + iq), 'rail2': (2 * rail_rms, 2 * (out_peak + iq)),
            'ground2': (2 * out_rms, 2 * out_peak), 'charge': (charge_avg / math.sqrt(duty), charge_avg / duty)}

SPECS = [
    ('放大板 IC 腳 3→L1', 'mono', 'L_OUT', 'U1.3', 'L1.1', 'output'),
    ('放大板 L1→喇叭端子', 'mono', 'L_SPK', 'L1.2', 'J2.1', 'output'),
    ('放大板 正電源端子→U1 腳 1', 'mono', 'VCC', 'J5.1', 'U1.1', 'rail1'),
    ('放大板 正電源端子→U1 腳 5', 'mono', 'VCC', 'J5.1', 'U1.5', 'rail1'),
    ('放大板 負電源端子→U1 腳 4', 'mono', 'VEE', 'J5.3', 'U1.4', 'rail1'),
    ('放大板 470µF C7→U1 腳 1', 'mono', 'VCC', 'C7.1', 'U1.1', 'rail1'),
    ('放大板 470µF C6→U1 腳 4', 'mono', 'VEE', 'C6.2', 'U1.4', 'rail1'),
    ('電源板 正軌 電容→L 輸出', 'psu', 'VCC', 'C202.1', 'J203.1', 'rail1'),
    ('電源板 正軌 電容→R 輸出', 'psu', 'VCC', 'C202.1', 'J204.1', 'rail1'),
    ('電源板 負軌 電容→L 輸出', 'psu', 'VEE', 'C204.2', 'J203.3', 'rail1'),
    ('電源板 負軌 電容→R 輸出', 'psu', 'VEE', 'C204.2', 'J204.3', 'rail1'),
    ('電源板 地 STAR→L 輸出', 'psu', 'GND', 'STAR', 'J203.2', 'output'),
    ('電源板 地 STAR→R 輸出', 'psu', 'GND', 'STAR', 'J204.2', 'output'),
    ('電源板 正橋→第一顆電容', 'psu', 'VCC', 'BR1.P', 'C202.1', 'charge'),
    ('電源板 正橋充電回地', 'psu', 'GND', 'C202.2', 'BR1.N', 'charge'),
    ('電源板 負橋→第一顆電容', 'psu', 'VEE', 'BR2.N', 'C204.2', 'charge'),
    ('電源板 負橋充電回地', 'psu', 'GND', 'C204.1', 'BR2.P', 'charge'),
    ('電源板 AC 端子→保險絲（+）', 'psu', 'POS_AC1', 'J201.1', 'F201.1', 'charge'),
    ('電源板 保險絲→正橋', 'psu', 'POS_AC_FUSED', 'F201.2', 'BR1.AC1', 'charge'),
    ('電源板 AC 回線（+）', 'psu', 'POS_AC2', 'BR1.AC2', 'J201.2', 'charge'),
    ('電源板 AC 端子→保險絲（−）', 'psu', 'NEG_AC1', 'J202.1', 'F202.1', 'charge'),
    ('電源板 保險絲→負橋', 'psu', 'NEG_AC_FUSED', 'F202.2', 'BR2.AC1', 'charge'),
    ('電源板 AC 回線（−）', 'psu', 'NEG_AC2', 'BR2.AC2', 'J202.2', 'charge'),
]
T1OZ = A.THICKNESS[0]
rows = []; lines = ['| 路徑 | 長度 mm | 最窄 V0.6→V0.6.1 | R V0.6 mΩ | R V0.6.1 mΩ | 變化 | 峰值 A | 峰值壓降 V0.6.1 mV | 發熱 V0.6.1 mW |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for title, board, net, a, b, cur in SPECS:
    r = {v: A.path(data[board, v], net, a, b) for v in ['06', '061']}
    ir, ip = CURRENTS[cur]
    R = {v: A.resistance(r[v], T1OZ, 25) for v in r}
    rows.append({'name': title, 'board': board, 'net': net, 'from': a, 'to': b, 'current_model': cur, 'rms_A': ir, 'peak_A': ip,
                 'versions': {v: {'geometry': r[v], 'R_1oz_25C_ohm': R[v], 'R_2oz_25C_ohm': A.resistance(r[v], A.THICKNESS[1], 25),
                                  'R_1oz_85C_ohm': A.resistance(r[v], T1OZ, 85), 'peak_drop_V': ip * R[v], 'heat_W': ir * ir * R[v]} for v in r}})
    lines.append(f"| {title} | {r['061']['length_mm']:.0f} | {r['06']['min_width_mm']:.1f}→{r['061']['min_width_mm']:.1f} | {R['06']*1000:.1f} | {R['061']*1000:.1f} | {(R['061']/R['06']-1)*100:+.0f} % | {ip:.1f} | {ip*R['061']*1000:.0f} | {ir*ir*R['061']*1000:.0f} |")
feedback = {v: {'sense_mm': A.path(data['mono', v], 'L_OUT', 'U1.3', 'R4.2', 'length')['length_mm'],
                'inverting_mm': A.path(data['mono', v], 'L_INV', 'U1.9', 'R4.1', 'length')['length_mm']} for v in ['06', '061']}
coupling = {v: A.coupling_screen(data['mono', v]) for v in ['06', '061']}
report = {'assumptions': {'Vrail': 30, 'load_ohm': 8, 'sizing_output_W': 40, 'Iq_per_rail_A': iq, 'rho25_ohm_mm': A.RHO, 'alpha_per_C': A.ALPHA,
                          'copper_thickness_mm': A.THICKNESS, 'charge_duty': duty,
                          'note': 'Centreline copper only; 1 oz nominal; 85 C and 2 oz are input sensitivities, not predictions. No thermal rise, inductance, pad, via, solder, connector, wire or ESR terms.'},
          'current_cases': {k: {'rms_A': v[0], 'peak_A': v[1]} for k, v in CURRENTS.items()}, 'paths': rows, 'feedback_lengths': feedback,
          'projected_coupling_screen': coupling,
          'sha256': {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in FILES.values()}}
(ROOT / 'pcb/current-budget-v061.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('\n'.join(lines))
print('\nfeedback lengths', feedback)
print('coupling', json.dumps(coupling, ensure_ascii=False))
tot = {v: sum(r['versions'][v]['heat_W'] for r in rows) for v in ['06', '061']}
print('sum heat W', tot)
