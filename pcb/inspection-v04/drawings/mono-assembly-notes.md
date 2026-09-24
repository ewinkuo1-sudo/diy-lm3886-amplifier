# 單聲道放大板：組裝與接腳對照

2026-09-24；PCB V0.4 工程草稿（放大板變體 D、電源板 V0.4）。下列為板檔網路，不代表實物腳位已核准。

兩片單聲道板絲印相同；右聲道原理圖編號請看 [左右聲道對照](../../mono-channel-mapping.csv)。

| 板上編號 | 元件值 | 焊盤號＝網路 | 注意事項 |
|---|---|---|---|
| U1 | LM3886T | 1=VCC / 2=unconnected-(U1-NC-Pad2) / 3=L_OUT / 4=VEE / 5=VCC / 6=unconnected-(U1-NC-Pad6) / 7=GND / 8=L_MUTE / 9=L_INV / 10=L_PLUS / 11=unconnected-(U1-NC-Pad11) | 1=VCC；2=unconnected-(U1-NC-Pad2)；3=L_OUT；4=VEE；5=VCC；6=unconnected-(U1-NC-Pad6)；7=GND；8=L_MUTE；9=L_INV；10=L_PLUS；11=unconnected-(U1-NC-Pad11) |
| C3 | 100n / 100V | 1=VCC / 2=GND | 依料號核對額定、腳徑與安裝方式 |
| C4 | 100n / 100V | 1=GND / 2=VEE | 依料號核對額定、腳徑與安裝方式 |
| C7 | 470u / 63V | 1=VCC / 2=GND | 有極性：1=正、2=負；1=VCC；2=GND |
| C6 | 470u / 63V | 1=GND / 2=VEE | 有極性：1=正、2=負；1=GND；2=VEE |
| R4 | 20k / 1% | 1=L_INV / 2=L_OUT | 依料號核對額定、腳徑與安裝方式 |
| R3 | 1k / 1% | 1=L_FB_AC / 2=L_INV | 依料號核對額定、腳徑與安裝方式 |
| R6 | 1k | 1=L_AC / 2=L_PLUS | 依料號核對額定、腳徑與安裝方式 |
| R2 | 22k | 1=GND / 2=L_PLUS | 依料號核對額定、腳徑與安裝方式 |
| R1 | 1M | 1=GND / 2=L_IN | 依料號核對額定、腳徑與安裝方式 |
| C1 | 2.2u / 100V film | 1=L_IN / 2=L_AC | 依料號核對額定、腳徑與安裝方式 |
| J1 | L RCA | 1=L_IN / 2=GND | 1=L_IN；2=GND |
| C2 | 47u / 63V BP | 1=GND / 2=L_FB_AC | 必須無極性 BP；不可以一般有極性電解直接替代 |
| L1 | 0.7uH / air core | 1=L_OUT / 2=L_SPK | 依料號核對額定、腳徑與安裝方式 |
| R7 | 10R / 2W | 1=L_OUT / 2=L_SPK | 依料號核對額定、腳徑與安裝方式 |
| J2 | L TEST OUT | 1=L_SPK / 2=GND | 1=L_SPK；2=GND |
| R5 | 2.7R / 2W | 1=L_ZOBEL / 2=L_OUT | 依料號核對額定、腳徑與安裝方式 |
| C5 | 100n / 100V film | 1=GND / 2=L_ZOBEL | 依料號核對額定、腳徑與安裝方式 |
| J5 | INTERNAL PSU | 1=VCC / 2=GND / 3=VEE | 1=VCC；2=GND；3=VEE |
| R8 | 22k / 0.6W | 1=L_MUTE / 2=L_RUN | 依料號核對額定、腳徑與安裝方式 |
| C8 | 100u / 100V | 1=GND / 2=L_MUTE | 有極性：1=正、2=負；1=GND；2=L_MUTE |
| JP1 | L RUN LINK | 1=L_RUN / 2=VEE | 1=L_RUN；2=VEE |
