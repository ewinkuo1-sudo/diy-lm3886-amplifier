"""Verify review-only boards, model dimensions, JSON audit and source bindings.
Run with KiCad Python. No geometry/thermal/stability certification.
"""
from pathlib import Path
import hashlib,json,re,math,struct
import pcbnew as p
R=Path(__file__).resolve().parents[1];O=R/'pcb/inspection-v03';sources=json.loads((O/'sources.json').read_text());audit=json.loads((O/'parts-audit.json').read_text())
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def parse(text):
 tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^()\s]+',text);stack=[];root=[];current=root
 for t in tokens:
  if t=='(':stack.append(current);new=[];current.append(new);current=new
  elif t==')':current=stack.pop()
  else:current.append(t)
 assert not stack
 return root
def strip_models(node):
 return [strip_models(x) if isinstance(x,list) else x for x in node if not (isinstance(x,list) and x and x[0]=='model')]
checks={}
for f,h in sources['sources'].items():assert sha(R/f)==h,f
for key in ['mono','psu']:
 src=R/'pcb'/f'{key}-layout-v03.kicad_pcb';dst=O/'3d'/f'{key}-layout-v03-preview.kicad_pcb'
 assert parse(src.read_text())==strip_models(parse(dst.read_text())),f'{key}: unexpected preview mutation'
 assert (src.with_suffix('.kicad_pro')).read_bytes()==dst.with_suffix('.kicad_pro').read_bytes()
 b=p.LoadBoard(str(dst));data=json.loads((R/'pcb'/f'{key}-layout-v03.json').read_text());fp={f.GetReference():f for f in b.GetFootprints()}
 assert b.GetCopperLayerCount()==2
 pads=0
 for c in data['parts']:
  f=fp[c['ref']];assert abs(p.ToMM(f.GetPosition().x)-c['x'])<1e-6 and abs(p.ToMM(f.GetPosition().y)-c['y'])<1e-6
  assert abs((f.GetOrientationDegrees()-c['angle']+180)%360-180)<1e-6
  mods=list(f.Models());assert len(mods)==1 and mods[0].m_Show
  path=Path(mods[0].m_Filename.replace('${KIPRJMOD}',str(O/'3d')));assert path.is_file()
  row=next(x for x in audit if x['board']==key and x['reference']==c['ref'])
  # First IndexedFaceSet is the body. Verify its bounds in millimeters.
  coords=[float(x)*2.54 for x in re.search(r'point \[([^]]+)\]',path.read_text()).group(1).replace(',',' ').split()]
  vertices=list(zip(coords[0::3],coords[1::3],coords[2::3]));lo=[min(v[i] for v in vertices) for i in range(3)];hi=[max(v[i] for v in vertices) for i in range(3)]
  x0,y0,x1,y1=c['body'];expect=[x0,-y1,1,x1,-y0,row['height_assumption_mm']]
  assert all(abs(x-y)<1e-5 for x,y in zip(lo+hi,expect)),(c['ref'],lo,hi,expect)
  for pad in f.Pads():
   v=next(x for x in data['pads'] if x['ref']==c['ref'] and x['number']==pad.GetNumber())
   assert pad.GetNetname()==v['net']==row['pad_nets'][pad.GetNumber()]
   assert math.dist([p.ToMM(pad.GetPosition().x),p.ToMM(pad.GetPosition().y)],[v['x'],v['y']])<1e-6
   pads+=1
  assert not row['verified'] and row['manufacturer_part_number'] is None
 assert pads==len(data['pads'])
 checks[key]={'native_loaded':True,'preview_only_adds_models':True,'project_rules_unchanged':True,'model_assignment_count':len(data['parts']),'model_body_bounds_match_assumptions':True,'pad_positions_and_nets_checked':pads}
 for view in ['top','bottom','assembly']:
  svg=(O/'drawings'/f'{key}-{view}.svg').read_text();assert '</svg>' in svg
  png=O/'drawings'/f'{key}-{view}.png';assert png.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
 for view in ['top','bottom','isometric']:
  for pref in ['', 'raw-']:
   png=O/'3d'/f'{pref}{key}-{view}.png';assert struct.unpack('>II',png.read_bytes()[16:24]) in [(1488,1064),(1500,1100),(1500,1340)]
 for side in ['top','bottom']:assert '</svg>' in (O/'native'/f'{key}-{side}.svg').read_text()
log=json.loads((O/'native-export-log.json').read_text());assert len(log)==10 and all(x['returncode']==0 for x in log)
assert len(audit)==37
report={'date':'2026-09-18','checks':checks,'audit_rows':len(audit),'native_exports':len(log),'scope':'source/geometry/model/asset consistency only; no new ERC/DRC/hardware testing','manual_visual_review':'Top/bottom copper, assembly polarity, native top/bottom/isometric component renders reviewed; see README limitations.','files':{f.relative_to(R).as_posix():sha(f) for f in sorted(O.rglob('*')) if f.is_file() and f.name!='verification.json' and f.suffix not in ['.kicad_prl']}}
(O/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(checks,indent=2))
