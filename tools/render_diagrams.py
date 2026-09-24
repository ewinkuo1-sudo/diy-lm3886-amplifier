"""SVG -> PNG for docs/diagrams with PyMuPDF (replaces render_diagrams.cjs / sharp on machines without node)."""
from pathlib import Path
import pymupdf
D=Path(__file__).resolve().parents[1]/'docs/diagrams'
for f in sorted((D/'svg').glob('*.svg')):
 pix=pymupdf.open(str(f))[0].get_pixmap(dpi=108,alpha=False);pix.save(str(D/(f.stem+'.png')));print(f.name,pix.width,pix.height)
