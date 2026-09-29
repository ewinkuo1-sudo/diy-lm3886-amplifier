"""V0.5.2 checks: native DRC clean, pad nets match the merged netlist, amplifier pour is one region, every pad inside
the edge clearance, and the supply-section GND copper reaches the pour only through the STAR link. Geometry only.
Also records the two-board chassis-fit numbers (BZ4312A2 layout A: both boards along the back wall, transformer
and control board in the front row, KBPC2510 x2 on the chassis floor between them).
"""
from pathlib import Path
import json,hashlib,datetime,math,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
name='mono-layout-v052'
data=json.loads((R/'pcb'/f'{name}.json').read_text(encoding='utf-8'))
drc=json.loads((R/'pcb/mono-v052-drc.json').read_text(encoding='utf-8'))
assert not drc['violations'] and not drc['unconnected_items']
expected={}
for net in ET.parse(R/'electrical/merged-v052-netlist.xml').findall('nets/net'):
 for node in net:expected[(node.get('ref'),node.get('pin'))]=net.get('name').lstrip('/')
refs={p['ref'] for p in data['parts']};expected={k:v for k,v in expected.items() if k[0] in refs}
actual={(p['ref'],p['number']):p['net'] for p in data['pads']}
assert actual==expected,'pad net mismatch'
w,h=data['size']
for pad in data['pads']:assert 0.5<=pad['x']-pad['dia']/2 and pad['x']+pad['dia']/2<=w-0.5 and 0.5<=pad['y']-pad['dia']/2 and pad['y']+pad['dia']/2<=h-0.5,(pad['ref'],'pad outside edge clearance')
zone=data['zones'][0];assert len(zone['filled'])==1,'pour split into islands'
zy=max(y for x,y in zone['outline'])
# supply-section GND pads must sit below the pour outline and connect by explicit copper, not by the pour
supply_gnd=[p for p in data['pads'] if p['net']=='GND' and p['ref'] in ('C201','C203','R201','R202','C205','C206','J6')]
assert all(p['y']>zy for p in supply_gnd),'supply GND pad inside pour outline'
links=[t for t in data['tracks'] if t['net']=='GND' and min(t['a'][1],t['b'][1])<zy<max(t['a'][1],t['b'][1])]
assert len(links)==1 and links[0]['group']=='pour-link',links
report={'status':'PASS','limits':'Draft only; merged netlist has no KiCad schematic yet. Footprints (upright C2 pitch, Terminal4), heating, stability, enclosure and harness remain unverified.',
 'board':{'size_mm':data['size'],'pad_net_count':len(actual),'native_DRC_violations':0,'native_DRC_unconnected':0,'tracks':len(data['tracks']),'vias':len(data['vias']),
  'ground_pour':{'net':'GND','layer':zone['layer'],'outline_y_max':zy,'filled_regions':1},'supply_gnd_pads_outside_pour':len(supply_gnd),'pour_links':1,'star':data['anchors']['STAR']},
 'chassis_fit_bz4312a2':{'inner_mm':[330,297,112],'board_along_wall_mm':w,'board_across_mm':h,'boards':2,
  'back_row_width_used_mm':2*h,'back_row_centre_spare_mm':330-2*h,'depth_used_mm':25+w+30+120,'depth_spare_mm':297-(25+w+30+120),
  'front_row':'transformer D120 + control board 120x105; width 20+120+20+120=280, spare 50. The two KBPC2510 sit on the floor in the 46 mm gap between the boards, facing both J6 terminals',
  'note':'V0.5 (3 boards): depth spare 22, front-row spare 45; control board sat between the amp boards. V0.5.2 moves it to the front row.'},
 'kicad_version':drc['kicad_version'],'checked_on':datetime.date.today().isoformat(),
 'minimum_copper_clearance_mm':json.loads((R/'pcb/mono-layout-v052.kicad_pro').read_text())['board']['design_settings']['rules']['min_clearance'],
 'sha256':{f.relative_to(R).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in [R/'pcb/mono-layout-v052.kicad_pcb',R/'pcb/mono-layout-v052.kicad_pro',R/'pcb/mono-v052-drc.json',R/'tools/make_netlist_v052.py',R/'electrical/lm3886-v01.kicad_sch',R/'electrical/internal-psu-v02.kicad_sch']}}
(R/'pcb/validation-v052.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'board':report['board'],'chassis':report['chassis_fit_bz4312a2']},indent=1))
