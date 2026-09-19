"""Silkscreen assembly marks for DraftV03 footprints (pure Python, no pcbnew).

Polarity convention verified 2026-09-19 against tools/pcb_layout_v03.py routes:
every CP_* electrolytic has pad 1 on the more positive node
(C7: VCC/GND, C6: GND/VEE, C8: GND/L_MUTE, C201/C202: VCC/GND, C203/C204: GND/VEE),
so the "+" mark sits at pad 1 and the negative stripe at pad 2.
LM3886T: pad 1 is the leftmost lead of the outer row; the tab (heatsink, tied to V-)
is the body rectangle on the -y side.

Geometry only. Footprint dimensions remain UNVERIFIED until parts arrive.
"""

def _cp_geom(pads,body):
 x0,y0,x1,y1=body
 cx,cy=(x0+x1)/2,(y0+y1)/2
 r=(x1-x0)/2
 return cx,cy,r

def silk_marks(name,pads,body):
 """Return [((x0,y0),(x1,y1)),width] segments on F.SilkS."""
 segs=[]
 if name.startswith('CP_'):
  cx,cy,r=_cp_geom(pads,body)
  a=max(.5,r*.09)            # plus-sign half arm
  px,py=cx-.5*r,cy-.5*r       # plus centre, upper-left quadrant near pad 1
  segs.append((((px-a,py),(px+a,py)),.15))
  segs.append((((px,py-a),(px,py+a)),.15))
  sx=cx+.8*r;h=(r*r-(sx-cx)**2)**.5*.9   # negative stripe at pad-2 side
  w=max(.4,r*.06)
  segs.append((((sx,cy-h),(sx,cy+h)),w))
 elif name.startswith('LM3886T'):
  x0,y0,x1,y1=body
  segs.append((((x0,y0-.6),(x1,y0-.6)),.3))   # heatsink / tab edge
 return segs

def silk_texts(name,pads,body):
 """Return [(text,(x,y),size)] on F.SilkS."""
 texts=[]
 if name.startswith('LM3886T'):
  x0,y0,x1,y1=body
  texts.append(('1',(-2.3,0),.8))             # pin-1 marker beside pad 1
  texts.append(('TAB = V-  HEATSINK',((x0+x1)/2,(y0+y1)/2),.7))   # inside tab outline
 return texts
