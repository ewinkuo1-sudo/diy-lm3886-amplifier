"""V0.6.1: V0.6 amplifier board (90 x 80) and PSU (92 x 120) with wider copper on every load-current path.
Same parts, same part positions, same nets, same board sizes, same chassis (弘宙 102, heatsinks 150 x 90 x 30 inside
the side walls) as V0.6 -- only track widths (and two trunk waypoints) change. NOT FOR FABRICATION.

Why: tools/analyze_pcb_v061.py (copper-path screen, same model as analyze_pcb_v03) put the V0.6 power paths at
2-30 mohm each on 1 oz copper. Small next to the transformer DCR (0.25 / 0.2 ohm measured) and the relay contacts,
but a few segments were thinner than the 0.3 mm clearance rule forces them to be, so this revision widens whatever
the neighbouring pads allow. Every limit below was checked against pad centres and radii before DRC:

Amplifier (mm, V0.6 -> V0.6.1)
 - VEE drop C4.2 -> U1.4 between pins 3 and 5: 0.5 -> 0.9. Hard limit: pads 1.8 on a 3.4 same-row pitch leave 1.6,
   minus 2 x 0.3 clearance = 1.0, and the 2.0 output stub leaving pin 3 sticks 0.1 past its pad, so 0.9 + stub 1.8.
   This one segment was 54 % of the J5 -> U1.4 path resistance.
 - V+ link U1.1 - U1.5 on B.Cu between the pin rows: 1.0 -> 2.0 (row gap 5.08 minus pads leaves 3.28).
 - Bulk caps to IC: C7 -> U1.1 (B.Cu) 2.0 -> 3.0; C6 -> C4.2 (F.Cu) 1.5 -> 2.5.
 - Feed J5.1 -> C7: 3.0 -> 4.0. Feed J5.3 -> C6: 3.0 -> 3.5 only (its x = 58 run sits between C5 at x = 55 and
   C2.2 at x = 62; 4.0 would touch C2.2).
 - Output trunk: pin-3 stub 2.0 -> 1.8 (see above), riser 2.5 -> 3.0, trunk to L1 3.0 -> 4.0 with the two trunk
   waypoints moved 0.6 up-left ((34,31.5)->(33.4,30.9), (22,43.5)->(21.4,42.9)) so the 4.0 trunk clears the 4.0
   VCC feed ending on C7.1; the Zobel feed now ends on the moved vertex. L1 -> R7 1.5 -> 3.0, L1 -> J2 3.0 -> 4.0.
 - Signal, feedback, mute, Zobel stubs: unchanged.
PSU (mm, V0.6 -> V0.6.1)
 - Rail / AC trunks 3.0 -> 5.0; VEE output runs 2.5 -> 4.0; NEG_AC2 return 2.0 -> 4.0 (it was the one AC trunk
   thinner than the rest and the hottest segment in the 15 % duty charge scenario).
 - GND star line 3.0 -> 4.0 (5.0 would sit 0.30 from the R202.2 pad at (50,74)).
 - J201.2 -> (13.5,110) stays 3.0 and the 5.0 column starts at y = 110 (a 5.0 end cap at the old (13.5,112.5)
   vertex overlapped the J201.1 pad); the two ground drops into J203.2 / J204.2
   stay 3.0 beside their 5.0 columns because the 3-way terminal pads are 3.0 on a 5.08 pitch.
 - Bleeder and 100 nF bypass stubs (0.8 / 1.0) carry no load current and are unchanged.
"""
import copy
from pcb_layout_v06 import AMP_V06, PSU_V06

