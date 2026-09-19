"""PCB B-layout engineering draft with explicit routing. NOT FOR FABRICATION.
Run in KiCad 10 Python environment after schematic netlist export.
All footprint dimensions are provisional, including the LM3886 lead pattern.
"""
from pathlib import Path
from pcb_layout_v03 import AMP, PSU
from silk_marks_v03 import silk_marks, silk_texts
import pcbnew as p
import xml.etree.ElementTree as ET
import math,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'pcb';OUT.mkdir(exist_ok=True)
LIB=OUT/'DraftV03.pretty';LIB.mkdir(exist_ok=True)
MM=p.FromMM
def v(x,y):return p.VECTOR2I(MM(x),MM(y))
def xy(a):return (p.ToMM(a.x),p.ToMM(a.y))
specs={}
def make_fp(name,pads,body,kind='rect'):
 f=p.FOOTPRINT(None);f.SetFPID(p.LIB_ID('DraftV03',name));f.SetAttributes(p.FP_THROUGH_HOLE)
 for num,x,y,diam,drill in pads:
  pad=p.PAD(f);pad.SetNumber(str(num));pad.SetAttribute(p.PAD_ATTRIB_PTH);pad.SetShape(p.PAD_SHAPE_CIRCLE)
  pad.SetSize(v(diam,diam));pad.SetDrillSize(v(drill,drill));pad.SetPosition(v(x,y));pad.SetLayerSet(p.PAD.PTHMask());f.Add(pad)
 x0,y0,x1,y1=body
 for layer,inflate in [(p.F_SilkS,0),(p.F_CrtYd,.5)]:
  sh=p.PCB_SHAPE(f);sh.SetLayer(layer);sh.SetWidth(MM(.15 if layer==p.F_SilkS else .05))
  if layer==p.F_CrtYd:
   sh.SetShape(p.SHAPE_T_RECT)
   sh.SetStart(v(min(x0,min(x-d/2 for _,x,y,d,h in pads))-.5,min(y0,min(y-d/2 for _,x,y,d,h in pads))-.5))
   sh.SetEnd(v(max(x1,max(x+d/2 for _,x,y,d,h in pads))+.5,max(y1,max(y+d/2 for _,x,y,d,h in pads))+.5))
  elif kind=='circle':sh.SetShape(p.SHAPE_T_CIRCLE);sh.SetCenter(v((x0+x1)/2,(y0+y1)/2));sh.SetEnd(v(x1+inflate,(y0+y1)/2))
  else:sh.SetShape(p.SHAPE_T_RECT);sh.SetStart(v(x0-inflate,y0-inflate));sh.SetEnd(v(x1+inflate,y1+inflate))
  f.Add(sh)
 f.Reference().SetPosition(v((x0+x1)/2,y0-1.7));f.Reference().SetTextSize(v(1,1));f.Reference().SetTextThickness(MM(.15))
 f.Value().SetVisible(False)
 for seg,w in silk_marks(name,pads,body):
  sh=p.PCB_SHAPE(f);sh.SetLayer(p.F_SilkS);sh.SetWidth(MM(w));sh.SetShape(p.SHAPE_T_SEGMENT);sh.SetStart(v(*seg[0]));sh.SetEnd(v(*seg[1]));f.Add(sh)
 for text,(tx,ty),size in silk_texts(name,pads,body):
  t=p.PCB_TEXT(f);t.SetText(text);t.SetLayer(p.F_SilkS);t.SetPosition(v(tx,ty));t.SetTextSize(v(size,size));t.SetTextThickness(MM(.12));f.Add(t)
 p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP).FootprintSave(str(LIB),f)
 specs[name]={'body':body,'kind':kind,'pads':pads}
 return name
make_fp('R_P7.5',[(1,0,0,1.8,.8),(2,7.5,0,1.8,.8)],(1.2,-1.25,6.3,1.25))
make_fp('R_2W_P20',[(1,0,0,2.4,1),(2,20,0,2.4,1)],(2.5,-2.5,17.5,2.5))
make_fp('Film_P15',[(1,0,0,2,1),(2,15,0,2,1)],(-1.5,-4,16.5,4))
make_fp('Film_P5',[(1,0,0,1.8,.8),(2,5,0,1.8,.8)],(-1.5,-2,6.5,2))
for name,dia,pitch in [('BP_D10_P5',10,5),('CP_D12.5_P5',12.5,5),('CP_D8_P3.5',8,3.5),('CP_D35_P10',35,10)]:
 make_fp(name,[(1,0,0,3 if dia==35 else 2,1.3 if dia==35 else .9),(2,pitch,0,3 if dia==35 else 2,1.3 if dia==35 else .9)],(pitch/2-dia/2,-dia/2,pitch/2+dia/2,dia/2),'circle')
