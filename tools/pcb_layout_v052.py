"""V0.5.2 candidate: one board per channel = V0.5 amplifier (D lineage, B.Cu pour) + that channel's filter
capacitors, bleeders and HF bypass. Coordinates in mm; angles follow KiCad. NOT FOR FABRICATION.
Netlist: electrical/merged-v052-netlist.xml (tools/make_netlist_v052.py); no KiCad schematic exists for this board yet.
Layout idea (2026-09-29, user's question "can we merge PSU + amp per board like many 2-board designs?"):
 - Rows 0-90: the V0.5 amplifier unchanged, minus J5. The IC edge (y=0) still faces the heatsink wall, so the
   board keeps 90 mm along the wall; the supply section extends the board across the chassis to 142 mm.
 - Rows 90-142: C201 (V+, left column x=19) and C203 (V-, right column x=71) standing 381LX D35x50; bleeders
   R201/R202 upright in the 16 mm gap; J6 4-way DC-in terminal at the bottom edge facing the front row where the
   two chassis-mounted KBPC2510 sit; C205/C206 HF bypass beside the STAR.
 - Grounding: the B.Cu pour covers ONLY the amplifier rows (y<=92). The supply section's GND is explicit 4 mm
   copper meeting at STAR (45,121); one 4 mm B.Cu link from STAR reaches into the pour at (45,86). Charging
   pulses from J6 therefore never flow through the amplifier pour.
 - Shared-rectifier, per-channel-filter: both boards hang on the same two bridges (one 2x22 Vac transformer).
   The AC side (fuses F201/F202, snubber provisions) leaves the PCB: chassis fuse holders or a small AC strip board.
Footprints and widths remain engineering assumptions. The upright C2 pitch (15) is still unmeasured.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pcb_layout_v05 import AMP_V05
_amp_layout={k:v for k,v in AMP_V05['layout'].items() if k!='J5'}
_amp_routes=[r for r in AMP_V05['routes'] if r[4] not in ('positive-feed','negative-feed','mute-supply')]
AMP_V052=dict(name='mono-layout-v052',size=(90,142),source='merged-v052-netlist.xml',layout={**_amp_layout,
# --- supply section ---
'C201':('CP_D35_P10',19,103,270),'C203':('CP_D35_P10',71,103,270),
'R201':('R_2W_P20',41,95,270),'R202':('R_2W_P20',49,95,270),
'J6':('Terminal4_P5.08',30,133,0),
'C205':('Film_P5',14,133,0),'C206':('Film_P5',60,133,0),
},anchors={'STAR':(45,121),'SG':(71.75,14.5)},labels=[l for l in AMP_V05['labels'] if l[0]!='V+  G  V-']+[
('BR1+  BR1-  BR2+  BR2-',37.6,139.5),('V+ FILTER',19,126.5),('V- FILTER',71,126.5)],
routes=_amp_routes+[
# rails from the on-board capacitors to the amplifier (same entry points as the V0.5 J5 feeds)
('VCC','F.Cu',3.0,['C201.1',(19,92),(36,75),(36,62),'C7.1'],'positive-feed'),
('VEE','F.Cu',3.0,['C203.2',(58,104),(58,79.6),(58,36),'C6.2'],'negative-feed'),
('VEE','F.Cu',0.8,[(58,79.6),(58.5,88),(80,88),'JP1.2'],'mute-supply'),
# DC in -> capacitors (charging paths; VCC/VEE on F.Cu, GND on B.Cu)
('VCC','F.Cu',4,['J6.1',(30,129),(14,129),(10,124),(10,103),'C201.1'],'positive-charge'),
('VEE','F.Cu',4,['J6.4',(50,129),(62,124),(65,124),(78,124),(78,113),'C203.2'],'negative-charge'),
('GND','B.Cu',4,['J6.2',(35.08,128),'STAR'],'charge-return'),
('GND','B.Cu',4,['J6.3',(40.16,128),'STAR'],'charge-return'),
('GND','B.Cu',4,['C201.2',(30,118),'STAR'],'charge-return'),
('GND','B.Cu',4,['C203.1',(60,103),'R202.1'],'charge-return'),
('GND','B.Cu',4,['R202.1',(45,100),'STAR'],'charge-return'),
('GND','B.Cu',4,[(45,86),(45,100)],'pour-link'),
# bleeders and HF bypass
('VCC','F.Cu',.8,['R201.1',(27,95),'C201.1'],'bleeder'),
('GND','B.Cu',.8,['R201.2','STAR'],'bleeder'),
('VEE','F.Cu',.8,['R202.2',(60,115),'C203.2'],'bleeder'),
('VCC','F.Cu',.8,['C205.1',(14,129)],'output-bypass'),
('GND','B.Cu',.8,['C205.2',(19,128),(35.08,128)],'output-bypass'),
('GND','B.Cu',.8,['C206.1',(55,128),'STAR'],'output-bypass'),
('VEE','F.Cu',.8,['C206.2',(65,124)],'output-bypass'),
],zones=[('GND','B.Cu',[(0,0),(90,0),(90,92),(0,92)])])
