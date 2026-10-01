"""PCB V0.6 engineering drafts for the control / protection board (CTRL) and the mains soft-start board
(MAINS). NOT FOR FABRICATION. Reuses build() from build_pcb_v03 and add_zones() from build_pcb_v04.

Footprints: relays, SIP-8, DIP-4, TO-92, TO-220, DO-41 and DO-35 are copied from the KiCad 10 library
(share/kicad/footprints) into pcb/DraftV03.pretty with pad numbers renamed to the schematic pin names, so the
3D models (${KICAD10_3DMODEL_DIR}) stay attached. Provisional outlines are made here for the NTC disc and
the small radial capacitors. Run in the KiCad 10 Python environment after
`kicad-cli sch export netlist` of control-v01 and mains-v01.
"""
from pathlib import Path
import json, re, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_pcb_v03 as v03
from build_pcb_v04 import add_zones
from pcb_layout_v06_ctrl import CTRL_V06, MAINS_V06
import pcbnew as p
OUT = v03.OUT; LIB = v03.LIB; v = v03.v; MM = v03.MM
KICAD_FP = Path(r'C:\Users\ewink\AppData\Local\Programs\KiCad\10.0\share\kicad\footprints')


def import_std(lib, src, name, rename=None, drop=()):
    """Copy a KiCad library footprint into DraftV03.pretty, renaming/dropping pads, and register its specs."""
    text = (KICAD_FP / (lib + '.pretty') / (src + '.kicad_mod')).read_text(encoding='utf-8')
    text = text.replace(f'(footprint "{src}"', f'(footprint "{name}"', 1)
    # drop whole pad blocks, then rename pad numbers
    for num in drop:
        text = re.sub(r'\n\t\(pad "%s" .*?\n\t\)' % re.escape(num), '', text, flags=re.S)
    for old, new in (rename or {}).items():
        text = text.replace(f'(pad "{old}" ', f'(pad "{new}" ')
    (LIB / (name + '.kicad_mod')).write_text(text, encoding='utf-8', newline='\n')
    f = p.FootprintLoad(str(LIB), name)
    bb = f.GetCourtyard(p.F_CrtYd).BBox()
    if bb.GetWidth() == 0:
        bb = f.GetBoundingBox(False, False)
    body = (p.ToMM(bb.GetLeft()), p.ToMM(bb.GetTop()), p.ToMM(bb.GetRight()), p.ToMM(bb.GetBottom()))
    pads = [(pad.GetNumber(), p.ToMM(pad.GetPosition().x), p.ToMM(pad.GetPosition().y),
             max(p.ToMM(pad.GetSize().x), p.ToMM(pad.GetSize().y)), p.ToMM(pad.GetDrillSize().x)) for pad in f.Pads()]
    v03.specs[name] = {'body': body, 'kind': 'rect', 'pads': pads}
    return name


