"""Run native DRC with fixed-rule assertions and bind reports to checked files."""
from pathlib import Path
import argparse,subprocess,json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
# kicad-cli on Windows writes CRLF reports; normalise to LF before hashing so bindings match the repo.
def lf(path):
 b=path.read_bytes()
 if b'\r\n' in b:path.write_bytes(b.replace(b'\r\n',b'\n'))
def rules(path):
 d=json.loads(path.read_text());r=d['board']['design_settings']['rules']
 expected={'min_clearance':.3,'min_track_width':.35,'min_copper_edge_clearance':.5,'min_via_annular_width':.2,'min_silk_clearance':.15}
 for k,v in expected.items():assert r[k]==v,(path,k,r[k],v)
 assert d['net_settings']['classes'][0]['clearance']==.3,path
 return expected
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--cli',default='kicad-cli');args=parser.parse_args()
 proof={'timestamp':datetime.datetime.now().astimezone().isoformat(),'boards':{}}
 for name in ['mono','psu']:
  board=ROOT/'pcb'/f'{name}-layout-v03.kicad_pcb';project=board.with_suffix('.kicad_pro');report=ROOT/'pcb'/f'{name}-v03-drc.json'
  expected=rules(project);before=sha(board)
  subprocess.run([args.cli,'pcb','drc','--format','json','--exit-code-violations','-o',str(report),str(board)],check=True)
  lf(report);assert before==sha(board);rules(project)
  d=json.loads(report.read_text());assert not d['violations'] and not d['unconnected_items']
  files=[board,project,report,board.with_suffix('.json')]
  proof['boards'][name]={'rules':expected,'kicad_version':d['kicad_version'],'sha256':{f.relative_to(ROOT).as_posix():sha(f) for f in files}}
 (ROOT/'pcb/drc-provenance-v03.json').write_text(json.dumps(proof,indent=2)+'\n')
 print('Native DRC PASS; rules checked before/after; report hashes bound to boards.')
