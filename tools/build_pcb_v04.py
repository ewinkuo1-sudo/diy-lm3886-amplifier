"""PCB V0.4 engineering draft (variant C first). NOT FOR FABRICATION.
Reuses the DraftV03 footprint library and build() from build_pcb_v03; only the
layout definition (pcb_layout_v04.py) differs. Run in the KiCad 10 Python environment
after `kicad-cli sch export netlist` (see pcb/README.md).
"""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_pcb_v03 as v03
from pcb_layout_v04 import AMP_C
import pcbnew as p

OUT=v03.OUT
# Reference labels that build() pins for V0.3 land on other parts in V0.4; move them after the fact.
REF_POS={'mono-layout-v04c':{'U1':(60,3),'C3':(54.5,19),'C4':(54.5,24.5),'J1':(90,21.5),'C2':(87,66),'J5':(50.8,72),'C5':(59,45),'R5':(36,58),'R4':(61.2,21.75),'R3':(70.8,21.75),'R1':(76.75,16.9),'C1':(78.5,2.5),'L1':(9.5,55),'R7':(20.5,55),'R2':(66.25,11.6)}}
BOARDS=(AMP_C,)

if __name__=='__main__':
 for config in BOARDS:
  data=v03.build(**config)
  path=OUT/(data['name']+'.kicad_pcb');board=p.LoadBoard(str(path))
  for f in board.GetFootprints():
   if f.GetReference() in REF_POS.get(data['name'],{}):
    f.Reference().SetPosition(v03.v(*REF_POS[data['name']][f.GetReference()]))
  p.SaveBoard(str(path),board);v03.lf(path)
  (OUT/(data['name']+'-footprints.csv')).write_text('reference,footprint,status\n'+''.join(f"{part['ref']},{part['footprint']},UNVERIFIED - same provisional DraftV03 outlines as V0.3; see pcb/mono-layout-v03-footprints.csv and docs/00\n" for part in data['parts']))
 print('V0.4 variant C: routed engineering draft; no manufacturing release.')
 for config in BOARDS:
  project=OUT/(config['name']+'.kicad_pro')
  settings=json.loads(project.read_text())
  settings['board']['design_settings']['rules'].update(min_clearance=.3,min_track_width=.35,min_copper_edge_clearance=.5,min_via_annular_width=.2,min_silk_clearance=.15)
  settings['net_settings']['classes'][0]['clearance']=.3
  project.write_text(json.dumps(settings,indent=2)+'\n')
