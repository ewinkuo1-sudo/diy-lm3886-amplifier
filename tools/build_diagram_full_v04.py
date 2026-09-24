"""One-channel, fully wired schematic guide for PCB V0.4 (amplifier board D + shared PSU).

Every connection is drawn as a wire (no net labels); reference designators are the ones printed on the
boards, so each symbol can be found on pcb/inspection-v04 drawings. Values come from electrical/*.kicad_sch.
Pure drawing script: reuses the SVG helpers from build_diagrams.py, writes docs/diagrams/svg/lm3886_full_v04.svg
and renders the PNG with PyMuPDF. No electrical or PCB file is modified.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_diagrams import SVG,BLUE,ORANGE,GREEN,RED,PURPLE,INK,GRAY,OUT,SRC
import pymupdf

TEAL='#0f7f8a'
W,H=2750,1980
d=SVG(W,H)
d.header('LM3886｜單聲道完整接線圖（PCB V0.4：放大板 D＋共用電源板）','每條線都畫出、沒有網路標籤；元件編號與板上絲印相同。右聲道放大板同圖，原理圖編號加 100（U2、R101…、J3/J4、JP2）。')

# ---------- board frames ----------
d.rect(40,165,W-80,960,'#fbfdff','#9fb6c4');d.text(60,200,'放大板 mono-layout-v04d（每聲道一片，115 × 90 mm）',27,INK,'bold')
d.rect(40,1160,W-80,700,'#fffaf3','#d2b48c');d.text(440,1195,'電源板 psu-layout-v04（兩聲道共用，160 × 120 mm）',27,ORANGE,'bold')

# ---------- rails ----------
VCC_Y,VEE_Y,GNDL_Y=290,1040,760
d.line([(640,VCC_Y),(2600,VCC_Y)],RED,5);d.text(2612,VCC_Y+9,'V+',26,RED,'bold')
d.line([(640,VEE_Y),(2600,VEE_Y)],BLUE,5);d.text(2612,VEE_Y+9,'V−',26,BLUE,'bold')

# ---------- U1 ----------
IX0,IX1,IY0,IY1=1180,1430,420,760
d.rect(IX0,IY0,IX1-IX0,IY1-IY0,'#fff0f0',RED,10)
d.text((IX0+IX1)/2,IY0+45,'U1 LM3886T',30,RED,'bold','middle')
d.text((IX0+IX1)/2,IY1-22,'背板 = V−，對散熱器絕緣',18,RED,anchor='middle')
def pin(x,y,num,name,side):
    d.text(x+(12 if side=='L' else -12),y+7,f'{num} {name}',22,RED,anchor='start' if side=='L' else 'end')
PLUS_Y,OUT_Y,INV_Y=540,500,640
pin(IX0,PLUS_Y,'10','+IN','L');pin(IX1,OUT_Y,'3','OUT','R');pin(IX1,INV_Y,'9','−IN','R')
for x,n in [(1240,'1'),(1320,'5')]:
    d.line([(x,IY0),(x,VCC_Y)],RED);d.text(x+8,IY0-10,n,20,RED)
d.text(1280,VCC_Y-14,'1、5 → V+',22,RED,anchor='middle')
MX,GX,VX=IX0+45,IX0+125,IX0+210
d.line([(GX,IY1),(GX,IY1+50)],GRAY);d.ground(GX,IY1+50);d.text(GX+14,IY1+30,'7 GND',20,RED)
d.line([(VX,IY1),(VX,VEE_Y)],BLUE);d.text(VX+12,IY1+30,'4 V−',20,RED);d.dot(VX,VEE_Y,BLUE)
MUTE_Y=830
d.line([(MX,IY1),(MX,MUTE_Y),(880,MUTE_Y)],PURPLE);d.text(MX-12,IY1+30,'8 MUTE',20,PURPLE,anchor='end')

# ---------- input network ----------
JX=700
d.rect(JX,PLUS_Y-40,70,110,'#fff',TEAL);d.text(JX+35,PLUS_Y-50,'J1 RCA',22,TEAL,anchor='middle')
d.text(JX+15,PLUS_Y+8,'1',20,TEAL);d.text(JX+15,PLUS_Y+62,'2',20,TEAL)
d.line([(JX+70,PLUS_Y),(860,PLUS_Y)],BLUE);d.dot(860,PLUS_Y)
d.cap(920,PLUS_Y,'C1 2.2µF / 100V');d.line([(965,PLUS_Y),(990,PLUS_Y)],BLUE)
d.resistor(1050,PLUS_Y,'R6 1kΩ');d.line([(1110,PLUS_Y),(IX0,PLUS_Y)],BLUE);d.dot(1140,PLUS_Y)
for x,label in [(860,'R1 1MΩ'),(1140,'R2 22kΩ')]:
    d.line([(x,PLUS_Y),(x,PLUS_Y+60)]);d.resistor(x,PLUS_Y+100,label,True);d.line([(x,PLUS_Y+140),(x,PLUS_Y+170)]);d.ground(x,PLUS_Y+170)
d.line([(JX+70,PLUS_Y+55),(810,PLUS_Y+55),(810,PLUS_Y+110)],GRAY);d.ground(810,PLUS_Y+110)
d.text(JX-10,PLUS_Y+150,'J1.2 訊號地',20,GRAY)

# ---------- feedback ----------
d.line([(IX1,OUT_Y),(1820,OUT_Y)],GREEN,5)
FBX=1660
d.dot(FBX,OUT_Y,GREEN);d.line([(FBX,OUT_Y),(FBX,INV_Y)],ORANGE)
d.line([(IX1,INV_Y),(1540,INV_Y)],ORANGE);d.resistor(1600,INV_Y,'R4 20kΩ / 1%',color=ORANGE)
d.dot(1500,INV_Y,ORANGE);d.line([(1500,INV_Y),(1500,INV_Y+50)],ORANGE)
d.resistor(1500,INV_Y+90,'R3 1kΩ / 1%',True,ORANGE);d.line([(1500,INV_Y+130),(1500,INV_Y+160)],ORANGE)
d.cap(1500,INV_Y+195,'C2 47µF / 63V 無極性',True,ORANGE);d.line([(1500,INV_Y+230),(1500,INV_Y+260)],ORANGE);d.ground(1500,INV_Y+260,ORANGE)
d.text(1440,INV_Y+330,'回授：R4 由 pin 3 取樣；R3 與 C2 串聯到地。增益 1+20k/1k = 21',19,ORANGE)

# ---------- Zobel and output network ----------
ZX=1760
d.dot(ZX,OUT_Y,GREEN);d.line([(ZX,OUT_Y),(ZX,OUT_Y+60)],GREEN);d.resistor(ZX,OUT_Y+100,'R5 2.7Ω / 2W',True,GREEN)
d.line([(ZX,OUT_Y+140),(ZX,OUT_Y+170)],GREEN);d.cap(ZX,OUT_Y+205,'C5 100nF / 100V',True,GREEN);d.line([(ZX,OUT_Y+240),(ZX,OUT_Y+270)],GREEN);d.ground(ZX,OUT_Y+270,GREEN)
d.text(ZX+30,OUT_Y+330,'Zobel',19,GREEN)
LX0=1880
d.dot(1820,OUT_Y,GREEN);d.line([(1820,OUT_Y),(LX0,OUT_Y)],GREEN,5)
d.items.append(f'<path d="M {LX0} {OUT_Y} '+' '.join('a 15 20 0 0 1 30 0' for _ in range(4))+f'" fill="none" stroke="{GREEN}" stroke-width="4"/>')
d.text(LX0+60,OUT_Y+52,'L1 0.7µH',22,GREEN,anchor='middle')
d.line([(1820,OUT_Y),(1820,OUT_Y-90),(1880,OUT_Y-90)],GREEN);d.resistor(1940,OUT_Y-90,'R7 10Ω / 2W',color=GREEN);d.line([(2000,OUT_Y-90),(2060,OUT_Y-90),(2060,OUT_Y)],GREEN)
d.line([(LX0+120,OUT_Y),(2160,OUT_Y)],GREEN,5);d.dot(2060,OUT_Y,GREEN)
d.rect(2160,OUT_Y-40,70,110,'#fff',TEAL);d.text(2195,OUT_Y-50,'J2 TEST OUT',22,TEAL,anchor='middle')
d.text(2175,OUT_Y+8,'1',20,TEAL);d.text(2175,OUT_Y+62,'2',20,TEAL)
d.line([(2230,OUT_Y+55),(2280,OUT_Y+55),(2280,OUT_Y+110)],GRAY);d.ground(2280,OUT_Y+110)
d.text(2200,OUT_Y+175,'J2.2 喇叭回地',20,GRAY)
d.text(2110,OUT_Y-130,'→ 假負載／（待設計）保護板 → 喇叭',20,GREEN)
d.text(LX0+60,OUT_Y+82,'L1∥R7 串在輸出上，不是 DC 保護',19,GREEN,anchor='middle')

# ---------- local decoupling column ----------
d.line([(2360,GNDL_Y),(2560,GNDL_Y)],GRAY,4);d.ground(2560,GNDL_Y);d.text(2360,GNDL_Y-14,'局部去耦地',20,GRAY)
for x,label,plus in [(2390,'C3 100nF',False),(2540,'C7 470µF / 63V',True)]:
    d.dot(x,VCC_Y,RED);d.line([(x,VCC_Y),(x,520)],RED);d.cap(x,555,'' if x==2390 else label,True,RED,plus);d.line([(x,590),(x,GNDL_Y)],RED);d.dot(x,GNDL_Y,GRAY)
    if x==2390:d.text(x-27,562,label,22,RED,anchor='end')
for x,label,plus in [(2390,'C4 100nF',False),(2540,'C6 470µF / 63V',True)]:
    d.line([(x,GNDL_Y),(x,865)],BLUE);d.cap(x,900,'' if x==2390 else label,True,BLUE,plus);d.line([(x,935),(x,VEE_Y)],BLUE);d.dot(x,VEE_Y,BLUE)
    if x==2390:d.text(x-27,907,label,22,BLUE,anchor='end')
d.text(2300,650,'C3/C4 為 100V 薄膜',19,GRAY);d.text(2300,1000,'C7 正端接 V+；C6 正端接 GND',19,GRAY)
d.text(1500,1100,'PCB：C3 跨 pin 5–7、C4 跨 pin 4–7；C6/C7 在 IC 正下方，都在放大板上。',20,GRAY)

# ---------- mute ----------
d.dot(880,MUTE_Y,PURPLE)
d.line([(880,MUTE_Y),(880,MUTE_Y+40)],PURPLE);d.resistor(880,MUTE_Y+80,'R8 22kΩ / 0.6W',True,PURPLE);d.line([(880,MUTE_Y+120),(880,MUTE_Y+140)],PURPLE)
d.rect(860,MUTE_Y+140,40,40,'#fff',PURPLE,4);d.text(910,MUTE_Y+168,'JP1 RUN 跳線：閉合＝播放，開路＝靜音',20,PURPLE)
d.line([(880,MUTE_Y+180),(880,VEE_Y)],PURPLE);d.dot(880,VEE_Y,BLUE)
d.line([(880,MUTE_Y),(790,MUTE_Y)],PURPLE);d.cap(745,MUTE_Y,'C8 100µF / 100V',color=PURPLE)
d.text(690,MUTE_Y-18,'+',22,PURPLE);d.line([(700,MUTE_Y),(680,MUTE_Y),(680,MUTE_Y+40)],GRAY);d.ground(680,MUTE_Y+40)
d.text(690,MUTE_Y+45,'C8 正端在 GND、負端在 pin 8',19,GRAY)

# ---------- J5 power input ----------
d.rect(400,860,90,150,'#fff',TEAL);d.text(445,848,'J5 電源入',22,TEAL,anchor='middle')
for y,name in [(890,'1 V+'),(935,'2 GND'),(980,'3 V−')]:
    d.text(410,y+7,name,20,TEAL)
d.line([(490,890),(640,890),(640,VCC_Y)],RED,5);d.dot(640,VCC_Y,RED)
d.line([(490,935),(560,935),(560,990)],GRAY,4);d.ground(560,990);d.text(500,1035,'J5.2 電源地',19,GRAY)
d.line([(490,980),(640,980),(640,VEE_Y)],BLUE,5);d.dot(640,VEE_Y,BLUE)
d.text(60,1100,'圖上所有接地符號在板上都是同一個 GND 網路：變體 D 以底層整面鋪銅相連；變體 C 各自拉線回 STAR。此圖是接線圖，不是走線圖。',20,GRAY)

# ---------- harness J5 <- J203 ----------
HX=2330;PY=1440
for i,(y,col) in enumerate([(890,RED),(935,GRAY),(980,BLUE)]):
    xx=300+30*i
    d.line([(400,y),(xx,y),(xx,1290+30*i),(HX-30*i-60,1290+30*i),(HX-30*i-60,PY-100+30*i),(HX,PY-100+30*i)],col,4,True)
d.text(400,1275,'三線束（同色虛線）：J203.1/2/3 → J5.1/2/3',21,INK)

# ---------- PSU ----------
rows=[(PY,'J201','F201','BR1','C201','C202','R201','C205','C207','C208','R203',RED,GRAY),
      (PY+220,'J202','F202','BR2','C203','C204','R202','C206','C209','C210','R204',GRAY,BLUE)]
for i,(cy,jref,fref,bref,ca,cb,rref,cf,cx,cs,rs,col_top,col_bot) in enumerate(rows):
    body=col_top if col_top!=GRAY else BLUE
    d.rect(70,cy-30,150,110,'#fff6e9',ORANGE);d.text(80,cy+5,jref,22,ORANGE,'bold');d.text(80,cy+35,'T1 22Vac',20,ORANGE);d.text(80,cy+62,'次級 '+str(i+1),20,ORANGE)
    d.line([(220,cy),(310,cy)],ORANGE);d.resistor(370,cy,fref+' 保險絲',color=ORANGE);d.line([(430,cy),(560,cy)],ORANGE)
    d.line([(220,cy+60),(560,cy+60)],ORANGE)
    sx=270;d.dot(sx,cy,ORANGE);d.dot(sx,cy+60,ORANGE)
    d.line([(sx,cy),(sx,cy+14)],ORANGE);d.items.append(f'<line x1="{sx-12}" y1="{cy+22}" x2="{sx+12}" y2="{cy+22}" stroke="{ORANGE}" stroke-width="3"/><line x1="{sx-12}" y1="{cy+32}" x2="{sx+12}" y2="{cy+32}" stroke="{ORANGE}" stroke-width="3"/>');d.line([(sx,cy+40),(sx,cy+60)],ORANGE)
    d.text(sx+16,cy+32,cx,17,ORANGE)
    d.text(230,cy+120,f'{cx} 與 {cs}+{rs} 並聯於繞組兩端（保險絲前）：snubber 預留位，只留孔不填料',17,ORANGE)
    d.rect(560,cy-30,130,120,'#fff',ORANGE);d.text(625,cy+38,bref,26,ORANGE,'bold','middle')
    d.text(572,cy+7,'AC1',16,ORANGE);d.text(572,cy+67,'AC2',16,ORANGE);d.text(688,cy+7,'P',16,ORANGE,anchor='end');d.text(688,cy+67,'N',16,ORANGE,anchor='end')
    d.text(625,cy-40,'4 位端子 ← KBPC2510 鎖機殼，四條 Faston 線',16,ORANGE,anchor='middle')
    d.line([(690,cy),(1900,cy)],col_top,5);d.line([(690,cy+60),(1900,cy+60)],col_bot,5)
    for x,label in [(900,ca),(1120,cb)]:
        d.line([(x,cy),(x,cy+5)],body);d.cap(x,cy+30,label,True,body,True);d.dot(x,cy,col_top);d.dot(x,cy+60,col_bot)
    d.text(1010,cy+100,'各 10,000µF / 63V',18,body,anchor='middle')
    d.resistor(1400,cy+30,rref+' 2.2kΩ / 2W',True,body);d.dot(1400,cy,col_top);d.dot(1400,cy+60,col_bot)
    d.text(1400,cy+100,'洩放',18,body,anchor='middle')
    d.cap(1680,cy+30,cf+' 100nF',True,body);d.dot(1680,cy,col_top);d.dot(1680,cy+60,col_bot)
d.line([(1900,PY+60),(1900,PY+220)],GRAY,5);d.text(1915,PY+190,'BR1 N 與 BR2 P 相接 = GND（STAR 在端子旁）',19,GRAY)
# J203 fully wired; J204 is the same three nets in parallel
d.rect(HX,PY-130,90,120,'#fff',TEAL);d.text(HX+45,PY-140,'J203',22,TEAL,anchor='middle');d.text(HX+45,PY+16,'→ 左聲道 J5',18,TEAL,anchor='middle')
d.text(HX+12,PY-92,'1 V+',18,TEAL);d.text(HX+12,PY-62,'2 GND',18,TEAL);d.text(HX+12,PY-32,'3 V−',18,TEAL)
d.line([(1900,PY),(2200,PY),(2200,PY-100),(HX,PY-100)],RED,5);d.dot(2200,PY,RED)
d.line([(1900,PY+140),(2240,PY+140),(2240,PY-70),(HX,PY-70)],GRAY,5);d.dot(1900,PY+140,GRAY)
d.line([(1900,PY+280),(2280,PY+280),(2280,PY-40),(HX,PY-40)],BLUE,5)
d.rect(HX+130,PY-130,90,120,'#fff',TEAL);d.text(HX+175,PY-140,'J204',22,TEAL,anchor='middle');d.text(HX+175,PY+16,'→ 右聲道 J5',18,TEAL,anchor='middle')
d.text(HX+142,PY-92,'1 V+',18,TEAL);d.text(HX+142,PY-62,'2 GND',18,TEAL);d.text(HX+142,PY-32,'3 V−',18,TEAL)
d.text(HX+110,PY+50,'J204 與 J203 三腳並聯（同一 V+／GND／V−），各自一組端子',18,TEAL,anchor='middle')
d.text(70,PY+385,'每軌 2 × 10,000µF = 20,000µF；C201/C202 正端接 V+，C203/C204 正端接 GND。約 ±30V 等級、非額定；一次側、保險絲值與變壓器繞組電流待實測。',20,ORANGE)

d.footer('依 electrical/lm3886-v01.kicad_sch、internal-psu-v02.kicad_sch 與 pcb/mono-layout-v04d、psu-layout-v04 繪製；元件值以 KiCad 原理圖為準。')
d.items=[s.replace('方案 C V0.3  •  2026-09-22','方案 C PCB V0.4  •  2026-09-24') for s in d.items]
d.save('lm3886_full_v04')
doc=pymupdf.open(str(SRC/'lm3886_full_v04.svg'));pix=doc[0].get_pixmap(dpi=108,alpha=False);pix.save(str(OUT/'lm3886_full_v04.png'))
print('lm3886_full_v04',pix.width,pix.height)
