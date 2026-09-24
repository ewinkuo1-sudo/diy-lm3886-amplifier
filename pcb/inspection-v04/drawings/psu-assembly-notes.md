# 共用電源板：組裝與接腳對照

2026-09-24；PCB V0.4 工程草稿（放大板變體 D、電源板 V0.4）。下列為板檔網路，不代表實物腳位已核准。

BR1／BR2 是 4 位端子（KBPC2510 鎖機殼，Faston 線接入）；C207–C210／R203／R204 為 snubber 預留位，只留孔不填料。

| 板上編號 | 元件值 | 焊盤號＝網路 | 注意事項 |
|---|---|---|---|
| J201 | T1 SEC 1 | 1=POS_AC1 / 2=POS_AC2 | 1=POS_AC1；2=POS_AC2 |
| J202 | T1 SEC 2 | 1=NEG_AC1 / 2=NEG_AC2 | 1=NEG_AC1；2=NEG_AC2 |
| F201 | TBD per transformer | 1=POS_AC1 / 2=POS_AC_FUSED | 依料號核對額定、腳徑與安裝方式 |
| F202 | TBD per transformer | 1=NEG_AC1 / 2=NEG_AC_FUSED | 依料號核對額定、腳徑與安裝方式 |
| BR1 | >=15A / >=200V TBD | AC1=POS_AC_FUSED / AC2=POS_AC2 / N=GND / P=VCC | AC1／AC2／P／N 為功能名稱，尚未對應實物腳位 |
| BR2 | >=15A / >=200V TBD | AC1=NEG_AC_FUSED / AC2=NEG_AC2 / N=VEE / P=GND | AC1／AC2／P／N 為功能名稱，尚未對應實物腳位 |
| C201 | 10000u / 63V | 1=VCC / 2=GND | 有極性：1=正、2=負；1=VCC；2=GND |
| C202 | 10000u / 63V | 1=VCC / 2=GND | 有極性：1=正、2=負；1=VCC；2=GND |
| C203 | 10000u / 63V | 1=GND / 2=VEE | 有極性：1=正、2=負；1=GND；2=VEE |
| C204 | 10000u / 63V | 1=GND / 2=VEE | 有極性：1=正、2=負；1=GND；2=VEE |
| R201 | 2.2k / 2W BLEED | 1=VCC / 2=GND | 依料號核對額定、腳徑與安裝方式 |
| R202 | 2.2k / 2W BLEED | 1=GND / 2=VEE | 依料號核對額定、腳徑與安裝方式 |
| C207 | TBD Cx (10n / 630V film) | 1=POS_AC2 / 2=POS_AC1 | 依料號核對額定、腳徑與安裝方式 |
| C208 | TBD Cs (150n / 630V film) | 1=POS_AC2 / 2=POS_SNUB | 依料號核對額定、腳徑與安裝方式 |
| R203 | TBD Rs (10R-47R / 2W) | 1=POS_SNUB / 2=POS_AC1 | 依料號核對額定、腳徑與安裝方式 |
| C209 | TBD Cx (10n / 630V film) | 1=NEG_AC2 / 2=NEG_AC1 | 依料號核對額定、腳徑與安裝方式 |
| C210 | TBD Cs (150n / 630V film) | 1=NEG_AC2 / 2=NEG_SNUB | 依料號核對額定、腳徑與安裝方式 |
| R204 | TBD Rs (10R-47R / 2W) | 1=NEG_SNUB / 2=NEG_AC1 | 依料號核對額定、腳徑與安裝方式 |
| C205 | 100n / 100V film | 1=VCC / 2=GND | 依料號核對額定、腳徑與安裝方式 |
| C206 | 100n / 100V film | 1=GND / 2=VEE | 依料號核對額定、腳徑與安裝方式 |
| J203 | TO L AMP J5 | 1=VCC / 2=GND / 3=VEE | 1=VCC；2=GND；3=VEE |
| J204 | TO R AMP J5 | 1=VCC / 2=GND / 3=VEE | 1=VCC；2=GND；3=VEE |