make_fp('Terminal2_P5.08',[(1,0,0,3,1.3),(2,5.08,0,3,1.3)],(-2.5,-4,7.58,4))
make_fp('Terminal3_P5.08',[(i+1,5.08*i,0,3,1.3) for i in range(3)],(-2.5,-4,12.66,4))
make_fp('Header2_P2.54',[(1,0,0,1.8,1),(2,2.54,0,1.8,1)],(-1.3,-1.3,3.84,1.3))
make_fp('AirCoil_P20',[(1,0,0,3,1.3),(2,20,0,3,1.3)],(2,-7,18,7))
make_fp('Fuse5x20_P25',[(1,0,0,3,1.3),(2,25,0,3,1.3)],(-2,-3.5,27,3.5))
make_fp('Bridge_LOGICAL_UNVERIFIED',[(num,x,y,4,1.5) for num,x,y in [('AC1',0,0),('AC2',0,17.5),('P',17.5,0),('N',17.5,17.5)]],(-6,-6,23.5,23.5))
make_fp('LM3886T_UNVERIFIED',[(i,1.7*(i-1),0 if i%2 else -5.08,1.65,.9) for i in range(1,12)],(-1.5,-12,18.5,-7))

def netlist(file):
 r=ET.parse(ROOT/'electrical'/file).getroot()
 values={c.get('ref'):c.findtext('value') for c in r.findall('components/comp')}
 nodes={}
 for n in r.findall('nets/net'):
  for x in n: nodes[(x.get('ref'),x.get('pin'))]=n.get('name').lstrip('/')
 return values,nodes
