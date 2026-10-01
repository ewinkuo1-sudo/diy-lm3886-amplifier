"""V0.6 CTRL / MAINS checks: native DRC clean, pad nets match the schematic netlists, every pad inside the
outline with edge clearance, the CTRL ground pour is one connected region, and on MAINS the copper of the
mains nets keeps >= 6.4 mm from every low-voltage copper item (pads and tracks, edge to edge). Geometry
only: not a safety certification, not thermal or EMC validation. Writes pcb/validation-v06-ctrl.json.
"""
from pathlib import Path
import json, hashlib, datetime, math, xml.etree.ElementTree as ET
R = Path(__file__).resolve().parents[1]
BOARDS = {'ctrl-layout-v06': ('ctrl-v06-drc', 'control-v01-netlist.xml'), 'mains-layout-v06': ('mains-v06-drc', 'mains-v01-netlist.xml')}
MAINS_NETS = {'L_IN', 'L_SW', 'L_T1', 'N_IN'}
CREEPAGE = 6.4
report = {'status': 'PASS', 'checked_on': datetime.date.today().isoformat(), 'boards': {}, 'sha256': {}}


def seg_dist(a, b, c, d):
    """Minimum distance between segments ab and cd (2-D)."""
    def pd(p, a, b):
        ax, ay = a; bx, by = b; px, py = p; dx, dy = bx - ax, by - ay
        if dx == dy == 0: return math.dist(p, a)
        t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
        return math.dist(p, (ax + t * dx, ay + t * dy))
    def cross(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    if (cross(a, b, c) * cross(a, b, d) < 0) and (cross(c, d, a) * cross(c, d, b) < 0): return 0.0
    return min(pd(a, c, d), pd(b, c, d), pd(c, a, b), pd(d, a, b))


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
    if data.get('zones'):
        regions = [len(z['filled']) for z in data['zones']]
        entry['gnd_pour_regions'] = regions
        assert regions == [1], (name, 'GND pour split into', regions)
    if name.startswith('mains'):
        items = []   # (net, kind, geometry)
        for pad in data['pads']:
            items.append((pad['net'], 'pad', ((pad['x'], pad['y']), (pad['x'], pad['y']), pad['dia'] / 2)))
        for t in data['tracks']:
            items.append((t['net'], 'track', (tuple(t['a']), tuple(t['b']), t['width'] / 2)))
        worst = (99, None, None)
        for n1, k1, (a1, b1, r1) in items:
            if n1 not in MAINS_NETS: continue
            for n2, k2, (a2, b2, r2) in items:
                if n2 in MAINS_NETS: continue
                d = seg_dist(a1, b1, a2, b2) - r1 - r2
                if d < worst[0]: worst = (d, (n1, k1), (n2, k2))
        entry['mains_to_lowvoltage_min_mm'] = round(worst[0], 2)
        entry['mains_to_lowvoltage_pair'] = [worst[1], worst[2]]
        assert worst[0] >= CREEPAGE, (name, 'creepage', worst)
    report['boards'][name] = entry
    for f in [R / 'pcb' / f'{name}.kicad_pcb', R / 'pcb' / f'{name}.kicad_pro', R / 'pcb' / f'{drc_name}.json']:
        report['sha256'][f.relative_to(R).as_posix()] = hashlib.sha256(f.read_bytes()).hexdigest()
for f in [R / 'electrical/control-v01.kicad_sch', R / 'electrical/mains-v01.kicad_sch']:
    report['sha256'][f.relative_to(R).as_posix()] = hashlib.sha256(f.read_bytes()).hexdigest()
report['kicad_version'] = drc['kicad_version']
report['limits'] = ('Draft only. Relay / UPC1237 / NTC footprints from the KiCad library or datasheets, no part in hand; '
                    'creepage check is copper-to-copper on the PCB only (connector bodies, wiring and chassis not included); '
                    'no electrical, thermal or safety test.')
(R / 'pcb' / 'validation-v06-ctrl.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report['boards'], indent=1))
