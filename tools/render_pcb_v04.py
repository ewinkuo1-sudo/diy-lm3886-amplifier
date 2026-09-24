"""Render the V0.4 variant-C placement/track JSON with the V0.3 drawing routine (same colours, top view)."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
R=Path(__file__).resolve().parents[1];D=R/'pcb';O=D/'preview';O.mkdir(exist_ok=True)
ZONE_HOOK='''
 for zn in data.get('zones',[]):
  for ring in zn['filled']:
   d.polygon([point(*q) for q in ring['outer']],fill='#3b6f9c')
   for hole in ring['holes']:d.polygon([point(*q) for q in hole],fill='#115b4d')
'''
src=(R/'tools/render_pcb_v03.py').read_text(encoding='utf-8')
ns={"__file__":str(R/"tools/render_pcb_v03.py")};exec(src[:src.index("mono=json.loads")].replace('V0.3 B / ENGINEERING DRAFT','V0.4 / ENGINEERING DRAFT').replace(" # actual copper, top view for both layers",ZONE_HOOK),ns)   # only the helpers, not the V0.3 render pass
draw_board,font=ns['draw_board'],ns['font']
for name,title in [('mono-layout-v04c','單聲道放大板 / 方案 C・V0.4 變體 C（改良星型接地）'),('mono-layout-v04d','單聲道放大板 / 方案 C・V0.4 變體 D（底層整面接地）')]:
 data=json.loads((D/f'{name}.json').read_text(encoding='utf-8'));scale=12
 w,h=data['size'];im=Image.new('RGB',(int(w*scale+160),int(h*scale+260)),'#101c25');d=ImageDraw.Draw(im)
 d.text((80,25),title,font=font(32),fill='#f1f8f7');d.text((80,72),f'{w} × {h} mm / 頂視，合併顯示兩層銅箔 / 封裝沿用 V0.3 暫定外框',font=font(20),fill='#9bbcbf')
 draw_board(im,data,(80,120),scale)
 for key,col in ([] if data.get('zones') else [('STAR','#fff3aa'),('SG','#9ad7ff')]):
  x,y=data['anchors'][key];cx=80+x*scale;cy=120+y*scale
  d.ellipse((cx-6,cy-6,cx+6,cy+6),outline=col,width=2);d.text((cx+9,cy+9),key,font=font(16),fill=col)
 y=120+h*scale+28;d.text((80,y),'橘：頂層銅箔　藍：底層銅箔　暗藍面：底層 GND 鋪銅' if data.get('zones') else '橘：頂層銅箔　藍：底層銅箔　黃圈：接地匯流點 STAR　藍圈：訊號地 SG',font=font(20),fill='#bdd1d2')
 d.text((80,y+34),'工程草稿：走線寬度、真實封裝與散熱尚待驗證，不可送板。',font=font(20),fill='#edc178')
 im.save(O/(name+'.png'));print('rendered',O/(name+'.png'))
