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
for name,title in [('mono-layout-v04c','單聲道放大板 / 方案 C・V0.4 變體 C（改良星型接地）'),('mono-layout-v04d','單聲道放大板 / 方案 C・V0.4 變體 D（底層整面接地）'),('psu-layout-v04','雙橋四電容電源板 / 方案 C・V0.4（每聲道端子＋snubber 預留）')]:
 data=json.loads((D/f'{name}.json').read_text(encoding='utf-8'));scale=10 if name.startswith('psu') else 12
 w,h=data['size'];im=Image.new('RGB',(int(w*scale+160),int(h*scale+260)),'#101c25');d=ImageDraw.Draw(im)
 d.text((80,25),title,font=font(32),fill='#f1f8f7');d.text((80,72),f'{w} × {h} mm / 頂視，合併顯示兩層銅箔 / 封裝沿用 V0.3 暫定外框',font=font(20),fill='#9bbcbf')
 draw_board(im,data,(80,120),scale)
 for key,col in ([] if data.get('zones') else [(k,c) for k,c in [('STAR','#fff3aa'),('SG','#9ad7ff')] if k in data['anchors']]):
  x,y=data['anchors'][key];cx=80+x*scale;cy=120+y*scale
  d.ellipse((cx-6,cy-6,cx+6,cy+6),outline=col,width=2);d.text((cx+9,cy+9),key,font=font(16),fill=col)
 y=120+h*scale+28;d.text((80,y),'橘：頂層銅箔　藍：底層銅箔　暗藍面：底層 GND 鋪銅' if data.get('zones') else ('橘：頂層銅箔　藍：底層銅箔　黃圈：接地匯流點 STAR　藍圈：訊號地 SG' if 'SG' in data['anchors'] else '橘：頂層銅箔　藍：底層銅箔　黃圈：接地匯流點 STAR'),font=font(20),fill='#bdd1d2')
 d.text((80,y+34),'工程草稿：走線寬度、真實封裝與散熱尚待驗證，不可送板。',font=font(20),fill='#edc178')
 im.save(O/(name+'.png'));print('rendered',O/(name+'.png'))

# System view: two variant-D amplifier boards (user's primary choice, 2026-09-24) plus the V0.4 supply.
mono=json.loads((D/'mono-layout-v04d.json').read_text(encoding='utf-8'))
psu=json.loads((D/'psu-layout-v04.json').read_text(encoding='utf-8'))
im=Image.new('RGB',(1900,1070),'#101c25');d=ImageDraw.Draw(im)
d.text((60,32),'LM3886 / 方案 C PCB V0.4（放大板變體 D＋電源板）',font=font(44),fill='#f3f8f7')
d.text((60,100),'兩片相同單聲道板（底層整面接地）+ 一片共用電源板（每聲道一組輸出端子、snubber 預留位）/ 2026-09-24 選定 D 為主、C 保留',font=font(25),fill='#adc7c8')
for data,pos,title in [(mono,(40,210),'左聲道 115 × 90 mm（D）'),(mono,(590,210),'右聲道 115 × 90 mm（D）'),(psu,(1150,210),'主電源 160 × 120 mm')]:
 d.text((pos[0],166),title,font=font(24),fill='#d0e8e4');draw_board(im,data,pos,4.6)
 if not data.get('zones'):
  sx,sy=data['anchors']['STAR'];cx=pos[0]+sx*4.6;cy=pos[1]+sy*4.6;d.ellipse((cx-5,cy-5,cx+5,cy+5),outline='#fff3aa',width=2)
d.text((60,664),'放大板：100n 旁路貼 IC 腳、470µF 在 IC 正下方、底層整面接地；輸出主幹走頂層。',font=font(23),fill='#adc7c8')
d.text((60,710),'電源板：左側交流／整流端子與 snubber 預留位，右側每聲道一組 V+／G／V- 端子。',font=font(23),fill='#adc7c8')
d.text((60,756),'變體 C（星型分路）板檔保留於 pcb/mono-layout-v04c，未實測前不宣稱 C／D 何者較佳。',font=font(23),fill='#adc7c8')
d.line((60,826,1840,826),fill='#36565c',width=2)
d.text((60,854),'保留：LM3886T × 2、雙 22Vac 次級、雙橋、每軌 2 × 10,000µF／63V；電路與零件沿用 V0.3，只改布局。',font=font(26),fill='#a2dfbd')
d.text((60,902),'待確認：LM3886T 實物腳位、線寬溫升、鋪銅與散熱器機構、變壓器振鈴（決定 snubber 值）、整機線束',font=font(25),fill='#e5c38a')
d.text((60,961),'依 PCB 資料繪製，尺寸為暫定；板間相對位置不代表機殼配置。三板 KiCad 10.0.6 DRC 0 違規。非製造版本。',font=font(23),fill='#93afb4')
im.save(O/'system-layout-v04.png');print('rendered',O/'system-layout-v04.png')
