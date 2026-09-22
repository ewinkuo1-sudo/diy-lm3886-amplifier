"""Build Plan C explanatory SVGs from code and native KiCad PDF vectors.

Requires PyMuPDF for the two native schematic guides. PNG conversion is performed
by render_diagrams.cjs (sharp). No electrical design or PCB files are modified.
"""
from pathlib import Path
import hashlib, html, json
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/diagrams'
SRC = OUT / 'svg'
SRC.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, GREEN, RED, PURPLE = '#1763a6', '#ad5800', '#16755a', '#b73940', '#7355a1'
INK, GRAY = '#183447', '#536978'

class SVG:
    def __init__(self,w,h):
        self.w,self.h=w,h
        self.items=[f'<rect width="{w}" height="{h}" fill="#f8fafc"/>']
    def text(self,x,y,s,size=24,color=INK,weight='normal',anchor='start'):
        self.items.append(f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" font-family="Microsoft JhengHei, Noto Sans CJK TC, sans-serif">{html.escape(s)}</text>')
    def line(self,pts,color=BLUE,width=4,dash=False):
        self.items.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in pts)}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"'+(' stroke-dasharray="10 7"' if dash else '')+'/>')
    def rect(self,x,y,w,h,color='#ffffff',stroke='#d0dce5',radius=12):
        self.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{color}" stroke="{stroke}" stroke-width="2"/>')
    def dot(self,x,y,color=BLUE):
        self.items.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{color}"/>')
    def ground(self,x,y,color=GRAY):
        self.line([(x,y),(x,y+12)],color)
        for i,w in enumerate((20,13,6)):self.line([(x-w,y+12+i*8),(x+w,y+12+i*8)],color,3)
    def resistor(self,x,y,label,vertical=False,color=BLUE):
        if vertical:
            self.line([(x,y-40),(x,y-22)],color);self.rect(x-10,y-22,20,44,'#fff',color,0);self.line([(x,y+22),(x,y+40)],color)
            self.text(x+24,y+7,label,23,color)
        else:
            self.line([(x-60,y),(x-35,y)],color);self.rect(x-35,y-10,70,20,'#fff',color,0);self.line([(x+35,y),(x+60,y)],color)
            self.text(x,y-24,label,23,color,anchor='middle')
    def cap(self,x,y,label,vertical=False,color=BLUE,plus=False):
        if vertical:
            self.line([(x,y-35),(x,y-7)],color);self.line([(x-19,y-7),(x+19,y-7)],color)
            self.line([(x-19,y+7),(x+19,y+7)],color);self.line([(x,y+7),(x,y+35)],color)
            self.text(x+27,y+7,label,22,color)
            if plus:self.text(x-36,y-13,'+',23,color)
        else:
            self.line([(x-45,y),(x-7,y)],color);self.line([(x-7,y-23),(x-7,y+23)],color)
            self.line([(x+7,y-23),(x+7,y+23)],color);self.line([(x+7,y),(x+45,y)],color)
            self.text(x,y-38,label,23,color,anchor='middle')
    def panel(self,x,y,w,title,lines,color=BLUE):
        self.rect(x,y,w,64+len(lines)*35,'#fff',color)
        self.text(x+22,y+38,title,27,color,'bold')
        for i,s in enumerate(lines):self.text(x+22,y+77+i*35,s,23)
    def header(self,title,sub):
        self.rect(0,0,self.w,135,'#183447','#183447',0)
        self.text(45,55,title,38,'white','bold');self.text(45,103,sub,23,'#dbe8f0')
    def footer(self,s):
        self.text(45,self.h-52,s,21,GRAY)
        self.text(45,self.h-20,'方案 C V0.3  •  2026-09-22  •  工程草稿／無硬體量測  •  docs/diagrams/README.md',19,GRAY)
    def save(self,name):
        (SRC/(name+'.svg')).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'+''.join(self.items)+'</svg>',encoding='utf-8')

