"""V0.6 amplifier board (90 x 80, IC flush with the heatsink edge) and power-supply board (92 x 120).
Coordinates in mm; angles follow KiCad. Same nets and parts as V0.5.1 (electrical/lm3886-v01.kicad_sch,
electrical/internal-psu-v02.kicad_sch) except the PSU snubber provisions, which are dropped (see below).
Chassis: 弘宙 102 (inner ~393 x 273 x 100), heatsinks 150 x 90 x 30 inside the side walls, amplifier boards
butt against the heatsink base plate, PSU in the middle of the rear row, transformer in front. NOT FOR FABRICATION.

Amplifier V0.6 vs V0.5 D (2026-10-01 night):
 1. U1 uses the KiCad library TO-220-11 vertical footprint (tab back 9.58 mm behind the odd pin row, even row
    5.08 mm in front). U1 sits at y = 9.58 so the tab back is flush with the board edge y = 0 and bolts straight to
    the heatsink base (user's option B). Datasheet geometry, not yet checked against the four ICs in hand.
 2. Nothing may run above the IC any more: the V0.5 Kelvin trace (B.Cu y = 4.3) and the mute trace (F.Cu y = 4)
    move below the pin rows (Kelvin B.Cu y = 17.5, mute F.Cu y = 12, dropping between pins 7 and 9); the
    redundant U1.1-U1.5 V+ jumper is gone (both pins are fed from C7 / C3).
 3. C3 / C4 follow the IC up (y 15 / 20.5). Board 90 x 90 -> 90 x 80: the output terminal, power terminal and
    the mute parts move up 10 mm; the input network, bulk caps and output section keep their V0.5 places,
    C2 (standing EGW) moves from y 52 to 49.
PSU V0.6 vs V0.5.1: board 125 x 130 -> 92 x 120 to fit the 102 centre column with the amplifier boards against
 the heatsinks. Four 381LX in two columns (positive x = 21, negative x = 71), bleeders in the 10 mm gap, GBJ
 bridges rotated 180 at the front (metal back toward the fuses, 10 mm heatsink envelope y 92-102), fuses and
 the AC terminals along the front edge toward the transformer, the two 3-way DC outputs along the rear edge
 toward the amplifier boards. GND star is the B.Cu link under the lower caps (y = 76). The snubber provisions
 C207-C210 / R203 / R204 do not fit and are NOT placed; if ringing needs them they go on the transformer leads.
"""
AMP_V06 = dict(name='mono-layout-v06', size=(90, 80), source='netlist.xml', layout={
    'U1': ('LM3886T_TO220-11', 39, 9.58, 0),          # odd pins y 9.58, even pins y 4.5, tab back at y 0
    'C3': ('Film_P5', 45.8, 15, 0), 'C4': ('Film_P5', 50.8, 20.5, 180),
    'C7': ('CP_D12.5_P5', 36, 34.5, 0), 'C6': ('CP_D12.5_P5', 54, 34.5, 0),
    'R4': ('R_P7.5', 64, 18, 270), 'R3': ('R_P7.5', 68, 25.5, 90),
    'R6': ('R_P7.5', 67.5, 8, 180), 'R2': ('R_P7.5', 70, 14.5, 180),
    'R1': ('R_P7.5', 73.5, 14.5, 270), 'C1': ('Film_P15', 85.5, 23, 90),
    'J1': ('Terminal2_P5.08', 85, 30, 270),
    'C2': ('BP_Axial_Vert_D20_P15', 77, 52, 180),
    'L1': ('AirCoil_P20', 9.5, 45, 270), 'R7': ('R_2W_P20', 20.5, 45, 270), 'J2': ('Terminal2_P5.08', 10, 74, 0),
    'R5': ('R_2W_P20', 46, 54, 180), 'C5': ('Film_P5', 55, 45, 270),
    'J5': ('Terminal3_P5.08', 45.72, 67, 0),
    'R8': ('R_P7.5', 66, 64.5, 0), 'C8': ('CP_D12.5_P5', 72, 73, 180), 'JP1': ('Header2_P2.54', 80, 64.5, 270),
}, anchors={'STAR': (50.8, 34.5), 'SG': (71.75, 14.5)}, labels=[
    ('TAB=EDGE', 62, 3), ('RCA IN', 84, 40), ('TEST OUT', 19, 71), ('V+  G  V-', 50.8, 73), ('RUN', 84, 61), ('GND PLANE B.Cu', 44, 42),
], routes=[
    # --- IC local bypass: C3 feeds pin 5, C4 feeds pin 4 (down between pins 3 and 5) ---
    ('VCC', 'F.Cu', 1.0, ['C3.1', 'U1.5'], 'positive-pin'),
    # pins 1 and 5 are both V+; join them on B.Cu between the two staggered pin rows (KiCad does not tie same-net pads)
    ('VCC', 'B.Cu', 1.0, ['U1.1', (39, 7), (45.8, 7), 'U1.5'], 'positive-pin'),
    ('VEE', 'F.Cu', 0.5, ['C4.2', (44.1, 18), 'U1.4'], 'negative-pin'),
    # --- bulk caps ---
    ('VCC', 'B.Cu', 2.0, ['C7.1', (36, 17), 'U1.1'], 'positive-local'),
    ('VEE', 'F.Cu', 1.5, ['C6.2', (59, 25), (48.5, 25), 'C4.2'], 'negative-local'),
    # --- power feed from J5 ---
    ('VCC', 'F.Cu', 3.0, ['J5.1', (40, 60), (36, 52), 'C7.1'], 'positive-feed'),
    ('VEE', 'F.Cu', 3.0, ['J5.3', (58, 62), (58, 36), 'C6.2'], 'negative-feed'),
    # --- output: power trunk on F.Cu, Kelvin sample on B.Cu below the pin rows ---
    ('L_OUT', 'F.Cu', 2.0, ['U1.3', (40.5, 17.5)], 'output-power'),
    ('L_OUT', 'F.Cu', 2.5, [(40.5, 17.5), (40.5, 25)], 'output-power'),
    ('L_OUT', 'F.Cu', 3.0, [(40.5, 25), (34, 31.5), (22, 43.5), 'L1.1'], 'output-power'),
    ('L_OUT', 'F.Cu', 1.5, ['L1.1', 'R7.1'], 'output-power'),
    ('L_OUT', 'F.Cu', 1.2, ['R5.2', (22, 43.5)], 'zobel-feed'),
    ('L_OUT', 'B.Cu', 0.35, ['U1.3', (42.4, 17.5), (58.5, 17.5), (58.5, 22), (62, 25.5), 'R4.2'], 'kelvin-feedback'),
    ('L_ZOBEL', 'F.Cu', 0.8, ['C5.2', 'R5.1'], 'zobel'),
    ('L_SPK', 'F.Cu', 3.0, ['L1.2', 'R7.2'], 'speaker'),
    ('L_SPK', 'F.Cu', 3.0, ['L1.2', 'J2.1'], 'speaker'),
    # --- feedback and input network ---
    ('L_INV', 'B.Cu', 0.35, ['U1.9', (52.6, 13), (57.5, 13), 'R4.1'], 'feedback'),
    ('L_INV', 'F.Cu', 0.35, ['R4.1', 'R3.2'], 'feedback'),
    ('L_FB_AC', 'F.Cu', 0.35, ['R3.1', (66, 28), (62, 50), 'C2.2'], 'feedback'),
    ('L_PLUS', 'F.Cu', 0.35, ['U1.10', 'R6.2'], 'input'),
    ('L_PLUS', 'B.Cu', 0.35, ['R6.2', 'R2.2'], 'input'),          # hops under the mute trace
    ('L_AC', 'F.Cu', 0.35, ['R6.1', 'C1.2'], 'input'),
    ('L_IN', 'F.Cu', 0.35, ['C1.1', 'J1.1'], 'input'),
    ('L_IN', 'F.Cu', 0.35, ['R1.2', 'C1.1'], 'input'),
    # --- mute: drops between pins 7 and 9, runs under the input network at y = 12, then down the right edge ---
    ('L_MUTE', 'F.Cu', 0.35, ['U1.8', (50.9, 12), (83, 12), (88.5, 12), (88.5, 58), (72, 62), 'R8.1'], 'mute'),
    ('L_MUTE', 'F.Cu', 0.35, ['R8.1', (67, 68.5), 'C8.2'], 'mute'),
    ('L_RUN', 'F.Cu', 0.35, ['R8.2', 'JP1.1'], 'mute'),
    ('VEE', 'F.Cu', 0.8, ['J5.3', (58.5, 69.6), (58.5, 78), (80, 78), 'JP1.2'], 'mute-supply'),
], zones=[('GND', 'B.Cu', [(0, 0), (90, 0), (90, 80), (0, 80)])])

