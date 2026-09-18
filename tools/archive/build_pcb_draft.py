# 歷史腳本（已歸檔）：只重建 pcb/archive/ 內的舊版板檔，不影響現行 V0.3；輸出路徑已改指向歸檔資料夾。
"""Editable PCB placement + partial routing study. NOT FOR FABRICATION.
Run in KiCad 10 Python environment after schematic netlist export.
All footprint dimensions are provisional, including the LM3886 lead pattern.
"""
from pathlib import Path
import pcbnew as p
import xml.etree.ElementTree as ET
import math,json,csv,heapq

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'pcb/archive/v01';OUT.mkdir(parents=True,exist_ok=True)
LIB=OUT/'Draft.pretty';LIB.mkdir(exist_ok=True)
MM=p.FromMM
def v(x,y):return p.VECTOR2I(MM(x),MM(y))
def xy(a):return (p.ToMM(a.x),p.ToMM(a.y))
specs={}
def make_fp(name,pads,body,kind='rect'):
 f=p.FOOTPRINT(None);f.SetFPID(p.LIB_ID('Draft',name));f.SetAttributes(p.FP_THROUGH_HOLE)
 for num,x,y,diam,drill in pads:
  pad=p.PAD(f);pad.SetNumber(str(num));pad.SetAttribute(p.PAD_ATTRIB_PTH);pad.SetShape(p.PAD_SHAPE_CIRCLE)
  pad.SetSize(v(diam,diam));pad.SetDrillSize(v(drill,drill));pad.SetPosition(v(x,y));pad.SetLayerSet(p.PAD.PTHMask());f.Add(pad)
 x0,y0,x1,y1=body
 for layer,inflate in [(p.F_SilkS,0),(p.F_CrtYd,.5)]:
  sh=p.PCB_SHAPE(f);sh.SetLayer(layer);sh.SetWidth(MM(.15 if layer==p.F_SilkS else .05))
  if kind=='circle':sh.SetShape(p.SHAPE_T_CIRCLE);sh.SetCenter(v((x0+x1)/2,(y0+y1)/2));sh.SetEnd(v(x1+inflate,(y0+y1)/2))
  else:sh.SetShape(p.SHAPE_T_RECT);sh.SetStart(v(x0-inflate,y0-inflate));sh.SetEnd(v(x1+inflate,y1+inflate))
  f.Add(sh)
 f.Reference().SetPosition(v((x0+x1)/2,y0-1.7));f.Reference().SetTextSize(v(1,1));f.Reference().SetTextThickness(MM(.15))
 f.Value().SetVisible(False)
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
def segment_distance(a,b,c):
 dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy
 t=max(0,min(1,((c[0]-a[0])*dx+(c[1]-a[1])*dy)/den)) if den else 0
 return math.hypot(c[0]-a[0]-t*dx,c[1]-a[1]-t*dy)
def intersect(a,b,c,d):
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 return cross(a,b,c)*cross(a,b,d)<0 and cross(c,d,a)*cross(c,d,b)<0
def segdist(a,b,c,d):
 if intersect(a,b,c,d):return 0
 return min(segment_distance(a,b,c),segment_distance(a,b,d),segment_distance(c,d,a),segment_distance(c,d,b))
