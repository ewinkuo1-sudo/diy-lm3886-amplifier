"""V0.4 amplifier board, variant C (improved star ground). Coordinates in mm; angles follow KiCad.
Same nets and parts as V0.3 (electrical/lm3886-v01.kicad_sch); only placement and copper change.
Design moves vs V0.3 (docs/pcb README):
 1. C3 sits across U1.5 (V+) / U1.7 (GND), C4 across U1.4 (V-) / U1.7, both directly below the pin row.
 2. C6/C7 470uF and the STAR moved up to y=34.5 right under the IC; STAR is the short strip between them.
 3. J1 signal and ground run side by side to the C1/R1/R2 corner; R1.1/R2.1 form the local SG node.
 4. Zobel C5 ground enters STAR directly (C5 at 55,45); R5 output end joins the output trunk.
 5. C2 laid flat across the right half (pad 2 next to R3.1); mute parts move to the lower right.
Footprints and widths remain engineering assumptions. NOT FOR FABRICATION.
"""
AMP_C=dict(name='mono-layout-v04c',size=(115,90),source='netlist.xml',layout={
'U1':('LM3886T_UNVERIFIED',39,14,0),
# local bypass, right under the pins
'C3':('Film_P5',45.8,19,0),'C4':('Film_P5',50.8,24.5,180),
# bulk caps flank the STAR strip
'C7':('CP_D12.5_P5',36,34.5,0),'C6':('CP_D12.5_P5',54,34.5,0),
# feedback / input network to the right of the IC
'R4':('R_P7.5',64,18,270),'R3':('R_P7.5',68,25.5,90),
'R6':('R_P7.5',67.5,8,180),'R2':('R_P7.5',70,14.5,180),'R1':('R_P7.5',73,14.5,0),
'C1':('Film_P15',86,8,180),'J1':('Terminal2_P5.08',94,27,270),
'C2':('BP_Axial_L40_D20_P50',112,53,180),
# output section, left
'L1':('AirCoil_P20',9.5,45,270),'R7':('R_2W_P20',20.5,45,270),'J2':('Terminal2_P5.08',10,76,0),
'R5':('R_2W_P20',46,54,180),'C5':('Film_P5',55,45,270),
# power in, bottom centre (GND pin on the trunk line x=50.8)
'J5':('Terminal3_P5.08',45.72,77,0),
# mute, lower right
'R8':('R_P7.5',100,66,270),'C8':('CP_D12.5_P5',95,83,180),'JP1':('Header2_P2.54',110,72,270),
},anchors={'STAR':(50.8,34.5),'SG':(71.5,14.5)},labels=[
('TAB=VEE',30,5),('RCA IN',104,30),('TEST OUT',13,83),('V+  G  V-',50.8,83),('RUN',110,69),('GND STAR',44,42),('SG',72.5,19.5),
],routes=[
# --- IC local bypass (change 1) ---
('VCC','F.Cu',1.0,['C3.1','U1.5'],'positive-pin'),
('VCC','F.Cu',1.2,['U1.1',(39,12),(45.8,12),'U1.5'],'positive-pin'),
('GND','B.Cu',1.0,['C3.2','U1.7'],'local-decoupling'),
('GND','B.Cu',1.5,['C3.2','C4.1'],'local-decoupling'),
('GND','B.Cu',1.5,['C4.1','STAR'],'local-decoupling'),
('VEE','B.Cu',0.5,['C4.2',(44.1,22.5),'U1.4'],'negative-pin'),
# --- bulk caps and STAR strip (change 2) ---
('VCC','F.Cu',2.0,['C7.1',(36,17),'U1.1'],'positive-local'),
('VCC','F.Cu',1.2,[(36,22),(43.5,22),'C3.1'],'positive-local'),
('VEE','F.Cu',1.5,['C6.2',(59,29),(47.6,26.3),'C4.2'],'negative-local'),
('GND','B.Cu',2.0,['C7.2','STAR'],'local-decoupling'),
('GND','B.Cu',2.0,['C6.1','STAR'],'local-decoupling'),
# --- power feed from J5 (bottom) ---
('VCC','F.Cu',3.0,['J5.1',(40,70),(36,62),'C7.1'],'positive-feed'),
('GND','B.Cu',3.0,['J5.2','STAR'],'supply-return'),
('VEE','F.Cu',3.0,['J5.3',(58,72),(58,36),'C6.2'],'negative-feed'),
# --- output: power trunk on B.Cu, Kelvin sample on B.Cu over the top of the IC ---
('L_OUT','B.Cu',2.0,['U1.3',(40.5,17.5)],'output-power'),
('L_OUT','B.Cu',2.5,[(40.5,17.5),(40.5,25)],'output-power'),
('L_OUT','B.Cu',3.0,[(40.5,25),(34,31.5),(22,43.5),'L1.1'],'output-power'),
('L_OUT','B.Cu',1.5,['L1.1','R7.1'],'output-power'),
('L_OUT','B.Cu',1.2,['R5.2',(22,43.5)],'zobel-feed'),
('L_OUT','B.Cu',0.35,['U1.3',(42.4,4.3),(58.5,4.3),(58.5,22),(62,25.5),'R4.2'],'kelvin-feedback'),
('L_ZOBEL','F.Cu',0.8,['C5.2','R5.1'],'zobel'),
('L_SPK','F.Cu',3.0,['L1.2','R7.2'],'speaker'),
('L_SPK','F.Cu',3.0,['L1.2','J2.1'],'speaker'),
# --- feedback and input network (change 3) ---
('L_INV','F.Cu',0.35,['U1.9',(55.5,16.5),'R4.1','R3.2'],'feedback'),
('L_FB_AC','F.Cu',0.35,['R3.1',(66,28),(66,50),'C2.2'],'feedback'),
('L_PLUS','F.Cu',0.35,['U1.10','R6.2','R2.2'],'input'),
('L_AC','F.Cu',0.35,['R6.1','C1.2'],'input'),
('L_IN','F.Cu',0.35,['C1.1',(91,8),(91,24),'J1.1'],'input'),
('L_IN','F.Cu',0.35,['R1.2','C1.1'],'input'),
# --- ground branches; each family meets the others only at STAR ---
('GND','F.Cu',0.6,['J1.2',(88.5,26.6),(88.5,17.3),(75.5,17.3),'R1.1'],'signal-ground'),
('GND','F.Cu',0.6,['R1.1','SG','R2.1'],'signal-ground'),
('GND','B.Cu',0.6,['C2.1',(112,44),(101,36),'J1.2'],'signal-ground'),
('GND','B.Cu',0.8,['R1.1',(73.5,17.5),(73.5,32),(64,36),(56.5,38),(53.5,37.5),'STAR'],'signal-ground-to-star'),
('GND','B.Cu',1.0,['C5.1',(54,40),'STAR'],'zobel-return'),
('GND','B.Cu',3.0,['J2.2',(30,66),(40,52),(43.5,43),(47,38),'STAR'],'speaker-return'),
# mute timing-cap return joins the signal-ground branch at C2.1 (few mA), no separate path to STAR
('GND','B.Cu',0.6,['C8.1',(104,88.5),(113,80),(113,58),'C2.1'],'signal-ground-mute'),
# --- mute ---
('L_MUTE','F.Cu',0.35,['U1.8',(50.9,4),(98,4),(98,62),'R8.1'],'mute'),
('L_MUTE','F.Cu',0.35,['R8.1',(97,68),(90,80),'C8.2'],'mute'),
('L_RUN','F.Cu',0.35,['R8.2','JP1.1'],'mute'),
# mute supply runs along the bottom edge on F.Cu so it never crosses the L_MUTE run
('VEE','F.Cu',0.8,['J5.3',(62,86),(104,86),(113,78),(113,76),'JP1.2'],'mute-supply'),
])

# Variant D: identical placement and signal/power copper, but every GND branch is replaced by a
# solid B.Cu ground pour (thermal spokes to pads). The STAR anchor stays only as the label position.
# 2026-09-24 (user picked D as primary, C kept): the 3 mm output trunk moves to F.Cu so the pour is not
# cut diagonally across the left half; the C7->U1.1 V+ feed moves to B.Cu instead (short vertical cut only),
# and the redundant V+ branch to C3.1 is dropped (C3.1 is fed through the pin 1 -> pin 5 link).
def _d_routes():
 out=[]
 for net,layer,width,path,group in AMP_C['routes']:
  if net=='GND':continue
  if group=='positive-local' and path[0]==(36,22):continue
  if group=='positive-local':layer='B.Cu'
  if group in ('output-power','zobel-feed'):layer='F.Cu'
  out.append((net,layer,width,path,group))
 return out
AMP_D=dict(AMP_C,name='mono-layout-v04d',
 routes=_d_routes(),
 labels=[l for l in AMP_C['labels'] if l[0] not in ('GND STAR','SG')]+[('GND PLANE B.Cu',44,42)],
 zones=[('GND','B.Cu',[(0,0),(115,0),(115,90),(0,90)])])