PSU_V06 = dict(name='psu-layout-v06', size=(92, 120), source='psu-netlist.xml', layout={
    # rear edge: one 3-way DC output per channel (pin 1 VCC, 2 GND, 3 VEE), HF bypass caps
    'J203': ('Terminal3_P5.08', 12, 4, 0),             # (12,4) VCC (17.08,4) GND (22.16,4) VEE  -> L amp
    'J204': ('Terminal3_P5.08', 67.84, 4, 0),          # (67.84,4) VCC (72.92,4) GND (78,4) VEE -> R amp
    'C205': ('Film_P5', 33, 10, 0),                    # (33,10) VCC (38,10) GND
    'C206': ('Film_P5', 84, 10, 0),                    # (84,10) GND (89,10) VEE
    # capacitor bank: positive column x = 21 (pads 26 = VCC, 16 = GND), negative column x = 71 (76 = GND, 66 = VEE)
    'C201': ('CP_D35_P10', 26, 31, 180), 'C202': ('CP_D35_P10', 26, 69, 180),
    'C203': ('CP_D35_P10', 76, 31, 180), 'C204': ('CP_D35_P10', 76, 69, 180),
    # bleeders standing in the column gap
    'R201': ('R_2W_P20', 44, 30, 270),                 # (44,30) VCC (44,50) GND
    'R202': ('R_2W_P20', 50, 54, 270),                 # (50,54) GND (50,74) VEE
    # bridges: rotation 180 -> metal back toward +y (fuses), marked face toward the capacitors
    'BR1': ('GBJ_Upright_P10_7.5_7.5', 31, 90, 180),   # P (31,90) AC1 (21,90) AC2 (13.5,90) N (6,90)
    'BR2': ('GBJ_Upright_P10_7.5_7.5', 86, 90, 180),   # P (86,90) AC1 (76,90) AC2 (68.5,90) N (61,90)
    # front edge: fuses and AC terminals toward the transformer
    'F201': ('Fuse5x20_P25', 8, 106.5, 0), 'F202': ('Fuse5x20_P25', 57, 106.5, 0),
    'J201': ('Terminal2_P5.08', 12, 116, 0),           # (12,116) POS_AC1 (17.08,116) POS_AC2
    'J202': ('Terminal2_P5.08', 74.92, 116, 0),        # (74.92,116) NEG_AC1 (80,116) NEG_AC2
}, anchors={'STAR': (46, 78)}, labels=[
    ('L AMP', 17, 11), ('R AMP', 72, 11), ('V0.6', 46, 44), ('2x22VAC', 46, 47.5), ('GND STAR B.Cu', 46, 81),
    ('GBJ2510 UPRIGHT', 46, 84), ('HEATSINK SIDE ->', 46, 96), ('T1 22V #1', 24, 113), ('T1 22V #2', 62, 113),
], routes=[
    # --- VCC: bank on F.Cu x = 26, bus y = 16 to both outputs ---
    ('VCC', 'F.Cu', 3.0, ['C202.1', 'C201.1', (26, 16), (12, 16), 'J203.1'], 'positive-bank'),
    ('VCC', 'F.Cu', 3.0, [(26, 16), (33, 16), (44, 16), (67.84, 16), 'J204.1'], 'positive-output'),
    ('VCC', 'F.Cu', 1.0, ['C205.1', (33, 16)], 'output-bypass'),
    ('VCC', 'F.Cu', 0.8, ['R201.1', (44, 16)], 'bleeder'),
    ('VCC', 'F.Cu', 3.0, ['BR1.P', (31, 80), (26, 76), 'C202.1'], 'positive-charge'),
    # --- GND: columns on B.Cu, star link under the lower caps, drops to the outputs ---
    ('GND', 'B.Cu', 3.0, ['C201.2', 'C202.2'], 'positive-bank-return'),
    ('GND', 'B.Cu', 3.0, ['C201.2', (16, 6), 'J203.2'], 'output-ground'),
    ('GND', 'B.Cu', 3.0, ['C203.1', 'C204.1'], 'negative-bank-return'),
    ('GND', 'B.Cu', 3.0, ['C203.1', (76, 13), (74, 11), (74, 6), 'J204.2'], 'output-ground'),
    ('GND', 'B.Cu', 1.0, ['C205.2', (38, 13), (76, 13)], 'output-bypass'),
    ('GND', 'B.Cu', 1.0, ['C206.1', (84, 13), (76, 13)], 'output-bypass'),
    ('GND', 'B.Cu', 3.0, ['C202.2', (16, 78), (44, 78), 'STAR', (47, 78), (76, 78), 'C204.1'], 'star'),
    ('GND', 'B.Cu', 0.8, ['R201.2', (44, 78)], 'bleeder'),
    ('GND', 'B.Cu', 0.8, ['R202.1', (47, 54), (47, 78)], 'bleeder'),
    ('GND', 'B.Cu', 3.0, ['BR1.N', (6, 78), (16, 78)], 'positive-charge-return'),
    ('GND', 'B.Cu', 3.0, ['BR2.P', (86, 78), (76, 78)], 'negative-charge-return'),
    # --- VEE: bank on F.Cu x = 66; right output on F.Cu, left output on B.Cu under the VCC bus ---
    ('VEE', 'F.Cu', 3.0, ['C203.2', 'C204.2'], 'negative-bank'),
    ('VEE', 'F.Cu', 2.5, ['C203.2', (66, 26), (78, 26), (89, 26), 'C206.2'], 'negative-output'),
    ('VEE', 'F.Cu', 2.5, [(78, 26), 'J204.3'], 'negative-output'),
    ('VEE', 'B.Cu', 2.5, ['C203.2', (66, 24.5), (22.16, 24.5), 'J203.3'], 'negative-output'),
    ('VEE', 'F.Cu', 3.0, ['C204.2', (66, 74), 'R202.2'], 'bleeder'),
    ('VEE', 'F.Cu', 3.0, ['BR2.N', (61, 78), (66, 74)], 'negative-charge'),
    # --- AC: terminal -> fuse -> bridge AC1 on F.Cu, AC2 return on B.Cu ---
    ('POS_AC1', 'F.Cu', 3.0, ['J201.1', (8, 112), 'F201.1'], 'ac-positive'),
    ('POS_AC_FUSED', 'F.Cu', 3.0, ['F201.2', (33, 100), (26, 93), 'BR1.AC1'], 'ac-positive'),
    ('POS_AC2', 'B.Cu', 3.0, ['J201.2', (13.5, 112.5), 'BR1.AC2'], 'ac-positive'),
    ('NEG_AC1', 'F.Cu', 3.0, ['J202.1', (60.5, 116), (57, 112.5), 'F202.1'], 'ac-negative'),
    ('NEG_AC_FUSED', 'F.Cu', 3.0, ['F202.2', (82, 100), (78, 92), 'BR2.AC1'], 'ac-negative'),
    ('NEG_AC2', 'B.Cu', 2.0, ['J202.2', (79, 115), (79, 110), (70.5, 103), (68.5, 101), 'BR2.AC2'], 'ac-negative'),
], zones=[])
