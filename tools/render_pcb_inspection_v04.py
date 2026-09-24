"""SVG -> PNG for the V0.4 review drawings with PyMuPDF (no node/sharp needed); vector sources untouched."""
from pathlib import Path
import fitz
D=Path(__file__).resolve().parents[1]/'pcb/inspection-v04/drawings'
for f in sorted(D.glob('*.svg')):
 doc=fitz.open(str(f));pix=doc[0].get_pixmap(dpi=96,alpha=False);pix.save(str(f.with_suffix('.png')));print(f.name,pix.width,pix.height)
