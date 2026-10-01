"""Draw the V0.6 control / protection board (CTRL) and the separate mains soft-start board (MAINS).

Two schematic projects, like the amplifier / PSU split: electrical/control-v01.kicad_sch and
electrical/mains-v01.kicad_sch. Requirements and timing come from docs/13 and docs/14; this file is the
first circuit, not a verified design. Decisions taken 2026-10-01 with the user: self-built board around a
UPC1237 protector IC (UTC datasheet QW-R107-065.B), Omron G2R-1-E 12 VDC relays for the speakers and the
soft-start bypass, G5LE-1 12 VDC for the 12 V trigger, Ametherm SL22 10005 NTC (10 ohm / 5 A / 90 J)
in the mains, two boards (low-voltage CTRL near the RCA side, MAINS on the other side of the chassis).

Deviations from docs/14 section 3, both deliberate:
 * un-mute is tied to the speaker relay instead of a separate 1-2 s timer: the two mute opto-couplers
   are fed from the relay-drive node, so RUN = relay ON; the 2.2 s R8/C8 ramp on the amplifier board
   still makes the un-mute soft. One timer less, same safety (mute drops the moment the relay drops);
 * UPC1237 VCC is the regulated +12 V, not the 25-60 V of the datasheet. Pin 8 is an internal 3.4 V
   reference fed through a resistor (15 k from 45 V in the datasheet = 2.8 mA), so R301 = 3.3 k from 12 V
   gives the same current; the relay driver (pin 6, 80 mA max) drives a PNP because two G2R-1-E coils
   draw 2 x 44 mA. To be confirmed on the bench (docs/14 section 9 style check).
"""
from build_schematic import Drawing, define, passive, line

TRI = '(polyline(pts(xy 2.54 2.54)(xy -2.54 0)(xy 2.54 -2.54)(xy 2.54 2.54))(stroke(width 0.254)(type default))(fill(type none)))'


