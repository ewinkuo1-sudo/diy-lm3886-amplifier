"""Reproducible copper-path screen; not a field solver or thermal simulation.
No capacitors/ICs/inductors are traversed. Pad and via barrel resistance are
excluded from trace paths. Shared currents/parallel copper are not solved.
"""
from pathlib import Path
import json,math,heapq,hashlib
ROOT=Path(__file__).resolve().parents[1]
RHO=17e-6 # ohm mm at 25 C; TI Analog Engineer's Pocket Reference, PCB and Wire
ALPHA=.0039
THICKNESS=[.0348,.0696] # mm; nominal 1 oz / 2 oz, finished copper not selected

def key(pt,layer):return (round(pt[0],6),round(pt[1],6),layer)
def fraction(a,b,p):
 dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy
 if not den:return None
 t=((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den
 if -.000001<=t<=1.000001 and math.hypot(a[0]+t*dx-p[0],a[1]+t*dy-p[1])<1e-5:return max(0,min(1,t))

def graph(data,net):
 tracks=[t for t in data['tracks'] if t['net']==net];points={layer:[] for layer in ['F.Cu','B.Cu']}
 for t in tracks:points[t['layer']].extend([t['a'],t['b']])
 pads=[p for p in data['pads'] if p['net']==net];vias=[v for v in data['vias'] if v['net']==net]
 for p in pads+vias:
  for layer in points:points[layer].append((p['x'],p['y']))
 # Add exact centerline intersections, including T junctions in the source paths.
 for i,a in enumerate(tracks):
  for b in tracks[i+1:]:
   if a['layer']!=b['layer']:continue
   ax,ay=a['a'];dx,dy=a['b'][0]-ax,a['b'][1]-ay
   bx,by=b['a'];ex,ey=b['b'][0]-bx,b['b'][1]-by
   den=dx*ey-dy*ex
   if abs(den)<1e-9:continue
   t=((bx-ax)*ey-(by-ay)*ex)/den;u=((bx-ax)*dy-(by-ay)*dx)/den
   if 0<=t<=1 and 0<=u<=1:points[a['layer']].append((ax+t*dx,ay+t*dy))
 edges={}
 def add(a,b,length,width,via=False):
  edges.setdefault(a,[]).append((b,length,width,via));edges.setdefault(b,[]).append((a,length,width,via))
 for tr in tracks:
  knots=sorted({(round(t,8),key(p,tr['layer'])) for p in points[tr['layer']] if (t:=fraction(tr['a'],tr['b'],p)) is not None})
  for (_,a),(_,b) in zip(knots,knots[1:]):
   length=math.dist(a[:2],b[:2])
   if length>1e-7:add(a,b,length,tr['width'])
 for p in pads+vias:add(key((p['x'],p['y']),'F.Cu'),key((p['x'],p['y']),'B.Cu'),0,1,p in vias)
 return edges

def point(data,s):
 if s in data['anchors']:return data['anchors'][s]
 ref,num=s.split('.')
 p=next(p for p in data['pads'] if p['ref']==ref and p['number']==num)
 return p['x'],p['y']

def path(data,net,start,end,metric='resistance'):
 g=graph(data,net);a=point(data,start);b=point(data,end)
 starts=[key(a,l) for l in ['F.Cu','B.Cu'] if key(a,l) in g];targets={key(b,l) for l in ['F.Cu','B.Cu']}
 dist={s:0 for s in starts};queue=[(0,s) for s in starts];heapq.heapify(queue);prev={};target=None
 while queue:
  cost,node=heapq.heappop(queue)
  if cost>dist[node]+1e-12:continue
  if node in targets:target=node;break
  for v,length,width,via in g[node]:
   step=length/width if metric=='resistance' else length
   new=cost+step
   if new+1e-10<dist.get(v,math.inf):dist[v]=new;prev[v]=(node,length,width,via);heapq.heappush(queue,(new,v))
 assert target is not None,(data['name'],net,start,end)
 segments=[]
 while target in prev:
  node,length,width,via=prev[target];segments.append((length,width,via));target=node
 physical=[s for s in segments if s[0]>0]
 return {'length_mm':sum(s[0] for s in physical),'sum_length_over_width':sum(s[0]/s[1] for s in physical),'min_width_mm':min(s[1] for s in physical),'via_transitions':sum(s[2] for s in segments)}

def resistance(route,t,temp):return RHO*route['sum_length_over_width']/t*(1+ALPHA*(temp-25))

def seg_distance(a,b,c,d):
 def pd(x,y,z):
  dx,dy=y[0]-x[0],y[1]-x[1];den=dx*dx+dy*dy
  t=max(0,min(1,((z[0]-x[0])*dx+(z[1]-x[1])*dy)/den)) if den else 0
  return math.hypot(z[0]-x[0]-t*dx,z[1]-x[1]-t*dy)
 def cross(x,y,z):return (y[0]-x[0])*(z[1]-x[1])-(y[1]-x[1])*(z[0]-x[0])
 if cross(a,b,c)*cross(a,b,d)<0 and cross(c,d,a)*cross(c,d,b)<0:return 0
 return min(pd(a,b,c),pd(a,b,d),pd(c,d,a),pd(c,d,b))
def coupling_screen(data):
 quiet=[t for t in data['tracks'] if t['group'] in ('feedback','input')]
 result={}
 for kind,groups in [('load',{'output-power','speaker'}),('supply',{'positive-feed','positive-local','positive-pin','negative-feed','negative-pin','negative-bypass'})]:
  power=[t for t in data['tracks'] if t['group'] in groups];minimum=math.inf;closest=None
  for a in quiet:
   for b in power:
    gap=seg_distance(a['a'],a['b'],b['a'],b['b'])-(a['width']+b['width'])/2
    if gap<minimum:minimum=gap;closest={'quiet_net':a['net'],'power_net':b['net'],'quiet_layer':a['layer'],'power_layer':b['layer']}
  result[kind]={'minimum_projected_trace_edge_gap_mm':minimum,'closest':closest}
 return result

def analyze():
 # Only the two V0.2 baseline JSONs survive under pcb/archive/v02/ (rest deleted 2026-09-21); V0.3 stays in pcb/.
 def layout_path(board,v):return ROOT/('pcb/archive/v02' if v=='02' else 'pcb')/f'{board}-layout-v{v}.json'
 data={(board,v):json.loads(layout_path(board,v).read_text()) for board in ['mono','psu'] for v in ['02','03']}
 # 40 W is a sizing case, not a promised output rating. Same-phase stereo is assumed.
 out_rms=math.sqrt(40/8);out_peak=out_rms*math.sqrt(2);iq=.085
 rail_rms=math.sqrt(out_peak**2/4+2*iq*out_peak/math.pi+iq**2);rail_avg=out_peak/math.pi+iq
 charge_avg=2*rail_avg
 duty=.15;charge_rms=charge_avg/math.sqrt(duty);charge_peak=charge_avg/duty
 currents={'output':(out_rms,out_peak),'rail1':(rail_rms,out_peak+iq),'rail2':(2*rail_rms,2*(out_peak+iq)), 'ground2':(2*out_rms,2*out_peak),'charge':(charge_rms,charge_peak)}
 specs=[
 ('IC 輸出至 L1','mono','L_OUT','U1.3','L1.1','output'),
 ('L1 至喇叭端子','mono','L_SPK','L1.2','J2.1','output'),
 ('喇叭回地至匯流區','mono','GND','J2.2','STAR','output'),
 ('放大板匯流區至電源地','mono','GND','STAR','J5.2','output'),
 ('正電源端子至 U1.1','mono','VCC','J5.1','U1.1','rail1'),
 ('正電源端子至 U1.5','mono','VCC','J5.1','U1.5','rail1'),
 ('負電源端子至 U1.4','mono','VEE','J5.3','U1.4','rail1'),
 ('共用電源正軌輸出','psu','VCC','C202.1','J203.1','rail2'),
 ('共用電源負軌輸出','psu','VEE','C204.2','J203.3','rail2'),
 ('共用電源輸出地','psu','GND','STAR','J203.2','ground2'),
 ]
 for sign,br,c,j,f in [('正','BR1','C201','J201','F201'),('負','BR2','C203','J202','F202')]:
  prefix='POS' if sign=='正' else 'NEG';rail='VCC' if sign=='正' else 'VEE'
  rail_pin='P' if sign=='正' else 'N';gnd_pin='N' if sign=='正' else 'P';cap_rail='1' if sign=='正' else '2';cap_gnd='2' if sign=='正' else '1'
  specs.extend([(sign+'橋至第一顆濾波電容','psu',rail,f'{br}.{rail_pin}',f'{c}.{cap_rail}','charge'),(sign+'橋充電回地','psu','GND',f'{c}.{cap_gnd}',f'{br}.{gnd_pin}','charge'),(sign+' AC 端子至保險絲','psu',prefix+'_AC1',j+'.1',f+'.1','charge'),(sign+'保險絲至整流橋','psu',prefix+'_AC_FUSED',f+'.2',br+'.AC1','charge'),(sign+' AC 回線','psu',prefix+'_AC2',br+'.AC2',j+'.2','charge')])
 rows=[]
 for title,board,net,a,b,current in specs:
  routes={v:path(data[board,v],net,a,b) for v in ['02','03']};ir,ip=currents[current]
  row={'name':title,'board':board,'net':net,'from':a,'to':b,'current_model':current,'rms_A':ir,'peak_A':ip,'versions':{}}
  for v,route in routes.items():
   row['versions'][v]={'geometry':route,'cases':[]}
   for thick in THICKNESS:
    for temp in [25,85]:
     r=resistance(route,thick,temp);row['versions'][v]['cases'].append({'copper_mm':thick,'assumed_copper_C':temp,'R_ohm':r,'peak_drop_V':ip*r,'heat_W':ir*ir*r})
  rows.append(row)
 loops=[]
 for label,cap,net,pin,cp,gp in [('C3→U1.1','C3','VCC','U1.1','1','2'),('C3→U1.5','C3','VCC','U1.5','1','2'),('C4→U1.4','C4','VEE','U1.4','2','1')]:
  result={'name':label,'versions':{}}
  for v in ['02','03']:
   rail=path(data['mono',v],net,cap+'.'+cp,pin,'length');ground=path(data['mono',v],'GND',cap+'.'+gp,'U1.7','length')
   result['versions'][v]={'rail_trace_mm':rail['length_mm'],'ground_to_U1_7_mm':ground['length_mm'],'external_trace_sum_mm':rail['length_mm']+ground['length_mm']}
  loops.append(result)
 feedback={v:{'sense_mm':path(data['mono',v],'L_OUT','U1.3','R4.2','length')['length_mm'],'inverting_mm':path(data['mono',v],'L_INV','U1.9','R4.1','length')['length_mm']} for v in ['02','03']}
 # Plated-barrel estimate only; no thermal prediction or via current rating.
 vias=[{'finished_hole_mm':.8,'plating_mm':p,'length_mm':1.6,'R25_mohm':1000*RHO*1.6/(math.pi*.8*p)} for p in [.015,.020,.025]]
 report={'assumptions':{'Vrail':30,'load_ohm':8,'sizing_output_W':40,'Iq_per_rail_A':iq,'rho25_ohm_mm':RHO,'alpha_per_C':ALPHA,'copper_thickness_mm':THICKNESS,'temperature_C':[25,85],'note':'85 C is an input sensitivity case, not a predicted temperature. No thermal rise solved.'},'current_cases':{k:{'rms_A':v[0],'peak_A':v[1]} for k,v in currents.items()},'charge_duty_sensitivity':[{'duty':d,'average_A':charge_avg,'rms_A':charge_avg/math.sqrt(d),'peak_A':charge_avg/d} for d in [.15,.25,.35]],'bypass_external_trace_lengths':loops,'feedback':feedback,'projected_coupling_screen':{v:coupling_screen(data['mono',v]) for v in ['02','03']},'paths':rows,'former_power_via_barrel_sensitivity':vias,'sha256':{str((layout_path(b,v)).relative_to(ROOT)):hashlib.sha256((layout_path(b,v)).read_bytes()).hexdigest() for b in ['mono','psu'] for v in ['02','03']}}
 (ROOT/'pcb/current-budget-v03.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 lines=['# PCB V0.3 銅箔計算表（程式輸出）','','由 `tools/analyze_pcb_v03.py` 依 PCB 走線資料計算。完整假設與限制見 [本輪審查](review-v03.md)。','', '以下採名義 1 oz 銅厚 0.0348 mm、假設銅溫 25°C。電流情境為 40W／8Ω；充電列另採 15% 導通占空比矩形脈衝假設。','', '| 路徑 | RMS A | V0.2 電阻 mΩ | V0.3 電阻 mΩ | V0.3 峰值壓降 mV | V0.3 發熱 W |','|---|---:|---:|---:|---:|---:|']
 for row in rows:
  a=row['versions']['02']['cases'][0];b=row['versions']['03']['cases'][0]
  lines.append(f"| {row['name']} | {row['rms_A']:.3f} | {a['R_ohm']*1000:.2f} | {b['R_ohm']*1000:.2f} | {b['peak_drop_V']*1000:.1f} | {b['heat_W']:.3f} |")
 lines+=['','2 oz 模型的電阻／壓降／發熱均為表中一半；假設銅溫 85°C 時，三者為 25°C 的 1.234 倍。這不是預測溫升。','','各列情境不代表同時可達成，不能把所有列發熱相加當整板結果。未計入零件、導線、接頭、焊接接觸、孔壁或高頻阻抗。','', '| 去耦外部銅箔長度指標 | V0.2 mm | V0.3 mm |','|---|---:|---:|']
 for loop in loops:lines.append(f"| {loop['name']} | {loop['versions']['02']['external_trace_sum_mm']:.1f} | {loop['versions']['03']['external_trace_sum_mm']:.1f} |")
 lines+=['','指標為電源腳至電容電源端，加電容地端至 U1.7 的中心線最短路徑。不是完整開關電流回路、迴路面積或電感模型。']
 (ROOT/'pcb/current-budget-v03.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps({'loops':loops,'feedback':feedback,'currents':report['current_cases']},ensure_ascii=False,indent=2))
if __name__=='__main__':analyze()
