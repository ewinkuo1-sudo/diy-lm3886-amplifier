"""V0.5 amplifier board (variant D lineage: solid B.Cu ground pour). Coordinates in mm; angles follow KiCad.
Same nets and parts as V0.3/V0.4 (electrical/lm3886-v01.kicad_sch); only placement and copper change.
Why V0.5 (2026-09-29, chassis BZ4312A2 fit): the 115 mm edge of the V0.4 board is the edge that lies along
the heatsink wall, so it eats chassis depth. Shrinking it to 90 mm is the only board change that buys depth.
Design moves vs V0.4 D:
 1. Board 115x90 -> 90x90. The IC block (U1, C3, C4, C6, C7, J5), output section (L1, R7, R5, C5, J2)
    and the feedback/input network (R1..R4, R6, C1) keep their V0.4 coordinates.
 2. C2 (ROE EGW 47uF BP, axial 40 x D20) stands upright instead of lying flat: new footprint
    BP_Axial_Vert_D20_P15 (pad 1 under the body centre, pad 2 = folded-down lead, 15 mm pitch). Pitch is a
    bench assumption until the real part is bent; body height above board ~42 mm, chassis inner height 112.
 3. R1 stands upright (x=73.5), C1 stands along the right edge (x=85.5, pads y 8/23) and J1 sits right
    under it (85,30); the corner mounting hole (86,4) then stays outside every courtyard.
 4. Mute parts (R8, C8, JP1) move from the removed strip (x>90) to the lower right under C2; L_MUTE runs
    along the top edge, between hole H2 and C1.2, down the right edge (x=88.5) and under C2 to R8.
 5. Mute VEE supply follows the bottom edge at y=88 to JP1.
NOT changed: U1 stays at y=14. Moving the IC to the board edge for direct heatsink-wall mounting (user's
option B, 2026-09-29) waits for the three IC measurements listed in docs/00 section 3.
Footprints and widths remain engineering assumptions. NOT FOR FABRICATION.
"""
AMP_V05=dict(name='mono-layout-v05d',size=(90,90),source='netlist.xml',layout={
'U1':('LM3886T_UNVERIFIED',39,14,0),
# local bypass, right under the pins (unchanged)
'C3':('Film_P5',45.8,19,0),'C4':('Film_P5',50.8,24.5,180),
# bulk caps flank the (former) STAR strip (unchanged)
'C7':('CP_D12.5_P5',36,34.5,0),'C6':('CP_D12.5_P5',54,34.5,0),
# feedback / input network to the right of the IC (unchanged)
'R4':('R_P7.5',64,18,270),'R3':('R_P7.5',68,25.5,90),
'R6':('R_P7.5',67.5,8,180),'R2':('R_P7.5',70,14.5,180),
# R1 stands upright and C1 stands along the right edge so the corner mounting hole H2 (86,4) stays clear
'R1':('R_P7.5',73.5,14.5,270),'C1':('Film_P15',85.5,23,90),
# input terminal moved in from the removed strip, right under C1
'J1':('Terminal2_P5.08',85,30,270),
# feedback DC-block cap now upright; pad 1 (GND, pour) under the body, pad 2 (L_FB_AC) toward R3
'C2':('BP_Axial_Vert_D20_P15',77,52,180),
# output section, left (unchanged)
'L1':('AirCoil_P20',9.5,45,270),'R7':('R_2W_P20',20.5,45,270),'J2':('Terminal2_P5.08',10,76,0),
'R5':('R_2W_P20',46,54,180),'C5':('Film_P5',55,45,270),
# power in, bottom centre (unchanged)
'J5':('Terminal3_P5.08',45.72,77,0),
# mute, lower right (relocated)
'R8':('R_P7.5',66,72,0),'C8':('CP_D12.5_P5',72,82,180),'JP1':('Header2_P2.54',80,72,270),
},anchors={'STAR':(50.8,34.5),'SG':(71.75,14.5)},labels=[
('TAB=VEE',30,5),('RCA IN',84,40),('TEST OUT',13,83),('V+  G  V-',50.8,83),('RUN',84,73),('GND PLANE B.Cu',44,42),
],routes=[
# --- IC local bypass (V0.4 change 1; D layers) ---
('VCC','F.Cu',1.0,['C3.1','U1.5'],'positive-pin'),
('VCC','F.Cu',1.2,['U1.1',(39,12),(45.8,12),'U1.5'],'positive-pin'),
('VEE','B.Cu',0.5,['C4.2',(44.1,22.5),'U1.4'],'negative-pin'),
# --- bulk caps (V0.4 change 2; D: C7 -> pin 1 feed on B.Cu, short vertical cut only) ---
('VCC','B.Cu',2.0,['C7.1',(36,17),'U1.1'],'positive-local'),
('VEE','F.Cu',1.5,['C6.2',(59,29),(47.6,26.3),'C4.2'],'negative-local'),
# --- power feed from J5 (bottom) ---
('VCC','F.Cu',3.0,['J5.1',(40,70),(36,62),'C7.1'],'positive-feed'),
('VEE','F.Cu',3.0,['J5.3',(58,72),(58,36),'C6.2'],'negative-feed'),
# --- output: power trunk on F.Cu (D), Kelvin sample on B.Cu over the top of the IC ---
('L_OUT','F.Cu',2.0,['U1.3',(40.5,17.5)],'output-power'),
('L_OUT','F.Cu',2.5,[(40.5,17.5),(40.5,25)],'output-power'),
('L_OUT','F.Cu',3.0,[(40.5,25),(34,31.5),(22,43.5),'L1.1'],'output-power'),
('L_OUT','F.Cu',1.5,['L1.1','R7.1'],'output-power'),
('L_OUT','F.Cu',1.2,['R5.2',(22,43.5)],'zobel-feed'),
('L_OUT','B.Cu',0.35,['U1.3',(42.4,4.3),(58.5,4.3),(58.5,22),(62,25.5),'R4.2'],'kelvin-feedback'),
('L_ZOBEL','F.Cu',0.8,['C5.2','R5.1'],'zobel'),
('L_SPK','F.Cu',3.0,['L1.2','R7.2'],'speaker'),
('L_SPK','F.Cu',3.0,['L1.2','J2.1'],'speaker'),
# --- feedback and input network ---
('L_INV','F.Cu',0.35,['U1.9',(55.5,16.5),'R4.1','R3.2'],'feedback'),
('L_FB_AC','F.Cu',0.35,['R3.1',(66,28),(62,50),'C2.2'],'feedback'),
('L_PLUS','F.Cu',0.35,['U1.10','R6.2','R2.2'],'input'),
('L_AC','F.Cu',0.35,['R6.1','C1.2'],'input'),
('L_IN','F.Cu',0.35,['C1.1','J1.1'],'input'),
('L_IN','F.Cu',0.35,['R1.2','C1.1'],'input'),
# --- mute ---
# hugs the top edge, slips between hole H2 and C1.2, then runs down the right edge and under C2 to R8
('L_MUTE','F.Cu',0.35,['U1.8',(50.9,4),(83,4),(83,6.3),(88.5,6.3),(88.5,40),(72,66),'R8.1'],'mute'),
('L_MUTE','F.Cu',0.35,['R8.1',(67,76),'C8.2'],'mute'),
('L_RUN','F.Cu',0.35,['R8.2','JP1.1'],'mute'),
# mute supply follows the bottom edge on F.Cu; never crosses the L_MUTE run
('VEE','F.Cu',0.8,['J5.3',(58.5,79.6),(58.5,88),(80,88),'JP1.2'],'mute-supply'),
],zones=[('GND','B.Cu',[(0,0),(90,0),(90,90),(0,90)])])
