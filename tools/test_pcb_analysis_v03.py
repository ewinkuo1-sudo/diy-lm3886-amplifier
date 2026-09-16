"""Regression tests for path topology, unit scaling, and reset DRC rules."""
import unittest,copy,json,tempfile
from pathlib import Path
from analyze_pcb_v03 import path,resistance
from run_pcb_drc_v03 import rules

def board(tracks,pads,vias=None):
 return {'name':'test','tracks':[{'a':a,'b':b,'width':w,'layer':l,'net':'N'} for a,b,w,l in tracks], 'pads':[{'ref':r,'number':'1','x':x,'y':y,'net':'N'} for r,x,y in pads],'vias':vias or [],'anchors':{}}
class Regression(unittest.TestCase):
 def test_mid_segment_terminal_is_connected(self):
  d=board([((0,0),(20,0),2,'F.Cu'),((10,0),(10,10),1,'F.Cu')],[('A',0,0),('B',10,10)])
  p=path(d,'N','A.1','B.1');self.assertAlmostEqual(p['length_mm'],20);self.assertAlmostEqual(p['sum_length_over_width'],15)
 def test_opposite_layers_require_physical_connection(self):
  d=board([((0,0),(10,0),1,'F.Cu'),((5,-5),(5,5),1,'B.Cu')],[('A',0,0),('B',5,5)])
  with self.assertRaises(AssertionError):path(d,'N','A.1','B.1')
  d['vias']=[{'x':5,'y':0,'net':'N'}]
  p=path(d,'N','A.1','B.1');self.assertEqual(p['via_transitions'],1);self.assertAlmostEqual(p['length_mm'],10)
 def test_mm_units_and_copper_temperature_scaling(self):
  # 100 mm x 2 mm, 34.8 um copper: independently calculated 24.4253 milliohms.
  route={'sum_length_over_width':50}
  r=resistance(route,.0348,25);self.assertAlmostEqual(r,.0244252873563,places=12)
  self.assertAlmostEqual(resistance(route,.0696,25),r/2)
  self.assertAlmostEqual(resistance(route,.0348,85),r*1.234)
 def test_reset_project_rules_are_rejected(self):
  source=Path(__file__).resolve().parents[1]/'pcb/mono-layout-v03.kicad_pro'
  self.assertEqual(rules(source)['min_clearance'],.3)
  data=json.loads(source.read_text());data['board']['design_settings']['rules']['min_clearance']=0
  with tempfile.TemporaryDirectory() as tmp:
   f=Path(tmp)/'reset.kicad_pro';f.write_text(json.dumps(data))
   with self.assertRaises(AssertionError):rules(f)
if __name__=='__main__':unittest.main()