# (net, group, V0.6 width) -> V0.6.1 width. Anything not listed keeps its V0.6 width.
AMP_WIDTHS = {
    ('VEE', 'negative-pin', 0.5): 0.9,
    ('VCC', 'positive-local', 2.0): 3.0,
    ('VEE', 'negative-local', 1.5): 2.5,
    ('VCC', 'positive-feed', 3.0): 4.0,
    ('VEE', 'negative-feed', 3.0): 3.5,
    ('L_OUT', 'output-power', 2.0): 1.8,
    ('L_OUT', 'output-power', 2.5): 3.0,
    ('L_OUT', 'output-power', 3.0): 4.0,
    ('L_OUT', 'output-power', 1.5): 3.0,
    ('L_SPK', 'speaker', 3.0): 4.0,
}
PSU_WIDTHS = {
    ('VCC', 'positive-bank', 3.0): 5.0, ('VCC', 'positive-output', 3.0): 5.0, ('VCC', 'positive-charge', 3.0): 5.0,
    ('VEE', 'negative-bank', 3.0): 5.0, ('VEE', 'negative-output', 2.5): 4.0, ('VEE', 'negative-charge', 3.0): 5.0,
    ('VEE', 'bleeder', 3.0): 5.0,
    ('GND', 'positive-bank-return', 3.0): 5.0, ('GND', 'negative-bank-return', 3.0): 5.0,
    ('GND', 'output-ground', 3.0): 5.0, ('GND', 'star', 3.0): 4.0,
    ('GND', 'positive-charge-return', 3.0): 5.0, ('GND', 'negative-charge-return', 3.0): 5.0,
    ('POS_AC1', 'ac-positive', 3.0): 5.0, ('POS_AC_FUSED', 'ac-positive', 3.0): 5.0, ('POS_AC2', 'ac-positive', 3.0): 5.0,
    ('NEG_AC1', 'ac-negative', 3.0): 5.0, ('NEG_AC_FUSED', 'ac-negative', 3.0): 5.0, ('NEG_AC2', 'ac-negative', 2.0): 4.0,
}


def _key(route): return (route[0], route[1], route[4], route[3][0])


def _widen(config, name, table, per_route=(), replace=()):
    """Copy a V0.6 config, rename it, rewrite widths by (net, group, width), then by (net, layer, group, first point),
    then replace whole routes keyed the same way."""
    cfg = copy.deepcopy(config); cfg['name'] = name; routes = []
    for net, layer, width, pts, group in cfg['routes']:
        new = table.get((net, group, width), width)
        for k, w in per_route:
            if (net, layer, group, pts[0]) == k: new = w
        routes.append((net, layer, new, pts, group))
    out = []
    for r in routes:
        hit = [new for k, new in replace if _key(r) == k]
        out.extend(hit[0] if hit else [r])
    cfg['routes'] = out
    return cfg


AMP_V061 = _widen(AMP_V06, 'mono-layout-v061', AMP_WIDTHS, per_route=[
    (('VCC', 'B.Cu', 'positive-pin', 'U1.1'), 2.0),      # pin 1 - pin 5 link between the rows
], replace=[
    (('L_OUT', 'F.Cu', 'output-power', (40.5, 25)), [('L_OUT', 'F.Cu', 4.0, [(40.5, 25), (33.4, 30.9), (21.4, 42.9), 'L1.1'], 'output-power')]),
    (('L_OUT', 'F.Cu', 'zobel-feed', 'R5.2'), [('L_OUT', 'F.Cu', 1.2, ['R5.2', (21.4, 42.9)], 'zobel-feed')]),
])
PSU_V061 = _widen(PSU_V06, 'psu-layout-v061', PSU_WIDTHS, replace=[
    (('GND', 'B.Cu', 'output-ground', 'C201.2'), [('GND', 'B.Cu', 5.0, ['C201.2', (16, 12)], 'output-ground'),
                                                  ('GND', 'B.Cu', 3.0, [(16, 12), (17.08, 8), 'J203.2'], 'output-ground')]),
    (('GND', 'B.Cu', 'output-ground', 'C203.1'), [('GND', 'B.Cu', 5.0, ['C203.1', (76, 13)], 'output-ground'),
                                                  ('GND', 'B.Cu', 3.0, [(76, 13), (74, 11), (74, 6), 'J204.2'], 'output-ground')]),
    (('POS_AC2', 'B.Cu', 'ac-positive', 'J201.2'), [('POS_AC2', 'B.Cu', 3.0, ['J201.2', (13.5, 110)], 'ac-positive'),
                                                    ('POS_AC2', 'B.Cu', 5.0, [(13.5, 110), 'BR1.AC2'], 'ac-positive')]),
])
