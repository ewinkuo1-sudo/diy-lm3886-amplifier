"""V0.6 amplifier / PSU checks: native DRC clean, pad nets match the schematic netlists, pads inside the outline,
amplifier GND pour is one region, the IC tab back sits on the heatsink edge (footprint body touches y = 0), and on the
PSU the GBJ bodies plus their 10 mm heatsink envelope (now on the +y / fuse side) clear every other part. Geometry
only. Writes pcb/validation-v06.json.
"""
from pathlib import Path
import json, hashlib, datetime, math, xml.etree.ElementTree as ET
R = Path(__file__).resolve().parents[1]
BOARDS = {'mono-layout-v06': ('mono-v06-drc', 'netlist.xml'), 'psu-layout-v06': ('psu-v06-drc', 'psu-netlist.xml')}
report = {'status': 'PASS', 'checked_on': datetime.date.today().isoformat(), 'boards': {}, 'sha256': {}}


def box(part, inflate=0):
    x0, y0, x1, y1 = part['body']; a = math.radians(part['angle'])
    pts = [(part['x'] + x * math.cos(a) + y * math.sin(a), part['y'] - x * math.sin(a) + y * math.cos(a)) for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]
    xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
    return (min(xs) - inflate, min(ys) - inflate, max(xs) + inflate, max(ys) + inflate)


def overlap(a, b): return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


for name, (drc_name, netlist) in BOARDS.items():
    data = json.loads((R / 'pcb' / f'{name}.json').read_text(encoding='utf-8'))
    drc = json.loads((R / 'pcb' / f'{drc_name}.json').read_text(encoding='utf-8'))
    errors = [v for v in drc['violations'] if v['severity'] == 'error']
    assert not errors and not drc['unconnected_items'], (name, len(errors), len(drc['unconnected_items']))
    expected = {}
    for net in ET.parse(R / 'electrical' / netlist).findall('nets/net'):
        for node in net: expected[(node.get('ref'), node.get('pin'))] = net.get('name').lstrip('/')
    refs = {p['ref'] for p in data['parts']}
    expected = {k: v for k, v in expected.items() if k[0] in refs}
    actual = {(p['ref'], p['number']): p['net'] for p in data['pads']}
    assert actual == expected, (name, 'pad net mismatch', set(actual.items()) ^ set(expected.items()))
    w, h = data['size']
    for pad in data['pads']:
        assert 0.5 <= pad['x'] - pad['dia'] / 2 and pad['x'] + pad['dia'] / 2 <= w - 0.5 and 0.5 <= pad['y'] - pad['dia'] / 2 and pad['y'] + pad['dia'] / 2 <= h - 0.5, (name, pad['ref'], 'pad outside edge clearance')
    entry = {'size_mm': data['size'], 'parts': len(data['parts']), 'pad_net_count': len(actual), 'native_DRC_errors': 0,
             'native_DRC_warnings': len(drc['violations']) - len(errors), 'native_DRC_unconnected': 0,
             'tracks': len(data['tracks']), 'vias': len(data['vias'])}
    parts = {p['ref']: p for p in data['parts']}
    if name.startswith('mono'):
        regions = [len(z['filled']) for z in data['zones']]
        entry['gnd_pour_regions'] = regions
        assert regions == [1], (name, 'GND pour split into', regions)
        u1 = box(parts['U1'])
        entry['u1_tab_back_y_mm'] = round(u1[1], 2)
        assert -0.5 <= u1[1] <= 0.3, (name, 'U1 tab back not at the heatsink edge', u1)
        entry['u1_odd_row_y_mm'] = parts['U1']['y']
    else:
        HS = 10.0
        bridges = {}
        for ref in ('BR1', 'BR2'):
            b = parts[ref]; assert b['footprint'] == 'GBJ_Upright_P10_7.5_7.5' and b['angle'] == 180, ref
            body = box(b, 0.5); hs = (body[0], body[3], body[2], body[3] + HS)       # metal back toward +y
            for other, o in parts.items():
                if other == ref: continue
                ob = box(o, 0.5)
                assert not overlap(body, ob), (ref, 'body overlaps', other)
                assert not overlap(hs, ob), (ref, 'heatsink envelope overlaps', other)
            fuse = parts['F201' if ref == 'BR1' else 'F202']
            bridges[ref] = {'body_mm': [round(x, 2) for x in body], 'heatsink_envelope_mm': [round(x, 2) for x in hs],
                            'gap_to_fuse_body_mm': round(box(fuse)[1] - hs[3], 2)}
        entry['bridges'] = bridges
        entry['snubber_provisions_placed'] = False
        entry['unplaced_schematic_parts'] = sorted({k[0] for net in ET.parse(R / 'electrical' / netlist).findall('nets/net') for k in [(n.get('ref'),) for n in net]} - refs)
    report['boards'][name] = entry
    for f in [R / 'pcb' / f'{name}.kicad_pcb', R / 'pcb' / f'{name}.kicad_pro', R / 'pcb' / f'{drc_name}.json']:
        report['sha256'][f.relative_to(R).as_posix()] = hashlib.sha256(f.read_bytes()).hexdigest()
report['kicad_version'] = drc['kicad_version']
report['limits'] = ('Draft only. U1 uses the KiCad library TO-220-11 geometry (tab back 9.58 mm behind the odd pin row), not the ICs in hand; '
                    'PSU snubber provisions C207-C210/R203/R204 are not placed; no electrical, thermal or enclosure test.')
(R / 'pcb' / 'validation-v06.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report['boards'], indent=1))
