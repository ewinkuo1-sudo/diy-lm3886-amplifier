"""Independent topology, polarity and harness audit for the secondary PSU."""
from pathlib import Path
import csv
import json
import xml.etree.ElementTree as ET

DEST = Path(__file__).resolve().parents[1] / 'electrical'


def verify():
    root = ET.parse(DEST/'psu-netlist.xml').getroot()
    nets = {n.get('name').lstrip('/'): {p.get('ref')+'.'+p.get('pin') for p in n} for n in root.findall('nets/net')}
    expected = {
        'VCC': {'BR1.P', 'C201.1', 'C202.1', 'R201.1', 'C205.1', 'J203.1'},
        'GND': {'BR1.N', 'BR2.P', 'C201.2', 'C202.2', 'R201.2', 'C205.2', 'C203.1', 'C204.1', 'R202.1', 'C206.1', 'J203.2'},
        'VEE': {'BR2.N', 'C203.2', 'C204.2', 'R202.2', 'C206.2', 'J203.3'},
    }
    for ch, j, f, br in [('POS', 'J201', 'F201', 'BR1'), ('NEG', 'J202', 'F202', 'BR2')]:
        expected[ch+'_AC1'] = {j+'.1', f+'.1'}
        expected[ch+'_AC_FUSED'] = {f+'.2', br+'.AC1'}
        expected[ch+'_AC2'] = {j+'.2', br+'.AC2'}
    if nets != expected:
        raise RuntimeError('PSU exported netlist does not match independent topology')
    erc = json.loads((DEST/'psu-erc.json').read_text())
    if any(s['violations'] for s in erc['sheets']):
        raise RuntimeError('PSU ERC violations')
    parts = root.findall('components/comp')
    if len(parts) != 15:
        raise RuntimeError('Expected 15 secondary PSU components')
    values = {p.get('ref'): p.findtext('value') for p in parts}
    for ref in ('C201', 'C202', 'C203', 'C204'):
        if values[ref] != '10000u / 63V':
            raise RuntimeError('Reservoir capacitance/rating mismatch')
    for ref in ('R201', 'R202'):
        if values[ref] != '2.2k / 2W BLEED':
            raise RuntimeError('Bleeder mismatch')
    amp = ET.parse(DEST/'netlist.xml').getroot()
    amp_nets = {n.get('name').lstrip('/'): {p.get('ref')+'.'+p.get('pin') for p in n} for n in amp.findall('nets/net')}
    for pin, net in [(1, 'VCC'), (2, 'GND'), (3, 'VEE')]:
        if f'J5.{pin}' not in amp_nets[net] or f'J203.{pin}' not in nets[net]:
            raise RuntimeError('PSU-to-amplifier harness mismatch')
    with (DEST/'psu-bom-draft.csv').open('w', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(['reference', 'quantity', 'value', 'symbol', 'footprint', 'note'])
        for p in parts:
            kind = p.find('libsource').get('part')
            note = {'Bridge': 'Logical pin IDs; map to selected MPN before PCB; cooling/IFSM TBD',
                    'Fuse': 'Rating and breaking capacity TBD; this is not a selected fuse',
                    'CP': 'Pin1 positive; ripple rating and dimensions TBD'}.get(kind, 'Component selection/footprint TBD')
            writer.writerow([p.get('ref'), 1, p.findtext('value'), kind, p.findtext('footprint', ''), note])
    with (DEST/'validation.md').open('a') as f:
        f.write(f'\n## 內建電源次級圖\n\nERC 0 錯誤、0 警告；{len(parts)} 個元件、{len(nets)} 個網路、{sum(map(len,nets.values()))} 個腳位通過獨立核對。兩個次級 AC 回路、橋式整流輸出串接、濾波／洩放極性及 J203→放大板 J5 的三線接序已核對。\n\n這是兩個獨立 KiCad 專案，以線束相連；ERC 不會自動檢查跨檔接線。Bridge 的 AC1／AC2／P／N 為功能端子，未選實體料號或 footprint。沒有完成一次側接線、軟啟動、保護控制器、PCB、耐壓／接地測試或實機量測。\n')
    print(f'PASS: PSU {len(parts)} parts, {len(nets)} nets; polarity and inter-board harness checked')


if __name__ == '__main__':
    verify()
