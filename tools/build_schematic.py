"""Generate the editable amplifier schematic; standard-library Python only.

Embedded project symbols have LM3886 pin numbers checked against TI SNAS091C.
Footprints remain deliberately unset pending actual component selection.
"""
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'electrical'
PROJECT = 'lm3886-v01'
LIB, PINS = {}, {}


def uid(key):
    return str(uuid5(NAMESPACE_URL, 'diy-lm3886/v01/' + str(key)))


def q(value):
    return json.dumps(str(value), ensure_ascii=False)


def effects(size=1.27, extra=''):
    return f'(effects(font(size {size} {size})){extra})'


def prop(name, value, x, y, hide=False):
    return f'(property {q(name)} {q(value)}(at {x} {y} 0){effects(1.27, "hide" if hide else "")})'


def line(x1, y1, x2, y2):
    return f'(polyline(pts(xy {x1} {y1})(xy {x2} {y2}))(stroke(width 0.254)(type default))(fill(type none)))'


def define(name, pins, graphics, reference):
    PINS[name] = pins
    body = ''.join(f'(pin {kind} line(at {x} {y} {angle})(length 2.54){"hide" if kind == "no_connect" or (name == "LM3886" and n == "5") else ""}'
                   f'(name {q(label)}{effects(1)})(number {q(n)}{effects(1)}))'
                   for n, label, kind, x, y, angle in pins)
    LIB[name] = (f'(symbol {q(name)}(pin_names(offset 0.254))(in_bom yes)(on_board yes)'
                 + prop('Reference', reference, 0, 5) + prop('Value', name, 0, -5)
                 + f'(symbol {q(name + "_1_1")}{graphics}{body}))')


passive = [('1', '~', 'passive', -5.08, 0, 0), ('2', '~', 'passive', 5.08, 0, 180)]
define('R', passive, '(rectangle(start -2.54 1.016)(end 2.54 -1.016)(stroke(width 0.254)(type default))(fill(type none)))', 'R')
capacitor = line(-0.762, -2.032, -0.762, 2.032) + line(0.762, -2.032, 0.762, 2.032) + line(-2.54, 0, -0.762, 0) + line(0.762, 0, 2.54, 0)
define('C', passive, capacitor, 'C')
# Polarized capacitor: pin 1 is positive, with an explicit plus mark.
define('CP', passive, capacitor + line(-2.8, 3.1, -1.2, 3.1) + line(-2, 2.3, -2, 3.9), 'C')
define('L', passive, ''.join(f'(arc(start {x} 0)(mid {x + 0.635} 0.9)(end {x + 1.27} 0)(stroke(width 0.254)(type default))(fill(type none)))' for x in (-2.54, -1.27, 0, 1.27)), 'L')
for count in (2, 3):
    pins = [(str(i + 1), str(i + 1), 'passive', -5.08, -i * 5.08, 0) for i in range(count)]
    define(f'Conn{count}', pins, f'(rectangle(start -2.54 2.54)(end 2.54 {-count * 5.08 + 2.54})(stroke(width 0.254)(type default))(fill(type background)))', 'J')
define('Flag', [('1', '~', 'power_out', 0, 0, 90)], line(0, 0, 0, 2.54) + line(0, 2.54, 1.27, 1.27), '#FLG')
triangle = '(polyline(pts(xy -5.08 5.08)(xy 5.08 0)(xy -5.08 -5.08)(xy -5.08 5.08))(stroke(width 0.254)(type default))(fill(type background)))'
define('LM3886', [('10', '+', 'input', -7.62, 2.54, 0), ('9', '-', 'input', -7.62, -2.54, 0),
                  ('4', 'V-', 'power_in', -2.54, -7.62, 90), ('3', 'OUT', 'output', 7.62, 0, 180),
                  ('1', 'V+', 'power_in', -2.54, 7.62, 270), ('5', 'V+', 'passive', -2.54, 7.62, 270),
                  ('7', 'GND', 'power_in', 2.54, -10.16, 90), ('8', 'M', 'input', 2.54, 10.16, 270),
                  ('2', 'NC', 'no_connect', -2.54, 3.81, 270), ('6', 'NC', 'no_connect', -5.08, -5.08, 90),
                  ('11', 'NC', 'no_connect', -5.08, 5.08, 270)], triangle, 'U')