def symbols():
    define('Bridge', [('AC1', '~1', 'passive', -12.7, 5.08, 0), ('AC2', '~2', 'passive', -12.7, -5.08, 0),
                      ('P', '+', 'passive', 12.7, 5.08, 180), ('N', '-', 'passive', 12.7, -5.08, 180)],
           '(rectangle(start -10.16 10.16)(end 10.16 -10.16)(stroke(width 0.254)(type default))(fill(type background)))', 'BR')
    # diode: pin 1 = cathode (left), pin 2 = anode (right); current flows right -> left as drawn
    define('D', [('1', 'K', 'passive', -5.08, 0, 0), ('2', 'A', 'passive', 5.08, 0, 180)], TRI + line(-2.54, 2.54, -2.54, -2.54), 'D')
    define('NTC', passive, '(rectangle(start -2.54 1.016)(end 2.54 -1.016)(stroke(width 0.254)(type default))(fill(type none)))' + line(-3.5, -2.5, 3.5, 2.5), 'RT')
    define('UPC1237', [('1', 'OVL', 'passive', -17.78, 7.62, 0), ('2', 'DC', 'passive', -17.78, 2.54, 0),
                       ('3', 'LATCH', 'passive', -17.78, -2.54, 0), ('4', 'ACOFF', 'passive', -17.78, -7.62, 0),
                       ('8', 'VREF', 'passive', 17.78, 7.62, 180), ('7', 'DELAY', 'passive', 17.78, 2.54, 180),
                       ('6', 'RLY', 'passive', 17.78, -2.54, 180), ('5', 'GND', 'passive', 0, -15.24, 90)],
           '(rectangle(start -15.24 12.7)(end 15.24 -12.7)(stroke(width 0.254)(type default))(fill(type background)))', 'U')
    define('Relay', [('A1', 'A1', 'passive', -10.16, 5.08, 0), ('A2', 'A2', 'passive', -10.16, -5.08, 0),
                     ('COM', 'COM', 'passive', 10.16, 5.08, 180), ('NO', 'NO', 'passive', 10.16, -5.08, 180)],
           '(rectangle(start -7.62 10.16)(end 7.62 -10.16)(stroke(width 0.254)(type default))(fill(type background)))'
           + line(-7.62, 5.08, -5.08, 5.08) + line(-5.08, 7.62, -5.08, 2.54) + line(-5.08, 2.54, -2.54, 2.54) + line(-2.54, 7.62, -2.54, 2.54)
           + line(-2.54, 5.08, 2.54, 5.08) + line(2.54, 5.08, 2.54, -2.54) + line(2.54, 5.08, 7.62, 5.08) + line(2.54, -2.54, 6.5, -6.0), 'K')
    # NPN: collector on top, emitter below. PNP: emitter on top (toward +12V), collector below.
    body = line(-5.08, 0, -1.27, 0) + line(-1.27, 3.81, -1.27, -3.81) + line(-1.27, 1.5, 2.54, 5.08) + line(-1.27, -1.5, 2.54, -5.08)
    define('NPN', [('B', 'B', 'passive', -7.62, 0, 0), ('C', 'C', 'passive', 2.54, 7.62, 270), ('E', 'E', 'passive', 2.54, -7.62, 90)], body + line(0.6, -2.0, 2.54, -5.08), 'Q')
    define('PNP', [('B', 'B', 'passive', -7.62, 0, 0), ('E', 'E', 'passive', 2.54, 7.62, 270), ('C', 'C', 'passive', 2.54, -7.62, 90)], body + line(2.54, 5.08, 0.6, 2.0), 'Q')
    define('Opto', [('A', 'A', 'passive', -10.16, 5.08, 0), ('K', 'K', 'passive', -10.16, -5.08, 0),
                    ('C', 'C', 'passive', 10.16, 5.08, 180), ('E', 'E', 'passive', 10.16, -5.08, 180)],
           '(rectangle(start -7.62 7.62)(end 7.62 -7.62)(stroke(width 0.254)(type default))(fill(type background)))' + line(-2.54, 0, 2.54, 0) + line(1.27, 1.27, 2.54, 0) + line(1.27, -1.27, 2.54, 0), 'U')
    define('TL431', [('REF', 'REF', 'passive', -7.62, 0, 0), ('K', 'K', 'passive', 2.54, 7.62, 270), ('A', 'A', 'passive', 2.54, -7.62, 90)],
           '(polyline(pts(xy -2.54 -3.81)(xy 2.54 0)(xy -2.54 3.81)(xy -2.54 -3.81))(stroke(width 0.254)(type default))(fill(type none)))' + line(2.54, 3.81, 2.54, -3.81) + line(-5.08, 0, -2.54, 0), 'U')
    define('Reg78', [('IN', 'IN', 'passive', -10.16, 2.54, 0), ('OUT', 'OUT', 'passive', 10.16, 2.54, 180), ('GND', 'GND', 'passive', 0, -7.62, 90)],
           '(rectangle(start -7.62 5.08)(end 7.62 -5.08)(stroke(width 0.254)(type default))(fill(type background)))', 'U')