def build(name,size,layout,source,routes,anchors,labels):
 board=p.BOARD();board.SetCopperLayerCount(2);board.GetDesignSettings().SetBoardThickness(MM(1.6))
 vals,nodes=netlist(source);nets={};pads={};parts=[];tracks=[]
 for ref,(fpname,x,y,angle) in layout.items():
  f=p.FootprintLoad(str(LIB),fpname);f.SetReference(ref);f.SetValue(vals[ref]);f.SetPosition(v(x,y));f.SetOrientationDegrees(angle)
  for pad in f.Pads():
   number=pad.GetNumber();net=nodes[(ref,number)]
   if net not in nets:
    nets[net]=p.NETINFO_ITEM(board,net);board.Add(nets[net])
   pad.SetNet(nets[net]);pads[(ref,number)]=pad
  if ref=='U1':f.Reference().SetPosition(v(47.5,4.5))
  if ref=='C3':f.Reference().SetPosition(v(34.5,23))
  if ref=='J1':f.Reference().SetPosition(v(90,36))
  if ref=='J203':f.Reference().SetPosition(v(150,48))
  if ref in ('C201','C202','C203','C204'):f.Reference().SetPosition(v(x,y-6))
  if ref=='R201':f.Reference().SetPosition(v(97,44))
  if ref=='R202':f.Reference().SetPosition(v(97,106))
  board.Add(f)
  parts.append({'ref':ref,'value':vals[ref],'footprint':fpname,'x':x,'y':y,'angle':angle,**specs[fpname]})
 w,h=size
 for a,b in [((0,0),(w,0)),((w,0),(w,h)),((w,h),(0,h)),((0,h),(0,0))]:
  sh=p.PCB_SHAPE();sh.SetShape(p.SHAPE_T_SEGMENT);sh.SetStart(v(*a));sh.SetEnd(v(*b));sh.SetLayer(p.Edge_Cuts);sh.SetWidth(MM(.05));board.Add(sh)
 # Explicitly separate mounting holes from schematic components.
 for i,(x,y) in enumerate([(4,4),(w-4,4),(4,h-4),(w-4,h-4)],1):
  f=p.FOOTPRINT(board);f.SetReference('H'+str(i));f.SetValue('M3 provisional');f.Reference().SetVisible(False);f.Value().SetVisible(False)
  pad=p.PAD(f);pad.SetNumber('');pad.SetAttribute(p.PAD_ATTRIB_NPTH);pad.SetShape(p.PAD_SHAPE_CIRCLE);pad.SetSize(v(3.2,3.2));pad.SetDrillSize(v(3.2,3.2));pad.SetLayerSet(p.PAD.PTHMask());f.Add(pad);f.SetPosition(v(x,y));board.Add(f)
 def label(s,x,y,sz):
  t=p.PCB_TEXT(board);t.SetText(s);t.SetPosition(v(x,y));t.SetTextSize(v(sz,sz));t.SetTextThickness(MM(.15));t.SetLayer(p.F_SilkS);board.Add(t)
 label('PLACEMENT DRAFT - NOT FOR FAB',w/2,h-4,1)
 for text,x,y in labels:label(text,x,y,1)
 def pos(item):
  if isinstance(item,str):
   if item in anchors:return tuple(anchors[item])
   ref,num=item.split('.')
   return xy(pads[(ref,num)].GetPosition())
  return tuple(item)
 vias=[];unattempted=[]
 for route in routes:
  net,layer,width,path,group=route
  points=[pos(pt) for pt in path]
  for u,z in zip(points,points[1:]):
   if math.dist(u,z)<.001:continue
   t=p.PCB_TRACK(board);t.SetStart(v(*u));t.SetEnd(v(*z));t.SetWidth(MM(width));t.SetLayer(p.F_Cu if layer=='F.Cu' else p.B_Cu);t.SetNet(nets[net]);board.Add(t)
   tracks.append({'a':u,'b':z,'width':width,'layer':layer,'net':net,'group':group})
 # Every named layer transition is a real plated via, never an apparent crossing.
 for key,point in anchors.items():
  if not key.startswith('via_'):continue
  touched=[t for t in tracks if tuple(point) in (tuple(t['a']),tuple(t['b']))]
  codes={t['net'] for t in touched};assert len(codes)==1,(key,codes)
  if len({t['layer'] for t in touched})<2:continue
  diam,drill=(1.6,.8) if key.startswith('via_power') else (.9,.4)
  net=codes.pop();via=p.PCB_VIA(board);via.SetPosition(v(*point));via.SetWidth(MM(diam));via.SetDrill(MM(drill));via.SetViaType(p.VIATYPE_THROUGH);via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNet(nets[net]);board.Add(via)
  vias.append({'x':point[0],'y':point[1],'net':net,'dia':diam,'drill':drill})
 path=OUT/(name+'.kicad_pcb');p.SaveBoard(str(path),board)
 # Independent round-trip pad-to-net audit, including each NC pin.
 check=p.LoadBoard(str(path));actual={(f.GetReference(),pad.GetNumber()):pad.GetNetname() for f in check.GetFootprints() if f.GetReference() in layout for pad in f.Pads()}
 expected={k:n for k,n in nodes.items() if k[0] in layout}
 assert actual==expected,(actual,expected)
 data={'name':name,'size':size,'parts':parts,'tracks':tracks,'pads':[{'ref':key[0],'number':key[1],'net':pad.GetNetname(),'x':xy(pad.GetPosition())[0],'y':xy(pad.GetPosition())[1],'dia':p.ToMM(pad.GetSize().x),'drill':p.ToMM(pad.GetDrillSize().x)} for key,pad in pads.items()], 'vias':vias,'anchors':anchors,'pending_connections':unattempted,'verified_pad_count':len(actual)}
 (OUT/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 print(name,len(layout),'components',len(actual),'pad nets verified;',len(tracks),'segments;',len(unattempted),'pending connection pairs')
 return data

if __name__=='__main__':
 for config in (AMP,PSU):
  data=build(**config)
  (OUT/(data['name']+'-footprints.csv')).write_text('reference,footprint,status\n'+''.join(f"{part['ref']},{part['footprint']},UNVERIFIED - ordered IC and transformer still in transit; all other MPNs TBD\n" for part in data['parts']))
 print('V0.3 layout B: routed engineering draft; no manufacturing release.')

 # SaveBoard can create/reset the sibling project. Apply draft rules AFTER all boards save.
 for config in (AMP,PSU):
  project=OUT/(config['name']+'.kicad_pro')
  settings=json.loads(project.read_text())
  settings['board']['design_settings']['rules'].update(min_clearance=.3,min_track_width=.35,min_copper_edge_clearance=.5,min_via_annular_width=.2,min_silk_clearance=.15)
  settings['net_settings']['classes'][0]['clearance']=.3
  project.write_text(json.dumps(settings,indent=2)+'\n')
