"""Power supply V0.5.1 layout: V0.5 with the bridge rectifiers ON the board (GBJ2510 upright) instead of
KBPC2510 on the chassis + four Faston wires per bridge. Coordinates in mm; angles follow KiCad. NOT FOR FABRICATION.
Same nets and parts as V0.5 (electrical/internal-psu-v02.kicad_sch); only BR1/BR2 footprint, their position and
the four charging/AC tracks that end on them change. Board stays 125 x 130.

Why (2026-10-01): transformer measured (2 x 22.29 Vac no-load, 4.2 A windings, ~0.3 ohm secondary loop) ->
each bridge sees ~2.5 A average, ~100 A first-cycle surge, 4-5 W at full sine. User chose GBJ2510 on board
(Diodes DS21221: body 30 x 20 x 3.8, flat leads 1.0 x 2.2, pitch 10 / 7.5 / 7.5, pin order + ~ ~ -, #6 hole,
IFSM 350 A, RthJC 1.0, ~20 C/W bare). Footprint GBJ_Upright_P10_7.5_7.5 (new in build_pcb_v051.py).

Placement: both bridges stand in the top strip at y=23, body (4 mm) between the fuse holders (body ends y=9.5)
and the capacitor courtyard (y=27 at the column centre). The marked face (+ ~ ~ -) looks toward the capacitors
(+y), so the metal back faces the board edge: a heatsink up to ~10 mm thick fits in y 11-21 over the AC tracks.
BR2 is NOT rotated 180 like the V0.5 terminal was (that would turn its metal back toward the capacitor), so the
right half is routed by hand instead of mirrored: P->GND, N->VEE on the negative winding.
"""
from pcb_layout_v05_psu import PSU_V05
import copy
PSU_V051=copy.deepcopy(PSU_V05)
PSU_V051['name']='psu-layout-v051'
PSU_V051['layout']['BR1']=('GBJ_Upright_P10_7.5_7.5',19,23,0)   # pads P 19 / AC1 29 / AC2 36.5 / N 44
PSU_V051['layout']['BR2']=('GBJ_Upright_P10_7.5_7.5',81,23,0)   # pads P 81 / AC1 91 / AC2 98.5 / N 106
PSU_V051['labels']=[('BR1 / BR2 GBJ2510 UPRIGHT',62.5,8),('HEATSINK SIDE TOWARD EDGE',62.5,11)]+[l for l in PSU_V05['labels'][2:]]
PSU_V051['labels']=[('V0.5.1' if l[0]=='V0.5' else l[0],l[1],l[2]) for l in PSU_V051['labels']]
REPLACE={
 'POS_AC_FUSED':('POS_AC_FUSED','F.Cu',4,['F201.2',(40,10),(29,13),'BR1.AC1'],'ac-positive'),
 'POS_AC2_main':('POS_AC2','B.Cu',4,['J201.2',(6,30),(36.5,30),'BR1.AC2'],'ac-positive'),
 'NEG_AC_FUSED':('NEG_AC_FUSED','F.Cu',4,['F202.2',(85,10),(91,13),'BR2.AC1'],'ac-negative'),
 'NEG_AC2_main':('NEG_AC2','B.Cu',4,['J202.2',(119,30),(98.5,30),'BR2.AC2'],'ac-negative'),
 'positive-charge':('VCC','F.Cu',4,['BR1.P',(19,29),'C201.1'],'positive-charge'),
 'positive-charge-return':('GND','B.Cu',4,['BR1.N',(44,55),'C201.2'],'positive-charge-return'),
 'negative-charge-return':('GND','B.Cu',4,['BR2.P',(81,36),'C203.1'],'negative-charge-return'),
 'negative-charge':('VEE','F.Cu',4,['BR2.N',(106,39),'C203.2'],'negative-charge'),
}
def key(route):
 net,layer,width,path,group=route
 if group in ('positive-charge','positive-charge-return','negative-charge-return','negative-charge'):return group
 if path[-1]=='BR1.AC1':return 'POS_AC_FUSED'
 if path[-1]=='BR1.AC2':return 'POS_AC2_main'
 if path[-1]=='BR2.AC1':return 'NEG_AC_FUSED'
 if path[-1]=='BR2.AC2':return 'NEG_AC2_main'
 return None
routes=[];seen=set()
for r in PSU_V05['routes']:
 k=key(r)
 if k is None:routes.append(r)
 else:routes.append(REPLACE[k]);seen.add(k)
assert seen==set(REPLACE),set(REPLACE)-seen
PSU_V051['routes']=routes
