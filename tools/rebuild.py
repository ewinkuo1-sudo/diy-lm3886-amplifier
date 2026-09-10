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
    run('kicad-cli', 'sch', 'erc', '--format', 'json', '--exit-code-violations', '-o', 'electrical/erc.json', SCH)
    run('kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', 'electrical/netlist.xml', SCH)
    run('kicad-cli', 'sch', 'export', 'pdf', '-o', 'electrical/preview/lm3886-v01.pdf', SCH)
    run('pdftoppm', '-scale-to', '2400', '-png', '-singlefile', 'electrical/preview/lm3886-v01.pdf', 'electrical/preview/lm3886-v01')
    run(sys.executable, 'tools/verify_electrical.py')
    output = subprocess.check_output([sys.executable, 'tools/power_budget.py'], cwd=ROOT, text=True)
    (ROOT / 'docs/02-calculations.md').write_text(output)
    print('All V0.1 deliverables rebuilt and electrical checks passed.')


if __name__ == '__main__':
    main()