class Drawing:
    def __init__(self, project=PROJECT, title='LM3886 stereo AB power amplifier'):
        self.project, self.title = project, title
        self.items, self.parts, self.pins = [], [], {}
        self.seq = 0

    def item(self, text):
        self.seq += 1
        self.items.append(text[:-1] + f'(uuid {uid(self.seq)}))')

    def text(self, x, y, value, size=1.5):
        self.item(f'(text {q(value)}(at {x} {y} 0){effects(size, "(justify left)")})')

    def wire(self, *points):
        for a, b in zip(points, points[1:]):
            if a != b:
                self.item(f'(wire(pts(xy {a[0]} {a[1]})(xy {b[0]} {b[1]}))(stroke(width 0)(type default)))')

    def junction(self, x, y):
        self.item(f'(junction(at {x} {y})(diameter 0)(color 0 0 0 0))')

    def label(self, x, y, name):
        self.item(f'(label {q(name)}(at {x} {y} 0){effects(1.1, "(justify left bottom)")})')

    def part(self, kind, ref, value, x, y, vertical=False):
        flag = kind == 'Flag'
        properties = prop('Reference', ref, x + (8 if vertical else 0), y - (2 if vertical else 7), flag)
        properties += prop('Value', value, x + (13 if vertical else 0), y + (1 if vertical else -4.5), flag)
        if kind == 'LM3886':
            properties = prop('Reference', ref, x + 17.78, y - 15.24) + prop('Value', value, x + 17.78, y - 12.7)
        if kind == 'Bridge':
            properties = prop('Reference', ref, x, y - 17.78) + prop('Value', value, x, y - 15.24)
        properties += prop('Footprint', '', x, y, True)
        properties += prop('Datasheet', 'https://www.ti.com/lit/ds/symlink/lm3886.pdf' if kind == 'LM3886' else '', x, y, True)
        self.items.append(f'(symbol(lib_id {q("Project:" + kind)})(at {x} {y} {90 if vertical else 0})(unit 1)'
                          f'(in_bom {"no" if flag else "yes"})(on_board {"no" if flag else "yes"})(dnp no)(uuid {uid(ref)})'
                          + properties + f'(instances(project {q(self.project)}(path {q("/" + uid(self.project))}(reference {q(ref)})(unit 1)))))')
        for num, _, pin_type, px, py, _ in PINS[kind]:
            if vertical:
                px, py = -py, px
            self.pins[ref, num] = (round(x + px, 4), round(y - py, 4))
            # Hidden NC pins are intentionally unconnected; no drawn wire or flag.
        if not flag:
            self.parts.append((ref, kind, value))

    def pin(self, ref, n):
        return self.pins[ref, str(n)]

    def terminal(self, ref, n, net, dx=0, dy=0):
        p = self.pin(ref, n)
        end = (round(p[0] + dx, 4), round(p[1] + dy, 4))
        self.wire(p, end)
        self.label(*end, net)

    def pair(self, kind, ref, value, x, y, first, second):
        self.part(kind, ref, value, x, y)
        self.terminal(ref, 1, first, dx=-5.08)
        self.terminal(ref, 2, second, dx=5.08)

    def save(self):
        lib = ''.join(v.replace('(symbol ' + q(k), '(symbol ' + q('Project:' + k), 1) for k, v in LIB.items())
        header = f'(kicad_sch(version 20250114)(generator "diy_lm3886")(uuid {uid(self.project)})(paper "A3")'
        header += f'(title_block(title {q(self.title)})(date "2026-09-16")(rev "0.3 DRAFT")(comment 1 "Internal PSU system / no PCB / no hardware measurements"))'
        (DEST / (self.project + '.kicad_sch')).write_text(header + f'(lib_symbols {lib})' + ''.join(self.items) + '(sheet_instances(path "/"(page "1"))))\n')
        (DEST / 'Project.kicad_sym').write_text('(kicad_symbol_lib(version 20231120)(generator "diy_lm3886")' + ''.join(LIB.values()) + ')\n')
        (DEST / 'sym-lib-table').write_text('(sym_lib_table\n  (version 7)\n  (lib (name "Project")(type "KiCad")(uri "${KIPRJMOD}/Project.kicad_sym")(options "")(descr "Project symbols"))\n)\n')
        (DEST / (self.project + '.kicad_pro')).write_text('{}\n')


