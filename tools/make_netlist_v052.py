"""Compose the V0.5.2 merged-board netlist (one channel: amplifier + its own filter capacitors) from the two
exported KiCad netlists. There is no KiCad schematic for this board yet; if V0.5.2 is chosen, a proper schematic
generator must follow and this file is retired. Output: electrical/merged-v052-netlist.xml (regenerable, ignored).

Rules:
 - every amplifier part except J5 (the 3P DC-in terminal; the rails now come from the on-board capacitors);
 - from the PSU: C201 (V+ filter), C203 (V- filter), R201/R202 (bleeders), C205/C206 (HF bypass at the STAR);
   their pins keep the PSU netlist assignment (VCC/GND/VEE);
 - new J6, a 4-way 5.08 mm screw terminal fed by the two chassis-mounted KBPC2510: 1=V+ (BR1.P), 2=GND (BR1.N),
   3=GND (BR2.P), 4=V- (BR2.N). Both channels' boards hang on the same two bridges (one 2x22 Vac transformer),
   so this is shared-rectifier / per-channel-filter, not true dual mono.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
R=Path(__file__).resolve().parents[1]/'electrical'
KEEP_PSU={'C201','C203','R201','R202','C205','C206'}
def load(name):
 root=ET.parse(R/name).getroot()
 comps={c.get('ref'):c.findtext('value') for c in root.findall('components/comp')}
 nets={}
 for n in root.findall('nets/net'):
  for x in n:nets.setdefault(n.get('name').lstrip('/'),[]).append((x.get('ref'),x.get('pin')))
 return comps,nets
acomps,anets=load('netlist.xml');pcomps,pnets=load('psu-netlist.xml')
comps={r:v for r,v in acomps.items() if r!='J5'}
comps.update({r:v for r,v in pcomps.items() if r in KEEP_PSU})
comps['J6']='DC IN 4P (BR1+ BR1- BR2+ BR2-)'
nets={}
for name,nodes in anets.items():
 kept=[n for n in nodes if n[0]!='J5']
 if kept:nets[name]=kept
for name,nodes in pnets.items():
 kept=[n for n in nodes if n[0] in KEEP_PSU]
 if kept:nets.setdefault(name,[]).extend(kept)
for pin,net in [('1','VCC'),('2','GND'),('3','GND'),('4','VEE')]:nets[net].append(('J6',pin))
assert {n for n in nets if n in ('VCC','GND','VEE')}=={'VCC','GND','VEE'}
out=['<?xml version="1.0" encoding="utf-8"?>','<export version="E"><design><source>merged by tools/make_netlist_v052.py from netlist.xml + psu-netlist.xml</source></design><components>']
for r,v in comps.items():out.append(f'<comp ref="{r}"><value>{escape(v or "")}</value></comp>')
out.append('</components><nets>')
for i,(name,nodes) in enumerate(sorted(nets.items()),1):
 out.append(f'<net code="{i}" name="/{name}">'+''.join(f'<node ref="{r}" pin="{p}"/>' for r,p in nodes)+'</net>')
out.append('</nets></export>')
(R/'merged-v052-netlist.xml').write_text('\n'.join(out)+'\n',encoding='utf-8')
print(len(comps),'components',len(nets),'nets;',sum(len(v) for v in nets.values()),'nodes')
