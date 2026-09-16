"""Render actual PCB placement/track JSON, not a fabricated product image."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math,os
R=Path(__file__).resolve().parents[1];D=R/'pcb';O=D/'preview';O.mkdir(exist_ok=True)
FONT=os.environ.get('LM3886_FONT', '/System/Library/Fonts/STHeiti Medium.ttc' if Path('/System/Library/Fonts/STHeiti Medium.ttc').exists() else r'C:\Windows\Fonts\msjh.ttc')
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
   if c['footprint'].startswith('CP_'):d.arc((center[0]-rad*.84,center[1]-rad*.84,center[0]+rad*.84,center[1]+rad*.84),-65-c['angle'],65-c['angle'],fill='#aac3cb',width=max(2,int(scale*.6)))
  else:d.polygon(pts,fill=fill,outline='#d0dbd5',width=max(1,int(scale*.15)))
  center=trans((x0+x1)/2,(y0+y1)/2)
  if c['ref']=='J203':center=point(c['x']-1,c['y']-6)
  if c['ref']=='J5':center=point(c['x']+5.08,c['y']-5.5)
  if c['footprint']=='CP_D8_P3.5':center=(center[0],center[1]-2.3*scale)
  text=c['ref'];size=1.7*scale if c['kind']=='circle' or c['ref'].startswith(('BR','U','L')) else 1.3*scale
  d.text(center,text,font=font(size),fill='#102932' if c['ref'].startswith('R') else '#edf7f3',anchor='mm')
  if c['footprint']=='CP_D35_P10':
   d.text((center[0],center[1]+9*scale),'10000µF',font=font(1.65*scale),fill='#edf7f3',anchor='mm')
   d.text((center[0],center[1]+12*scale),'Ø35 / P10',font=font(1.5*scale),fill='#a9c6c4',anchor='mm')
 for pad in data['pads']:
  x,y=point(pad['x'],pad['y']);r=pad['dia']*scale/2;hole=pad['drill']*scale/2
  d.ellipse((x-r,y-r,x+r,y+r),fill='#e4c16e',outline='#f8dda0')
  d.ellipse((x-hole,y-hole,x+hole,y+hole),fill='#102c29')
 for via in data.get('vias',[]):
  xx,yy=point(via['x'],via['y']);rad=via['dia']*scale/2
  d.ellipse((xx-rad,yy-rad,xx+rad,yy+rad),fill='#e4c16e')
  rad=via['drill']*scale/2;d.ellipse((xx-rad,yy-rad,xx+rad,yy+rad),fill='#102c29')
 for x,y in [(4,4),(w-4,4),(4,h-4),(w-4,h-4)]:
  xx,yy=point(x,y);r=1.6*scale;d.ellipse((xx-r,yy-r,xx+r,yy+r),fill='#101c25',outline='#c0d5ca')
 d.text(point(w/2,h-7),'V0.2 B / ENGINEERING DRAFT',font=font(1.65*scale),fill='#e3f4e9',anchor='mm')
 return d

mono=json.loads((D/'mono-layout-v02.json').read_text(encoding='utf-8'))
psu=json.loads((D/'psu-layout-v02.json').read_text(encoding='utf-8'))
for data,scale in [(mono,12),(psu,10)]:
 w,h=data['size'];im=Image.new('RGB',(int(w*scale+160),int(h*scale+260)),'#101c25');d=ImageDraw.Draw(im)
 title='單聲道放大板 / B 方案 V0.2' if data is mono else '雙橋四電容電源板 / B 方案 V0.2'
 d.text((80,25),title,font=font(32),fill='#f1f8f7');d.text((80,72),f'{w} × {h} mm / 頂視，合併顯示兩層銅箔 / 封裝待到料核對',font=font(20),fill='#9bbcbf')
 draw_board(im,data,(80,120),scale)
 star=data['anchors']['STAR'];cx=80+star[0]*scale;cy=120+star[1]*scale
 d.ellipse((cx-6,cy-6,cx+6,cy+6),outline='#fff3aa',width=2)
 d.text((cx+9,cy+9),'GND STAR',font=font(16),fill='#fff3aa')
 y=120+h*scale+28;d.text((80,y),'橘：頂層銅箔　藍：底層銅箔　黃圈：接地匯流點',font=font(20),fill='#bdd1d2')
 d.text((80,y+34),'工程草稿：走線寬度、真實封裝與散熱尚待驗證，不可送板。',font=font(20),fill='#edc178')
 im.save(O/(data['name']+'.png'))
im=Image.new('RGB',(1900,1070),'#101c25');d=ImageDraw.Draw(im)
d.text((60,32),'LM3886 / B 方案 PCB 修訂 V0.2',font=font(44),fill='#f3f8f7')
d.text((60,100),'兩片相同單聲道板 + 一片共用主電源板 / 已訂 IC 與變壓器均在寄送中',font=font(25),fill='#adc7c8')
for data,pos,title in [(mono,(60,210),'左聲道 100 × 90 mm'),(mono,(570,210),'右聲道 100 × 90 mm'),(psu,(1080,210),'主電源 160 × 120 mm')]:
 d.text((pos[0],166),title,font=font(24),fill='#d0e8e4');draw_board(im,data,pos,4.6)
 sx,sy=data['anchors']['STAR'];cx=pos[0]+sx*4.6;cy=pos[1]+sy*4.6
 d.ellipse((cx-5,cy-5,cx+5,cy+5),outline='#fff3aa',width=2)
d.text((60,664),'放大板：右側輸入與回授、左側輸出、下方電源。',font=font(23),fill='#adc7c8')
d.text((60,710),'接地：訊號、喇叭、Zobel、靜音分路回到匯流點。',font=font(23),fill='#adc7c8')
d.text((60,756),'電源板：左側交流／整流，右側直流輸出。',font=font(23),fill='#adc7c8')
d.line((60,826,1840,826),fill='#36565c',width=2)
d.text((60,854),'保留：LM3886T × 2、雙 22Vac 次級、雙橋、每軌 2 × 10,000µF／63V',font=font(26),fill='#a2dfbd')
d.text((60,902),'待確認：所有實體封裝、整流橋與主電容料號、線寬溫升、散熱器與整機線束',font=font(25),fill='#e5c38a')
d.text((60,961),'依 PCB 資料繪製，尺寸為暫定；板間相對位置不代表機殼配置。非製造版本。',font=font(23),fill='#93afb4')
im.save(O/'system-layout-v02.png')
print('Rendered V0.2 PCB data to',O)
