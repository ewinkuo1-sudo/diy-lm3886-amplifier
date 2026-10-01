"""V0.6 control / protection board (CTRL, 70 x 120) and mains soft-start board (MAINS, 70 x 100).
Coordinates in mm, angles follow KiCad (CCW; pad (px,py) -> (x + px cos a + py sin a, y - px sin a + py cos a)).
Nets and parts come from electrical/control-v01.kicad_sch and electrical/mains-v01.kicad_sch (2026-10-01).
NOT FOR FABRICATION: footprints are KiCad library outlines or provisional DraftV03 outlines, relays not in hand.

CTRL floor plan (y = 0 is the rear edge, toward the amplifier boards and the back panel):
  y  1- 9   J303 J302 (speaker in/out, R and L)   J304 J305 (mute to the amplifier JP1 positions)
  y 12-40   K301 (contacts face the rear) K302 (contacts face the left edge)   U303 U304 mute optos on the right
  y 43-52   relay driver Q301 + flyback D302/D303 + R308/R303; RLY trunk on y = 47
  y 56-80   U302 UPC1237 with its DC / AC-off / delay networks; aux bridge D306-D309 + J301 on the right
  y 84-118  +12V bus on y = 92; timer (TL431) centre, 7812 + caps right, LEDs + J308/J309 left
GND is a B.Cu pour. +12V runs on B.Cu (x = 50) between the F.Cu bus y = 39 (via) and y = 92 (via); R301/R308
reach it with short B.Cu stubs. The AMP_L/R_OUT sense runs are B.Cu (x = 26 / 11) from a relay COM pad to
R304 / R305. The G2RL footprint has two pads per contact terminal: a short track joins each pair.

MAINS: mains copper (L_IN, L_SW, L_T1, N_IN) stays at x >= 32 (relay contact side, NTC, connectors on the
right edge); the 12 V coil side (TRIG_*, BYP_HI, GND_CTRL) stays at x <= 24. The two relays bridge the gap,
coil pins at x = 12 and contacts at x >= 32 (15 mm inside the G2RL footprint itself). No ground pour.
"""
CTRL_V06 = dict(name='ctrl-layout-v06', size=(70, 120), source='control-v01-netlist.xml', layout={
    # --- rear edge connectors (Terminal2: pin 1 at (x, y), pin 2 at (x + 5.08, y); rotation 180 mirrors) ---
    'J303': ('Terminal2_P5.08', 14.58, 5, 180),   # 1 AMP_R_OUT (14.58,5)  2 SPK_R (9.5,5)
    'J302': ('Terminal2_P5.08', 26, 5, 0),         # 1 AMP_L_OUT (26,5)     2 SPK_L (31.08,5)
    'J304': ('Terminal2_P5.08', 44, 5, 0),         # 1 RUN_L (44,5)         2 VEE_L (49.08,5)
    'J305': ('Terminal2_P5.08', 56, 5, 0),         # 1 RUN_R (56,5)         2 VEE_R (61.08,5)
    # --- speaker relays (G2RL-1-E: A1 (0,0) A2 (7.5,0) COM (0/7.5,20) NO (0/7.5,25)) ---
    'K301': ('Relay_G2RL-1-E', 6, 22, 90),         # A1 (6,22) A2 (6,14.5) COM (26,22)(26,14.5) NO (31,22)(31,14.5)
    'K302': ('Relay_G2RL-1-E', 31, 29.5, 270),     # A1 (31,29.5) A2 (31,37) COM (11,29.5)(11,37) NO (6,29.5)(6,37)
    # --- mute opto-couplers (DIP-4: A (0,0) K (0,2.54) E (7.62,2.54) C (7.62,0)) ---
    'U303': ('Opto_DIP-4', 44, 19, 90),            # A (44,19) K (46.54,19) E (46.54,11.38) C (44,11.38)
    'U304': ('Opto_DIP-4', 56, 19, 90),            # A (56,19) K (58.54,19) E (58.54,11.38) C (56,11.38)
    'R309': ('R_P7.5', 44, 30, 90),                # 1 RLY (44,30) 2 OPTO_A (44,22.5)
    # --- relay driver (TO-92 wide: pins at 0 / 2.54 / 5.08) ---
    'D302': ('D_DO-41_P10.16', 14.16, 45, 180),    # 1 K RLY (14.16,45) 2 A GND (4,45)
    'D303': ('D_DO-41_P10.16', 28.16, 45, 180),    # 1 K RLY (28.16,45) 2 A GND (18,45)
    'Q301': ('TO-92W_CBE', 37, 43, 0),             # C (37,43) B (39.54,43) E (42.08,43)
    'R308': ('R_P7.5', 46, 45, 0),                 # 1 Q1B (46,45) 2 +12V (53.5,45)
    'R303': ('R_P7.5', 42.7, 59.5, 90),            # 1 RLYDRV (42.7,59.5) 2 Q1B (42.7,52)
    # --- UPC1237 and its networks (SIP-8 pins at x = 30 + 2.54 (n-1), y = 66) ---
    'U302': ('SIP-8_P2.54', 30, 66, 0),
    'R301': ('R_P7.5', 47.78, 60.5, 90),           # 1 VREF (47.78,60.5) 2 +12V (47.78,53)
    'R302': ('R_P7.5', 45.24, 70, 270),            # 1 DELAY (45.24,70) 2 VREF (45.24,77.5)
    'C305': ('CP_D5_P2', 41, 72, 180),             # 1 DELAY (41,72) 2 GND (39,72)
    'R304': ('R_P7.5', 26, 68, 270),               # 1 AMP_L_OUT (26,68) 2 DCDET (26,75.5)
    'R305': ('R_P7.5', 11, 68, 270),               # 1 AMP_R_OUT (11,68) 2 DCDET (11,75.5)
    'C306': ('CP_D6.3_P2.5', 18, 80, 0),           # 1 DCDET (18,80) 2 GND (20.5,80)
    'R306': ('R_P7.5', 52, 50, 0),                 # 1 ACDET (52,50) 2 ACSENSE (59.5,50)
    'D301': ('D_DO-35_P7.62', 63, 50, 90),         # 1 K ACSENSE (63,50) 2 A AC_A (63,42.38)
    'R307': ('R_P7.5', 52, 56, 270),               # 1 ACDET (52,56) 2 GND (52,63.5)
    'C307': ('CP_D5_P2', 57, 56, 0),               # 1 ACDET (57,56) 2 GND (59,56)
    # --- auxiliary supply, right side ---
    'J301': ('Terminal2_P5.08', 65, 38, 90),       # 1 AC_A (65,38) 2 AC_B (65,32.92)
    'D306': ('D_DO-41_P10.16', 56.5, 64, 0),       # 1 K RAW (56.5,64) 2 A AC_A (66.66,64)
    'D307': ('D_DO-41_P10.16', 56.5, 68, 0),       # 1 K RAW (56.5,68) 2 A AC_B (66.66,68)
    'D308': ('D_DO-41_P10.16', 56.5, 72, 0),       # 1 K AC_A (56.5,72) 2 A GND (66.66,72)
    'D309': ('D_DO-41_P10.16', 56.5, 76, 0),       # 1 K AC_B (56.5,76) 2 A GND (66.66,76)
    'C301': ('CP_D12.5_P5', 54, 88, 90),           # 1 RAW (54,88) 2 GND (54,83)
    'C302': ('Film_P5', 38, 86, 0),                # 1 RAW (38,86) 2 GND (43,86)
    'U301': ('TO-220_IN-GND-OUT', 62, 98, 0),      # IN (62,98) GND (64.54,98) OUT (67.08,98)
    'C303': ('CP_D5_P2', 63, 86, 0),               # 1 +12V (63,86) 2 GND (65,86)
    'C304': ('Film_P5', 63, 92, 0),                # 1 +12V (63,92) 2 GND (68,92)
    # --- soft-start bypass timer, centre front ---
    'R312': ('R_P7.5', 30, 98, 0),                 # 1 +12V (30,98) 2 TMR (37.5,98)
    'D305': ('D_DO-35_P7.62', 30, 101.5, 0),       # 1 K +12V (30,101.5) 2 A TMR (37.62,101.5)
    'C308': ('CP_D5_P2', 42, 98, 0),               # 1 TMR (42,98) 2 GND (44,98)
    'U305': ('TO-92W_REF-A-K', 38, 106.5, 0),      # REF (38,106.5) A (40.54,106.5) K (43.08,106.5)
    'R313': ('R_P7.5', 45.5, 106, 0),              # 1 TLK (45.5,106) 2 +12V (53,106)
    'R314': ('R_P7.5', 45.5, 110, 0),              # 1 TLK (45.5,110) 2 Q2B (53,110)
    'Q302': ('TO-92W_CBE', 58.5, 112.5, 90),       # C (58.5,112.5) B (58.5,109.96) E (58.5,107.42)
    'R315': ('R_P7.5', 44, 114.5, 0),              # 1 TMR (44,114.5) 2 BYP_HI (51.5,114.5)
    'J306': ('Terminal2_P5.08', 66, 111, 90),      # 1 BYP_HI (66,111) 2 GND (66,105.92)
    # --- LEDs and ground, left front ---
    'R310': ('R_P7.5', 3, 104, 270),               # 1 RLY (3,104) 2 LED_G (3,111.5)
    'J307': ('Terminal2_P5.08', 9, 112, 0),        # 1 LED_G (9,112) 2 GND (14.08,112)
    'R311': ('R_P7.5', 26, 98.5, 270),             # 1 +12V (26,98.5) 2 LED_R (26,106)
    'J308': ('Terminal2_P5.08', 26, 112, 180),     # 1 LED_R (26,112) 2 RLY (20.92,112)
    'J309': ('Terminal2_P5.08', 6, 88, 0),         # 1 GND (6,88) 2 GND (11.08,88)
}, anchors={'via_power_12a': (50, 39), 'via_power_12b': (50, 92)}, labels=[
    ('MUTE L', 50, 27), ('MUTE R', 62, 27),
    ('12VAC', 58, 31), ('GND STAR', 5, 82.5), ('LED G', 11.5, 106), ('LED R', 21, 105), ('K_BYP', 61, 117.5),
    ('GND PLANE B.Cu', 48, 36), ('+12V B.Cu', 47, 42),
], routes=[
    # --- speaker path, 2.0 mm; the two pads of each relay contact are joined by a short track ---
    ('AMP_L_OUT', 'F.Cu', 2.0, ['J302.1', (26, 14.5), (26, 22)], 'speaker'),           # K301 COM pads
    ('SPK_L', 'F.Cu', 2.0, ['J302.2', (31, 14.5), (31, 22)], 'speaker'),               # K301 NO pads
    ('AMP_R_OUT', 'F.Cu', 2.0, ['J303.1', (13.5, 8), (13.5, 27), (11, 29.5), (11, 37)], 'speaker'),   # K302 COM
    ('SPK_R', 'F.Cu', 2.0, ['J303.2', (3.5, 8), (3.5, 27), (6, 29.5), (6, 37)], 'speaker'),         # K302 NO
    # DC-detect sense runs on B.Cu from a COM pad straight to R304 / R305 pad 1
    ('AMP_L_OUT', 'B.Cu', 0.5, [(26, 22), 'R304.1'], 'dc-sense'),
    ('AMP_R_OUT', 'B.Cu', 0.5, [(11, 37), 'R305.1'], 'dc-sense'),
    # --- relay drive: RLY trunk on y = 47 and its branches ---
    ('RLY', 'F.Cu', 0.5, [(3, 47), (8.5, 47), (14.16, 47), (28.16, 47), (37, 47)], 'relay-drive'),
    ('RLY', 'F.Cu', 0.5, ['D302.1', (14.16, 47)], 'relay-drive'),
    ('RLY', 'F.Cu', 0.5, ['D303.1', (28.16, 47)], 'relay-drive'),
    ('RLY', 'F.Cu', 0.5, ['Q301.C', (37, 47)], 'relay-drive'),
    ('RLY', 'F.Cu', 0.5, [(8.5, 47), (8.5, 25), 'K301.A1'], 'relay-drive'),            # K301 A1 (6,22)
    ('RLY', 'F.Cu', 0.5, ['Q301.C', (37, 40), (33.5, 40), (33.5, 32), 'K302.A1'], 'relay-drive'),   # (31,29.5)
    ('RLY', 'F.Cu', 0.5, [(37, 40), (40, 37), (40, 30), 'R309.1'], 'relay-drive'),
    ('RLY', 'F.Cu', 0.5, [(3, 47), (3, 96), (3, 104)], 'relay-drive'),                  # left column to R310.1
    ('RLY', 'F.Cu', 0.5, [(3, 104), 'R310.1'], 'relay-drive'),
    ('RLY', 'F.Cu', 0.5, [(3, 96), (20.92, 96), 'J308.2'], 'relay-drive'),              # (20.92,112)
    # --- Q301 base ---
    ('Q1B', 'F.Cu', 0.35, ['R303.2', (46, 52), 'R308.1'], 'driver'),                   # (42.7,52) -> (46,45)
    ('Q1B', 'F.Cu', 0.35, ['R308.1', (39.54, 45), 'Q301.B'], 'driver'),
    ('RLYDRV', 'F.Cu', 0.35, ['U302.6', 'R303.1'], 'driver'),                           # (42.7,66) -> (42.7,59.5)
    # --- +12V: F.Cu stub y = 39 -> via -> B.Cu drop at x = 50 -> via -> F.Cu bus y = 92 ---
    ('+12V', 'F.Cu', 0.8, ['Q301.E', (42.08, 39), (50, 39)], 'power-12'),
    ('+12V', 'B.Cu', 0.8, [(50, 39), (50, 45), (50, 53), (50, 92)], 'power-12'),
    ('+12V', 'B.Cu', 0.8, ['R308.2', (50, 45)], 'power-12'),                              # (51.5,45)
    ('+12V', 'B.Cu', 0.8, ['R301.2', (50, 53)], 'power-12'),                              # (47.78,53)
    ('+12V', 'F.Cu', 0.8, [(26, 92), (30, 92), (50, 92), (54.5, 92), (54.5, 106), 'R313.2'], 'power-12'),
    ('+12V', 'F.Cu', 0.8, ['R311.1', (26, 92)], 'power-12'),
    ('+12V', 'F.Cu', 0.8, ['R312.1', (30, 92)], 'power-12'),
    ('+12V', 'F.Cu', 0.8, ['D305.1', 'R312.1'], 'power-12'),                              # (30,102) -> (30,98)
    ('+12V', 'F.Cu', 0.8, ['Q302.E', (58.5, 106), 'R313.2'], 'power-12'),                 # (58.5,107.42) -> (53,106)
    ('+12V', 'F.Cu', 0.8, ['U301.OUT', (68.5, 99.5), (68.5, 102.5), (60.5, 102.5), 'Q302.E'], 'power-12'),
    ('+12V', 'F.Cu', 0.8, ['U301.OUT', (67.08, 94), 'C304.1'], 'power-12'),               # (63,92)
    ('+12V', 'F.Cu', 0.8, ['C304.1', 'C303.1'], 'power-12'),                              # (63,92) -> (63,86)
    # --- UPC1237 reference, delay, detectors ---
    ('VREF', 'F.Cu', 0.35, ['R301.1', 'U302.8'], 'protector'),
    ('VREF', 'F.Cu', 0.35, ['R302.2', (49.5, 77.5), (49.5, 68), 'U302.8'], 'protector'),
    ('DELAY', 'F.Cu', 0.35, ['U302.7', 'R302.1'], 'protector'),
    ('DELAY', 'F.Cu', 0.35, ['R302.1', (41, 70), 'C305.1'], 'protector'),
    ('DCDET', 'F.Cu', 0.35, ['R305.2', (11, 78), (18, 78), (26, 78), (32.54, 78), 'U302.2'], 'protector'),
    ('DCDET', 'F.Cu', 0.35, ['R304.2', (26, 78)], 'protector'),
    ('DCDET', 'F.Cu', 0.35, ['C306.1', (18, 78)], 'protector'),
    ('ACDET', 'F.Cu', 0.35, ['U302.4', (37.62, 63.5), (36, 62), (36, 55.5), (52, 55.5), 'R307.1'], 'protector'),
    ('ACDET', 'F.Cu', 0.35, ['R306.1', 'R307.1'], 'protector'),                           # (52,50) -> (52,56)
    ('ACDET', 'F.Cu', 0.35, ['R307.1', 'C307.1'], 'protector'),
    ('ACSENSE', 'F.Cu', 0.35, ['R306.2', 'D301.1'], 'protector'),
    ('AC_A', 'F.Cu', 0.5, ['D301.2', 'J301.1'], 'aux-ac'),                                 # (63,42.38) -> (65,38)
    # --- auxiliary bridge and raw rail ---
    ('AC_A', 'F.Cu', 0.5, ['J301.1', (66.66, 40), 'D306.2'], 'aux-ac'),                   # (66.66,64)
    ('AC_A', 'B.Cu', 0.5, ['D306.2', 'D308.1'], 'aux-ac'),                                 # under D307
    ('AC_B', 'F.Cu', 0.5, ['J301.2', (68.5, 36), (68.5, 66), 'D307.2'], 'aux-ac'),         # (65,32.92) -> (66.66,68)
    ('AC_B', 'F.Cu', 0.5, ['D307.2', (63.5, 69), (63.5, 74), (58.5, 74), 'D309.1'], 'aux-ac'),
    ('RAW', 'F.Cu', 1.0, ['D306.1', 'D307.1'], 'aux-raw'),
    ('RAW', 'F.Cu', 1.0, ['D307.1', (53, 71.5), (53, 78), (46.5, 80), (46.5, 90), 'C301.1'], 'aux-raw'),
    ('RAW', 'F.Cu', 1.0, [(46.5, 80), (38, 80), 'C302.1'], 'aux-raw'),
    ('RAW', 'F.Cu', 1.0, ['C301.1', (57, 91), (57, 95), (62, 98)], 'aux-raw'),             # U301.IN
    # --- mute optos ---
    ('OPTO_A', 'F.Cu', 0.35, ['R309.2', 'U303.A'], 'mute'),
    ('OPTO_M', 'F.Cu', 0.35, ['U303.K', 'U304.A'], 'mute'),
    ('RUN_L', 'F.Cu', 0.35, ['U303.C', 'J304.1'], 'mute'),
    ('VEE_L', 'F.Cu', 0.35, ['U303.E', (49.08, 8.84), 'J304.2'], 'mute'),
    ('RUN_R', 'F.Cu', 0.35, ['U304.C', 'J305.1'], 'mute'),
    ('VEE_R', 'F.Cu', 0.35, ['U304.E', (61.08, 8.84), 'J305.2'], 'mute'),
    # --- timer ---
    ('TMR', 'F.Cu', 0.35, ['R312.2', 'C308.1'], 'timer'),
    ('TMR', 'F.Cu', 0.35, ['D305.2', 'R312.2'], 'timer'),
    ('TMR', 'F.Cu', 0.35, ['R312.2', (38, 100), 'U305.REF'], 'timer'),
    ('TMR', 'F.Cu', 0.35, ['U305.REF', (38, 114.5), 'R315.1'], 'timer'),
    ('TLK', 'F.Cu', 0.35, ['U305.K', 'R313.1'], 'timer'),
    ('TLK', 'F.Cu', 0.35, ['R313.1', 'R314.1'], 'timer'),
    ('Q2B', 'F.Cu', 0.35, ['R314.2', 'Q302.B'], 'timer'),
    ('BYP_HI', 'F.Cu', 0.5, ['Q302.C', (58.5, 114.5), 'R315.2'], 'timer'),
    ('BYP_HI', 'F.Cu', 0.5, [(58.5, 114.5), (62.5, 114.5), (64.5, 112.5), 'J306.1'], 'timer'),
    # --- LEDs ---
    ('LED_G', 'F.Cu', 0.35, ['R310.2', 'J307.1'], 'led'),
    ('LED_R', 'F.Cu', 0.35, ['R311.2', 'J308.1'], 'led'),
], zones=[('GND', 'B.Cu', [(0, 0), (70, 0), (70, 120), (0, 120)])])