def signal(mode='all'):
    d=SVG(1800,870)
    d.text(80,65,'左聲道 U1；右聲道 U2 相同，R/C 編號加 100，L1→L2、J1/J2→J3/J4。',25)
    d.rect(800,160,230,310,'#fff0f0',RED)
    d.text(915,217,'U1 LM3886T',29,RED,'bold','middle')
    d.text(818,268,'10  +IN',24,RED);d.text(818,365,'9   −IN',24,RED)
    d.text(1008,309,'3 OUT',24,RED,anchor='end')
    d.text(818,440,'7 GND',23,RED);d.text(1008,440,'4 VEE',23,RED,anchor='end')
    d.text(915,135,'1、5 → VCC',24,RED,anchor='middle')
    d.text(915,500,'8 MUTE → 見電源／靜音圖',22,PURPLE,anchor='middle')
    input_start=len(d.items)
    d.line([(100,260),(305,260)]);d.text(80,210,'J1.1 RCA',25,BLUE)
    d.cap(350,260,'C1 2.2µF / 100V')
    d.line([(395,260),(460,260)]);d.resistor(520,260,'R6 1kΩ')
    d.line([(580,260),(800,260)])
    for x,label in [(200,'R1 1MΩ'),(675,'R2 22kΩ')]:
        d.dot(x,260);d.line([(x,260),(x,345)]);d.resistor(x,385,label if x==200 else '',True);d.line([(x,425),(x,460)]);d.ground(x,460)
    d.text(640,445,'R2 22kΩ',23,BLUE,anchor='end')
    d.text(80,540,'J1.2 → 訊號地',23,GRAY)
    if mode=='output':
        d.items=d.items[:input_start]
        d.line([(700,260),(800,260)])
        d.text(700,240,'來自輸入級',22,BLUE)
    d.line([(800,360),(745,360),(745,565),(890,565)],ORANGE)
    d.resistor(950,565,'R4 20kΩ / 1%',color=ORANGE)
    d.line([(1010,565),(1140,565),(1140,300)],ORANGE)
    d.dot(745,565,ORANGE);d.line([(745,565),(745,615)],ORANGE)
    d.resistor(745,655,'R3 1kΩ / 1%',True,ORANGE)
    d.line([(745,695),(745,705)],ORANGE);d.cap(745,740,'C2 47µF / 63V 無極性',True,ORANGE)
    d.ground(745,775,ORANGE)
    output_start=len(d.items)
    d.line([(1030,300),(1370,300)],GREEN);d.dot(1140,300,GREEN)
    d.dot(1240,300,GREEN);d.line([(1240,300),(1240,365)],GREEN)
    d.resistor(1240,405,'R5 2.7Ω / 2W',True,GREEN)
    d.line([(1240,445),(1240,485)],GREEN);d.cap(1240,520,'C5 100nF / 100V',True,GREEN);d.ground(1240,555,GREEN)
    # L1 and R7 have the same two endpoints: they are in parallel.
    d.items.append('<path d="M 1395 300 '+' '.join('a 15 20 0 0 1 30 0' for _ in range(4))+f'" fill="none" stroke="{GREEN}" stroke-width="4"/>')
    d.line([(1370,300),(1395,300)],GREEN);d.line([(1515,300),(1660,300)],GREEN)
    d.text(1455,354,'L1 0.7µH',24,GREEN,anchor='middle')
    d.line([(1370,300),(1370,205),(1395,205)],GREEN)
    d.resistor(1455,205,'R7 10Ω / 2W',color=GREEN)
    d.line([(1515,205),(1540,205),(1540,300)],GREEN)
    d.dot(1370,300,GREEN);d.dot(1540,300,GREEN)
    d.text(1570,265,'J2.1 TEST OUT',23,GREEN)
    d.text(1550,410,'8Ω 假負載',26,GREEN)
    d.resistor(1660,460,'',True,GREEN);d.line([(1660,300),(1660,420)],GREEN);d.line([(1660,500),(1660,560)],GREEN);d.ground(1660,560,GREEN)
    d.text(1500,615,'J2.2 → 負載回地',23,GREEN)
    if mode=='input':
        d.items=d.items[:output_start]
        d.line([(1030,300),(1140,300)],GREEN)
        d.dot(1140,300,GREEN)
        d.text(1080,265,'至輸出級',22,GREEN,anchor='middle')
    if mode!='output':
        d.panel(70,620,550,'回授重點',['R4 由 IC pin 3 取樣，位於 L1 之前。','pin 9 → R3 → C2 → GND：兩者串聯。','IC 中頻增益 21 倍；直流增益約 1 倍。'],ORANGE)
    if mode!='input':
        d.panel(1120,680,610,'輸出重點',['R5 與 C5 串聯到地，是 Zobel 網路。','L1 與 R7 並聯後串入輸出，不是 DC 保護。'],GREEN)
    return d

