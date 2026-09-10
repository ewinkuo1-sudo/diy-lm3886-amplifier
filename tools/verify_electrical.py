"""Audit KiCad's exported nets against an independent circuit specification."""
import csv
import json
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ELECTRICAL = ROOT / 'electrical'


def verify():
    root = ET.parse(ELECTRICAL / 'netlist.xml').getroot()
    actual = {n.get('name').lstrip('/'): {f'{p.get("ref")}.{p.get("pin")}' for p in n}
              for n in root.findall('nets/net')}
    expected = {'GND': {'J5.2'}, 'VCC': {'J5.1'}, 'VEE': {'J5.3'}}
    # Pin-level specification independently transcribed from the intended circuit.
    for ch, base, u, j_in, j_out, jp, coil in [
        ('L', 0, 'U1', 'J1', 'J2', 'JP1', 'L1'),
        ('R', 100, 'U2', 'J3', 'J4', 'JP2', 'L2')]:
        r = lambda n: f'R{base+n}'
        c = lambda n: f'C{base+n}'
        expected['VCC'].update([u+'.1', u+'.5', c(3)+'.1', c(7)+'.1'])
        expected['VEE'].update([u+'.4', c(4)+'.2', c(6)+'.2', jp+'.2'])
        expected['GND'].update([u+'.7', j_in+'.2', j_out+'.2', r(1)+'.1', r(2)+'.1',
                                c(2)+'.1', c(3)+'.2', c(4)+'.1', c(5)+'.1', c(6)+'.1', c(7)+'.2', c(8)+'.1'])
        for name, pins in {
            'IN': [j_in+'.1', r(1)+'.2', c(1)+'.1'],
            'AC': [c(1)+'.2', r(6)+'.1'],
            'PLUS': [r(6)+'.2', r(2)+'.2', u+'.10'],
            'INV': [u+'.9', r(4)+'.1', r(3)+'.2'],
            'FB_AC': [r(3)+'.1', c(2)+'.2'],
            'OUT': [u+'.3', r(4)+'.2', r(5)+'.2', coil+'.1', r(7)+'.1'],
            'ZOBEL': [r(5)+'.1', c(5)+'.2'],
            'SPK': [coil+'.2', r(7)+'.2', j_out+'.1'],
            'MUTE': [u+'.8', c(8)+'.2', r(8)+'.1'],
            'RUN': [r(8)+'.2', jp+'.1'],
        }.items():
            expected[ch+'_'+name] = set(pins)
        for pin in (2, 6, 11):
            expected[f'unconnected-({u}-NC-Pad{pin})'] = {f'{u}.{pin}'}
    if actual != expected:
        delta = {n: {'actual': sorted(actual.get(n, set())), 'expected': sorted(expected.get(n, set()))}
                 for n in actual.keys() | expected.keys() if actual.get(n) != expected.get(n)}
        raise RuntimeError('Net mismatch: ' + json.dumps(delta, indent=2))
    erc = json.loads((ELECTRICAL / 'erc.json').read_text())
    violations = [v for s in erc['sheets'] for v in s['violations']]
    if violations:
        raise RuntimeError(f'ERC has {len(violations)} violations')
    components = root.findall('components/comp')
    if len(components) != 43:
        raise RuntimeError(f'Expected 43 components, found {len(components)}')
    values = {c.get('ref'): c.findtext('value') for c in components}
    for base, u, coil in [(0, 'U1', 'L1'), (100, 'U2', 'L2')]:
        wanted = {u: 'LM3886T', coil: '0.7uH / air core'}
        for number, value in {1: '1M', 2: '22k', 3: '1k / 1%', 4: '20k / 1%',
                              5: '2.7R / 2W', 6: '1k', 7: '10R / 2W', 8: '22k / 0.25W'}.items():
            wanted[f'R{base+number}'] = value
        for number, value in {1: '2.2u / 63V film', 2: '47u / 63V BP', 3: '100n / 63V',
                              4: '100n / 63V', 5: '100n / 100V film', 6: '470u / 63V',
                              7: '470u / 63V', 8: '100u / 63V'}.items():
            wanted[f'C{base+number}'] = value
        for ref, value in wanted.items():
            if values.get(ref) != value:
                raise RuntimeError(f'{ref}: expected {value}, got {values.get(ref)}')
    requirements = {
        'LM3886': 'LM3886T/NOPB; non-isolated T package; footprint TBD',
        'R': '1% metal film; 0.25W unless value specifies 2W; output resistors low inductance',
        'C': 'Film unless 47u BP (nonpolar); 100n supply bypass may use X7R',
        'CP': 'Polarized; pin 1 positive, pin 2 negative; verify ripple and temperature rating',
        'L': 'Air core; DCR <=0.05 ohm target; >=4A peak; thermal validation required',
        'Conn2': 'Connector/panel hardware TBD; RUN switch contacts >=60V DC if substituted',
        'Conn3': 'DC power input; pin1 VCC, pin2 GND, pin3 VEE; current rating TBD',
    }
    with (ELECTRICAL / 'bom-draft.csv').open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['reference', 'quantity', 'value', 'symbol', 'footprint', 'selection_notes'])
        for component in components:
            kind = component.find('libsource').get('part')
            w.writerow([component.get('ref'), 1, component.findtext('value'), kind,
                        component.findtext('footprint', ''), requirements[kind]])
    count = sum(len(v) for v in actual.values())
    version = subprocess.check_output(['kicad-cli', 'version'], text=True).strip()
    report = f'''# V0.1 電氣驗證紀錄

本報告由 `python3 tools/rebuild.py` 在 KiCad {version} 完成檢查後產生。

| 檢查 | 結果 |
|---|---|
| 原理圖載入與 PDF 匯出 | 通過 |
| KiCad ERC，未排除規則 | 0 錯誤、0 警告 |
| 元件數 | {len(components)}，BOM 由 KiCad netlist 匯出 |
| IC 及被動元件數值 | 與獨立設計規格一致 |
| 網路與腳位核對 | {len(actual)} 個網路、{count} 個元件腳位通過獨立規格比對；包含 6 個單腳 NC 網路 |
| 正負電源與 IC 腳位 | pin 1/5=VCC、4=VEE、7=GND；2/6/11 不接 |
| 回授、輸出隔離、左右聲道 | 拓樸及網路連接通過 |
| 負軌與靜音電解極性 | 正端在 GND，負端分別在 VEE／MUTE |
| 手動靜音回路 | 各聲道 pin 8→電阻→RUN 跳線→VEE，兩個控制節點分開 |

ERC 與網路核對不驗證 PCB 寄生、穩定度、失真、散熱、保護或喇叭相容性。本版尚無 footprint／PCB、SPICE 元件模擬或硬體量測。計算報告是理想模型，不能當實測。

產生的 `erc.json`／`netlist.xml` 為本機檢查中間檔，未版控。BOM、PDF、PNG 及本報告隨版本提交。KiCad 檔案中的符號庫檢查未關閉。
'''
    (ELECTRICAL / 'validation.md').write_text(report)
    print(f'PASS: {len(components)} components, {len(actual)} nets, {count} pins; ERC clean; BOM written')


if __name__ == '__main__':
    verify()
