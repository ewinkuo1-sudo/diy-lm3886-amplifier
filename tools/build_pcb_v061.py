"""PCB V0.6.1 engineering drafts (V0.6 with wider power copper; see pcb_layout_v061.py): amplifier board (90 x 80, IC flush with the heatsink edge) and PSU (92 x 120).
NOT FOR FABRICATION. Reuses build() from build_pcb_v03, add_zones() from build_pcb_v04, the GBJ footprint from
build_pcb_v051 and import_std() from build_pcb_v06_ctrl. New footprint: LM3886T_TO220-11, copied from the KiCad
library TO-220-11 StaggerOdd vertical footprint (datasheet geometry, 3D model attached). Run in the KiCad 10 Python
environment after `kicad-cli sch export netlist` of lm3886-v01 and internal-psu-v02.
"""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_pcb_v03 as v03
from build_pcb_v04 import add_zones
import build_pcb_v051            # defines GBJ_Upright_P10_7.5_7.5 at import time
from build_pcb_v06_ctrl import import_std
from pcb_layout_v061 import AMP_V061 as AMP_V06, PSU_V061 as PSU_V06
import pcbnew as p
OUT = v03.OUT; v = v03.v

# ROE EGW 47uF BP standing upright (as V0.5): pad 1 under the body, pad 2 = folded lead at 15 mm (assumption).
v03.make_fp('BP_Axial_Vert_D20_P15', [(1, 0, 0, 2.6, 1.2), (2, 15, 0, 2.6, 1.2)], (-10, -10, 10, 10), 'circle')
# LM3886T as TO-220-11 vertical (KiCad library): odd pins at y 0, even pins at y -5.08, tab back at y -9.58.
import_std('Package_TO_SOT_THT', 'TO-220-11_P3.4x5.08mm_StaggerOdd_Lead4.58mm_Vertical', 'LM3886T_TO220-11')

REFS = {
    'mono-layout-v061': {'U1': (62, 7), 'C3': (54.5, 15), 'C4': (55, 21), 'J1': (78, 33), 'C2': (77, 64), 'J5': (50.8, 62), 'C5': (59, 45),
                        'R5': (36, 58), 'R4': (61.2, 21.75), 'R3': (70.8, 21.75), 'R1': (76, 18), 'C1': (79, 11), 'L1': (9.5, 55), 'R7': (20.5, 55),
                        'R2': (66.25, 11.6), 'C8': (60.5, 72), 'JP1': (80, 60.5), 'J2': (10, 68.5), 'R8': (69.75, 62), 'C7': (36, 27), 'C6': (54, 27)},
    'psu-layout-v061': {'J203': (17, 10.5), 'J204': (73, 10.5), 'C205': (35.5, 7), 'C206': (86.5, 7), 'R201': (41, 40), 'R202': (53, 64),
                       'BR1': (18, 97), 'BR2': (73, 97), 'F201': (20.5, 101.5), 'F202': (69.5, 101.5), 'J201': (14.5, 111.3), 'J202': (77.5, 111.3),
                       'C201': (26, 25), 'C202': (26, 63), 'C203': (76, 25), 'C204': (76, 63)},
}

if __name__ == '__main__':
    for config in (AMP_V06, PSU_V06):
        zones = config.get('zones', []); data = v03.build(**{k: val for k, val in config.items() if k != 'zones'})
        path = OUT / (data['name'] + '.kicad_pcb'); board = p.LoadBoard(str(path))
        if zones:
            nets = {n.GetNetname(): n for n in board.GetNetInfo().NetsByName().values()}
            data['zones'] = add_zones(board, zones, nets)
            (OUT / (data['name'] + '.json')).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        for f in board.GetFootprints():
            if f.GetReference() in REFS.get(data['name'], {}):
                f.Reference().SetPosition(v(*REFS[data['name']][f.GetReference()]))
        p.SaveBoard(str(path), board); v03.lf(path)
        (OUT / (data['name'] + '-footprints.csv')).write_text('reference,footprint,status\n' + ''.join(
            f"{part['ref']},{part['footprint']},UNVERIFIED - DraftV03 provisional outline, or KiCad library TO-220-11 for U1 (datasheet geometry, not checked against the ICs in hand); see docs/00\n" for part in data['parts']))
    print('V0.6.1 amplifier + PSU: routed engineering drafts; no manufacturing release.')
    for config in (AMP_V06, PSU_V06):
        project = OUT / (config['name'] + '.kicad_pro')
        settings = json.loads(project.read_text())
        settings['board']['design_settings']['rules'].update(min_clearance=.3, min_track_width=.35, min_copper_edge_clearance=.5, min_via_annular_width=.2, min_silk_clearance=.15)
        settings['net_settings']['classes'][0]['clearance'] = .3
        project.write_text(json.dumps(settings, indent=2) + '\n')
