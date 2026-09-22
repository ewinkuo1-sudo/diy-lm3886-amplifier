"""Generate review drawings, explicit provisional VRML models, and part audit.
No changes to electrical/layout sources. Python stdlib; native exports/render separate.
"""
from pathlib import Path
import json, math, hashlib, re, html
R=Path(__file__).resolve().parents[1]; P=R/'pcb'; O=P/'inspection-v03'
(O/'3d/models').mkdir(parents=True,exist_ok=True); (O/'drawings').mkdir(exist_ok=True);(O/'native').mkdir(exist_ok=True)
# 2026-09-22: Film_P15=15 (WIMA MKS4 2.2u/100V 8x15x18), Film_P5=6.5 (MKS2 2.5x6.5x7.2), LM3886T=22 (TI overall), CP_D35=50 (CDE A05); others remain assumptions.
HEIGHT={'R_P7.5':2.5,'R_2W_P20':5,'Film_P15':15,'Film_P5':6.5,'BP_D10_P5':16,'CP_D12.5_P5':20,'CP_D8_P3.5':12,'CP_D35_P10':50,'Terminal2_P5.08':12,'Terminal3_P5.08':12,'Header2_P2.54':6,'AirCoil_P20':14,'Fuse5x20_P25':10,'Bridge_LOGICAL_UNVERIFIED':12,'LM3886T_UNVERIFIED':22}
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def tr(c,x,y):
 a=math.radians(c['angle']);return(c['x']+x*math.cos(a)+y*math.sin(a),c['y']-x*math.sin(a)+y*math.cos(a))
def color(c):
 return '#cd9b54' if c['ref'].startswith('R') else '#be6f44' if c['ref'].startswith('L') else '#398797' if c['ref'].startswith('J') else '#bb6554' if c['kind']!='circle' and c['ref'].startswith('C') else '#354752'
def shape(g,col):
 rgb=' '.join(str(int(col[i:i+2],16)/255) for i in (1,3,5));return f'Shape {{ appearance Appearance {{ material Material {{ diffuseColor {rgb} }} }} geometry {g} }}'
def model(c):
 x0,y0,x1,y1=c['body'];h=HEIGHT[c['footprint']];z0=1
 shapes=[]
 def mesh(verts,faces,col):
  coords=', '.join(' '.join(f'{v/2.54:.8f}' for v in pt) for pt in verts)
  indices=', '.join(' '.join(map(str,f))+ ' -1' for f in faces)
  shapes.append(shape(f'IndexedFaceSet {{ solid FALSE coord Coordinate {{ point [{coords}] }} coordIndex [{indices}] }}',col))
 def box(x0,y0,x1,y1,z0,z1,col):
  vs=[(x,y,z) for z in [z0,z1] for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]]
  mesh(vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],col)
 def cylinder(cx,cy,r,z0,z1,col,n=32):
  vs=[(cx+r*math.cos(2*math.pi*i/n),cy+r*math.sin(2*math.pi*i/n),z) for z in [z0,z1] for i in range(n)]
  fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
  mesh(vs,fs,col)
 if c['kind']=='circle':cylinder((x0+x1)/2,-(y0+y1)/2,(x1-x0)/2,z0,h,color(c))
 else:box(x0,-y1,x1,-y0,z0,h,color(c))
 for n,x,y,d,dr in c['pads']:cylinder(x,-y,.22,-3,2,'#c4ccd0',8)
 return '#VRML V2.0 utf8\n# PROVISIONAL; NOT MANUFACTURER CAD; all coordinates in 0.1 inch units\n'+'\n'.join(shapes)+'\n'
def add_models(src, dest, parts):
 s=src.read_text();out=[];i=0;n=0
 # Parse balanced footprint blocks, preserving source bytes outside appended model.
 while True:
  start=s.find('\n\t(footprint ',i)
  if start<0:out.append(s[i:]);break
  out.append(s[i:start]);beg=start+2;depth=0;quoted=False;escape=False;end=None
  for j in range(beg,len(s)):
   ch=s[j]
   if quoted:
    if escape:escape=False
    elif ch=='\\':escape=True
    elif ch=='"':quoted=False
   elif ch=='"':quoted=True
   elif ch=='(':depth+=1
   elif ch==')':
    depth-=1
    if depth==0:end=j;break
  block=s[start:end+1];ref=re.search(r'\(property "Reference" "([^"]+)"',block).group(1)
  if ref in parts:
   c=parts[ref];fn=c['footprint']+'.wrl'
   block=block[:-1]+f'\t(model "${{KIPRJMOD}}/models/{fn}" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))\n\t)';n+=1
  out.append(block);i=end+1
 dest.write_text(''.join(out));return n