MAINS_V06 = dict(name='mains-layout-v06', size=(70, 100), source='mains-v01-netlist.xml', layout={
    # low-voltage side, x <= 24
    'J403': ('Terminal2_P5.08', 6, 10.5, 0),        # 1 TRIG_IN (6,10.5) 2 TRIG_N (11.08,10.5)
    'D402': ('D_DO-41_P10.16', 22.16, 17.5, 180),   # 1 K TRIG_P (22.16,17.5) 2 A TRIG_N (12,17.5)
    'K401': ('Relay_G2RL-1-E', 12, 30, 90),         # A1 TRIG_P (12,30) A2 TRIG_N (12,22.5) COM L_IN (32,30)(32,22.5) NO L_SW (37,30)(37,22.5)
    'D401': ('D_DO-41_P10.16', 13, 40, 180),        # 1 K TRIG_P (13,40) 2 A TRIG_IN (2.84,40)
    'D403': ('D_DO-41_P10.16', 22.16, 46, 180),     # 1 K BYP_HI (22.16,46) 2 A GND_CTRL (12,46)
    'K402': ('Relay_G2RL-1-E', 12, 60, 90),         # A1 BYP_HI (12,60) A2 GND_CTRL (12,52.5) COM L_SW (32,60)(32,52.5) NO L_T1 (37,60)(37,52.5)
    'J404': ('Terminal2_P5.08', 11.08, 70, 180),    # 1 BYP_HI (11.08,70) 2 GND_CTRL (6,70)
    # mains side, x >= 32
    'J401': ('Terminal2_P5.08', 65, 16, 270),       # 1 L_IN (65,16) 2 N_IN (65,21.08)
    'J402': ('Terminal2_P5.08', 65, 32, 270),       # 1 L_IN (65,32) 2 L_SW (65,37.08)
    'RT401': ('NTC_D22_P10', 40, 80, 90),           # 1 L_SW (40,80) 2 L_T1 (40,70)
    'J405': ('Terminal2_P5.08', 65, 86, 90),        # 1 L_T1 (65,86) 2 N_IN (65,80.92)
}, anchors={}, labels=[
    ('Z10 TRIG', 14, 4.5), ('FROM CTRL J306', 16, 76), ('AC IN (L,N)', 55, 9), ('SWITCH', 56, 42), ('TO T1 PRI', 54, 93),
    ('MAINS SIDE >= 6.4 mm', 44, 46), ('LIVE 110 VAC', 50, 60), ('NTC SL22 10005', 40, 93),
], routes=[
    # low voltage (0.5 mm)
    ('TRIG_IN', 'F.Cu', 0.5, ['J403.1', (4, 12.5), (4, 38), 'D401.2'], 'trigger'),
    ('TRIG_N', 'F.Cu', 0.5, ['J403.2', (12, 14), 'D402.2'], 'trigger'),
    ('TRIG_N', 'F.Cu', 0.5, ['D402.2', 'K401.A2'], 'trigger'),                         # (12,17) -> (12,22.5)
    ('TRIG_P', 'F.Cu', 0.5, ['D401.1', (13, 36), 'K401.A1'], 'trigger'),                # (13,40) -> (12,30)
    ('TRIG_P', 'F.Cu', 0.5, ['D402.1', (23.5, 18), (23.5, 36), (13, 36)], 'trigger'),
    ('GND_CTRL', 'F.Cu', 0.5, ['J404.2', (4, 68), (4, 46), 'D403.2'], 'bypass-coil'),  # (6,70) -> (12,46)
    ('GND_CTRL', 'F.Cu', 0.5, ['D403.2', 'K402.A2'], 'bypass-coil'),                    # (12,46) -> (12,52.5)
    ('BYP_HI', 'F.Cu', 0.5, ['J404.1', (13, 68), (13, 66), 'K402.A1'], 'bypass-coil'), # (11.08,70) -> (12,60)
    ('BYP_HI', 'F.Cu', 0.5, ['D403.1', (23.5, 48), (23.5, 66), (13, 66)], 'bypass-coil'),
    # mains (2.0 mm); the two pads of each relay contact are joined
    ('L_IN', 'F.Cu', 2.0, ['J401.1', (61, 18), (32, 18), (32, 22.5), (32, 30)], 'mains'),
    ('L_IN', 'F.Cu', 2.0, [(61, 18), (60, 19), (60, 30), 'J402.1'], 'mains'),
    ('L_SW', 'F.Cu', 2.0, ['J402.2', (62, 37), (42, 37), (37, 33), (37, 30), (37, 22.5)], 'mains'),
    ('L_SW', 'F.Cu', 2.0, [(42, 37), (42, 48), (32, 48), (32, 52.5), (32, 60), (32, 76), 'RT401.1'], 'mains'),
    ('L_T1', 'F.Cu', 2.0, [(37, 52.5), (37, 60), (37, 66), (40, 69), 'RT401.2'], 'mains'),
    ('L_T1', 'F.Cu', 2.0, ['RT401.2', (50, 70), (61, 70), (61, 83), 'J405.1'], 'mains'),
    ('N_IN', 'F.Cu', 1.5, ['J401.2', (68.5, 24), (68.5, 78), 'J405.2'], 'mains'),
], zones=[])