def embed(d,other,x,y,w,h,view=None):
    d.items.append(f'<svg x="{x}" y="{y}" width="{w}" height="{h}" overflow="hidden" viewBox="{view or f"0 0 {other.w} {other.h}"}">'+''.join(other.items)+'</svg>')

def supply(d,y=0):
    # Exact dual-bridge topology; no AC connection between the isolated windings.
    for i,cy in enumerate((300+y,700+y)):
        d.rect(65,cy-35,230,160,'#fff6e9',ORANGE)
        d.text(85,cy+4,f'T1 獨立次級 {i+1}',25,ORANGE,'bold')
        d.text(85,cy+50,'22Vac（浮接）',25,ORANGE)
        d.line([(295,cy),(345,cy)],ORANGE);d.resistor(405,cy,f'F{201+i} 待定',color=ORANGE)
        d.line([(465,cy),(540,cy)],ORANGE);d.line([(295,cy+95),(540,cy+95)],ORANGE)
        d.rect(540,cy-30,200,155,'#fff',ORANGE)
        d.text(560,cy+10,'~',28,ORANGE);d.text(560,cy+105,'~',28,ORANGE)
        d.text(642,cy+60,f'BR{i+1}',29,ORANGE,'bold','middle')
        d.text(710,cy+10,'+',27,ORANGE);d.text(710,cy+105,'−',27,ORANGE)
    d.line([(740,300+y),(1510,300+y)],RED)
    d.line([(740,395+y),(870,395+y),(870,580+y)],GRAY)
    d.line([(740,700+y),(870,700+y),(870,580+y),(1510,580+y)],GRAY)
    d.dot(870,580+y,GRAY);d.text(1525,625+y,'GND = BR1− 與 BR2+',22,GRAY);d.text(1525,655+y,'的 DC 中點',22,GRAY)
    d.line([(740,795+y),(1510,795+y)],BLUE)
    for x,labels in [(1020,('C201','C203')),(1290,('C202','C204'))]:
        for yy,a,b,label,col in [(440+y,300+y,580+y,labels[0],RED),(680+y,580+y,795+y,labels[1],BLUE)]:
            d.line([(x,a),(x,yy-35)],col);d.cap(x,yy,label,True,col,True);d.line([(x,yy+35),(x,b)],col)
            d.dot(x,a,col);d.dot(x,b,GRAY if b==580+y else BLUE)
    d.text(1525,308+y,'VCC',28,RED,'bold');d.text(1525,588+y,'GND',28,GRAY,'bold');d.text(1525,803+y,'VEE',28,BLUE,'bold')
    d.text(965,220+y,'C201–C204：各 10,000µF / 63V',27)
    d.text(965,255+y,'每軌兩顆並聯 = 20,000µF',26)
    d.text(65,920+y,'AC 次級彼此不相接；只在橋後 DC 端形成共同中點。負軌電容正端接 GND。',25,ORANGE)

