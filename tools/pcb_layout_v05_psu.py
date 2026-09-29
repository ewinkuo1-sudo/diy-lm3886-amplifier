"""Power supply V0.5 layout. Coordinates in mm; angles follow KiCad. NOT FOR FABRICATION.
Same nets and parts as V0.4 (electrical/internal-psu-v02.kicad_sch); only placement and copper change.
Why V0.5 (2026-09-29, chassis BZ4312A2 fit): V0.4 is 160 wide because the AC/rectifier-terminal strip
(x 0-50) and the output-terminal strip (x 126-160) flank the 2x2 capacitor bank. V0.5 stacks the strips:
 - top strip (y 0-27): AC-in terminal, fuse and 4-way bridge terminal per winding, positive on the left,
   negative on the right, mirrored;
 - middle: the four 381LX (D35) in two columns, positive bank x=35, negative bank x=90; the lower cap of
   each column is rotated 90 deg so the two GND pads (positive bank) / two VEE pads (negative bank) face
   each other and the bank bus is a straight segment under the bodies; the other rail bypasses the column
   on the outer side (VCC at x=24 F.Cu, GND at x=79 B.Cu);
 - bleeders R201/R202 stand in the 20 mm gap between the columns;
 - snubber provisions (Cx, Cs+Rs per winding, footprints only) stand along the left and right margins;
 - bottom strip (y 107-130): GND STAR with the two HF bypass caps, one 3P terminal per channel, VCC bus
   on F.Cu at y=113, GND on B.Cu at y=113, VEE around the outside at y=127 (its 4 mm stubs up to the
   terminal pads stop 1 mm short of the VCC bus).
Board 160x120 -> 125x130. Chassis front row: transformer D120 + this board leaves ~45 mm spare width.
"""
PSU_V05=dict(name='psu-layout-v05',size=(125,130),source='psu-netlist.xml',layout={
# top strip, positive winding (left) and negative winding (right, mirrored)
'J201':('Terminal2_P5.08',6,13,270),'F201':('Fuse5x20_P25',15,6,0),'BR1':('BridgeTerminal4_P5.08',21,23,0),
'J202':('Terminal2_P5.08',119,13,270),'F202':('Fuse5x20_P25',110,6,180),'BR2':('BridgeTerminal4_P5.08',104,23,180),
# capacitor bank: positive column x=35, negative column x=90; lower caps rotated so like pads face each other
'C201':('CP_D35_P10',35,45,270),'C202':('CP_D35_P10',35,93,90),
'C203':('CP_D35_P10',90,45,270),'C204':('CP_D35_P10',90,93,90),
# bleeders in the column gap
'R201':('R_2W_P20',57,60,270),'R202':('R_2W_P20',68,60,270),
# snubber provisions along the margins (Cx across the winding; Cs+Rs in series across the winding)
'C207':('Film_P15',7,27,270),'C208':('Film_P15',7,47,270),'R203':('R_2W_P20',7,67,270),
'C209':('Film_P15',118,27,270),'C210':('Film_P15',118,47,270),'R204':('R_2W_P20',118,67,270),
# bottom strip: HF bypass at the STAR, one 3P terminal per channel
'C205':('Film_P5',52,109,0),'C206':('Film_P5',68,109,0),
'J203':('Terminal3_P5.08',26,118,0),'J204':('Terminal3_P5.08',81,118,0),
},anchors={'STAR':(62.5,109)},labels=[
('BR1 / BR2 KBPC2510 ON CHASSIS',62.5,8),('4 FASTON WIRES EACH',62.5,11),
('V0.5',62.5,36),('2x22VAC',62.5,40),('SECONDARY ONLY',62.5,44),
('SNUB N/F',9,97),('SNUB N/F',116,97),('GND STAR',62.5,104.5),
('L AMP V+ G V-',31,111),('R AMP V+ G V-',86,111)],
routes=[
# --- positive winding: AC in -> fuse -> bridge terminal (F.Cu), AC2 return on B.Cu ---
('POS_AC1','F.Cu',4,['J201.1',(10,9),'F201.1'],'ac-positive'),
('POS_AC_FUSED','F.Cu',4,['F201.2',(40,13),(21,13),'BR1.AC1'],'ac-positive'),
('POS_AC2','B.Cu',4,['J201.2',(6,30),(26.08,30),'BR1.AC2'],'ac-positive'),
# --- negative winding, mirrored ---
('NEG_AC1','F.Cu',4,['J202.1',(115,9),'F202.1'],'ac-negative'),
('NEG_AC_FUSED','F.Cu',4,['F202.2',(85,13),(104,13),'BR2.AC1'],'ac-negative'),
('NEG_AC2','B.Cu',4,['J202.2',(119,30),(98.92,30),'BR2.AC2'],'ac-negative'),
# --- snubber provisions (thin; ringing current only), left margin ---
('POS_AC2','B.Cu',1.0,['C207.1',(7,30)],'snubber'),
('POS_AC2','F.Cu',1.0,['C208.1',(12,43),(12,31),'C207.1'],'snubber'),
('POS_SNUB','F.Cu',1.0,['C208.2','R203.1'],'snubber'),
('POS_AC1','F.Cu',1.0,['J201.1',(2,17),(2,87),'R203.2'],'snubber'),
('POS_AC1','F.Cu',1.0,['C207.2',(2,42)],'snubber'),
# --- snubber provisions, right margin ---
('NEG_AC2','B.Cu',1.0,['C209.1',(118,30)],'snubber'),
('NEG_AC2','F.Cu',1.0,['C210.1',(113,43),(113,31),'C209.1'],'snubber'),
('NEG_SNUB','F.Cu',1.0,['C210.2','R204.1'],'snubber'),
('NEG_AC1','F.Cu',1.0,['J202.1',(123,17),(123,87),'R204.2'],'snubber'),
('NEG_AC1','F.Cu',1.0,['C209.2',(123,42)],'snubber'),
# --- charging enters the first capacitor; output is taken from the second ---
('VCC','F.Cu',4,['BR1.P',(31.16,34),(35,40),'C201.1'],'positive-charge'),
('GND','B.Cu',4,['BR1.N',(40,30),(40,55),'C201.2'],'positive-charge-return'),
('GND','B.Cu',4,['C201.2','C202.2'],'positive-bank-return'),
('VCC','F.Cu',4,['C201.1',(24,50),(24,88),'C202.1'],'positive-bank'),
('GND','B.Cu',4,['BR2.P',(93.84,34),(90,40),'C203.1'],'negative-charge-return'),
('VEE','F.Cu',4,['BR2.N',(85,30),(85,55),'C203.2'],'negative-charge'),
('VEE','F.Cu',4,['C203.2','C204.2'],'negative-bank'),
('GND','B.Cu',4,['C203.1',(79,50),(79,88),'C204.1'],'negative-bank-return'),
# --- output: GND star on B.Cu, VCC bus on F.Cu at y=113, VEE around the outside at y=127 ---
('GND','B.Cu',4,['C202.2',(48,96),'STAR'],'positive-star-branch'),
('GND','B.Cu',4,['C204.1',(77,96),'STAR'],'negative-star-branch'),
('GND','B.Cu',4,['STAR','C205.2'],'output-ground'),
('GND','B.Cu',4,['STAR','C206.1'],'output-ground'),
('GND','B.Cu',4,['STAR',(62.5,113),(31.08,113),'J203.2'],'output-ground'),
('GND','B.Cu',4,[(62.5,113),(86.08,113),'J204.2'],'output-ground'),
('VCC','F.Cu',4,['C202.1',(35,100),(26,109),(26,113),'J203.1'],'positive-output'),
('VCC','F.Cu',4,[(26,113),(81,113),'J204.1'],'positive-output'),
('VEE','F.Cu',4,['C204.2',(103,88),(103,118),'J204.3'],'negative-output'),
('VEE','F.Cu',4,[(103,118),(103,127),(36.16,127),'J203.3'],'negative-output'),
# --- bleeders span their own bank; HF bypass sits at the star ---
('VCC','F.Cu',.8,['R201.1',(46,58),'C201.1'],'bleeder'),
('GND','B.Cu',.8,['R201.2',(40,80),(35,80)],'bleeder'),
('GND','B.Cu',.8,['R202.1',(79,60)],'bleeder'),
('VEE','F.Cu',.8,['R202.2',(80,80),(90,80)],'bleeder'),
('VCC','F.Cu',.8,['C205.1',(52,113)],'output-bypass'),
('VEE','F.Cu',.8,['C206.2',(76,106),(103,106)],'output-bypass'),
])
