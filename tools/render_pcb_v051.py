"""Render the V0.5.1 PSU (bridges on board) and a side-by-side with V0.5 (bridges on chassis) at one scale."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
R=Path(__file__).resolve().parents[1];D=R/'pcb';O=D/'preview';O.mkdir(exist_ok=True)
src=(R/'tools/render_pcb_v03.py').read_text(encoding='utf-8')
ns={"__file__":str(R/"tools/render_pcb_v03.py")};exec(src[:src.index("mono=json.loads")].replace('V0.3 B / ENGINEERING DRAFT','V0.5.1 / ENGINEERING DRAFT'),ns)
draw_board,font=ns['draw_board'],ns['font']
name='psu-layout-v051';scale=9
data=json.loads((D/f'{name}.json').read_text(encoding='utf-8'))
w,h=data['size'];im=Image.new('RGB',(int(w*scale+160),int(h*scale+260)),'#101c25');d=ImageDraw.Draw(im)
d.text((80,25),'雙橋四電容電源板 / 方案 C・V0.5.1（整流橋 GBJ2510 直立上板、125×130 不變）',font=font(32),fill='#f1f8f7')
d.text((80,72),f'{w} × {h} mm / 頂視，合併顯示兩層銅箔 / GBJ 封裝依 Diodes DS21221 畫，實物未到；粗線那一側是金屬背面＝散熱片側',font=font(20),fill='#9bbcbf')
draw_board(im,data,(80,120),scale)
x,y=data['anchors']['STAR'];cx=80+x*scale;cy=120+y*scale
d.ellipse((cx-6,cy-6,cx+6,cy+6),outline='#fff3aa',width=2);d.text((cx+9,cy+9),'STAR',font=font(16),fill='#fff3aa')
# heatsink envelopes
for ref in ('BR1','BR2'):
 b=next(p for p in data['parts'] if p['ref']==ref);x0=80+(b['x']-2.5)*scale;x1=80+(b['x']+27.5)*scale;y1=120+(b['y']-2)*scale;y0=y1-10*scale
 d.rectangle((x0,y0,x1,y1),outline='#e8c27a',width=2);d.text((x0+6,y0+4),'散熱片空間 10 mm 內',font=font(15),fill='#e8c27a')
yy=120+h*scale+28;d.text((80,yy),'橘：頂層銅箔　藍：底層銅箔　黃圈：接地匯流點 STAR　黃框：GBJ 金屬背面側預留的散熱片空間',font=font(20),fill='#bdd1d2')
d.text((80,yy+34),'工程草稿：走線寬度、真實封裝與散熱尚待驗證，不可送板。',font=font(20),fill='#edc178')
im.save(O/(name+'.png'));print('rendered',O/(name+'.png'))

S=4.2
old=json.loads((D/'psu-layout-v05.json').read_text(encoding='utf-8'))
ns_old={"__file__":str(R/"tools/render_pcb_v03.py")};exec(src[:src.index("mono=json.loads")].replace('V0.3 B / ENGINEERING DRAFT','V0.5 / ENGINEERING DRAFT'),ns_old)   # footer label of the old board
im=Image.new('RGB',(1340,820),'#101c25');d=ImageDraw.Draw(im)
d.text((50,28),'電源板 V0.5（橋堆鎖機殼）→ V0.5.1（GBJ2510 直立上板），同比例',font=font(38),fill='#f3f8f7')
d.text((50,84),'電路、零件、網路、板尺寸都不變；只換 BR1／BR2 的封裝與位置，並重接進出整流橋的四條大電流走線',font=font(23),fill='#adc7c8')
for dat,pos,title,drawer in [(old,(50,170),'V0.5：4 位端子接機殼上的 KBPC2510（每橋 4 條 Faston 線）',ns_old['draw_board']),(data,(720,170),'V0.5.1：GBJ2510 站在板上，金屬背朝板邊，散熱片放黃框',draw_board)]:
 d.text((pos[0],pos[1]-34),title,font=font(21),fill='#d0e8e4');drawer(im,dat,pos,S)
for ref in ('BR1','BR2'):
 b=next(p for p in data['parts'] if p['ref']==ref);x0=720+(b['x']-2.5)*S;x1=720+(b['x']+27.5)*S;y1=170+(b['y']-2)*S;y0=y1-10*S
 d.rectangle((x0,y0,x1,y1),outline='#e8c27a',width=2)
d.text((50,760),'V0.5.1 KiCad 10.0.6 DRC 0 違規、0 未連通，50 焊盤網路與原理圖相符。GBJ 腳孔 2.6×1.4 長孔、腳距 10／7.5／7.5 取自原廠規格書，實物到貨要核對。非製造版本。',font=font(19),fill='#93afb4')
im.save(O/'psu-layout-v051-compare.png');print('rendered',O/'psu-layout-v051-compare.png')

# System view (2026-10-01): the three boards that make up the current V0.5.1 machine, at one scale.
# Amplifier boards are V0.5 D (solid B.Cu pour -> needs the zone hook); PSU is V0.5.1 (bridges on board).
ZONE_HOOK='''
 for zn in data.get('zones',[]):
  for ring in zn['filled']:
   d.polygon([point(*q) for q in ring['outer']],fill='#3b6f9c')
   for hole in ring['holes']:d.polygon([point(*q) for q in hole],fill='#115b4d')
'''
ns_amp={"__file__":str(R/"tools/render_pcb_v03.py")};exec(src[:src.index("mono=json.loads")].replace('V0.3 B / ENGINEERING DRAFT','V0.5 / ENGINEERING DRAFT').replace(" # actual copper, top view for both layers",ZONE_HOOK),ns_amp)
amp=json.loads((D/'mono-layout-v05d.json').read_text(encoding='utf-8'))
S=3.6
im=Image.new('RGB',(1900,780),'#101c25');d=ImageDraw.Draw(im)
d.text((60,32),'LM3886 / 方案 C PCB V0.5.1（現行）：兩片放大板 D 90×90 ＋ 電源板 125×130，同比例',font=font(44),fill='#f3f8f7')
d.text((60,100),'放大板與 V0.5 相同；電源板的整流橋 GBJ2510 直接站在板上（黃框＝金屬背面側預留的散熱片空間），不再用 Faston 線接機殼上的橋堆',font=font(25),fill='#adc7c8')
for dat,pos,title,drawer in [(amp,(60,190),'放大板 D（左聲道）90×90',ns_amp['draw_board']),(amp,(520,190),'放大板 D（右聲道）90×90',ns_amp['draw_board']),(data,(1000,190),'電源板 V0.5.1 125×130（GBJ2510 ×2 上板）',draw_board)]:
 d.text((pos[0],pos[1]-34),title,font=font(24),fill='#d0e8e4');drawer(im,dat,pos,S)
for ref in ('BR1','BR2'):
 b=next(p for p in data['parts'] if p['ref']==ref);x0=1000+(b['x']-2.5)*S;x1=1000+(b['x']+27.5)*S;y1=190+(b['y']-2)*S;y0=y1-10*S
 d.rectangle((x0,y0,x1,y1),outline='#e8c27a',width=2)
d.text((1620,220),'BZ4312A2 內 330×297',font=font(22),fill='#e5c38a')
d.text((1620,252),'配置 A：深餘 22、前排寬餘 45',font=font(20),fill='#a2dfbd')
d.text((60,700),'三板 KiCad 10.0.6 DRC 0 違規、0 未連通。C2 站立腳距 15、GBJ 高度 20 為假設，實物到貨要量。U1 仍在 y=14，方案 B 等三項實量後再改。非製造版本。',font=font(23),fill='#93afb4')
im.save(O/'system-layout-v051.png');print('rendered',O/'system-layout-v051.png')