def build():
    base=signal()
    d=SVG(1800,1510);d.header('LM3886｜完整電路導讀（單聲道）','雙聲道成機使用兩套相同放大電路，共用方案 C 次級電源。')
    embed(d,base,0,150,1800,870)
    d.panel(45,1050,820,'共用電源：雙橋、四顆主濾波電容',['獨立 22Vac 次級 1 → BR1：+ 接 VCC，− 接 GND。','獨立 22Vac 次級 2 → BR2：+ 接 GND，− 接 VEE。','C201/C202 接 VCC–GND；C203/C204 接 GND–VEE。','四顆各 10,000µF / 63V，每軌 20,000µF。','J203 的 1/2/3 → 放大板 J5 的 1/2/3。'],ORANGE)
    d.panel(905,1050,850,'供電、靜音與整機邊界',['VCC → pin 1、5；VEE → pin 4；GND → pin 7。','各軌具 100nF + 470µF 局部去耦，詳電源→IC 圖。','pin 8 → R8 22kΩ → JP1 → VEE；C8 正端接 GND。','成機：TEST OUT → 待設計 DC 保護／繼電器 → 喇叭。','約 ±30V 等級；30–40W/8Ω 為探索範圍，非額定。'],PURPLE)
    d.footer('此圖為分區導讀；未畫出全部供電支路，完整接線以兩份 KiCad 原理圖為準。');d.save('lm3886_complete')
    d=SVG(1800,1200);d.header('LM3886｜輸入級與回授網路','元件編號與 V0.3 KiCad 一致；圖示左聲道，音量由 Eversolo DAC-Z10 控制。')
    embed(d,signal('input'),50,155,1700,800,'40 85 1140 760')
    d.panel(50,990,1700,'讀圖重點',['C1 隔直；R1 位於 C1 前，R2 位於 R6 後。回授 R4 接 IC 輸出，R3 與 C2 串聯到地。','IC 中頻增益 = 1 + 20k/1k = 21；含 R6/R2 衰減約 20.09 倍（未計前級輸出阻抗）。'],ORANGE)
    d.footer('詳細輸出穩定網路見 IC→輸出級圖；供電與靜音見電源→IC 圖。');d.save('lm3886_input_stage')
    d=SVG(1800,1190);d.header('LM3886｜IC 到輸出級','Zobel 與輸出隔離網路不等於喇叭 DC 保護；目前輸出端供假負載測試。')
    embed(d,signal('output'),25,160,1750,790,'680 85 1100 760')
    d.panel(50,980,1700,'PCB V0.3 對應',['R4 由 U1.3 獨立取樣；主輸出改 B.Cu。回授位於 L1/R7 之前，元件值與網路未改。','成機需另加 DC 偵測、延遲接通與掉電斷開控制；目前不能把 TEST OUT 當完成保護的喇叭端。'],GREEN)
    d.footer('實際 PCB 走線與剩餘問題見 pcb/README.md；此圖不是走線施工圖。');d.save('lm3886_ic_to_output')
    d=SVG(1800,1860);d.header('LM3886｜電源級到 IC','雙獨立 22Vac 次級各接全橋；12Vac 輔助繞組留供控制，模組輸入與電流待定。')
    supply(d)
    d.panel(50,980,815,'PSU → 放大板線束',['J203.1 → J5.1 VCC → U1/U2 pin 1、5。','J203.2 → J5.2 GND → U1/U2 pin 7 及各回地。','J203.3 → J5.3 VEE → U1/U2 pin 4。','兩份原理圖靠實體線束相接，同名標籤不跨檔接線。','R201/R202 各 2.2kΩ / 2W，分別跨正／負軌。','C205/C206 各 100nF / 100V，分別跨正／負軌。'],BLUE)
    d.panel(905,980,845,'局部去耦（左聲道，右聲道編號 +100）',['VCC–GND：C3 100nF / 100V；C7 470µF / 63V。','GND–VEE：C4 100nF / 100V；C6 470µF / 63V。','C7 正端接 VCC；C6 正端接 GND。','PCB V0.3：C3/C4 地端在 IC 附近回 pin 7，','再由局部去耦支路回匯流區；訊號地另走支路。','GND 網名不表示各路電流應共用同一段細線。'],GREEN)
    d.panel(50,1290,815,'靜音支路（左聲道）',['pin 8 → R8 22kΩ / 0.6W → JP1 → VEE。','C8 100µF / 100V：正端 GND，負端 pin 8。','JP1 閉合 RUN；開路 MUTE。右聲道為 JP2。','這是板級測試跳線；自動啟停／掉電控制待設計。'],PURPLE)
    d.panel(905,1290,845,'供電條件與選型狀態',['22×√2 − 2×1.1 ≈ 28.9V／軌：未扣紋波／下陷。','35.8V／軌是高市電空載假設，非最大電壓保證。','變壓器、IC、全部 R／C 已下單待到貨（9/16、9/20）。','橋堆、保險絲、電感、接頭、浪湧控制及散熱未購／未定案。'],ORANGE)
    d.panel(50,1540,1700,'機構與整機保護',['LM3886T 背板接 VEE，與接地機殼／散熱器間須具電氣絕緣；pin 2、6、11 為 NC。','保護接地 PE 的機殼連接不可由訊號 GND 替代；本圖僅次級與放大板導讀，一次側接線另行設計。'],RED)
    d.footer('四顆主電容 CDE 381LX 已購待到貨；兩顆橋堆未購、未指定 KBPC2510，未宣稱實際輸出額定。');d.save('lm3886_power_to_ic')
    annotated('lm3886-v01','lm3886_sch_annotated',False)
    annotated('internal-psu-v02','lm3886_psu_sch_annotated',True)
    # .kicad_sch files carry fresh UUIDs on every rebuild, so their hashes are not reproducible; bind generators and exported PDFs only.
    sources=['tools/build_schematic.py','tools/build_power_supply.py','tools/build_diagrams.py','electrical/preview/lm3886-v01.pdf','electrical/preview/internal-psu-v02.pdf']
    def digest(p):
        b=(ROOT/p).read_bytes()
        if p.endswith('.py'): b=b.replace(b'\r\n',b'\n')  # LF-normalise text so Windows autocrlf checkouts match the repository hash
        return hashlib.sha256(b).hexdigest()
    (OUT/'sources.json').write_text(json.dumps({'version':'Plan C V0.3','updated':'2026-09-22','note':'kicad_sch and pcb/README.md removed from binding: sch UUIDs change per rebuild, README changes independently of the diagrams. Text sources hashed LF-normalised.','sha256':{p:digest(p) for p in sources}},indent=2,ensure_ascii=False),encoding='utf-8')

