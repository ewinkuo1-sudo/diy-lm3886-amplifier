"""V0.5 checks: native DRC clean, pad nets match the schematic, amplifier ground pour is one region.
The amplifier is a variant-D board (solid B.Cu pour), so the V0.4 branch-separation check does not apply;
the PSU returns join at the capacitor banks and the STAR by design. Geometry only: not EMC, stability,
thermal or enclosure validation. Also records the chassis-fit numbers this version exists for.
"""
from pathlib import Path
import json,hashlib,datetime,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
report={'status':'PASS','limits':'Draft only. Footprints (incl. the new upright C2 pitch), heating, stability, enclosure and harness remain unverified.','boards':{}}
for name,source in [('mono-layout-v05d','netlist.xml'),('psu-layout-v05','psu-netlist.xml')]:
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
 record={'size_mm':data['size'],'pad_net_count':len(actual),'native_DRC_violations':0,'native_DRC_unconnected':0,'tracks':len(data['tracks']),'vias':len(data['vias'])}
 if data.get('zones'):
  record['ground_pour']=[{'net':z['net'],'layer':z['layer'],'filled_regions':len(z['filled'])} for z in data['zones']]
  assert all(len(z['filled'])==1 for z in data['zones']),'pour split into islands'
 # every part must sit inside the outline (pads and courtyard-ish body box) - the shrink is the point of V0.5
 w,h=data['size']
 for part in data['parts']:
  for pad in data['pads']:
   if pad['ref']==part['ref']:assert 0.5<=pad['x']-pad['dia']/2 and pad['x']+pad['dia']/2<=w-0.5 and 0.5<=pad['y']-pad['dia']/2 and pad['y']+pad['dia']/2<=h-0.5,(name,pad['ref'],'pad outside edge clearance')
 report['boards'][name]=record
 report['kicad_version']=drc['kicad_version']
# chassis fit (BZ4312A2 inner 330 x 297 x 112, layout A: amp boards along the back wall, PSU + transformer in front)
amp=json.loads((R/'pcb/mono-layout-v05d.json').read_text(encoding='utf-8'))['size'];psu=json.loads((R/'pcb/psu-layout-v05.json').read_text(encoding='utf-8'))['size']
report['chassis_fit_bz4312a2']={'inner_mm':[330,297,112],'amp_board_along_wall_mm':amp[0],'amp_board_across_mm':amp[1],'psu_mm':psu,
 'depth_used_mm':25+amp[0]+30+max(psu[1],120),'depth_spare_mm':297-(25+amp[0]+30+max(psu[1],120)),
 'front_row_width_used_mm':20+120+20+psu[0],'front_row_width_spare_mm':330-(20+120+20+psu[0]),
 'note':'V0.4 left 7 mm depth and 10 mm front-row width. Figures assume 25 mm rear-panel connector band, 30 mm row gap, transformer D120 with 20 mm gaps.'}
report['checked_on']=datetime.date.today().isoformat()
report['minimum_copper_clearance_mm']=json.loads((R/'pcb/mono-layout-v05d.kicad_pro').read_text())['board']['design_settings']['rules']['min_clearance']
report['sha256']={f.relative_to(R).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in [R/'pcb/mono-layout-v05d.kicad_pcb',R/'pcb/mono-layout-v05d.kicad_pro',R/'pcb/mono-v05d-drc.json',R/'pcb/psu-layout-v05.kicad_pcb',R/'pcb/psu-layout-v05.kicad_pro',R/'pcb/psu-v05-drc.json',R/'electrical/lm3886-v01.kicad_sch',R/'electrical/internal-psu-v02.kicad_sch']}
(R/'pcb'/'validation-v05.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'boards':report['boards'],'chassis':report['chassis_fit_bz4312a2']},indent=1))
