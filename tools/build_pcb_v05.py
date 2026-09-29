"""PCB V0.5 engineering draft (chassis-fit shrink of V0.4 D + PSU). NOT FOR FABRICATION.
Reuses the DraftV03 footprint library and build() from build_pcb_v03 plus add_zones() from build_pcb_v04;
only the layout definitions (pcb_layout_v05.py, pcb_layout_v05_psu.py) differ. Adds one footprint:
BP_Axial_Vert_D20_P15 (ROE EGW 47uF standing upright, folded lead at 15 mm). Run in the KiCad 10 Python
environment after `kicad-cli sch export netlist` (see pcb/README.md).
"""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_pcb_v03 as v03
from build_pcb_v04 import add_zones
from pcb_layout_v05 import AMP_V05
from pcb_layout_v05_psu import PSU_V05
import pcbnew as p

OUT=v03.OUT
# ROE EGW 47uF BP measured 2026-09-23: body ~40 x D20 axial, lead 0.8-1.0 mm. Upright: pad 1 under the body
# centre (lead straight down), pad 2 = other lead folded down along the body, 15 mm pitch (assumption, check by
# bending the real part; body radius 10 + sleeve + bend). Drill 1.2 as in the flat footprint.
v03.make_fp('BP_Axial_Vert_D20_P15',[(1,0,0,2.6,1.2),(2,15,0,2.6,1.2)],(-10,-10,10,10),'circle')
REFS_AMP={'U1':(60,3),'C3':(54.5,19),'C4':(54.5,24.5),'J1':(78,33),'C2':(77,65),'J5':(50.8,72),'C5':(59,45),'R5':(36,58),'R4':(61.2,21.75),'R3':(70.8,21.75),'R1':(76,18),'C1':(79,11),'L1':(9.5,55),'R7':(20.5,55),'R2':(66.25,11.6),'C8':(69.5,74.5),'JP1':(80,68.5)}
REFS_PSU={'J203':(31,124),'J204':(86,124),'C207':(12,27),'C208':(12,47),'R203':(12,67),'C209':(113,27),'C210':(113,47),'R204':(113,67),'C205':(54.5,104.5),'C206':(70.5,104.5),'R201':(57,54),'R202':(68,54),'J201':(6,22.8),'J202':(119,22.8),'BR1':(28,16),'BR2':(96,16)}
REF_POS={'mono-layout-v05d':REFS_AMP,'psu-layout-v05':REFS_PSU}
BOARDS=(AMP_V05,PSU_V05)

if __name__=='__main__':
 for config in BOARDS:
  zones=config.get('zones',[]);data=v03.build(**{k:v for k,v in config.items() if k!='zones'})
  path=OUT/(data['name']+'.kicad_pcb');board=p.LoadBoard(str(path))
  if zones:
   nets={n.GetNetname():n for n in board.GetNetInfo().NetsByName().values()}
   data['zones']=add_zones(board,zones,nets);(OUT/(data['name']+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
  for f in board.GetFootprints():
   if f.GetReference() in REF_POS.get(data['name'],{}):
    f.Reference().SetPosition(v03.v(*REF_POS[data['name']][f.GetReference()]))
  p.SaveBoard(str(path),board);v03.lf(path)
  (OUT/(data['name']+'-footprints.csv')).write_text('reference,footprint,status\n'+''.join(f"{part['ref']},{part['footprint']},UNVERIFIED - same provisional DraftV03 outlines as V0.3/V0.4 (BP_Axial_Vert_D20_P15 new, pitch unmeasured); see docs/00\n" for part in data['parts']))
 print('V0.5 boards: routed engineering drafts; no manufacturing release.')
 for config in BOARDS:
  project=OUT/(config['name']+'.kicad_pro')
  settings=json.loads(project.read_text())
  settings['board']['design_settings']['rules'].update(min_clearance=.3,min_track_width=.35,min_copper_edge_clearance=.5,min_via_annular_width=.2,min_silk_clearance=.15)
  settings['net_settings']['classes'][0]['clearance']=.3
  project.write_text(json.dumps(settings,indent=2)+'\n')