def build_ctrl():
    d = Drawing('control-v01', 'LM3886 V0.6 control / protection board (CTRL) - low voltage only')
    d.date, d.rev, d.comment = '2026-10-01', '0.6 FIRST DRAFT', 'V0.6 control board / circuit draft only / no hardware measurements'
    d.text(15, 14, 'CTRL BOARD V0.6 / FIRST CIRCUIT DRAFT 2026-10-01 / UPC1237 protector + 12 V aux + soft-start timer / NO HARDWARE MEASUREMENT', 2.4)
    d.text(15, 21, 'Supply: T1 12 VAC winding (12.27 V no-load measured 2026-10-01, 1 A label) -> bridge -> 2200u -> 7812 -> +12V for relays, logic and UPC1237.', 1.5)
    d.text(15, 27, 'GND of this board ties to the PSU GND star at ONE point (J309). Relay coil current never flows through the amplifier signal ground (docs/13).', 1.5)
    # --- A. auxiliary supply -----------------------------------------------------------------------------
    y = 50.8
    d.text(15, y - 12, 'A. 12 V AUXILIARY SUPPLY', 1.8)
    d.part('Conn2', 'J301', 'T1 12VAC', 30.48, y - 2.54)
    d.terminal('J301', 1, 'AC_A', dx=-10.16)
    d.terminal('J301', 2, 'AC_B', dx=-10.16)
    d.part('Bridge', 'BR301', 'DF06M 1A/600V', 66.04, y)
    d.terminal('BR301', 'AC1', 'AC_A', dx=-7.62)
    d.terminal('BR301', 'AC2', 'AC_B', dx=-7.62)
    d.terminal('BR301', 'P', 'RAW', dx=7.62)
    d.terminal('BR301', 'N', 'GND', dx=7.62)
    d.pair('CP', 'C301', '2200u / 25V', 106.68, y, 'RAW', 'GND')
    d.pair('C', 'C302', '100n', 106.68, y + 15.24, 'RAW', 'GND')
    d.part('Reg78', 'U301', '7812 (TO-220, to chassis)', 142.24, y)
    d.terminal('U301', 'IN', 'RAW', dx=-7.62)
    d.terminal('U301', 'OUT', '+12V', dx=7.62)
    d.terminal('U301', 'GND', 'GND', dy=5.08)
    d.pair('CP', 'C303', '10u / 25V', 182.88, y, '+12V', 'GND')
    d.pair('C', 'C304', '100n', 182.88, y + 15.24, '+12V', 'GND')
    d.text(15, y + 28, 'RAW ~15-17 VDC at 150 mA (2 x 44 mA coils + bypass coil 44 mA + logic). 7812 dissipates ~1 W: bolt to chassis. Ripple 2200u @150 mA ~0.6 Vpp (docs/14 6.5).', 1.3)
    # --- B. UPC1237 protector --------------------------------------------------------------------------------
    y = 127
    d.text(15, y - 40, 'B. UPC1237 PROTECTOR (UTC QW-R107-065.B)', 1.8)
    d.text(15, y - 35, 'Thresholds: pin 2 +0.62 V / -0.17 V (DC), pin 4 0.74 V (AC-off), pin 8 = 3.4 V reference, pin 6 sinks <= 80 mA.', 1.3)
    d.part('UPC1237', 'U302', 'UPC1237 SIP-8', 101.6, y)
    # pin 8 reference fed from +12V (datasheet: 15k from 45V = 2.8 mA; 3.3k from 12 V = 2.6 mA)
    d.part('R', 'R301', '3.3k', 139.7, y - 7.62)
    d.wire(d.pin('U302', 8), d.pin('R301', 1))
    d.label(*d.pin('U302', 8), 'VREF')
    d.terminal('R301', 2, '+12V', dx=5.08)
    # delay: 56k from VREF to pin 7, 47u to GND -> relay ON ~3-4 s after VREF appears (datasheet 56k/33u ~2-3 s); trim on the bench
    d.part('R', 'R302', '56k', 165.1, y - 2.54)
    d.wire(d.pin('U302', 7), d.pin('R302', 1))
    d.terminal('R302', 2, 'VREF', dx=5.08)
    d.part('CP', 'C305', '47u / 16V DELAY', 165.1, y + 10.16)
    d.terminal('C305', 1, 'DELAY', dx=-5.08)
    d.label(*d.pin('U302', 7), 'DELAY')
    d.terminal('C305', 2, 'GND', dx=5.08)
    # relay driver: pin 6 sinks the PNP base current; R303 limits it to ~10 mA
    d.part('R', 'R303', '1k', 139.7, y + 2.54)
    d.wire(d.pin('U302', 6), d.pin('R303', 1))
    d.terminal('R303', 2, 'Q1B', dx=5.08)
    d.terminal('U302', 5, 'GND', dy=5.08)
    d.terminal('U302', 1, 'GND', dx=-5.08)     # overload detector unused -> grounded (test-circuit SW1 position 2)
    d.terminal('U302', 3, 'GND', dx=-5.08)     # pin 3 to GND = automatic reset; 22n to GND instead = latch
    d.text(15, y + 27, 'Pin 1 (overload) and pin 3 grounded: overload detector unused, automatic reset. For LATCH put 22n from pin 3 to GND instead.', 1.3)
    # DC detector: both outputs through 56k into one node, 100u to GND
    d.part('R', 'R304', '56k', 55.88, y - 2.54)
    d.terminal('R304', 1, 'AMP_L_OUT', dx=-5.08)
    d.wire(d.pin('R304', 2), d.pin('U302', 2))
    d.part('R', 'R305', '56k', 55.88, y + 7.62)
    d.terminal('R305', 1, 'AMP_R_OUT', dx=-5.08)
    d.terminal('R305', 2, 'DCDET', dx=5.08)
    d.label(*d.pin('U302', 2), 'DCDET')
    d.part('CP', 'C306', '100u / 16V (datasheet 330u)', 55.88, y + 17.78)
    d.terminal('C306', 1, 'DCDET', dx=-5.08)
    d.terminal('C306', 2, 'GND', dx=5.08)
    d.text(15, y + 32, 'DC trip (one channel, other at 0 V): +1.24 V / -0.34 V at the speaker output. 56k||56k x 100u = 2.8 s: 30 V fault trips in ~120 ms; 25 Vpk at 10 Hz leaves 0.07 V at pin 2 (<0.17 V).', 1.3)
    # AC-off detector: half-wave from the winding through 56k, 10k || 4.7u to GND; falls below 0.74 V ~60 ms after mains loss
    d.part('D', 'D301', '1N4148', 55.88, y - 22.86)
    d.terminal('D301', 2, 'AC_A', dx=5.08)
    d.part('R', 'R306', '56k', 40.64, y - 22.86)
    d.wire(d.pin('D301', 1), d.pin('R306', 2))
    d.terminal('R306', 1, 'ACDET', dx=-5.08)
    d.part('R', 'R307', '10k', 40.64, y - 12.7)
    d.terminal('R307', 1, 'ACDET', dx=-5.08)
    d.terminal('R307', 2, 'GND', dx=5.08)
    d.part('CP', 'C307', '4.7u / 25V', 71.12, y - 12.7)
    d.terminal('C307', 1, 'ACDET', dx=-5.08)
    d.terminal('C307', 2, 'GND', dx=5.08)
    d.terminal('U302', 4, 'ACDET', dx=-5.08)
    d.text(15, y + 37, 'AC-off: 17 Vpk x 10k/66k = 2.6 V at pin 4 while mains is on (droop between peaks to 1.8 V); after loss 10k x 4.7u decays below 0.74 V in ~60 ms (docs/14 6.4 budget <60 ms).', 1.3)
    # --- C. speaker relays, mute opto-couplers, status LEDs -------------------------------------------------
    y = 127
    x = 231.14
    d.text(x - 20, y - 40, 'C. SPEAKER RELAYS (G2R-1-E 12VDC, 16 A, 2 x 44 mA), MUTE OPTOS, STATUS LEDS', 1.8)
    d.part('PNP', 'Q301', 'BC327-40 (PNP, 800 mA)', x, y - 15.24)
    d.terminal('Q301', 'B', 'Q1B', dx=-5.08)
    d.terminal('Q301', 'E', '+12V', dy=-5.08)
    d.terminal('Q301', 'C', 'RLY', dy=5.08)
    d.part('R', 'R308', '10k', x - 2.54, y - 30.48)
    d.terminal('R308', 1, 'Q1B', dx=-5.08)
    d.terminal('R308', 2, '+12V', dx=5.08)
    for i, (k, dio, ch) in enumerate((('K301', 'D302', 'L'), ('K302', 'D303', 'R'))):
        yy = y + 12.7 + i * 35.56
        d.part('Relay', k, 'G2R-1-E 12VDC', x + 40.64, yy)
        d.terminal(k, 'A1', 'RLY', dx=-7.62)
        d.terminal(k, 'A2', 'GND', dx=-7.62)
        d.terminal(k, 'COM', 'AMP_%s_OUT' % ch, dx=7.62)
        d.terminal(k, 'NO', 'SPK_%s' % ch, dx=7.62)
        d.part('D', dio, '1N4007 flyback', x + 10.16, yy)
        d.terminal(dio, 1, 'RLY', dx=-5.08)
        d.terminal(dio, 2, 'GND', dx=5.08)
        j = 'J302' if ch == 'L' else 'J303'
        d.part('Conn2', j, 'AMP %s OUT -> SPK %s+' % (ch, ch), x + 83.82, yy - 2.54)
        d.terminal(j, 1, 'AMP_%s_OUT' % ch, dx=-10.16)
        d.terminal(j, 2, 'SPK_%s' % ch, dx=-10.16)
    d.text(x - 20, y + 73, 'Speaker return wire goes straight from the binding post to the amplifier J2.2 / J4.2, never through this board (docs/14 4).', 1.3)
    d.text(x - 20, y + 78, 'Relay DC breaking: G2R-1-E is rated 30 VDC; a 33.5 V / 8 ohm fault (4.5 A) is a one-shot protective break, accepted 2026-10-01 (docs/14 6.3 asks >=36 VDC).', 1.3)
    # mute opto-couplers: LEDs in series from RLY (RUN = relay ON); transistors switch RUN -> VEE on each amplifier board
    yy = y + 99.06
    d.part('R', 'R309', '1k', x, yy)
    d.terminal('R309', 1, 'RLY', dx=-5.08)
    d.terminal('R309', 2, 'OPTO_A', dx=5.08)
    for i, ch in enumerate(('L', 'R')):
        u = 'U303' if ch == 'L' else 'U304'
        ox = x + 35.56 + i * 76.2
        d.part('Opto', u, 'H11D1 (Vceo 300 V)', ox, yy)
        d.terminal(u, 'A', 'OPTO_A' if ch == 'L' else 'OPTO_M', dx=-5.08)
        d.terminal(u, 'K', 'OPTO_M' if ch == 'L' else 'GND', dx=-5.08)
        d.terminal(u, 'C', 'RUN_%s' % ch, dx=5.08)
        d.terminal(u, 'E', 'VEE_%s' % ch, dx=5.08)
        j = 'J304' if ch == 'L' else 'J305'
        d.part('Conn2', j, 'AMP %s JP1 (RUN, VEE)' % ch, ox + 35.56, yy - 2.54)
        d.terminal(j, 1, 'RUN_%s' % ch, dx=-7.62)
        d.terminal(j, 2, 'VEE_%s' % ch, dx=-7.62)
    d.text(x - 20, yy + 14, 'Opto collector -> amplifier RUN (R8 end), emitter -> that board VEE: closes the JP1 position, 1.3 mA. Two independent paths; the L and R mute nodes stay isolated (docs/13).', 1.3)
    d.text(x - 20, yy + 19, 'Opto must stand |VEE| = 36 V when off: H11D1 (300 V) or SFH617A (70 V); NOT PC817 (35 V). LED chain 2 x 1.2 V at ~8 mA from RLY through R309.', 1.3)
    # status LEDs on the front panel: green = relay ON (from RLY), red = +12V present but relay OFF (returns into RLY node)
    # front-panel LEDs live in the lower-left block, under the timer (sheet space)
    yy = 262
    d.text(15, yy - 12, 'E. FRONT PANEL LEDS: green = speakers ON (from RLY), red = +12V present but relay OFF (returns into RLY)', 1.8)
    d.part('R', 'R310', '1k GREEN', 40.64, yy)
    d.terminal('R310', 1, 'RLY', dx=-5.08)
    d.terminal('R310', 2, 'LED_G', dx=5.08)
    d.part('Conn2', 'J307', 'FRONT LED GREEN (A, K)', 76.2, yy - 2.54)
    d.terminal('J307', 1, 'LED_G', dx=-7.62)
    d.terminal('J307', 2, 'GND', dx=-7.62)
    d.part('R', 'R311', '1.5k RED', 114.3, yy)
    d.terminal('R311', 1, '+12V', dx=-5.08)
    d.terminal('R311', 2, 'LED_R', dx=5.08)
    d.part('Conn2', 'J308', 'FRONT LED RED (A, K->RLY)', 149.86, yy - 2.54)
    d.terminal('J308', 1, 'LED_R', dx=-7.62)
    d.terminal('J308', 2, 'RLY', dx=-7.62)
    d.text(15, yy + 9, 'Red LED returns into RLY: lit while RLY sits low (~6 mA through the coils, far below pull-in), dark once Q301 pulls RLY high.', 1.3)
    # --- D. soft-start bypass timer -------------------------------------------------------------------------
    y = 208.28
    d.text(15, y - 27.94, 'D. SOFT-START BYPASS TIMER: K_BYP (on MAINS board) pulls in ~1.1 s after +12V (docs/14 6.2 recommends 1 s)', 1.8)
    d.part('R', 'R312', '220k', 40.64, y)
    d.terminal('R312', 1, '+12V', dx=-5.08)
    d.terminal('R312', 2, 'TMR', dx=5.08)
    d.part('D', 'D305', '1N4148 (fast reset)', 40.64, y - 10.16)
    d.terminal('D305', 1, '+12V', dx=-5.08)
    d.terminal('D305', 2, 'TMR', dx=5.08)
    d.part('CP', 'C308', '22u / 25V', 40.64, y + 10.16)
    d.terminal('C308', 1, 'TMR', dx=-5.08)
    d.terminal('C308', 2, 'GND', dx=5.08)
    d.part('TL431', 'U305', 'TL431 (2.5 V comparator)', 76.2, y)
    d.terminal('U305', 'REF', 'TMR', dx=-5.08)
    d.terminal('U305', 'A', 'GND', dy=5.08)
    d.terminal('U305', 'K', 'TLK', dy=-5.08)
    d.part('R', 'R313', '2.2k', 101.6, y - 12.7)
    d.terminal('R313', 1, 'TLK', dx=-5.08)
    d.terminal('R313', 2, '+12V', dx=5.08)
    d.part('R', 'R314', '1k', 101.6, y)
    d.terminal('R314', 1, 'TLK', dx=-5.08)
    d.terminal('R314', 2, 'Q2B', dx=5.08)
    d.part('PNP', 'Q302', 'BC327-40', 134.62, y)
    d.terminal('Q302', 'B', 'Q2B', dx=-5.08)
    d.terminal('Q302', 'E', '+12V', dy=-5.08)
    d.terminal('Q302', 'C', 'BYP_HI', dy=5.08)
    d.part('R', 'R315', '1M hysteresis', 101.6, y + 12.7)
    d.terminal('R315', 1, 'TMR', dx=-5.08)
    d.terminal('R315', 2, 'BYP_HI', dx=5.08)
    d.part('Conn2', 'J306', 'TO MAINS K_BYP COIL (BYP_HI, GND)', 170.18, y - 2.54)
    d.terminal('J306', 1, 'BYP_HI', dx=-10.16)
    d.terminal('J306', 2, 'GND', dx=-10.16)
    d.part('Conn2', 'J309', 'GND TO PSU STAR (one point)', 170.18, y + 17.78)
    d.terminal('J309', 1, 'GND', dx=-10.16)
    d.terminal('J309', 2, 'GND', dx=-10.16)
    d.text(15, y + 28, 't = 220k x 22u x ln(12/9.5) = 1.1 s. TL431 snaps at 2.5 V (sharp, no relay chatter); R315 adds ~0.3 V hysteresis; D305 empties C308 within ms at power-off so a quick off-on restarts the NTC limit.', 1.3)
    d.text(15, y + 33, 'Flyback diode for K_BYP sits on the MAINS board next to the coil (D403). K_TRIG is on the MAINS board, powered by the Z10 trigger, not by this board.', 1.3)
    d.text(15, 280, 'NOT DRAWN YET: single-rail-loss detector (docs/13 P5, optional), over-temperature (P6, optional). Component values are first-pass; every timing and threshold is to be measured per docs/14 9 before the board goes into the chassis.', 1.4)
    d.save()
    print(f'Generated CTRL draft: {len(d.parts)} components')


