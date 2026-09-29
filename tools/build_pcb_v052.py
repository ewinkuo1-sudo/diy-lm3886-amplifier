"""PCB V0.5.2 candidate (one merged amplifier+filter board per channel). NOT FOR FABRICATION.
Reuses the DraftV03 footprint library and build() from build_pcb_v03, add_zones() from build_pcb_v04 and the
upright C2 footprint from build_pcb_v05. Adds Terminal4_P5.08 (4-way 5.08 mm screw terminal for the DC feed
from the two chassis bridges). Run tools/make_netlist_v052.py first, then this in the KiCad 10 Python environment.
"""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_pcb_v03 as v03
from build_pcb_v04 import add_zones
import build_pcb_v05   # registers BP_Axial_Vert_D20_P15 in the library
from pcb_layout_v052 import AMP_V052
import pcbnew as p

OUT=v03.OUT
v03.make_fp('Terminal4_P5.08',[(i+1,5.08*i,0,3,1.3) for i in range(4)],(-2.5,-4,17.74,4))
REFS={**build_pcb_v05.REFS_AMP,'R201':(41,91),'R202':(49,91),'C205':(16.5,130),'C206':(62.5,130),'J6':(37.6,126.5)}
REFS.pop('J5',None)
BOARDS=(AMP_V052,)

if __name__=='__main__':
 for config in BOARDS:
  zones=config.get('zones',[]);data=v03.build(**{k:v for k,v in config.items() if k!='zones'})
  path=OUT/(data['name']+'.kicad_pcb');board=p.LoadBoard(str(path))
  if zones:
   nets={n.GetNetname():n for n in board.GetNetInfo().NetsByName().values()}
   data['zones']=add_zones(board,zones,nets);(OUT/(data['name']+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
  for f in board.GetFootprints():
   if f.GetReference() in REFS:
    f.Reference().SetPosition(v03.v(*REFS[f.GetReference()]))
  p.SaveBoard(str(path),board);v03.lf(path)
  (OUT/(data['name']+'-footprints.csv')).write_text('reference,footprint,status\n'+''.join(f"{part['ref']},{part['footprint']},UNVERIFIED - provisional DraftV03 outlines (BP_Axial_Vert_D20_P15 pitch and Terminal4_P5.08 unmeasured); see docs/00\n" for part in data['parts']))
 print('V0.5.2 board: routed engineering draft; no manufacturing release.')
 for config in BOARDS:
  project=OUT/(config['name']+'.kicad_pro')
  settings=json.loads(project.read_text())
  settings['board']['design_settings']['rules'].update(min_clearance=.3,min_track_width=.35,min_copper_edge_clearance=.5,min_via_annular_width=.2,min_silk_clearance=.15)
  settings['net_settings']['classes'][0]['clearance']=.3
  project.write_text(json.dumps(settings,indent=2)+'\n')
