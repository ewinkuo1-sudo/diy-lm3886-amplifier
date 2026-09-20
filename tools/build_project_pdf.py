"""Build current Plan C PDFs. Requires reportlab, pypdf and a CJK TTF/TTC font.
Run after tools/rebuild.py. Set LM3886_FONT for non-Windows environments.
"""
from pathlib import Path
import os,re,csv,html
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,KeepTogether,KeepInFrame
from reportlab.graphics.shapes import Drawing,Rect,String,Line,Polygon
from pypdf import PdfReader,PdfWriter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf'; OUT.mkdir(parents=True,exist_ok=True)
TMP=ROOT/'tmp/pdfs'; TMP.mkdir(parents=True,exist_ok=True)
font=os.environ.get('LM3886_FONT',r'C:\Windows\Fonts\msjh.ttc')
pdfmetrics.registerFont(TTFont('CJK',font,subfontIndex=0))
pdfmetrics.registerFontFamily('CJK',normal='CJK',bold='CJK',italic='CJK',boldItalic='CJK')
INK=colors.HexColor('#19384b'); TEAL=colors.HexColor('#176b73')
styles={
 'body':ParagraphStyle('body',fontName='CJK',fontSize=9.5,leading=14,wordWrap='CJK',spaceAfter=5,textColor=INK),
 'h1':ParagraphStyle('h1',fontName='CJK',fontSize=21,leading=29,spaceAfter=16,textColor=TEAL,keepWithNext=True),
 'h2':ParagraphStyle('h2',fontName='CJK',fontSize=13,leading=19,spaceBefore=12,spaceAfter=7,textColor=TEAL,keepWithNext=True),
 'small':ParagraphStyle('small',fontName='CJK',fontSize=8,leading=11,wordWrap='CJK',textColor=INK),
}
def markup(s):
 s=html.escape(s.strip().replace('≤','<=').replace('≥','>=').replace('−','-').replace('–','-').replace('—','-'))
 s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m: '<link href="'+m[2]+'" color="#176b73">'+m[1]+'</link>' if m[2].startswith('https://') else m[1],s)
 s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s)
 return s.replace('`','')
