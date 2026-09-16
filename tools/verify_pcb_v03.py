"""Check native DRC results, schematic pad count, and mono return separation.
Run after build_pcb_v03.py and native KiCad DRC. The sampled ground check is
supplemental; it neither replaces DRC nor validates EMC/stability/temperature.
"""
from pathlib import Path
import json,math,hashlib,datetime,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
proof=json.loads((R/'pcb/drc-provenance-v03.json').read_text())
for record in proof['boards'].values():
 for rel,digest in record['sha256'].items():assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==digest,('stale DRC proof',rel)
def distance(a,b,q):
 dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy
 t=max(0,min(1,((q[0]-a[0])*dx+(q[1]-a[1])*dy)/den)) if den else 0
 return math.hypot(q[0]-a[0]-t*dx,q[1]-a[1]-t*dy)
def family(track):
 g=track['group']
 return 'signal' if g.startswith('signal-ground') else g
report={'status':'PASS','limits':'Draft only. Footprints, heating, stability, enclosure and harness remain unverified.','boards':{}}
for name,source in [('mono','netlist.xml'),('psu','psu-netlist.xml')]:
 data=json.loads((R/'pcb'/f'{name}-layout-v03.json').read_text())
 drc=json.loads((R/'pcb'/f'{name}-v03-drc.json').read_text())
 assert not drc['violations'] and not drc['unconnected_items'],name
 expected={}
 for net in ET.parse(R/'electrical'/source).findall('nets/net'):
  for node in net:expected[(node.get('ref'),node.get('pin'))]=net.get('name').lstrip('/')
 refs={p['ref'] for p in data['parts']}
 expected={key:value for key,value in expected.items() if key[0] in refs}
 actual={(p['ref'],p['number']):p['net'] for p in data['pads']}
 assert actual==expected,(name,'pad net mismatch')
 record={'pad_net_count':len(actual),'native_DRC_violations':0,'native_DRC_unconnected':0,'tracks':len(data['tracks']),'vias':len(data['vias'])}
 if name=='mono':
  ground=[t for t in data['tracks'] if t['net']=='GND'];star=data['anchors']['STAR'];contacts=[]
  # Quantified join region: all ground families may meet within radius 4 mm.
  # Outside that region, swept copper from different return families must not touch.
  for i,a in enumerate(ground):
   for b in ground[i+1:]:
    if family(a)==family(b) or a['layer']!=b['layer']:continue
    n=max(1,math.ceil(math.dist(a['a'],a['b'])/.1))
    for j in range(n+1):
     q=tuple(a['a'][k]+(a['b'][k]-a['a'][k])*j/n for k in [0,1])
     if math.dist(q,star)<=4:continue
     if distance(b['a'],b['b'],q)<(a['width']+b['width'])/2-.02:
      contacts.append((family(a),family(b),tuple(round(x,2) for x in q)));break
  assert not contacts,contacts
  record['ground_families']=sorted({family(t) for t in ground})
  record['ground_join_region_mm']={'center':star,'radius':4}
  record['ground_check']='No cross-family copper contact found outside join region; 0.1 mm centerline sampling with trace radii.'
 report['boards'][name]=record
report['baseline_commit']='d39b62360c13417d566d6ab0d0b95fe969c4c5b0'
report['checked_on']=datetime.date.today().isoformat()
report['kicad_version']=drc['kicad_version']
report['minimum_copper_clearance_mm']=json.loads((R/'pcb/mono-layout-v03.kicad_pro').read_text())['board']['design_settings']['rules']['min_clearance']
report['sha256']={str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [R/'pcb/mono-layout-v03.kicad_pcb',R/'pcb/psu-layout-v03.kicad_pcb',R/'pcb/mono-layout-v03.kicad_pro',R/'pcb/psu-layout-v03.kicad_pro',R/'electrical/lm3886-v01.kicad_sch',R/'electrical/internal-psu-v02.kicad_sch']}
(R/'pcb'/'validation-v03.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
