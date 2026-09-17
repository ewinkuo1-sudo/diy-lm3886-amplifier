"""Frame native 3D renders with model assumptions, using Pillow."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import os
R=Path(__file__).resolve().parents[1];O=R/'pcb/inspection-v03/3d'
FONT=os.environ.get('LM3886_FONT','/System/Library/Fonts/STHeiti Medium.ttc')
def f(n):return ImageFont.truetype(FONT,n)
for key,label in [('mono','單聲道放大板｜每台兩片'),('psu','共用電源板｜每台一片')]:
 for v,title in [('top','正面'),('bottom','背面'),('isometric','斜視')]:
  src=Image.open(O/f'raw-{key}-{v}.png').convert('RGB');im=Image.new('RGB',(1500,1340),'#101e28');im.paste(src,(0,130));d=ImageDraw.Draw(im)
  d.text((50,22),label+' / 3D '+title,font=f(34),fill='#f1f7f6')
  d.text((50,78),'PCB V0.3｜KiCad 原生算繪＋暫定元件外框模型',font=f(24),fill='#c0d7dc')
  d.text((50,1244),'外形與高度未經實物核對；不是原廠模型，也不是可加工的裝配圖。',font=f(24),fill='#efc077')
  d.text((50,1285),'無散熱器、機殼、焊錫及公差；模型小柱僅標示焊盤位置。',font=f(22),fill='#b0c7d0')
  im.save(O/f'{key}-{v}.png')
im=Image.new('RGB',(2100,1110),'#101e28');d=ImageDraw.Draw(im)
d.text((55,28),'LM3886｜PCB V0.3 立體配置預覽',font=f(42),fill='#f1f7f6')
d.text((55,90),'兩片相同放大板＋一片共用電源板；下圖各展示一種板。',font=f(27),fill='#b0c7d0')
for key,x,label in [('mono',35,'放大板 100 × 90 mm，需兩片'),('psu',1070,'電源板 160 × 120 mm，需一片')]:
 d.text((x+15,155),label,font=f(26),fill='#f1f7f6');src=Image.open(O/f'raw-{key}-isometric.png').convert('RGB');src.thumbnail((995,800));im.paste(src,(x,210))
d.text((55,1000),'暫定外形與假設高度，僅供檢視；兩圖縮放不同，不代表機殼配置。',font=f(28),fill='#efc077')
d.text((55,1050),'實際腳位、料號、散熱與機構確認後，才能完成製造版。',font=f(25),fill='#b0c7d0')
im.save(O/'overview.png')
