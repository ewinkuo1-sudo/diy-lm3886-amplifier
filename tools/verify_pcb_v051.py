"""V0.5.1 checks (PSU only): native DRC clean, pad nets match the schematic, parts inside the outline, and the
bridge geometry this version exists for: GBJ body clear of the fuse-holder body and the capacitor courtyards,
and a 10 mm heatsink envelope on the metal-back side clear of every other part body. Geometry only: not
thermal, EMC or enclosure validation. The amplifier board is unchanged V0.5 and is not re-checked here.
"""
from pathlib import Path
import json,hashlib,datetime,math,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
name='psu-layout-v051'
data=json.loads((R/'pcb'/f'{name}.json').read_text(encoding='utf-8'))
drc=json.loads((R/'pcb'/'psu-v051-drc.json').read_text(encoding='utf-8'))
assert not drc['violations'] and not drc['unconnected_items'],name
expected={}
for net in ET.parse(R/'electrical/psu-netlist.xml').findall('nets/net'):
 for node in net:expected[(node.get('ref'),node.get('pin'))]=net.get('name').lstrip('/')
refs={p['ref'] for p in data['parts']}
expected={key:value for key,value in expected.items() if key[0] in refs}
actual={(p['ref'],p['number']):p['net'] for p in data['pads']}
assert actual==expected,(name,'pad net mismatch')
w,h=data['size']
for pad in data['pads']:
 assert 0.5<=pad['x']-pad['dia']/2 and pad['x']+pad['dia']/2<=w-0.5 and 0.5<=pad['y']-pad['dia']/2 and pad['y']+pad['dia']/2<=h-0.5,(pad['ref'],'pad outside edge clearance')
# bridge geometry
def box(part,inflate=0):
 x0,y0,x1,y1=part['body'];a=math.radians(part['angle'])
 pts=[(part['x']+x*math.cos(a)+y*math.sin(a),part['y']-x*math.sin(a)+y*math.cos(a)) for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]]
 xs=[q[0] for q in pts];ys=[q[1] for q in pts];return (min(xs)-inflate,min(ys)-inflate,max(xs)+inflate,max(ys)+inflate)
def overlap(a,b):return not (a[2]<=b[0] or b[2]<=a[0] or a[3]<=b[1] or b[3]<=a[1])
parts={p['ref']:p for p in data['parts']}
HS=10.0   # heatsink envelope thickness on the metal-back (-y) side
bridges={}
for ref in ('BR1','BR2'):
 b=parts[ref];assert b['footprint']=='GBJ_Upright_P10_7.5_7.5' and b['angle']==0,ref
 body=box(b,0.5);hs=(body[0],body[1]-HS,body[2],body[1])
 for other,o in parts.items():
  if other==ref:continue
  ob=box(o,0.5)
  assert not overlap(body,ob),(ref,'body overlaps',other)
  assert not overlap(hs,ob),(ref,'heatsink envelope overlaps',other)
 bridges[ref]={'body_mm':[round(x,2) for x in body],'heatsink_envelope_mm':[round(x,2) for x in hs],'gap_to_fuse_body_mm':round(hs[1]-box(parts['F201' if ref=='BR1' else 'F202'])[3],2)}
# capacitor courtyard (circle) vs bridge body: nearest point of the circle at the bridge's y
for ref,cap in (('BR1','C201'),('BR2','C203')):
 b=parts[ref];c=parts[cap];r=(c['body'][2]-c['body'][0])/2+0.5
 cx=c['x']+(c['body'][0]+c['body'][2])/2*math.cos(math.radians(c['angle']));cy=c['y']
 body=box(b,0.5);dy=min(abs(cy-body[3]),r);top=cy-math.sqrt(max(r*r-0,0))
 assert body[3]<=top,(ref,'bridge courtyard enters capacitor courtyard',body[3],top)
 bridges[ref]['gap_to_capacitor_courtyard_mm']=round(top-body[3],2)
report={'status':'PASS','limits':'Draft only. GBJ footprint from datasheet, part not in hand; heating of the bridge next to 105 C capacitors, heatsink choice, enclosure and harness unverified. Amplifier board unchanged (V0.5).',
 'board':{'size_mm':data['size'],'pad_net_count':len(actual),'native_DRC_violations':0,'native_DRC_unconnected':0,'tracks':len(data['tracks']),'vias':len(data['vias'])},
 'bridges':bridges,'kicad_version':drc['kicad_version'],'checked_on':datetime.date.today().isoformat(),
 'minimum_copper_clearance_mm':json.loads((R/'pcb'/f'{name}.kicad_pro').read_text())['board']['design_settings']['rules']['min_clearance'],
 'sha256':{f.relative_to(R).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in [R/'pcb'/f'{name}.kicad_pcb',R/'pcb'/f'{name}.kicad_pro',R/'pcb/psu-v051-drc.json',R/'electrical/internal-psu-v02.kicad_sch']}}
(R/'pcb'/'validation-v051.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'board':report['board'],'bridges':bridges},indent=1))