def build():
    d = Drawing()
    d.text(15, 16, 'LM3886 / STEREO POWER AMP / EXTERNAL PREAMP / V0.3 / PLAN C', 2.5)
    d.text(15, 25, 'Plan C: stereo / 8 ohms / 2 x 22 VAC supply. Output rating TBD by clipping and thermal tests.', 1.6)
    for index, ch in enumerate(('L', 'R')):
        base, y = index * 100, 71.12 + index * 101.6
        r = lambda n: 'R' + str(base + n)
        c = lambda n: 'C' + str(base + n)
        u, ji, jo = 'U' + str(index + 1), 'J' + str(index * 2 + 1), 'J' + str(index * 2 + 2)
        d.text(15, y - 30, ch + ' CHANNEL / gain = 1 + 20k/1k = 21 V/V', 1.8)
        d.part('Conn2', ji, ch + ' RCA', 35.56, y - 2.54)
        d.terminal(ji, 1, ch + '_IN', dx=-5.08)
        d.terminal(ji, 2, 'GND', dx=-5.08)
        d.part('LM3886', u, 'LM3886T', 154.94, y)
        d.part('C', c(1), '2.2u / 63V film', 88.9, y - 2.54)
        d.part('R', r(6), '1k', 109.22, y - 2.54)
        d.wire((66.04, y - 2.54), (76.2, y - 2.54), d.pin(c(1), 1))
        d.label(66.04, y - 2.54, ch + '_IN')
        d.wire(d.pin(c(1), 2), d.pin(r(6), 1))
        d.label(*d.pin(c(1), 2), ch + '_AC')
        d.wire(d.pin(r(6), 2), (121.92, y - 2.54), d.pin(u, 10))
        d.label(121.92, y - 2.54, ch + '_PLUS')
        for n, x, val in [(1, 76.2, '1M'), (2, 121.92, '22k')]:
            d.part('R', r(n), val, x, y + 15.24, True)
            d.wire(d.pin(r(n), 2), (x, y - 2.54))
            d.junction(x, y - 2.54)
            d.terminal(r(n), 1, 'GND', dy=5.08)
        d.terminal(u, 1, 'VCC', dy=-7.62)
        d.terminal(u, 4, 'VEE', dy=7.62)
        d.terminal(u, 7, 'GND', dy=7.62)
        d.terminal(u, 8, ch + '_MUTE', dy=-12.7)
        d.part('R', r(4), '20k / 1%', 160.02, y + 30.48)
        d.wire(d.pin(u, 9), (139.7, y + 2.54), (139.7, y + 30.48), d.pin(r(4), 1))
        d.label(139.7, y + 30.48, ch + '_INV')
        d.wire(d.pin(u, 3), (182.88, y), (190.5, y), (198.12, y))
        d.label(182.88, y, ch + '_OUT')
        d.wire(d.pin(r(4), 2), (182.88, y + 30.48), (182.88, y))
        d.junction(182.88, y)
        d.part('R', r(3), '1k / 1%', 139.7, y + 45.72, True)
        d.part('C', c(2), '47u / 63V BP', 139.7, y + 63.5, True)
        d.wire((139.7, y + 30.48), d.pin(r(3), 2))
        d.junction(139.7, y + 30.48)
        d.wire(d.pin(r(3), 1), d.pin(c(2), 2))
        d.label(*d.pin(c(2), 2), ch + '_FB_AC')
        d.terminal(c(2), 1, 'GND', dy=5.08)
        d.part('R', r(5), '2.7R / 2W', 190.5, y + 15.24, True)
        d.part('C', c(5), '100n / 100V film', 190.5, y + 35.56, True)
        d.wire((190.5, y), d.pin(r(5), 2))
        d.junction(190.5, y)
        d.wire(d.pin(r(5), 1), d.pin(c(5), 2))
        d.label(*d.pin(c(5), 2), ch + '_ZOBEL')
        d.terminal(c(5), 1, 'GND', dy=5.08)
        coil = 'L' + str(index + 1)
        d.part('L', coil, '0.7uH / air core', 213.36, y)
        d.part('R', r(7), '10R / 2W', 213.36, y - 20.32)
        d.wire((198.12, y), d.pin(coil, 1))
        d.wire((198.12, y), (198.12, y - 20.32), d.pin(r(7), 1))
        d.junction(198.12, y)
        d.wire(d.pin(coil, 2), (228.6, y), (241.3, y))
        d.wire(d.pin(r(7), 2), (228.6, y - 20.32), (228.6, y))
        d.junction(228.6, y)
        d.label(228.6, y, ch + '_SPK')
        d.part('Conn2', jo, ch + ' TEST OUT', 246.38, y)
        d.terminal(jo, 2, 'GND', dy=5.08)
        d.text(267, y - 17, ch + ' LOCAL DECOUPLING (at IC pins)', 1.7)
        d.pair('C', c(3), '100n / 63V', 287.02, y, 'VCC', 'GND')
        d.pair('C', c(4), '100n / 63V', 358.14, y, 'GND', 'VEE')
        d.pair('CP', c(7), '470u / 63V', 287.02, y + 25.4, 'VCC', 'GND')
        d.pair('CP', c(6), '470u / 63V', 358.14, y + 25.4, 'GND', 'VEE')
        d.text(267, y + 40, 'MUTE: jumper open = mute; fitted = run.', 1.4)
        d.pair('R', r(8), '22k / 0.25W', 287.02, y + 55.88, ch + '_MUTE', ch + '_RUN')
        d.pair('CP', c(8), '100u / 63V', 358.14, y + 55.88, 'GND', ch + '_MUTE')
        jp = 'JP' + str(index + 1)
        d.part('Conn2', jp, ch + ' RUN LINK', 358.14, y + 68.58)
        d.terminal(jp, 1, ch + '_RUN', dx=-7.62)
        d.terminal(jp, 2, 'VEE', dx=-7.62)
    d.text(15, 258, 'J5: internal PSU harness. Bench current-limited supply for first amplifier-only tests.', 1.5)
    d.text(15, 265, 'Tab = VEE: insulate from grounded chassis / heatsink.', 1.5)
    d.text(15, 272, 'GND is a net name; route input, feedback and load returns separately.', 1.5)
    d.part('Conn3', 'J5', 'INTERNAL PSU', 35.56, 215.9)
    for n, name in [(1, 'VCC'), (2, 'GND'), (3, 'VEE')]:
        d.terminal('J5', n, name, dx=-7.62)
        ref = '#FLG' + str(n)
        d.part('Flag', ref, 'PWR_FLAG', 50.8 + (n - 1) * 17.78, 241.3)
        d.terminal(ref, 1, name)
    d.text(15, 279, 'No mains, fuse or speaker relay circuit in this revision. Pin 5 shares VCC with pin 1; pins 2/6/11 are NC.', 1.4)
    DEST.mkdir(parents=True, exist_ok=True)
    d.save()
    print(f'Generated {len(d.parts)} components in {DEST}')


if __name__ == '__main__':
    build()
