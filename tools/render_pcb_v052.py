"""Render the V0.5.2 merged board (V0.3 drawing routine) and a system view: V0.5 three boards vs V0.5.2 two boards."""
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
ns={"__file__":str(R/"tools/render_pcb_v03.py")};exec(src[:src.index("mono=json.loads")].replace('V0.3 B / ENGINEERING DRAFT','ENGINEERING DRAFT').replace(" # actual copper, top view for both layers",ZONE_HOOK),ns)
draw_board,font=ns['draw_board'],ns['font']
def star(im,data,pos,scale):
 x,y=data['anchors']['STAR'];cx=pos[0]+x*scale;cy=pos[1]+y*scale;d=ImageDraw.Draw(im)
 d.ellipse((cx-6,cy-6,cx+6,cy+6),outline='#fff3aa',width=2);d.text((cx+9,cy-4),'STAR',font=font(16),fill='#fff3aa')
data=json.loads((D/'mono-layout-v052.json').read_text(encoding='utf-8'));scale=9
w,h=data['size'];im=Image.new('RGB',(int(w*scale+160),int(h*scale+260)),'#101c25');d=ImageDraw.Draw(im)
d.text((80,25),'單聲道放大＋濾波合板 / 方案 C・V0.5.2 候選',font=font(32),fill='#f1f8f7')
d.text((80,70),f'{w} × {h} mm / 上半＝V0.5 放大板不動、下半＝該聲道兩顆 10,000µF / 頂視，合併顯示兩層銅箔 / 封裝沿用暫定外框；J6 四位 DC 端子與 C2 站立封裝為新增假設',font=font(20),fill='#9bbcbf')
draw_board(im,data,(80,120),scale);star(im,data,(80,120),scale)
y=120+h*scale+28;d.text((80,y),'橘：頂層銅箔　藍：底層銅箔　暗藍面：底層 GND 鋪銅（只蓋放大區 y≤92）　黃圈：電源區接地匯流點 STAR，由一條 4 mm 底層線接進鋪銅',font=font(20),fill='#bdd1d2')
d.text((80,y+34),'工程草稿：合成網路表尚無 KiCad 原理圖；走線寬度、真實封裝與散熱尚待驗證，不可送板。',font=font(20),fill='#edc178')
im.save(O/'mono-layout-v052.png');print('rendered',O/'mono-layout-v052.png')

S=3.6
amp5=json.loads((D/'mono-layout-v05d.json').read_text(encoding='utf-8'));psu5=json.loads((D/'psu-layout-v05.json').read_text(encoding='utf-8'))
im=Image.new('RGB',(1900,1330),'#101c25');d=ImageDraw.Draw(im)
d.text((60,32),'LM3886 / 方案 C：V0.5 三板（現行） vs V0.5.2 兩板合板（候選），同比例',font=font(44),fill='#f3f8f7')
d.text((60,100),'電路、零件、網路不變。V0.5.2 把每聲道的兩顆 10,000µF、洩放與旁路搬到放大板下半；電源板消失，兩顆 KBPC2510 仍鎖機殼、AC 保險絲改機殼保險絲座',font=font(24),fill='#adc7c8')
for data,pos,title in [(amp5,(60,200),'V0.5 放大板 D 90×90'),(amp5,(460,200),'V0.5 放大板 D 90×90'),(psu5,(870,200),'V0.5 電源板 125×130'),(data,(1400,200),'V0.5.2 合板 90×142 ×2')]:
 d.text((pos[0],pos[1]-34),title,font=font(24),fill='#d0e8e4');draw_board(im,data,pos,S)
 if not data.get('zones') or data['name']=='mono-layout-v052':star(im,data,pos,S)
d.line((1330,170,1330,760),fill='#36565c',width=2)
d.text((1400,740),'（第二片相同，未畫）',font=font(20),fill='#93afb4')
rows=[('板數','3（放大 ×2＋電源 ×1）','2（合板 ×2）'),('板面積','2×8,100＋16,250＝32,450 mm²','2×12,780＝25,560 mm²'),
('電源→IC 粗線','電源板→放大板約 20–30 cm 線束 ×2','板上 5 cm 銅箔'),('板間線束','每聲道 3 條 DC＋橋堆 4 條 Faston','每板 4 條 DC；橋堆 ×2 鎖在兩板中間 46 mm 空隙的機殼底，DC 端子正對著它'),
('接地匯流點','電源板一個 STAR，兩聲道共用','每板一個 STAR，兩板地在機殼再匯一次（哼聲風險，要處理）'),
('AC 保險絲／snubber','電源板上','離板：機殼保險絲座或小 AC 板'),('BZ4312A2 配置 A','後排 90＋150＋90，控制板在中；深餘 22、前排寬餘 45','後排 142＋46＋142，控制板改到前排；深餘 32、前排寬餘 50'),
('原理圖','兩份既有 KiCad 原理圖','**尚無**，網路表由腳本合成，選定後要補生成器')]
y0=800;d.text((60,y0-40),'比較',font=font(28),fill='#f1f8f7')
for i,(k,a,b) in enumerate(rows):
 yy=y0+i*44;d.text((60,yy),k,font=font(22),fill='#e5c38a');d.text((330,yy),a,font=font(22),fill='#cfe3e6');d.text((1060,yy),b.replace('**',''),font=font(22),fill='#a2dfbd' if i not in (4,7) else '#f0b0a0')
d.text((60,1240),'V0.5.2：KiCad 10.0.6 DRC 0 違規、0 未連通；放大區鋪銅單一連通區、0 過孔；電源區 GND 焊盤全在鋪銅外、只經一條 STAR 連線接入（verify_pcb_v052.py）。非製造版本。',font=font(22),fill='#93afb4')
d.text((60,1276),'共用整流、各板濾波，不是真正雙單聲道（變壓器只有一組 2×22 Vac）。',font=font(22),fill='#93afb4')
im.save(O/'system-layout-v052-compare.png');print('rendered',O/'system-layout-v052-compare.png')
