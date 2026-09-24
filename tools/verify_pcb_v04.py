"""V0.4 checks: native DRC clean, pad nets match the schematic, ground families meet only at STAR.
Variant C keeps the V0.3 rule (separate return branches join in one region). Join radius is 5 mm here
(V0.3 used 4 mm) because the J5 return trunk is 3 mm wide and the speaker/zobel/signal branches
fan in around it; this is a geometry check only, not EMC/stability/thermal validation.
"""
from pathlib import Path
import json,math,hashlib,datetime,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
JOIN_RADIUS=5
def distance(a,b,q):
 dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy
 t=max(0,min(1,((q[0]-a[0])*dx+(q[1]-a[1])*dy)/den)) if den else 0
 return math.hypot(q[0]-a[0]-t*dx,q[1]-a[1]-t*dy)
def family(track):
 g=track['group']
 return 'signal' if g.startswith('signal-ground') else g
report={'status':'PASS','limits':'Draft only. Footprints, heating, stability, enclosure and harness remain unverified.','boards':{}}
for name,source in [('mono-layout-v04c','netlist.xml')]:
 data=json.loads((R/'pcb'/f'{name}.json').read_text(encoding='utf-8'))
 drc=json.loads((R/'pcb'/(name.replace('-layout','')+'-drc.json')).read_text(encoding='utf-8'))
 assert not drc['violations'] and not drc['unconnected_items'],name
 expected={}
 for net in ET.parse(R/'electrical'/source).findall('nets/net'):
  for node in net:expected[(node.get('ref'),node.get('pin'))]=net.get('name').lstrip('/')
 refs={p['ref'] for p in data['parts']}
 expected={key:value for key,value in expected.items() if key[0] in refs}
 actual={(p['ref'],p['number']):p['net'] for p in data['pads']}
 assert actual==expected,(name,'pad net mismatch')
 record={'pad_net_count':len(actual),'native_DRC_violations':0,'native_DRC_unconnected':0,'tracks':len(data['tracks']),'vias':len(data['vias'])}
 ground=[t for t in data['tracks'] if t['net']=='GND'];star=data['anchors']['STAR'];contacts=[]
 for i,a in enumerate(ground):
  for b in ground[i+1:]:
   if family(a)==family(b) or a['layer']!=b['layer']:continue
   n=max(1,math.ceil(math.dist(a['a'],a['b'])/.1))
   for j in range(n+1):
    q=tuple(a['a'][k]+(a['b'][k]-a['a'][k])*j/n for k in [0,1])
    if math.dist(q,star)<=JOIN_RADIUS:continue
    if distance(b['a'],b['b'],q)<(a['width']+b['width'])/2-.02:
     contacts.append((family(a),family(b),tuple(round(x,2) for x in q)));break
 assert not contacts,contacts
 record['ground_families']=sorted({family(t) for t in ground})
 record['ground_join_region_mm']={'center':star,'radius':JOIN_RADIUS}
 record['ground_check']=f'No cross-family copper contact found outside the {JOIN_RADIUS} mm join region; 0.1 mm centerline sampling with trace radii.'
 report['boards'][name]=record
 report['kicad_version']=drc['kicad_version']
report['checked_on']=datetime.date.today().isoformat()
report['minimum_copper_clearance_mm']=json.loads((R/'pcb/mono-layout-v04c.kicad_pro').read_text())['board']['design_settings']['rules']['min_clearance']
report['sha256']={f.relative_to(R).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in [R/'pcb/mono-layout-v04c.kicad_pcb',R/'pcb/mono-layout-v04c.kicad_pro',R/'pcb/mono-v04c-drc.json',R/'electrical/lm3886-v01.kicad_sch']}
(R/'pcb'/'validation-v04.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report['boards'],indent=1))
