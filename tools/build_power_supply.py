"""Draw the isolated-secondary portion of the internal supply, not mains wiring."""
from build_schematic import Drawing, define, passive


def build():
    define('Fuse', passive,
           '(rectangle(start -2.54 1.016)(end 2.54 -1.016)(stroke(width 0.254)(type default))(fill(type none)))', 'F')
    define('Bridge', [('AC1', '~1', 'passive', -12.7, 5.08, 0),
                      ('AC2', '~2', 'passive', -12.7, -5.08, 0),
                      ('P', '+', 'passive', 12.7, 5.08, 180),
                      ('N', '-', 'passive', 12.7, -5.08, 180)],
           '(rectangle(start -10.16 10.16)(end 10.16 -10.16)(stroke(width 0.254)(type default))(fill(type background)))', 'BR')
    d = Drawing('internal-psu-v02', 'LM3886 internal PSU - isolated secondaries only')
    d.text(15, 16, 'INTERNAL LINEAR PSU / V0.3 / PLAN C / SECONDARY-SIDE DRAFT', 2.6)
    d.text(15, 25, 'T1 ordered: 110 VAC primary; 2 x 22 VAC independent + 12 VAC auxiliary. Seller: 200 W; VA / currents TBD.', 1.5)
    d.text(15, 33, 'Two bridges; connect BR1 negative to BR2 positive at the reservoir star point. Do not pre-join the AC windings.', 1.5)
    for i, (ch, y, positive, negative) in enumerate([('POS', 76.2, 'VCC', 'GND'), ('NEG', 177.8, 'GND', 'VEE')]):
        j, fuse, br = 'J'+str(201+i), 'F'+str(201+i), 'BR'+str(i+1)
        d.text(15, y-22, ch + ' RAIL / floating 22 VAC secondary', 1.8)
        d.part('Conn2', j, 'T1 SEC '+str(i+1), 40.64, y-5.08)
        d.terminal(j, 1, ch+'_AC1', dx=-10.16)
        d.terminal(j, 2, ch+'_AC2', dx=-10.16)
        d.part('Fuse', fuse, 'TBD per transformer', 96.52, y-5.08)
        d.terminal(fuse, 1, ch+'_AC1', dx=-5.08)
        d.part('Bridge', br, '>=15A / >=200V TBD', 157.48, y)
        d.wire(d.pin(fuse, 2), d.pin(br, 'AC1'))
        d.label(111.76, y-5.08, ch+'_AC_FUSED')
        d.terminal(br, 'AC2', ch+'_AC2', dx=-17.78)
        d.terminal(br, 'P', positive, dx=10.16)
        d.terminal(br, 'N', negative, dx=10.16)
        for n, x in enumerate((233.68, 312.42)):
            d.pair('CP', 'C'+str(201+i*2+n), '10000u / 63V', x, y, positive, negative)
        d.pair('R', 'R'+str(201+i), '2.2k / 2W BLEED', 233.68, y+30.48, positive, negative)
        d.pair('C', 'C'+str(205+i), '100n / 100V film', 312.42, y+30.48, positive, negative)
    d.part('Conn3', 'J203', 'TO AMP J5', 381, 129.54)
    for n, net in ((1, 'VCC'), (2, 'GND'), (3, 'VEE')):
        d.terminal('J203', n, net, dx=-10.16)
    d.text(15, 238, 'C201/C202: positive lead to VCC. C203/C204: positive lead to GND.', 1.6)
    d.text(15, 247, 'C plan: 20,000 uF per rail. C201-C204 CDE 381LX delivered 2026-09-23 (D35 x 50, snap-in); both bridges NOT purchased.', 1.5)
    d.text(15, 256, 'Fuse ratings / bridge cooling / inrush / PE chassis bond / speaker protection: design and verify before assembly.', 1.4)
    d.text(15, 265, '12 VAC auxiliary: reserved for control / speaker protection; AC vs DC module input and current rating TBD.', 1.4)
    d.text(15, 274, 'Separate schematic projects: J203 pin 1/2/3 wires to amplifier J5 pin 1/2/3. Same-label text does not wire the two files.', 1.35)
    d.save()
    print(f'Generated internal PSU secondary draft: {len(d.parts)} components')


if __name__ == '__main__':
    build()
