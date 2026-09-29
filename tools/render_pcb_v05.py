"""Render the V0.5 placement/track JSON with the V0.3 drawing routine (same colours, top view) plus a
system view that shows the boards at the same scale as the V0.4 ones they replace."""
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
ns={"__file__":str(R/"tools/render_pcb_v03.py")};exec(src[:src.index("mono=json.loads")].replace('V0.3 B / ENGINEERING DRAFT','V0.5 / ENGINEERING DRAFT').replace(" # actual copper, top view for both layers",ZONE_HOOK),ns)   # only the helpers, not the V0.3 render pass
draw_board,font=ns['draw_board'],ns['font']
for name,title,scale in [('mono-layout-v05d','單聲道放大板 / 方案 C・V0.5（D 系、縮為 90×90、C2 站立）',12),('psu-layout-v05','雙橋四電容電源板 / 方案 C・V0.5（AC 區上緣、輸出區下緣、125×130）',9)]:
 data=json.loads((D/f'{name}.json').read_text(encoding='utf-8'))
 w,h=data['size'];im=Image.new('RGB',(int(w*scale+160),int(h*scale+260)),'#101c25');d=ImageDraw.Draw(im)
 d.text((80,25),title,font=font(32),fill='#f1f8f7');d.text((80,72),f'{w} × {h} mm / 頂視，合併顯示兩層銅箔 / 封裝沿用 V0.3 暫定外框（C2 站立封裝為新增假設）',font=font(20),fill='#9bbcbf')
 draw_board(im,data,(80,120),scale)
 if not data.get('zones'):
  x,y=data['anchors']['STAR'];cx=80+x*scale;cy=120+y*scale
  d.ellipse((cx-6,cy-6,cx+6,cy+6),outline='#fff3aa',width=2);d.text((cx+9,cy+9),'STAR',font=font(16),fill='#fff3aa')
 y=120+h*scale+28;d.text((80,y),'橘：頂層銅箔　藍：底層銅箔　暗藍面：底層 GND 鋪銅' if data.get('zones') else '橘：頂層銅箔　藍：底層銅箔　黃圈：接地匯流點 STAR',font=font(20),fill='#bdd1d2')
 d.text((80,y+34),'工程草稿：走線寬度、真實封裝與散熱尚待驗證，不可送板。',font=font(20),fill='#edc178')
 im.save(O/(name+'.png'));print('rendered',O/(name+'.png'))

# System view: V0.4 (D + PSU) next to V0.5 at one scale, so the size change is visible.
S=3.6
old_amp=json.loads((D/'mono-layout-v04d.json').read_text(encoding='utf-8'));old_psu=json.loads((D/'psu-layout-v04.json').read_text(encoding='utf-8'))
amp=json.loads((D/'mono-layout-v05d.json').read_text(encoding='utf-8'));psu=json.loads((D/'psu-layout-v05.json').read_text(encoding='utf-8'))
im=Image.new('RGB',(1900,1290),'#101c25');d=ImageDraw.Draw(im)
d.text((60,32),'LM3886 / 方案 C PCB V0.5（機殼配合縮板）：上排 V0.4、下排 V0.5，同比例',font=font(44),fill='#f3f8f7')
d.text((60,100),'電路、零件、網路不變；只改板形與零件位置，讓兩片放大板貼牆那一邊由 115 縮到 90、電源板由 160×120 改成 125×130',font=font(25),fill='#adc7c8')
row=[(old_amp,(60,190),'V0.4 放大板 D 115×90'),(old_amp,(520,190),'V0.4 放大板 D 115×90'),(old_psu,(1000,190),'V0.4 電源板 160×120')]
row2=[(amp,(60,700),'V0.5 放大板 D 90×90'),(amp,(520,700),'V0.5 放大板 D 90×90'),(psu,(1000,700),'V0.5 電源板 125×130')]
for data,pos,title in row+row2:
 d.text((pos[0],pos[1]-34),title,font=font(24),fill='#d0e8e4');draw_board(im,data,pos,S)
d.line((60,650,1840,650),fill='#36565c',width=2)
d.text((1620,220),'BZ4312A2 內 330×297',font=font(22),fill='#e5c38a')
d.text((1620,252),'V0.4：深餘 7、前排寬餘 10',font=font(20),fill='#e5c38a')
d.text((1620,282),'V0.5：深餘 22、前排寬餘 45',font=font(20),fill='#a2dfbd')
d.text((60,1200),'兩板 KiCad 10.0.6 DRC 0 違規、0 未連通；放大板底層鋪銅單一連通區、0 過孔。C2 站立封裝腳距 15 為假設，要拿實物彎腳量過。非製造版本。',font=font(23),fill='#93afb4')
d.text((60,1236),'U1 仍在 y=14；IC 移到板邊直接鎖散熱牆（方案 B）等三項實量後再改。',font=font(23),fill='#93afb4')
im.save(O/'system-layout-v05.png');print('rendered',O/'system-layout-v05.png')