def build(name,size,layout,source,skip_ground=False):
 board=p.BOARD();board.SetCopperLayerCount(2);board.GetDesignSettings().SetBoardThickness(MM(1.6))
 vals,nodes=netlist(source);nets={};pads={};parts=[];tracks=[]
 for ref,(fpname,x,y,angle) in layout.items():
  f=p.FootprintLoad(str(LIB),fpname);f.SetReference(ref);f.SetValue(vals[ref]);f.SetPosition(v(x,y));f.SetOrientationDegrees(angle)
  for pad in f.Pads():
   number=pad.GetNumber();net=nodes[(ref,number)]
   if net not in nets:
    nets[net]=p.NETINFO_ITEM(board,net);board.Add(nets[net])
   pad.SetNet(nets[net]);pads[(ref,number)]=pad
  if ref=='U1': f.Reference().SetPosition(v(43.5,5))
  if ref=='L1': f.Reference().SetPosition(v(18,57.5))
  if ref=='C6': f.Reference().SetPosition(v(48.5,44.1))
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
 label('MONO x2 / TAB=VEE' if skip_ground else '2x22VAC / DUAL BRIDGE / 4x10000uF',w/2,h-8,1)
 # Route only obstacle-clear endpoint-to-endpoint candidates; all others stay unrouted.
 # No guessed ground plane: amplifier signal and load-return topology remains explicit work.
 groups={}
 for key,pad in pads.items():groups.setdefault(pad.GetNetname(),[]).append(key)
 unattempted=[]
 for net,keys in sorted(groups.items(),key=lambda kv: (kv[0] in ('VCC','VEE','GND'),kv[0])):
  if len(keys)<2 or net.startswith('unconnected-'):continue
  connected={keys[0]};remaining=set(keys[1:]);pairs=[]
  while remaining:
   _,a,b=min((math.dist(xy(pads[a].GetPosition()),xy(pads[b].GetPosition())),a,b) for a in connected for b in remaining)
   pairs.append((a,b));connected.add(b);remaining.remove(b)
  for ka,kb in pairs:
   a,b=xy(pads[ka].GetPosition()),xy(pads[kb].GetPosition())
   if net=='GND' and skip_ground:unattempted.append([ka,kb,net]);continue
   width=(1.0 if net in ('VCC','VEE','GND') or net.endswith(('_OUT','_SPK')) else .35) if skip_ground else 2.0
   candidates=[[a,b],[a,(a[0],b[1]),b],[a,(b[0],a[1]),b]]
   for offset in (3,-3,6,-6,10,-10):
    candidates.extend([[a,(a[0]+offset,a[1]),(a[0]+offset,b[1]),b],[a,(a[0],a[1]+offset),(b[0],a[1]+offset),b]])
   def clear(path,layer):
    for u,z in zip(path,path[1:]):
     if any(not(.8<pt[0]<w-.8 and .8<pt[1]<h-.8) for pt in [u,z]):return False
     for key,pad in pads.items():
      if pad.GetNetname()==net:continue
      if segment_distance(u,z,xy(pad.GetPosition()))<p.ToMM(pad.GetSize().x)/2+width/2+.3:return False
     for x,y in [(4,4),(w-4,4),(4,h-4),(w-4,h-4)]:
      if segment_distance(u,z,(x,y))<2.1+width/2:return False
     for tr in tracks:
      if tr['net']!=net and tr['layer']==layer and segdist(u,z,tr['a'],tr['b'])<width/2+tr['width']/2+.3:return False
    return True
   choice=next(((path,layer) for path in candidates for layer in ['F.Cu','B.Cu'] if clear(path,layer)),None)
   if not choice:unattempted.append([ka,kb,net]);continue
   path,layer=choice
   for u,z in zip(path,path[1:]):
    if math.dist(u,z)<.001:continue
    t=p.PCB_TRACK(board);t.SetStart(v(*u));t.SetEnd(v(*z));t.SetWidth(MM(width));t.SetLayer(p.F_Cu if layer=='F.Cu' else p.B_Cu);t.SetNet(nets[net]);board.Add(t)
    tracks.append({'a':u,'b':z,'width':width,'layer':layer,'net':net})
 path=OUT/(name+'.kicad_pcb');p.SaveBoard(str(path),board)
 # Independent round-trip pad-to-net audit, including each NC pin.
 check=p.LoadBoard(str(path));actual={(f.GetReference(),pad.GetNumber()):pad.GetNetname() for f in check.GetFootprints() if f.GetReference() in layout for pad in f.Pads()}
 expected={k:n for k,n in nodes.items() if k[0] in layout}
 assert actual==expected,(actual,expected)
 data={'name':name,'size':size,'parts':parts,'tracks':tracks,'pads':[{'ref':key[0],'number':key[1],'net':pad.GetNetname(),'x':xy(pad.GetPosition())[0],'y':xy(pad.GetPosition())[1],'dia':p.ToMM(pad.GetSize().x),'drill':p.ToMM(pad.GetDrillSize().x)} for key,pad in pads.items()], 'pending_connections':unattempted,'verified_pad_count':len(actual)}
 (OUT/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 print(name,len(layout),'components',len(actual),'pad nets verified;',len(tracks),'segments;',len(unattempted),'pending connection pairs')
 return data

amp={
 'U1':('LM3886T_UNVERIFIED',35,14,0),
 'J1':('Terminal2_P5.08',80,36,90),'J2':('Terminal2_P5.08',9,54,90),'J5':('Terminal3_P5.08',40,61,0),
 'C1':('Film_P15',61,36,0),'R1':('R_P7.5',69,46,0),'R6':('R_P7.5',57,23,0),'R2':('R_P7.5',72,22,90),
 'R4':('R_P7.5',45,21,0),'R3':('R_P7.5',49,27,0),'C2':('BP_D10_P5',58,46,0),
 'C3':('Film_P5',35,23,0),'C4':('Film_P5',29,26,90),
 'C7':('CP_D12.5_P5',28,43,0),'C6':('CP_D12.5_P5',40,43,0),
 'R5':('R_2W_P20',12,20,270),'C5':('Film_P5',15,50,0),
 'L1':('AirCoil_P20',8,33,270),'R7':('R_2W_P20',20,28,270),
 'R8':('R_P7.5',56,54,0),'C8':('CP_D8_P3.5',69,57,0),'JP1':('Header2_P2.54',80,58,90)}
# L1 uses 270 degrees -> pads progress downward; keep body inside the outline.
amp.update({'J1':('Terminal2_P5.08',84,38,90),'J2':('Terminal2_P5.08',9,64,0),'J5':('Terminal3_P5.08',40,64,0),'C1':('Film_P15',76,36,180),'C7':('CP_D12.5_P5',35,51,0),'C6':('CP_D12.5_P5',46,36,0),'R5':('R_2W_P20',8,26,0), 'C4':('Film_P5',30,19,90),'C5':('Film_P5',18,9,0),'L1':('AirCoil_P20',8,48,0),'R7':('R_2W_P20',8,37,0),'R8':('R_P7.5',56,57,0),'C8':('CP_D8_P3.5',69,59,0)})
psu={
 'J201':('Terminal2_P5.08',10,15,90),'J202':('Terminal2_P5.08',10,66,90),
 'F201':('Fuse5x20_P25',18,14,0),'F202':('Fuse5x20_P25',18,66,0),
 'BR1':('Bridge_LOGICAL_UNVERIFIED',28,27,0),'BR2':('Bridge_LOGICAL_UNVERIFIED',28,78,0),
 'C201':('CP_D35_P10',72,27,0),'C202':('CP_D35_P10',113,27,0),
 'C203':('CP_D35_P10',72,78,0),'C204':('CP_D35_P10',113,78,0),
 'C205':('Film_P5',68,51,0),'C206':('Film_P5',96,55,0),
 'R201':('R_2W_P20',67,6,0),'R202':('R_2W_P20',108,6,0),
 'J203':('Terminal3_P5.08',140,48,270)}
a=build('mono-placement-v01',(90,80),amp,'netlist.xml',True)
b=build('psu-placement-v01',(150,110),psu,'psu-netlist.xml')
with (OUT/'footprint-assumptions.csv').open('w',encoding='utf-8',newline='') as f:
 wr=csv.writer(f);wr.writerow(['board','reference','value','draft_footprint','status'])
 for data in (a,b):
  for x in data['parts']:wr.writerow([data['name'],x['ref'],x['value'],x['footprint'],'UNVERIFIED dimensional placeholder; verify actual MPN before fabrication'])
with (OUT/'mono-channel-mapping.csv').open('w',encoding='utf-8',newline='') as f:
 wr=csv.writer(f);wr.writerow(['mono_board_ref','left_schematic_ref','right_schematic_ref'])
 for ref in amp:
  right={'U1':'U2','J1':'J3','J2':'J4','J5':'J5 (shared PSU split into two harnesses)','JP1':'JP2','L1':'L2'}.get(ref)
  if right is None:right=ref[0]+str(int(ref[1:])+100)
  wr.writerow([ref,ref,right])
(OUT/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Draft")(type "KiCad")(uri "${KIPRJMOD}/Draft.pretty")(options "")(descr "Unverified draft placeholders")))\n')
print('No Gerbers generated. Ground return routing and all MPN dimensions remain open.')




