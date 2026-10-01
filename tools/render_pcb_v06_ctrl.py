"""Render the V0.6 CTRL and MAINS boards (top view, both copper layers) side by side at one scale."""
from pathlib import Path
from PIL import Image, ImageDraw
import json
R = Path(__file__).resolve().parents[1]; D = R / 'pcb'; O = D / 'preview'; O.mkdir(exist_ok=True)
src = (R / 'tools/render_pcb_v03.py').read_text(encoding='utf-8')
ZONE_HOOK = '''
 for zn in data.get('zones',[]):
  for ring in zn['filled']:
   d.polygon([point(*q) for q in ring['outer']],fill='#3b6f9c')
   for hole in ring['holes']:d.polygon([point(*q) for q in hole],fill='#115b4d')
'''
ns = {"__file__": str(R / "tools/render_pcb_v03.py")}
exec(src[:src.index("mono=json.loads")].replace('V0.3 B / ENGINEERING DRAFT', 'V0.6 / ENGINEERING DRAFT').replace(" # actual copper, top view for both layers", ZONE_HOOK), ns)
draw_board, font = ns['draw_board'], ns['font']
ctrl = json.loads((D / 'ctrl-layout-v06.json').read_text(encoding='utf-8'))
mains = json.loads((D / 'mains-layout-v06.json').read_text(encoding='utf-8'))
S = 7
im = Image.new('RGB', (1700, int(120 * S + 300)), '#101c25'); d = ImageDraw.Draw(im)
d.text((60, 28), 'LM3886 V0.6：控制／保護板 CTRL 70×120 ＋ 市電板 MAINS 70×100（頂視，合併顯示兩層銅箔）', font=font(30), fill='#f1f8f7')
d.text((60, 76), '橘：頂層銅箔　藍：底層銅箔（CTRL 底層整面接地）　繼電器 G2RL-1-E 每個觸點兩個焊盤以短線相連　MAINS 右半為市電側，與左半低壓側銅箔距離 ≥6.4 mm', font=font(17), fill='#9bbcbf')
for dat, pos, title in [(ctrl, (60, 150), 'CTRL：UPC1237 保護＋12 V 輔助電源＋旁通計時'), (mains, (60 + 70 * S + 120, 150), 'MAINS：NTC 軟啟動＋K_BYP＋K_TRIG（市電！）')]:
    d.text((pos[0], pos[1] - 32), title, font=font(22), fill='#d0e8e4'); draw_board(im, dat, pos, S)
# mains / low-voltage split line on MAINS
x0 = 60 + 70 * S + 120
d.line([(x0 + 28 * S, 150), (x0 + 28 * S, 150 + 100 * S)], fill='#e8c27a', width=2)
d.text((x0 + 28 * S + 8, 150 + 100 * S - 30), '← 低壓 12 V　市電 →', font=font(17), fill='#e8c27a')
d.text((60, 150 + 120 * S + 30), 'KiCad 10.0.6 DRC：兩板 0 錯誤、0 未連通。封裝：繼電器／SIP／DIP／TO／二極體取自 KiCad 函式庫，NTC 與小電解為暫定外框；全部零件未到貨。工程草稿，不可送板。', font=font(17), fill='#edc178')
im.save(O / 'ctrl-mains-layout-v06.png'); print('rendered', O / 'ctrl-mains-layout-v06.png')