def annotated(source,name,psu):
    d=SVG(2200,1940)
    d.header('LM3886｜'+('電源次級原理圖色塊導讀' if psu else '雙聲道放大板原理圖色塊導讀'),'底圖直接取自現行 KiCad V0.3 向量 PDF；彩色框為功能區域，不代表額外接線。')
    doc=fitz.open(ROOT/f'electrical/preview/{source}.pdf');page=doc[0]
    raw=page.get_svg_image(text_as_path=True)
    # Nested native SVG preserves all original text, wires, symbols and title block.
    import re
    raw=re.sub(r'<svg\b', '<svg x="40" y="155"',raw,count=1)
    raw=re.sub(r'width="[^"]+"','width="2120"',raw,count=1)
    raw=re.sub(r'height="[^"]+"','height="1500"',raw,count=1)
    d.items.append(raw)
    def region(x,y,w,h,col):
        d.items.append(f'<rect x="{40+x*2120}" y="{155+y*1500}" width="{w*2120}" height="{h*1500}" fill="{col}" fill-opacity="0.045" stroke="{col}" stroke-width="4" rx="8"/>')
    if psu:
        region(.05,.17,.41,.56,ORANGE);region(.47,.18,.36,.55,GREEN);region(.85,.39,.10,.16,BLUE)
        d.panel(40,1680,670,'橙框｜雙橋整流',['兩組獨立 22Vac 分別進 BR1／BR2。','AC 不互接；BR1− 與 BR2+ 接 GND。'],ORANGE)
        d.panel(765,1680,670,'綠框｜濾波、洩放',['C201–C204 各 10,000µF / 63V。','負軌電容正端朝 GND；每軌 20,000µF。'],GREEN)
        d.panel(1490,1680,670,'藍框｜輸出線束',['J203.1/2/3 → 放大板 J5.1/2/3。','VCC／GND／VEE；橋堆、保險絲、接頭仍待購。'],BLUE)
    else:
        for y in (.17,.51):
            region(.05,y,.36,.16,BLUE);region(.31,y+.135,.14,.185,ORANGE);region(.435,y-.025,.16,.275,GREEN);region(.63,y,.28,.32,PURPLE)
        d.panel(40,1680,500,'藍／橙框｜輸入與回授',['R6 為 1kΩ 串阻；R4 為 20kΩ。','R3 與 C2 串聯，右聲道編號 +100。'],BLUE)
        d.panel(580,1680,760,'綠框｜輸出穩定網路',['R5+C5 串聯到地；L1∥R7 串在輸出。','TEST OUT 供假負載，喇叭 DC 保護仍待設計。'],GREEN)
        d.panel(1380,1680,780,'紫框｜去耦與靜音',['負軌 C6、靜音 C8 的正端接 GND。','PCB V0.3 縮短 C3/C4 回 pin 7 路徑，網路未改。'],PURPLE)
    d.footer('來源：electrical/preview/'+source+'.pdf（2026-09-16 重建）；底圖內耐壓值與採購註記待 KiCad 重建後更新。');d.save(name)
    doc.close()

if __name__=='__main__':
    build()
    print('Built six SVG guides and source hashes.')
