"""Regenerate project deliverables and stop on any verification failure."""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCH = 'electrical/lm3886-v01.kicad_sch'


def run(*args):
    subprocess.run(args, cwd=ROOT, check=True)


def main():
    for tool in ('kicad-cli', 'pdftoppm'):
        if not shutil.which(tool):
            raise SystemExit(f'Missing prerequisite: {tool}')
    run(sys.executable, 'tools/build_schematic.py')
    run(sys.executable, 'tools/build_power_supply.py')
    run('kicad-cli', 'sch', 'erc', '--format', 'json', '--exit-code-violations', '-o', 'electrical/erc.json', SCH)
    run('kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', 'electrical/netlist.xml', SCH)
    run('kicad-cli', 'sch', 'export', 'pdf', '-o', 'electrical/preview/lm3886-v01.pdf', SCH)
    run('pdftoppm', '-scale-to', '2400', '-png', '-singlefile', 'electrical/preview/lm3886-v01.pdf', 'electrical/preview/lm3886-v01')
    run(sys.executable, 'tools/verify_electrical.py')
    psu = 'electrical/internal-psu-v02.kicad_sch'
    run('kicad-cli', 'sch', 'erc', '--format', 'json', '--exit-code-violations', '-o', 'electrical/psu-erc.json', psu)
    run('kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', 'electrical/psu-netlist.xml', psu)
    run('kicad-cli', 'sch', 'export', 'pdf', '-o', 'electrical/preview/internal-psu-v02.pdf', psu)
    run('pdftoppm', '-scale-to', '2400', '-png', '-singlefile', 'electrical/preview/internal-psu-v02.pdf', 'electrical/preview/internal-psu-v02')
    run(sys.executable, 'tools/verify_power_supply.py')
    output = subprocess.check_output([sys.executable, 'tools/power_budget.py'], cwd=ROOT, text=True, encoding="utf-8")
    (ROOT / 'docs/02-功率與散熱估算.md').write_text(output, encoding="utf-8")
    # docs/06 was merged into docs/05 on 2026-09-21; mains_budget.py now prints to stdout only.
    # Re-run `python3 tools/mains_budget.py` by hand and update the estimate section in docs/05.
    print('All V0.3 deliverables rebuilt and electrical checks passed.')
    print('Reminder: docs/05 power estimates are not auto-written; run tools/mains_budget.py and update that section.')


if __name__ == '__main__':
    main()
