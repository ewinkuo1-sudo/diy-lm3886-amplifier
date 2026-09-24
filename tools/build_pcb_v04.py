"""PCB V0.4 engineering draft (variant C first). NOT FOR FABRICATION.
Reuses the DraftV03 footprint library and build() from build_pcb_v03; only the
layout definition (pcb_layout_v04.py) differs. Run in the KiCad 10 Python environment
after `kicad-cli sch export netlist` (see pcb/README.md).
"""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_pcb_v03 as v03
from pcb_layout_v04 import AMP_C,AMP_D
import pcbnew as p

OUT=v03.OUT
# Reference labels that build() pins for V0.3 land on other parts in V0.4; move them after the fact.
REFS={'U1':(60,3),'C3':(54.5,19),'C4':(54.5,24.5),'J1':(90,21.5),'C2':(87,66),'J5':(50.8,72),'C5':(59,45),'R5':(36,58),'R4':(61.2,21.75),'R3':(70.8,21.75),'R1':(76.75,16.9),'C1':(78.5,2.5),'L1':(9.5,55),'R7':(20.5,55),'R2':(66.25,11.6)}
REF_POS={'mono-layout-v04c':REFS,'mono-layout-v04d':REFS}
BOARDS=(AMP_C,AMP_D)
MM=v03.MM
def add_zones(board,zones,nets):
 out=[]
 for net,layer,outline in zones:
  z=p.ZONE(board);z.SetLayer(p.F_Cu if layer=='F.Cu' else p.B_Cu);z.SetNet(nets[net]);z.SetLocalClearance(MM(.3));z.SetMinThickness(MM(.35))
  z.SetPadConnection(p.ZONE_CONNECTION_THERMAL);z.SetThermalReliefGap(MM(.5));z.SetThermalReliefSpokeWidth(MM(.8));z.SetZoneName(net+'_'+layer)
  poly=z.Outline();poly.NewOutline()
  for x,y in outline:poly.Append(MM(x),MM(y))
  board.Add(z);out.append(z)
 p.ZONE_FILLER(board).Fill(board.Zones())
 data=[]
 for z,(net,layer,outline) in zip(out,zones):
  polys=z.GetFilledPolysList(z.GetFirstLayer());rings=[]
  for i in range(polys.OutlineCount()):
   o=polys.Outline(i);ring={'outer':[(p.ToMM(o.CPoint(j).x),p.ToMM(o.CPoint(j).y)) for j in range(o.PointCount())],'holes':[]}
   for h in range(polys.HoleCount(i)):
    ho=polys.Hole(i,h);ring['holes'].append([(p.ToMM(ho.CPoint(j).x),p.ToMM(ho.CPoint(j).y)) for j in range(ho.PointCount())])
   rings.append(ring)
  data.append({'net':net,'layer':layer,'outline':outline,'filled':rings})
 return data

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
  (OUT/(data['name']+'-footprints.csv')).write_text('reference,footprint,status\n'+''.join(f"{part['ref']},{part['footprint']},UNVERIFIED - same provisional DraftV03 outlines as V0.3; see pcb/mono-layout-v03-footprints.csv and docs/00\n" for part in data['parts']))
 print('V0.4 variant C: routed engineering draft; no manufacturing release.')
 for config in BOARDS:
  project=OUT/(config['name']+'.kicad_pro')
  settings=json.loads(project.read_text())
  settings['board']['design_settings']['rules'].update(min_clearance=.3,min_track_width=.35,min_copper_edge_clearance=.5,min_via_annular_width=.2,min_silk_clearance=.15)
  settings['net_settings']['classes'][0]['clearance']=.3
  project.write_text(json.dumps(settings,indent=2)+'\n')
