"""V0.4 native KiCad exports (derived from the V0.3 script).
"""
"""Native KiCad layer exports and 3D render of review-only model boards."""
from pathlib import Path
import subprocess,argparse,json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'pcb/inspection-v04'
NAME={'mono':'mono-layout-v04d','psu':'psu-layout-v04'}   # V0.4: variant D is the primary amplifier board; C stays in pcb/ as backup

a=argparse.ArgumentParser();a.add_argument('--cli',default='kicad-cli');args=a.parse_args()
commands=[]
def run(cmd):
 print(' '.join(cmd),flush=True);p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace');print(p.stdout,flush=True)
 if p.returncode:raise RuntimeError(p.stderr+'\n'+p.stdout)
 commands.append({'args':[x.replace(str(R)+'/', '') for x in cmd[1:]],'stdout':p.stdout,'stderr':p.stderr,'returncode':p.returncode})
for key in ['mono','psu']:
 board=R/'pcb'/(NAME[key]+'.kicad_pcb')
 for side,layer in [('top','F.Cu'),('bottom','B.Cu')]:
  dest=O/'native'/f'{key}-{side}.svg'
  cmd=[args.cli,'pcb','export','svg','--layers',layer+',Edge.Cuts','--mode-single','--fit-page-to-board','--exclude-drawing-sheet','-o',str(dest)]
  if side=='bottom':cmd.append('--mirror')
  run(cmd+[str(board)])
  dest.write_text('\n'.join(line.rstrip() for line in dest.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
 preview=O/'3d'/(NAME[key]+'-preview.kicad_pcb')
 for view in ['top','bottom','isometric']:
  cmd=[args.cli,'pcb','render','--width','1500','--height','1100','--background','opaque','--zoom','0.8','--side','bottom' if view=='bottom' else 'top']
  if view=='isometric':cmd+=['--rotate','315,0,30']
  run(cmd+['-o',str(O/'3d'/f'raw-{key}-{view}.png'),str(preview)])
(O/'native-export-log.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