def P(s,sty='body'): return Paragraph(markup(s),styles[sty])
def table(rows,width=499):
 n=len(rows[0]); sizes=[width/n]*n
 if rows[0][0]=='購' and n==4: sizes=[24,200,55,width-279]
 if n==5: sizes=[width*x for x in (.18,.32,.09,.15,.26)]
 if n==3: sizes=[width*x for x in (.23,.47,.30)]
 cells=[[P(c,'small') for c in row] for row in rows]
 t=Table(cells,colWidths=sizes,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#d6e9eb')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f2f6f7')]),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),.6,TEAL),('LINEBELOW',(0,1),(-1,-1),.2,colors.HexColor('#c8d4d9'))]))
 return t
def markdown(s):
 lines=s.splitlines(); flow=[];i=0;code=False
 while i<len(lines):
  line=lines[i].strip();i+=1
  if line.startswith('```'): code=not code;continue
  if not line: continue
  if line.startswith('|'):
   rows=[]
   while True:
    cells=[x.strip() for x in line.strip('|').split('|')]
    if not all(re.fullmatch(r'[:\- ]+',c or '-') for c in cells): rows.append(cells)
    if i>=len(lines) or not lines[i].strip().startswith('|'):break
    line=lines[i].strip();i+=1
   if rows and all(len(x)==len(rows[0]) for x in rows):flow.extend([table(rows),Spacer(1,8)])
   continue
  if code: flow.append(P(line,'small'));continue
  if line.startswith('# '):flow.append(P(line[2:],'h1'))
  elif line.startswith('##'):flow.append(P(line.lstrip('# '),'h2'))
  else:flow.append(P(line.lstrip('> ')))
 return flow
def footer(c,d):
 c.setStrokeColor(TEAL);c.line(48,38,547,38);c.setFont('CJK',8);c.setFillColor(INK)
 c.drawString(48,25,'LM3886 | Plan C | V0.3 | 2026-09-16 | 設計草案 / 未實測')
 c.drawRightString(547,25,str(d.page))
def build(path,flow):
 SimpleDocTemplate(str(path),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=45,bottomMargin=52,title='LM3886 C 方案 V0.3',author='LM3886 DIY Project').build(flow,onFirstPage=footer,onLaterPages=footer)
def overview():
 d=Drawing(499,395)
 def box(x,y,w,h,lines,pending=False):
  d.add(Rect(x,y,w,h,rx=5,ry=5,strokeColor=TEAL,fillColor=colors.HexColor('#fff2d6' if pending else '#e9f3f4')))
  for k,line in enumerate(lines):d.add(String(x+w/2,y+h-17-k*14,line,fontName='CJK',fontSize=9,textAnchor='middle',fillColor=INK))
 def arrow(x1,y1,x2,y2):
  d.add(Line(x1,y1,x2,y2,strokeColor=TEAL,strokeWidth=1))
  if x1==x2:d.add(Polygon([x2,y2,x2-3,y2+6,x2+3,y2+6],fillColor=TEAL,strokeColor=TEAL))
  else:d.add(Polygon([x2,y2,x2-6,y2-3,x2-6,y2+3],fillColor=TEAL,strokeColor=TEAL))
 box(0,329,122,54,['AC110V 入口','保險絲 / 開關 / 浪湧','待設計'],True)
 box(154,329,166,54,['已訂環形變壓器','22Vac ×2 + 12Vac','VA / 各繞組電流待確認'])
 arrow(122,356,154,356)
 box(154,229,166,60,['BR1 + BR2 雙橋','10,000µF / 63V ×4','正、負軌各 20,000µF'])
 arrow(237,329,237,289)
 box(350,229,149,60,['12Vac 輔助電源','AC / DC 介面待選','保護 / 啟停控制'],True)
 d.add(Line(320,345,424,345,strokeColor=TEAL));arrow(424,345,424,289)
 box(154,129,166,58,['LM3886T 左 + 右聲道','共用 VCC / GND / VEE','散熱與電氣絕緣'])
 arrow(237,229,237,187)
 box(0,129,122,58,['Eversolo DAC-Z10','RCA 左 / 右輸入','由 Z10 控制音量'])
 arrow(122,158,154,158)
 box(350,129,149,58,['雙聲道 DC 保護','延遲接通 / 掉電斷開','繼電器額定待選'],True)
 arrow(320,158,350,158);arrow(424,229,424,187)
 box(350,39,149,45,['左 / 右喇叭','8Ω；保護驗證後接入'])
 arrow(424,129,424,84)
 box(0,39,320,45,['PE 保護接地直接接機殼專用固定點','整機功能圖，不是一次側施工接線圖'],True)
 return d

flow=[P('LM3886 雙聲道後級','h1'),P('C 方案設計與電路彙整 / V0.3','h2'),P('2026-09-16｜双 22Vac 主電源｜雙橋整流｜四顆主濾波電容'.replace('双','雙')),P('只有變壓器及 LM3886T 已下單、待到貨。整流橋、全部電容與其餘料件均未購。'),P('本版更新電路圖供電標示、22Vac 電源與熱試算、採購及上電計畫。原放大電路與雙橋接法保留。主電源之外的保護與一次側仍待設計，沒有 PCB 或硬體量測。'),P('閱讀順序','h2'),P('整機概覽 → 修訂計畫 → 放大電路 → 內建電源 → 功率／散熱與電源估算 → 上電程序 → 採購與驗證 → 兩張 A3 向量原理圖。'),P('圖面版本','h2'),P('新版原理圖圖框為 V0.3；舊檔名保留以維持 repo 連結。2026-09-11 PDF 及舊導讀圖為歷史資料，不再作採購依據。'),PageBreak(),P('整機功能與介面','h1'),overview(),P('淡黃色區塊含未定案的設計；圖中的 12Vac 控制路徑僅表示用途，不代表可直接接到 DC12V 模組。'),P('雙橋建立正負電源，並非左右各一個獨立電源。兩個 22Vac 繞組保持獨立，DC 橋輸出在電容匯流點形成 GND。')]
for name in ['docs/00-採購總表.md','docs/01-設計規格.md','docs/05-內建電源與機構.md','docs/02-功率與散熱估算.md','docs/04-上電與驗收.md','electrical/validation.md']:
 flow.append(PageBreak())
 content=markdown((ROOT/name).read_text(encoding='utf-8'))
 if name=='docs/05-內建電源與機構.md': flow.append(KeepInFrame(499,730,content,mode='shrink'))
 else: flow.extend(content)
body=TMP/'report-body.pdf';build(body,flow)
writer=PdfWriter();writer.append(body,outline_item='C 方案現行設計與採購')
for filename,label in [('lm3886-v01.pdf','V0.3 雙聲道放大板原理圖（A3）'),('internal-psu-v02.pdf','V0.3 雙橋四電容主電源原理圖（A3）')]:writer.append(ROOT/'electrical/preview'/filename,outline_item=label)
writer.add_metadata({'/Title':'LM3886 Plan C V0.3 - 2026-09-16'})
with (OUT/'LM3886_Plan_C_V03.pdf').open('wb') as f:writer.write(f)
shopping=[P('LM3886 C 方案採購勾選清單','h1'),P('2026-09-16｜以下皆為一台雙聲道總用量，不必再乘二。'),P('已下單：雙 22Vac＋單 12Vac 變壓器、LM3886T（訂單數量待確認；設計需 2 顆）。只有這兩項已購。'),P('主電源與機構','h2')]
rows=[['購','品項 / 候選規格','數量','狀態 / 核對重點'],['□','主整流橋，至少 15A / 200V','2','未購；腳位、浪湧與散熱待選'],['□','10,000µF / 63V 電解','4','未購；每軌 2 顆；系列、紋波、尺寸待選'],['□','100nF / 100V 薄膜','2','主電源旁路'],['□','2.2kΩ / 2W 電阻','2','每軌洩放'],['□','次級保險絲 / 座','2 組','額定待變壓器電流确认'.replace('确认','確認')],['□','散熱器 / 絕緣片 / 螺絲套','2 組','散熱 ≤0.4°C/W、介面 ≤0.3°C/W 初選'],['□','雙聲道 DC 保護與繼電器','1 組','AC / DC 供電、正負 DC 偵測、掉電斷開'],['□','輔助整流 / 濾波 / 穩壓','待定','先核對 12Vac 繞組電流與保護板'],['□','AC 入口 / 開關 / 保險絲 / 浪湧','1 組','規格待選；含三芯線與機殼 PE'],['□','金屬機殼 / 固定件 / 配線','1 批','依實際板與散熱器尺寸選定']]
shopping.append(table(rows));shopping.append(PageBreak())
shopping.extend(markdown((ROOT/'docs/00-採購總表.md').read_text(encoding='utf-8')));shopping.append(PageBreak())
shopping.extend([Spacer(1,10),P('測試用品：8Ω 非感性假負載 ×2（各連續至少 100W，依規格散熱）、限流雙電源、萬用表、示波器／訊號產生器、溫度計與焊接工具。先盤點可借用設備，不必重複採購。'),P('本清單不是已完成 PCB 的套件 BOM；尺寸與 footprint 尚待核對。')])
build(OUT/'LM3886_Shopping_V03.pdf',shopping)
for p in OUT.glob('*.pdf'):
 reader=PdfReader(p);text=''.join(x.extract_text() or '' for x in reader.pages)
 assert 'LM3886' in text and len(reader.pages)>1
 print(p.name,len(reader.pages),'pages',len(text),'text characters')

