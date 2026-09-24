"""Power supply V0.4 layout. Coordinates in mm; angles follow KiCad. NOT FOR FABRICATION.
V0.3 AC / rectifier-terminal / capacitor-bank placement is kept. New in V0.4:
 - one 3P output terminal per channel (J203 left amp, J204 right amp), STAR moved next to them;
 - one RC snubber provision per secondary winding (Cx || Rs+Cs) in a row under each bridge terminal.
   Snubber parts are footprints only; fit after measuring the winding ringing with the real transformer.
"""
PSU_V04=dict(name='psu-layout-v04',size=(160,120),source='psu-netlist.xml',layout={
'J201':('Terminal2_P5.08',8,21,270),'J202':('Terminal2_P5.08',8,81,270),
'F201':('Fuse5x20_P25',17,10,0),'F202':('Fuse5x20_P25',17,70,0),
'BR1':('BridgeTerminal4_P5.08',24,30,270),'BR2':('BridgeTerminal4_P5.08',24,90,270),
'C201':('CP_D35_P10',75,24,270),'C202':('CP_D35_P10',119,24,270),
'C203':('CP_D35_P10',75,84,270),'C204':('CP_D35_P10',119,84,270),
'R201':('R_2W_P20',97,18,270),'R202':('R_2W_P20',97,80,270),
# snubber provisions: Cx across the winding, Cs+Rs in series across the winding
'C207':('Film_P15',25,53,180),'C208':('Film_P15',30,53,0),'R203':('R_2W_P20',49,53,0),
'C209':('Film_P15',25,113,180),'C210':('Film_P15',30,113,0),'R204':('R_2W_P20',49,113,0),
# output side: HF bypass at the STAR, one 3P terminal per channel
'C205':('Film_P5',133,52,0),'C206':('Film_P5',138,66,0),
'J203':('Terminal3_P5.08',151,42,270),'J204':('Terminal3_P5.08',151,66,270),
},anchors={'STAR':(138,59.08)},labels=[
('2x22VAC / V0.4',85,57),('<- 4 FASTON WIRES',48,36),('BR1 KBPC2510 ON CHASSIS',48,40),('<- 4 FASTON WIRES',48,96),('BR2 KBPC2510 ON CHASSIS',48,100),
('SNUBBER Cx+Rs/Cs  NOT FITTED',47,59.5),('SNUBBER Cx+Rs/Cs  NOT FITTED',47,106.5),('GND STAR',128,62),('L AMP: V+ G V-',151,37),('R AMP: V+ G V-',151,61),('SECONDARY ONLY',110,113)],
routes=[
# AC charging loops stay in the left-hand section (unchanged from V0.3)
('POS_AC1','F.Cu',4,['J201.1',(8,10),'F201.1'],'ac-positive'),
('POS_AC_FUSED','F.Cu',4,['F201.2',(48,10),(48,20),(24,20),'BR1.AC1'],'ac-positive'),
('POS_AC2','B.Cu',4,['J201.2',(12,30),(12,35.08),'BR1.AC2'],'ac-positive'),
('NEG_AC1','F.Cu',4,['J202.1',(8,70),'F202.1'],'ac-negative'),
('NEG_AC_FUSED','F.Cu',4,['F202.2',(48,70),(48,80),(24,80),'BR2.AC1'],'ac-negative'),
('NEG_AC2','B.Cu',4,['J202.2',(12,90),(12,95.08),'BR2.AC2'],'ac-negative'),
# snubber provisions hang off the winding terminals (pre-fuse side); thin traces carry ringing current only
('POS_AC2','B.Cu',1.0,[(12,35.08),(12,50),'C207.1'],'snubber'),
('POS_AC2','F.Cu',1.0,['C207.1','C208.1'],'snubber'),
('POS_SNUB','F.Cu',1.0,['C208.2','R203.1'],'snubber'),
('POS_AC1','F.Cu',1.0,['J201.1',(5,24),(5,48.5),(71,48.5),'R203.2'],'snubber'),
('POS_AC1','F.Cu',1.0,['C207.2',(10,48.5)],'snubber'),
('NEG_AC2','B.Cu',1.0,[(12,95.08),(12,110),'C209.1'],'snubber'),
('NEG_AC2','F.Cu',1.0,['C209.1','C210.1'],'snubber'),
('NEG_SNUB','F.Cu',1.0,['C210.2','R204.1'],'snubber'),
# NEG side return runs at y=110.6: the VEE charge trace (F.Cu, 4 mm) occupies y<=109.5 here
('NEG_AC1','F.Cu',1.0,['J202.1',(5,84),(5,110.6),(71,110.6),'R204.2'],'snubber'),
('NEG_AC1','F.Cu',1.0,['C209.2',(10,110.6)],'snubber'),
# charging enters the first capacitor; output is taken from the second (unchanged)
('VCC','F.Cu',4,['BR1.P',(31,40.16),(55,30),'C201.1'],'positive-charge'),
('VCC','F.Cu',4,['C201.1',(75,8),(119,8),'C202.1'],'positive-bank'),
('GND','B.Cu',4,['BR1.N',(31,45.24),(57,47.5),'C201.2'],'positive-charge-return'),
('GND','B.Cu',4,['C201.2',(75,48),(119,48),'C202.2'],'positive-bank-return'),
('GND','B.Cu',4,['BR2.P',(31,100.16),(54,90),'C203.1'],'negative-charge-return'),
('GND','B.Cu',4,['C203.1',(75,73),(119,73),'C204.1'],'negative-bank-return'),
('VEE','F.Cu',4,['BR2.N',(31,105.24),(56,107.5),'C203.2'],'negative-charge'),
('VEE','F.Cu',4,['C203.2',(75,110),(119,110),'C204.2'],'negative-bank'),
# output rails: VCC and VEE on F.Cu, GND star on B.Cu feeding one pad per terminal
('VCC','F.Cu',4,['C202.1',(145,24),(145,42),'J203.1'],'positive-output'),
('VCC','F.Cu',4,['J203.1',(157,42),(157,66),'J204.1'],'positive-output'),
('VEE','F.Cu',4,['C204.2',(145,94),(145,76.16),'J204.3'],'negative-output'),
('VEE','F.Cu',4,[(145,76.16),(145,52.16),'J203.3'],'negative-output'),
('GND','B.Cu',4,['C202.2',(126,41),(126,52),'STAR'],'positive-star-branch'),
('GND','B.Cu',4,['C204.1',(126,77),(126,66),'STAR'],'negative-star-branch'),
('GND','B.Cu',4,['STAR',(138,47.08),'J203.2'],'output-ground'),
('GND','B.Cu',4,['STAR',(138,71.08),'J204.2'],'output-ground'),
# bleeders span their own bank; HF bypass sits at the star
('VCC','F.Cu',.8,['R201.1',(97,8)],'bleeder'),
('GND','B.Cu',.8,['R201.2',(97,48)],'bleeder'),
('GND','B.Cu',.8,['R202.1',(97,73)],'bleeder'),
('VEE','F.Cu',.8,['R202.2',(97,110)],'bleeder'),
('VCC','F.Cu',.8,['C205.1',(133,42),(145,42)],'output-bypass'),
('VEE','F.Cu',.8,['C206.2',(145,66)],'output-bypass'),
])