def build_mains():
    d = Drawing('mains-v01', 'LM3886 V0.6 mains soft-start / trigger board (MAINS) - LIVE MAINS')
    d.date, d.rev, d.comment = '2026-10-01', '0.6 FIRST DRAFT', 'V0.6 mains board / circuit draft only / LIVE MAINS / no hardware measurements'
    d.text(15, 14, 'MAINS BOARD V0.6 / FIRST CIRCUIT DRAFT 2026-10-01 / LIVE 110 VAC: creepage >= 6.4 mm between mains and the 12 V coil side, PE to chassis stud (not on this board)', 2.2)
    d.text(15, 21, 'Path (docs/14 2): IEC inlet + fuse holder (chassis) -> J401 -> [manual switch J402 || K_TRIG contact] -> NTC RT401 (K_BYP contact across it) -> J405 -> T1 primary.', 1.5)
    y = 63.5
    d.part('Conn2', 'J401', 'FROM IEC + FUSE (L, N)', 30.48, y - 2.54)
    d.terminal('J401', 1, 'L_IN', dx=-10.16)
    d.terminal('J401', 2, 'N_IN', dx=-10.16)
    d.part('Conn2', 'J402', 'FRONT POWER SWITCH', 30.48, y + 27.94)
    d.terminal('J402', 1, 'L_IN', dx=-10.16)
    d.terminal('J402', 2, 'L_SW', dx=-10.16)
    d.part('Relay', 'K401', 'K_TRIG G5LE-1 12VDC (10 A)', 91.44, y + 22.86)
    d.terminal('K401', 'COM', 'L_IN', dx=7.62)
    d.terminal('K401', 'NO', 'L_SW', dx=7.62)
    d.terminal('K401', 'A1', 'TRIG_P', dx=-7.62)
    d.terminal('K401', 'A2', 'TRIG_N', dx=-7.62)
    d.part('D', 'D401', '1N4007 series (reverse-polarity)', 55.88, y + 50.8)
    d.terminal('D401', 2, 'TRIG_IN', dx=5.08)
    d.terminal('D401', 1, 'TRIG_P', dx=-5.08)
    d.part('D', 'D402', '1N4007 flyback', 55.88, y + 63.5)
    d.terminal('D402', 1, 'TRIG_P', dx=-5.08)
    d.terminal('D402', 2, 'TRIG_N', dx=5.08)
    d.part('Conn2', 'J403', 'Z10 12V TRIGGER (tip +, sleeve -)', 30.48, y + 73.66)
    d.terminal('J403', 1, 'TRIG_IN', dx=-10.16)
    d.terminal('J403', 2, 'TRIG_N', dx=-10.16)
    d.text(15, y + 92, 'K_TRIG coil 33 mA at 12 V from the Z10 trigger output (<= 50 mA budget, Z10 spec unknown). Contact in parallel with the front switch (OR). If the Z10 cannot source 33 mA: latch via the 12 V aux (docs/14 6.7).', 1.3)
    d.part('NTC', 'RT401', 'SL22 10005 (10R / 5A / 90J)', 165.1, y)
    d.terminal('RT401', 1, 'L_SW', dx=-5.08)
    d.terminal('RT401', 2, 'L_T1', dx=5.08)
    d.part('Relay', 'K402', 'K_BYP G2R-1-E 12VDC (16 A)', 165.1, y + 27.94)
    d.terminal('K402', 'COM', 'L_SW', dx=7.62)
    d.terminal('K402', 'NO', 'L_T1', dx=7.62)
    d.terminal('K402', 'A1', 'BYP_HI', dx=-7.62)
    d.terminal('K402', 'A2', 'GND_CTRL', dx=-7.62)
    d.part('D', 'D403', '1N4007 flyback', 129.54, y + 55.88)
    d.terminal('D403', 1, 'BYP_HI', dx=-5.08)
    d.terminal('D403', 2, 'GND_CTRL', dx=5.08)
    d.part('Conn2', 'J404', 'FROM CTRL J306 (BYP_HI, GND)', 104.14, y + 73.66)
    d.terminal('J404', 1, 'BYP_HI', dx=-10.16)
    d.terminal('J404', 2, 'GND_CTRL', dx=-10.16)
    d.part('Conn2', 'J405', 'TO T1 PRIMARY (L, N)', 226.06, y - 2.54)
    d.terminal('J405', 1, 'L_T1', dx=-10.16)
    d.terminal('J405', 2, 'N_IN', dx=-10.16)
    d.text(15, y + 100, 'NTC: primary 1.79 A rms steady (197 VA label), 10 ohm cold limits the first half-cycle to ~15 A; 90 J rating vs 38 J estimated absorption (docs/14 6.2). Bypassed after ~1.1 s by K402.', 1.3)
    d.text(15, y + 105, 'If K402 never pulls in, RT401 carries 1.79 A continuously: SL22 10005 is rated 5 A steady, so it survives (hot, ~1 ohm) - the failure is only lost inrush limiting on a quick off-on.', 1.3)
    d.text(15, y + 110, 'Mains-side parts: J401, J402, J405, RT401, K401/K402 contacts. Low-voltage: K401/K402 coils, D401-D403, J403, J404. Keep >= 6.4 mm creepage; slot under the relays.', 1.3)
    d.save()
    print(f'Generated MAINS draft: {len(d.parts)} components')


if __name__ == '__main__':
    symbols()
    build_ctrl()
    build_mains()
