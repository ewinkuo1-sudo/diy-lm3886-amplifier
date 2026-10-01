"""PCB V0.5.1 engineering draft: V0.5 PSU with GBJ2510 bridges on board. NOT FOR FABRICATION.
Only the power-supply board is rebuilt; the amplifier board stays V0.5 (mono-layout-v05d). Reuses the DraftV03
footprint library and build() from build_pcb_v03. Adds one footprint, GBJ_Upright_P10_7.5_7.5, with oval pads
for the 1.0 x 2.2 mm flat leads (make_fp only knows round pads). Run in the KiCad 10 Python environment after
`kicad-cli sch export netlist` (see pcb/README.md).
"""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_pcb_v03 as v03
from pcb_layout_v051_psu import PSU_V051
import pcbnew as p
OUT=v03.OUT;v=v03.v;MM=v03.MM

def make_fp_oval(name,pads,body,drill_xy,size_xy,texts=(),marks=()):
 """pads: (number,x,y) with a shared oblong drill/size (mm, x along the lead row). body: silk rectangle."""
 f=p.FOOTPRINT(None);f.SetFPID(p.LIB_ID('DraftV03',name));f.SetAttributes(p.FP_THROUGH_HOLE)
 for num,x,y in pads:
  pad=p.PAD(f);pad.SetNumber(str(num));pad.SetAttribute(p.PAD_ATTRIB_PTH);pad.SetShape(p.PAD_SHAPE_OVAL)
  pad.SetSize(v(*size_xy));pad.SetDrillShape(p.PAD_DRILL_SHAPE_OBLONG);pad.SetDrillSize(v(*drill_xy));pad.SetPosition(v(x,y));pad.SetLayerSet(p.PAD.PTHMask());f.Add(pad)
 x0,y0,x1,y1=body;half=max(size_xy)/2
 for layer,inflate in [(p.F_SilkS,0),(p.F_CrtYd,.5)]:
  sh=p.PCB_SHAPE(f);sh.SetLayer(layer);sh.SetWidth(MM(.15 if layer==p.F_SilkS else .05));sh.SetShape(p.SHAPE_T_RECT)
  if layer==p.F_CrtYd:
   sh.SetStart(v(min(x0,min(x-half for _,x,y in pads))-.5,min(y0,min(y-half for _,x,y in pads))-.5))
   sh.SetEnd(v(max(x1,max(x+half for _,x,y in pads))+.5,max(y1,max(y+half for _,x,y in pads))+.5))
  else:sh.SetStart(v(x0,y0));sh.SetEnd(v(x1,y1))
  f.Add(sh)
 for (a,b),w in marks:
  sh=p.PCB_SHAPE(f);sh.SetLayer(p.F_SilkS);sh.SetWidth(MM(w));sh.SetShape(p.SHAPE_T_SEGMENT);sh.SetStart(v(*a));sh.SetEnd(v(*b));f.Add(sh)
 for text,(tx,ty),size in texts:
  t=p.PCB_TEXT(f);t.SetText(text);t.SetLayer(p.F_SilkS);t.SetPosition(v(tx,ty));t.SetTextSize(v(size,size));t.SetTextThickness(MM(.12));f.Add(t)
 f.Reference().SetPosition(v((x0+x1)/2,y0-1.7));f.Reference().SetTextSize(v(1,1));f.Reference().SetTextThickness(MM(.15));f.Value().SetVisible(False)
 p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP).FootprintSave(str(v03.LIB),f);v03.lf(v03.LIB/(name+'.kicad_mod'))
 # specs entry in make_fp's shape so render/verify treat the pad as a circle of the long dimension
 v03.specs[name]={'body':body,'kind':'rect','pads':[(num,x,y,max(size_xy),max(drill_xy)) for num,x,y in pads]}
 return name

# GBJ2510 (Diodes DS21221, May 2025): A 30 wide, D 3.8-4.2 thick, leads H 2.0-2.4 x I 0.9-1.1 (flat, wide side along the
# row), pitch G 9.8-10.2 then E 7.3-7.7 twice, first lead J 2.3-2.7 from the body end; polarity + ~ ~ - moulded on the
# marked face. Drill 2.6 x 1.4 oblong (0.2 mm per side), pad 3.8 x 2.6. Marked face toward +y, metal back toward -y.
make_fp_oval('GBJ_Upright_P10_7.5_7.5',[('P',0,0),('AC1',10,0),('AC2',17.5,0),('N',25,0)],(-2.5,-2,27.5,2),(2.6,1.4),(3.8,2.6),
 texts=[('+',(0,3.6),1),('~',(10,3.6),1),('~',(17.5,3.6),1),('-',(25,3.6),1),('HS',(12.5,-4.0),.9)],
 marks=[(((-2.5,-2.6),(27.5,-2.6)),.4)])   # thick line = metal back / heatsink face

REFS_PSU={'J203':(31,124),'J204':(86,124),'C207':(12,27),'C208':(12,47),'R203':(12,67),'C209':(113,27),'C210':(113,47),'R204':(113,67),'C205':(54.5,104.5),'C206':(70.5,104.5),'R201':(57,54),'R202':(68,54),'J201':(6,22.8),'J202':(119,22.8),'BR1':(50,23),'BR2':(112,23)}

if __name__=='__main__':
 data=v03.build(**PSU_V051)
 path=OUT/(data['name']+'.kicad_pcb');board=p.LoadBoard(str(path))
 for f in board.GetFootprints():
  if f.GetReference() in REFS_PSU:f.Reference().SetPosition(v(*REFS_PSU[f.GetReference()]))
 p.SaveBoard(str(path),board);v03.lf(path)
 (OUT/(data['name']+'-footprints.csv')).write_text('reference,footprint,status\n'+''.join(f"{part['ref']},{part['footprint']},UNVERIFIED - same provisional DraftV03 outlines as V0.5 (GBJ_Upright_P10_7.5_7.5 new from Diodes DS21221, part not yet in hand); see docs/00\n" for part in data['parts']))
 print('V0.5.1 PSU: routed engineering draft; no manufacturing release.')
 project=OUT/(PSU_V051['name']+'.kicad_pro')
 settings=json.loads(project.read_text())
 settings['board']['design_settings']['rules'].update(min_clearance=.3,min_track_width=.35,min_copper_edge_clearance=.5,min_via_annular_width=.2,min_silk_clearance=.15)
 settings['net_settings']['classes'][0]['clearance']=.3
 project.write_text(json.dumps(settings,indent=2)+'\n')
