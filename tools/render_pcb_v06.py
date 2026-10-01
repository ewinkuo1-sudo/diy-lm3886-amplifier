"""Render the V0.6 amplifier board, the V0.6 PSU, and the four-board system view at one scale."""
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
amp = json.loads((D / 'mono-layout-v06.json').read_text(encoding='utf-8'))
psu = json.loads((D / 'psu-layout-v06.json').read_text(encoding='utf-8'))
ctrl = json.loads((D / 'ctrl-layout-v06.json').read_text(encoding='utf-8'))
mains = json.loads((D / 'mains-layout-v06.json').read_text(encoding='utf-8'))


def hs_envelope(d, data, pos, S):
    for ref in ('BR1', 'BR2'):
        b = next(p for p in data['parts'] if p['ref'] == ref)
        x0 = pos[0] + (b['x'] - 27.5) * S; x1 = pos[0] + (b['x'] + 2.5) * S; y0 = pos[1] + (b['y'] + 2) * S; y1 = y0 + 10 * S
        d.rectangle((x0, y0, x1, y1), outline='#e8c27a', width=2)


# amplifier
S = 9
im = Image.new('RGB', (1500, int(80 * S + 260)), '#101c25'); d = ImageDraw.Draw(im)
d.text((80, 25), '放大板 V0.6（90×80）：IC 背板貼板邊直接鎖散熱器，其餘沿用 V0.5 D', font=font(30), fill='#f1f8f7')
d.text((80, 72), 'U1 改用 KiCad 函式庫 TO-220-11 直立封裝（背板在奇數腳後 9.58 mm，型錄幾何未對實物）；IC 上方不再走線，Kelvin 與靜音線改走腳排下方', font=font(19), fill='#9bbcbf')
draw_board(im, amp, (80, 120), S)
d.line((80, 120, 80 + 90 * S, 120), fill='#e8c27a', width=4)
d.text((80, 120 + 80 * S + 28), '橘：頂層　藍：底層（整面接地）　黃線＝散熱器底板位置（IC 背板貼齊）', font=font(20), fill='#bdd1d2')
d.text((80, 120 + 80 * S + 60), '工程草稿：IC 腳距幾何、C2 站立腳距 15 都未對實物，不可送板。', font=font(20), fill='#edc178')
im.save(O / 'mono-layout-v06.png'); print('rendered', O / 'mono-layout-v06.png')

# PSU
S = 7
im = Image.new('RGB', (int(92 * S + 160), int(120 * S + 260)), '#101c25'); d = ImageDraw.Draw(im)
d.text((80, 25), '電源板 V0.6（92×120）：四顆 381LX 兩欄、GBJ2510 ×2 朝前、保險絲與 AC 端子朝變壓器', font=font(30), fill='#f1f8f7')
d.text((80, 72), 'DC 輸出兩組 3P 端子在後緣朝放大板；GND 星點在下方底層連線；snubber 預留位已移除（放不下）', font=font(19), fill='#9bbcbf')
draw_board(im, psu, (80, 120), S); hs_envelope(d, psu, (80, 120), S)
x, y = psu['anchors']['STAR']; cx = 80 + x * S; cy = 120 + y * S
d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), outline='#fff3aa', width=2); d.text((cx + 9, cy + 9), 'STAR', font=font(16), fill='#fff3aa')
d.text((80, 120 + 120 * S + 28), '橘：頂層　藍：底層　黃框：GBJ 金屬背面側的散熱片空間（朝保險絲）　黃圈：接地星點', font=font(20), fill='#bdd1d2')
d.text((80, 120 + 120 * S + 60), '工程草稿，不可送板。', font=font(20), fill='#edc178')
im.save(O / 'psu-layout-v06.png'); print('rendered', O / 'psu-layout-v06.png')

# system view: all four boards
S = 4.2
im = Image.new('RGB', (2250, 820), '#101c25'); d = ImageDraw.Draw(im)
d.text((60, 28), 'LM3886 PCB V0.6：放大板 90×80 ×2、電源板 92×120、控制板 70×120、市電板 70×100（同比例）', font=font(40), fill='#f3f8f7')
d.text((60, 90), '弘宙 102 後排：放大板 L｜電源板｜放大板 R（IC 貼兩側散熱器）；前排變壓器居中，控制板左前、市電板右前', font=font(24), fill='#adc7c8')
for dat, pos, title in [(amp, (60, 180), '放大板 L 90×80'), (psu, (500, 180), '電源板 92×120'), (amp, (940, 180), '放大板 R 90×80'), (ctrl, (1380, 180), '控制板 70×120'), (mains, (1740, 180), '市電板 70×100')]:
    d.text((pos[0], pos[1] - 34), title, font=font(23), fill='#d0e8e4'); draw_board(im, dat, pos, S)
hs_envelope(d, psu, (500, 180), S)
d.text((60, 740), '四板 KiCad 10.0.6 DRC 0 錯誤、0 未連通。放大板 IC 幾何與 C2 腳距、電源板 GBJ、控制板繼電器與 NTC 皆未對實物；非製造版本。', font=font(22), fill='#93afb4')
im.save(O / 'system-layout-v06.png'); print('rendered', O / 'system-layout-v06.png')
