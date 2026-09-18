# 歷史腳本（已歸檔）：只重建 pcb/archive/ 內的舊版板檔，不影響現行 V0.3；輸出路徑已改指向歸檔資料夾。
"""Render actual PCB placement/track JSON, not a fabricated product image."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math
R=Path(__file__).resolve().parents[2];D=R/'pcb/archive/v01';O=D/'preview';O.mkdir(exist_ok=True)
FONT=r'C:\Windows\Fonts\msjh.ttc'
def font(n):return ImageFont.truetype(FONT,max(8,int(n)))
def draw_board(im,data,origin,scale,show_pending=True):
 d=ImageDraw.Draw(im);ox,oy=origin;w,h=data['size']
 def point(x,y):return (ox+x*scale,oy+y*scale)
 d.rectangle([point(0,0),point(w,h)],fill='#115b4d',outline='#60bca1',width=max(1,int(scale*.3)))
 # actual copper, top view for both layers
 for t in data['tracks']:
  d.line([point(*t['a']),point(*t['b'])],fill='#eaad5d' if t['layer']=='F.Cu' else '#529cdb',width=max(1,int(t['width']*scale)))
 pd={(x['ref'],x['number']):x for x in data['pads']}
 if show_pending:
  for a,b,n in data['pending_connections']:
   a,b=pd[tuple(a)],pd[tuple(b)];a,b=point(a['x'],a['y']),point(b['x'],b['y']);length=math.dist(a,b)
   for j in range(0,int(length),10):
    u=j/length;v=min(1,(j+4)/length);d.line([(a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u),(a[0]+(b[0]-a[0])*v,a[1]+(b[1]-a[1])*v)],fill='#7fa99b',width=1)
 for c in data['parts']:
  x0,y0,x1,y1=c['body'];ang=math.radians(c['angle'])
  def trans(x,y):return point(c['x']+x*math.cos(ang)+y*math.sin(ang),c['y']-x*math.sin(ang)+y*math.cos(ang))
  pts=[trans(x0,y0),trans(x1,y0),trans(x1,y1),trans(x0,y1)]
  fill='#173443' if c['kind']=='circle' else '#28383d'
  if c['ref'].startswith('R'):fill='#b7a88a'
  if c['ref'].startswith('L'):fill='#9f572b'
  if c['ref'].startswith('J'):fill='#237b9a'
  if c['ref'].startswith('C') and c['kind']!='circle':fill='#b44b39'
  if c['kind']=='circle':
   center=trans((x0+x1)/2,(y0+y1)/2);rad=(x1-x0)*scale/2
   d.ellipse((center[0]-rad,center[1]-rad,center[0]+rad,center[1]+rad),fill=fill,outline='#d0dbd5',width=max(1,int(scale*.2)))
   if c['footprint'].startswith('CP_'):d.arc((center[0]-rad*.84,center[1]-rad*.84,center[0]+rad*.84,center[1]+rad*.84),-65,65,fill='#aac3cb',width=max(2,int(scale*.6)))
  else:d.polygon(pts,fill=fill,outline='#d0dbd5',width=max(1,int(scale*.15)))
  center=trans((x0+x1)/2,(y0+y1)/2)
  text=c['ref'];size=1.7*scale if c['kind']=='circle' or c['ref'].startswith(('BR','U','L')) else 1.3*scale
  d.text(center,text,font=font(size),fill='#102932' if c['ref'].startswith('R') else '#edf7f3',anchor='mm')
  if c['footprint']=='CP_D35_P10':
   d.text((center[0],center[1]+4*scale),'10000µF',font=font(1.65*scale),fill='#edf7f3',anchor='mm')
   d.text((center[0],center[1]+7*scale),'Ø35 / P10',font=font(1.5*scale),fill='#a9c6c4',anchor='mm')
 for pad in data['pads']:
  x,y=point(pad['x'],pad['y']);r=pad['dia']*scale/2;hole=pad['drill']*scale/2
  d.ellipse((x-r,y-r,x+r,y+r),fill='#e4c16e',outline='#f8dda0')
  d.ellipse((x-hole,y-hole,x+hole,y+hole),fill='#102c29')
 for x,y in [(4,4),(w-4,4),(4,h-4),(w-4,h-4)]:
  xx,yy=point(x,y);r=1.6*scale;d.ellipse((xx-r,yy-r,xx+r,yy+r),fill='#101c25',outline='#c0d5ca')
 d.text(point(w/2,h-7),'PLACEMENT DRAFT',font=font(1.65*scale),fill='#e3f4e9',anchor='mm')
 return d

mono=json.loads((D/'mono-placement-v01.json').read_text(encoding='utf-8'))
psu=json.loads((D/'psu-placement-v01.json').read_text(encoding='utf-8'))
for data,scale in [(mono,14),(psu,10)]:
 w,h=data['size'];im=Image.new('RGB',(int(w*scale+160),int(h*scale+260)),'#101c25');d=ImageDraw.Draw(im)
 title='單聲道放大板（製作兩片）' if data is mono else '雙橋・四電容主電源板'
 d.text((80,25),title,font=font(32),fill='#f1f8f7');d.text((80,72),f'{w} × {h} mm / 暫定封裝 / 實際 PCB 資料俯視示意',font=font(20),fill='#9bbcbf')
 draw_board(im,data,(80,120),scale)
 y=120+h*scale+28;d.text((80,y),'橘色：頂層銅箔　藍色：底層銅箔　灰色虛線：未完成連線',font=font(20),fill='#bdd1d2')
 d.text((80,y+34),'配置與初步走線草稿；不可送板、不可依此接電。',font=font(20),fill='#edc178')
 im.save(O/(data['name']+'.png'))
im=Image.new('RGB',(1750,960),'#101c25');d=ImageDraw.Draw(im)
d.text((60,32),'LM3886・三片板的配置草稿',font=font(44),fill='#f3f8f7')
d.text((60,96),'兩片相同單聲道板 + 一片共用主電源板 / 比例一致 / V0.1 PLACEMENT',font=font(25),fill='#adc7c8')
for data,pos,title in [(mono,(60,205),'左聲道 90 × 80 mm'),(mono,(515,205),'右聲道 90 × 80 mm'),(psu,(970,205),'主電源 150 × 110 mm')]:
 d.text((pos[0],163),title,font=font(23),fill='#d0e8e4');draw_board(im,data,pos,4.5)
d.text((70,597),'↑ 上緣 LM3886 鎖散熱器；T 背板需絕緣',font=font(22),fill='#e5c38a')
d.text((70,645),'兩片用同一版型；各自接 RCA 輸入與喇叭保護。',font=font(22),fill='#adc7c8')
d.text((70,688),'主電源以兩組 VCC / GND / VEE 線束分送左右聲道。',font=font(22),fill='#adc7c8')
d.line((60,753,1685,753),fill='#36565c',width=2)
d.text((60,785),'已完成：零件配置、部分銅箔、腳位與網路對照',font=font(25),fill='#a2dfbd')
d.text((60,833),'尚待：放大板接地回流與餘下走線、真實封裝、線寬載流與散熱驗證',font=font(23),fill='#e5c38a')
d.text((60,888),'本圖由 KiCad 草稿資料生成，非實物照片；尺寸與封裝均可再修。不可直接製造。',font=font(21),fill='#93afb4')
im.save(O/'system-placement-overview.png')
print('Rendered PCB data to',O)