def footprints():
    # Omron G2RL-1-E: IEC numbering 11 = COM, 12 = NC (unused, removed), 14 = NO; two pads per contact terminal.
    import_std('Relay_THT', 'Relay_SPDT_Omron_G2RL-1-E', 'Relay_G2RL-1-E', {'11': 'COM', '14': 'NO'}, drop=('12',))
    import_std('Package_SIP', 'SIP-8_19x3mm_P2.54mm', 'SIP-8_P2.54')
    import_std('Package_DIP', 'DIP-4_W7.62mm', 'Opto_DIP-4', {'1': 'A', '2': 'K', '3': 'E', '4': 'C'})
    # TO-92 with spread leads (2.54 pitch): the 1.27 mm inline footprint breaks the 0.3 mm / 0.2 mm board rules
    import_std('Package_TO_SOT_THT', 'TO-92_Inline_Wide', 'TO-92W_CBE', {'1': 'C', '2': 'B', '3': 'E'})        # BC327: C B E
    import_std('Package_TO_SOT_THT', 'TO-92_Inline_Wide', 'TO-92W_REF-A-K', {'1': 'REF', '2': 'A', '3': 'K'})  # TL431 LP: REF A K
    import_std('Package_TO_SOT_THT', 'TO-220-3_Vertical', 'TO-220_IN-GND-OUT', {'1': 'IN', '2': 'GND', '3': 'OUT'})
    import_std('Diode_THT', 'D_DO-41_SOD81_P10.16mm_Horizontal', 'D_DO-41_P10.16')   # pad 1 = cathode
    import_std('Diode_THT', 'D_DO-35_SOD27_P7.62mm_Horizontal', 'D_DO-35_P7.62')
    # provisional outlines (DraftV03 style): NTC disc, small radial electrolytics
    v03.make_fp('NTC_D22_P10', [(1, 0, 0, 2.6, 1.3), (2, 10, 0, 2.6, 1.3)], (5 - 11.5, -11.5, 5 + 11.5, 11.5), 'circle')
    v03.make_fp('CP_D5_P2', [(1, 0, 0, 1.6, 0.8), (2, 2, 0, 1.6, 0.8)], (1 - 2.75, -2.75, 1 + 2.75, 2.75), 'circle')
    v03.make_fp('CP_D6.3_P2.5', [(1, 0, 0, 1.6, 0.8), (2, 2.5, 0, 1.6, 0.8)], (1.25 - 3.4, -3.4, 1.25 + 3.4, 3.4), 'circle')


REFS = {
    'ctrl-layout-v06': {'K301': (18, 38), 'K302': (18, 42), 'U302': (38, 62), 'U303': (50, 24.5), 'U304': (62, 24.5),
                        'J301': (58, 35), 'J302': (28.5, 10.5), 'J303': (12, 10.5), 'J304': (46.5, 10.5), 'J305': (58.5, 10.5),
                        'J306': (61.5, 101.5), 'J307': (17.5, 110), 'J308': (29.5, 110), 'J309': (8.5, 94),
                        'C301': (58, 80), 'C304': (60, 92), 'U301': (55, 101.5), 'U305': (41, 103.8), 'Q301': (39.5, 48.5), 'Q302': (56.5, 117.5),
                        'D306': (49, 64), 'D307': (49, 68), 'D308': (49, 72), 'D309': (49, 76), 'D305': (33.8, 104.5), 'R310': (6, 104),
                        'R313': (49.25, 104.3), 'R314': (49.25, 112), 'R315': (47.75, 117)},
    'mains-layout-v06': {'K401': (24, 26), 'K402': (24, 56), 'RT401': (40, 60), 'J401': (56, 18), 'J402': (56, 34),
                         'J405': (56, 83), 'J403': (8.5, 4.5), 'J404': (8.5, 76), 'D402': (17, 13.5)},
}

if __name__ == '__main__':
    footprints()
    for config in (CTRL_V06, MAINS_V06):
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
            f"{part['ref']},{part['footprint']},UNVERIFIED - KiCad library outline (relays, SIP/DIP/TO, diodes) or provisional DraftV03 outline (NTC, small radials); no part in hand yet\n" for part in data['parts']))
    print('V0.6 CTRL + MAINS: routed engineering drafts; no manufacturing release.')
    for k in ('Relay_G2RL-1-E','SIP-8_P2.54','Opto_DIP-4','TO-92W_CBE','TO-220_IN-GND-OUT','D_DO-41_P10.16','D_DO-35_P7.62'):
        print(k, 'body', [round(x,2) for x in v03.specs[k]['body']], 'pads', [(n,x,y,round(d,2)) for n,x,y,d,h in v03.specs[k]['pads']])
    for config in (CTRL_V06, MAINS_V06):
        project = OUT / (config['name'] + '.kicad_pro')
        settings = json.loads(project.read_text())
        settings['board']['design_settings']['rules'].update(min_clearance=.3, min_track_width=.35, min_copper_edge_clearance=.5, min_via_annular_width=.2, min_silk_clearance=.15)
        settings['net_settings']['classes'][0]['clearance'] = .3
        project.write_text(json.dumps(settings, indent=2) + '\n')