def note(c,pads):
 ref=c['ref'];fp=c['footprint']; pins='；'.join(f"{p['number']}={p['net']}" for p in pads)
 if fp.startswith('CP_'):return '有極性：1=正、2=負；'+pins
 if fp.startswith('BP_'):return '必須無極性 BP；不可以一般有極性電解直接替代'
 if ref.startswith('BR'):return 'AC1／AC2／P／N 為功能名稱，尚未對應實物腳位'
 if ref.startswith(('J','U')):return pins
 return '依料號核對額定、腳徑與安裝方式'

manifest={'baseline':'a71b2c4','scope':'review artifacts only; PCB V0.3 electrical layout unchanged','sources':{},'boards':{},'model_units':'1 VRML unit = 2.54 mm; bodies generated in mm then scaled','height_status':'All heights are illustrative assumptions, not verified or guaranteed maximum envelopes.'}
allrows=[]
for key in ['mono','psu']:
 name=key+'-layout-v03';data=json.loads((P/(name+'.json')).read_text());parts={c['ref']:c for c in data['parts']}
 for ext in ['.json','.kicad_pcb','.kicad_pro']:
  f=P/(name+ext);manifest['sources'][str(f.relative_to(R))]=sha(f)
 for c in parts.values():(O/'3d/models'/(c['footprint']+'.wrl')).write_text(model(c))
 dest=O/'3d'/(name+'-preview.kicad_pcb');count=add_models(P/(name+'.kicad_pcb'),dest,parts)
 (dest.with_suffix('.kicad_pro')).write_bytes((P/(name+'.kicad_pro')).read_bytes())
 manifest['boards'][key]={'components':len(parts),'assigned_models':count,'pads':len(data['pads']),'tracks':len(data['tracks']),'size_mm':data['size']}
 # Per-pad assembly companion, including right-channel mapping explicitly.
 rows=['# '+('單聲道放大板' if key=='mono' else '共用電源板')+'：組裝與接腳對照','', '2026-09-18；PCB V0.3 工程草稿。下列為板檔網路，不代表實物腳位已核准。','', '兩片單聲道板絲印相同；右聲道原理圖編號請看 [左右聲道對照](../../mono-channel-mapping.csv)。' if key=='mono' else '雙橋 AC1／AC2／P／N 尚為功能端子，選料後需重新對應。','', '| 板上編號 | 元件值 | 焊盤號＝網路 | 注意事項 |','|---|---|---|---|']
 for c in data['parts']:
  pads=[p for p in data['pads'] if p['ref']==c['ref']];x0,y0,x1,y1=c['body'];pitch=math.dist(c['pads'][0][1:3],c['pads'][1][1:3]) if len(c['pads'])==2 else None
  ORDERED={'U1':'已訂（拆機）到貨未回報；封裝未核對','C1':'已購 WIMA MKS4 100V 已到貨待量','C2':'已購 ROE EGW 臥式已到貨待量；立式改臥式必改','C3':'已購 WIMA MKS2 100V 已到貨待量','C4':'已購 WIMA MKS2 100V 已到貨待量','C5':'已購 WIMA MKS2 100V 已到貨待量','C6':'已購 ROE EKE 已到貨待量；量直徑腳距','C7':'已購 ROE EKE 已到貨待量；量直徑腳距','C8':'已購 CDE 361R 100V 已到貨待量；量直徑','R1':'已購 MRS25 已到貨待量','R2':'已購 MRS25 已到貨待量','R3':'已購 MRS25 已到貨待量','R4':'已購 MRS25 已到貨待量','R5':'已購 RNU2 已到貨待量','R6':'已購 MRS25 已到貨待量','R7':'已購 PR02 已到貨待量','R8':'已購 MRS25 0.6W 已到貨待量','C201':'已購 CDE 381LX 已到貨待量；量直徑高度腳距','C202':'已購 CDE 381LX 已到貨待量；量直徑高度腳距','C203':'已購 CDE 381LX 已到貨待量；量直徑高度腳距','C204':'已購 CDE 381LX 已到貨待量；量直徑高度腳距','C205':'已購 WIMA MKS2 100V 已到貨待量','C206':'已購 WIMA MKS2 100V 已到貨待量','R201':'已購 PR02 已到貨待量','R202':'已購 PR02 已到貨待量'}
  status=ORDERED.get(c['ref'],'待購／未選料號')
  info={'board':key,'reference':c['ref'],'value':c['value'],'footprint':c['footprint'],'body_xy_mm':[x1-x0,y1-y0],'height_assumption_mm':HEIGHT[c['footprint']],'two_pin_pitch_mm':round(pitch,3) if pitch else None,'drills_mm':sorted(set(p['drill'] for p in pads)),'pad_positions_local_mm':c['pads'],'pad_nets':{p['number']:p['net'] for p in pads},'purchase_status':status,'verified':False,'manufacturer_part_number':None,'notes':note(c,pads)};allrows.append(info)
  rows.append('| '+c['ref']+' | '+c['value']+' | '+' / '.join(f"{p['number']}={p['net']}" for p in pads)+' | '+note(c,pads)+' |')
 (O/'drawings'/(key+'-assembly-notes.md')).write_text('\n'.join(rows)+'\n')
 # Vector explanatory drawings: strictly transformed existing pads/tracks/bodies.
 w,h=data['size'];S=9 if key=='mono' else 7; left=80;top=155;W=int(w*S+160);H=int(h*S+315)
 for view in ['top','bottom','assembly']:
  mirror=view=='bottom';project=lambda x,y:(left+(w-x if mirror else x)*S,top+y*S)
  svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',f'<rect width="{W}" height="{H}" fill="#101e28"/>','<g font-family="Arial, STHeiti, sans-serif">']
  def txt(x,y,t,size=16,fill='#c6d9df',anchor='start'):svg.append(f'<text x="{x:.2f}" y="{y:.2f}" fill="{fill}" font-size="{size}" text-anchor="{anchor}">{html.escape(str(t))}</text>')
  txt(60,46,('單聲道放大板' if key=='mono' else '共用電源板')+' / PCB V0.3',26,'#f1f7f6')
  txt(60,82,{'top':'正面銅箔 F.Cu｜由元件面觀看','bottom':'背面銅箔 B.Cu｜由板底觀看','assembly':'正面組裝圖｜元件位置、焊盤編號與極性'}[view],20)
  txt(60,112,f'{w} x {h} mm | '+('相對頂視圖左右翻面；不是從正面透視' if mirror else '板檔座標原點位於左上角'),16,'#eac180')
  svg.append(f'<rect x="{left}" y="{top}" width="{w*S}" height="{h*S}" fill="#173d3b" stroke="#79ada2"/>')
  if view!='assembly':
   for t in data['tracks']:
    if t['layer']!=('B.Cu' if mirror else 'F.Cu'):continue
    a,b=project(*t['a']),project(*t['b']);svg.append(f'<path d="M {a[0]} {a[1]} L {b[0]} {b[1]}" fill="none" stroke="{"#6eb6ef" if mirror else "#f0b962"}" stroke-width="{t["width"]*S}" stroke-linecap="round"/>')
  for c in data['parts']:
   x0,y0,x1,y1=c['body'];pts=[project(*tr(c,x,y)) for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]];cx,cy=project(*tr(c,(x0+x1)/2,(y0+y1)/2))
   if view=='assembly':
    if c['kind']=='circle':svg.append(f'<circle cx="{cx}" cy="{cy}" r="{(x1-x0)*S/2}" fill="{color(c)}" stroke="#a1c2c6"/>')
    else:svg.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="{color(c)}" stroke="#a1c2c6"/>')
   # body-center labels on copper maps are callouts, not backside components or silkscreen.
   size=12 if key=='mono' else 13
   txt(cx+(26 if c['ref']=='JP1' else 0),cy+(30 if c['ref']=='J5' else 65 if c['ref']=='J203' else 4),c['ref'],size,'#ffffff','middle')
  for p in data['pads']:
   x,y=project(p['x'],p['y']);r=p['dia']*S/2;rr=p['drill']*S/2
   svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ecc77b"/><circle cx="{x}" cy="{y}" r="{rr}" fill="#10232b"/>')
   if view=='assembly':
    # IC dense two rows: place labels outward from each pad row.
    dy=14 if p['ref']=='U1' and int(p['number'])%2 else -11
    if p['ref']!='U1':dy=-12
    label=p['number']
    if parts[p['ref']]['footprint'].startswith('CP_'):label+=(' +' if p['number']=='1' else ' -')
    txt(x,y+dy,label,10,'#fff6d1','middle')
  for v in data['vias']:
   x,y=project(v['x'],v['y']);svg.append(f'<circle cx="{x}" cy="{y}" r="{v["dia"]*S/2}" fill="#ecc77b"/><circle cx="{x}" cy="{y}" r="{v["drill"]*S/2}" fill="#10232b"/>')
  for i,(x,y) in enumerate([(4,4),(w-4,4),(w-4,h-4),(4,h-4)],1):
   a,b=project(x,y);svg.append(f'<circle cx="{a}" cy="{b}" r="{1.6*S}" fill="#101e28" stroke="#bfcccf"/>')
  yy=top+h*S+32
  txt(60,yy,'暫定封裝｜工程審查圖，非製造版',18,'#f2bd76')
  txt(60,yy+29,'極性與接頭用途：請搭配逐腳對照表閱讀。',15)
  txt(60,yy+55,'編號是導讀標示，不是實際絲印。圖片不可直接作為製板底片。',14)
  txt(60,yy+80,'底面圖已左右翻轉；元件仍裝在正面，編號僅供定位。' if mirror else '板厚暫定 1.6 mm；固定孔、實物腳距及高度尚待核對。',14)
  svg.append('</g></svg>');(O/'drawings'/f'{key}-{view}.svg').write_text('\n'.join(svg))
(O/'parts-audit.json').write_text(json.dumps(allrows,ensure_ascii=False,indent=2)+'\n')
(O/'sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(manifest['boards'],indent=2))
