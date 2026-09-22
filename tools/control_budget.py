"""V0.4 control / protection board budget: soft-start, relay, aux supply, hold-up, mute, trigger.

Pure standard library. Prints a Markdown report to stdout; docs/14 quotes it.
Every number is a calculation from stated assumptions. Nothing here is measured.
Transformer VA, winding currents and Z10 trigger current capability are unknown
until delivery; those inputs are marked ASSUMED and must be replaced.
"""
from math import sqrt, log, pi
from power_budget import IQ  # quiescent current per rail per IC (A)

# ---- shared assumptions (from docs/05 / mains_budget.py) ----
VAC_MAIN, VAC_AUX, HZ = 22.0, 12.0, 60.0
CAP_RAIL = 0.020                  # F per rail (2 x 10,000 uF)
V_RAIL_NOM = 22 * sqrt(2) - 2.2   # loaded peak, standard mains (V)
V_RAIL_HIGH = 22 * 1.10 * 1.08 * sqrt(2) - 1.2   # +10% mains, no load (V)
BLEED = 2200.0                    # ohm per rail
LINE, LINE_HIGH = 110.0, 121.0
VA_LABEL = 200.0                  # seller label "200W"; NOT a verified VA
TURNS = VAC_MAIN / LINE           # secondary/primary ratio

# ---- relay / load ----
LOADS = (8.0, 4.0)
COIL_MA = {'喇叭繼電器 ×2（DC12V 線圈）': 2 * 40, '軟啟動旁通繼電器': 40, '狀態燈與控制邏輯': 20}
# ASSUMED coil currents; replace with datasheet values when relays are selected.

# ---- aux supply ----
C_AUX = 0.001                     # F, ASSUMED first-pass reservoir
VF_BRIDGE = 0.7                   # V per diode (small bridge, light load)
V_REG = 12.0
V_REG_DROP = 2.0                  # 78xx headroom ASSUMED

# ---- mute network (existing amplifier board) ----
R8, C8 = 22e3, 100e-6
V_MUTE_PIN = 0.7                  # approx. pin 8 clamp (TI SNAS091: I_mute >= 0.5 mA needed)

# ---- soft-start ----
R_SOFT = (22.0, 33.0, 47.0)      # ohm, candidate primary series resistors / cold NTC values
T_BYPASS = (0.5, 1.0, 2.0)        # s, candidate bypass delays


def section(title):
    return ['', f'## {title}', '']


def report():
    L = ['# V0.4 控制與保護板估算（docs/14 §6 的來源）', '',
         '由 `python3 tools/control_budget.py` 產生；**沒有硬體量測**。變壓器 VA、各繞組電流、'
         'Z10 trigger 輸出能力、繼電器線圈電流全部是假設值，到貨或選料後要重跑。']

    # 1. stored energy and inrush
    L += section('1. 儲能與未限流湧流')
    e_nom = 0.5 * CAP_RAIL * V_RAIL_NOM ** 2
    e_high = 0.5 * CAP_RAIL * V_RAIL_HIGH ** 2
    L.append(f'- 每軌 {CAP_RAIL*1e6:.0f}µF；標稱軌壓 {V_RAIL_NOM:.1f}V 時每軌儲能 {e_nom:.1f}J、兩軌 {2*e_nom:.1f}J；'
             f'高市電空載 {V_RAIL_HIGH:.1f}V 時兩軌 {2*e_high:.1f}J。這是軟啟動元件要吸收的能量下限。')
    L.append('- 未限流時充電峰值只受變壓器繞組電阻與整流橋限制，該電阻**未知**。情境表（次級側總串聯電阻 R，'
             f'峰值≈√2×22V／R；一次側折算×{TURNS:.2f}）：')
    L += ['', '| 次級迴路 R | 次級峰值 | 一次側折算峰值 | 對 200VA 一次側額定 1.8A 的倍數 |', '|---:|---:|---:|---:|']
    i_pri_rated = VA_LABEL / LINE
    for r in (0.3, 0.5, 1.0, 2.0):
        ipk = sqrt(2) * VAC_MAIN / r
        L.append(f'| {r:.1f}Ω | {ipk:.0f}A | {ipk*TURNS:.1f}A | {ipk*TURNS/i_pri_rated:.0f}× |')
    L.append('')
    L.append('環形變壓器本身在市電相位不利時的鐵心磁化湧流另計，常見 10～50× 額定，與電容充電湧流疊加。'
             '這兩項都會讓 110V／15A 迴路的斷路器或一次側保險絲誤動作，**軟啟動列為必要**。')

    # 2. soft-start sizing
    L += section('2. 一次側軟啟動（串聯電阻／NTC＋延遲旁通）')
    L.append(f'一次側額定電流以賣場 200W 估 {i_pri_rated:.2f}A（**未驗證**）。串聯電阻 R_s 把一次側峰值壓到 155V／R_s；'
             '電阻吸收的能量約等於電容儲能加變壓器損耗，以兩軌儲能 ×1.5 估。旁通前電容經 R_s 折算到次級的等效電阻充電，'
             '時間常數 τ = R_s×(22/110)²×C。')
    L += ['', '| R_s（一次側） | 一次側峰值 | 折算次級 R | τ／軌 | 5τ（充飽） | 吸收能量估 | 建議額定 |', '|---:|---:|---:|---:|---:|---:|---|']
    for r in R_SOFT:
        ipk = LINE * sqrt(2) / r
        r_sec = r * TURNS ** 2
        tau = r_sec * CAP_RAIL
        L.append(f'| {r:.0f}Ω | {ipk:.1f}A | {r_sec:.2f}Ω | {tau*1000:.0f}ms | {5*tau*1000:.0f}ms | {1.5*2*e_high:.0f}J | '
                 f'NTC 能量額定 ≥{1.5*2*e_high*1.5:.0f}J 且穩態電流 ≥{i_pri_rated*1.5:.1f}A；或線繞電阻 ≥10W 脈衝級 |')
    L.append('')
    L.append('- 5τ 都在 0.2s 內，所以旁通延遲 0.5～2s 主要是等變壓器磁化與一次側電流穩定，不是等電容充飽。'
             '**建議 1s**，由控制板 RC 或 MCU 計時。')
    L.append('- 旁通繼電器觸點：AC250V、≥5A、阻性；它切的是穩態一次側電流，不是湧流。')
    L.append('- 只用 NTC 不旁通會持續發熱且熱態阻值隨室溫變，快速關開時 NTC 未冷卻就失去限流。**旁通為必要**。')
    L.append('- 旁通失效模式：繼電器不吸合時 R_s 持續承受一次側電流（'
             + '、'.join(f'{r:.0f}Ω→{i_pri_rated**2*r:.0f}W' for r in R_SOFT)
             + '），必須燒不起來，或以熱熔斷／保險絲保護。')

    # 3. relay contacts
    L += section('3. 喇叭繼電器 DC 分斷需求')
    L += ['| 軌壓情境 | 8Ω 故障電流 | 4Ω 故障電流 |', '|---|---:|---:|']
    for label, v in (('標稱 ' + f'{V_RAIL_NOM:.1f}V', V_RAIL_NOM), ('高市電空載 ' + f'{V_RAIL_HIGH:.1f}V', V_RAIL_HIGH)):
        L.append(f'| {label} | {v/8:.2f}A | {v/4:.2f}A |')
    L.append('')
    L.append(f'選型門檻：**DC 分斷電壓 ≥{V_RAIL_HIGH:.0f}V（建議 48VDC 級）、DC 分斷電流 ≥{V_RAIL_HIGH/4:.0f}A（含 4Ω）**，'
             '觸點 AgSnO₂／AgNi。標「10A 250VAC」不算，要看廠商曲線裡的 DC 電阻性負載線。'
             '兩組觸點串聯給同一聲道可把每觸點分斷電壓減半，值得評估。')

    # 4. hold-up vs release time
    L += section('4. 掉電時序：軌壓衰減 vs 繼電器釋放')
    i_idle = 2 * IQ + V_RAIL_NOM / BLEED
    dvdt = i_idle / CAP_RAIL
    t_to_20 = (V_RAIL_NOM - 20) / dvdt
    L.append(f'- 靜態（無訊號）每軌負載 ≈ 2×{IQ*1000:.0f}mA 靜態電流 + 洩放 {V_RAIL_NOM/BLEED*1000:.0f}mA = {i_idle*1000:.0f}mA，'
             f'軌壓衰減率 {dvdt:.1f}V/s，從 {V_RAIL_NOM:.1f}V 掉到 20V 約 {t_to_20:.1f}s。')
    L.append('- 12Vac 消失偵測：半波週期 8.3ms，濾波後 20～40ms 內可判定；繼電器釋放 5～15ms。**合計 <60ms，'
             f'遠小於 {t_to_20:.1f}s**，所以「從 12Vac 整流前取樣」的關機快斷在時序上成立。')
    L.append('- 反過來若從主軌 DC 取樣，要等軌壓掉到門檻才動作，期間 IC 已進入不對稱供電，這就是 13 號文件禁止的原因。')
    L.append('- 大訊號時每軌電流更大、衰減更快（40W／8Ω 約 2.2A → '
             f'{2.2/CAP_RAIL:.0f}V/s），仍有 0.1s 以上，但靜音應在繼電器釋放同時或之前下達。')

    # 5. aux supply
    L += section('5. 12Vac 輔助電源預算')
    vpk = VAC_AUX * sqrt(2) - 2 * VF_BRIDGE
    vpk_hi = VAC_AUX * 1.10 * 1.08 * sqrt(2) - 2 * VF_BRIDGE
    i_load = sum(COIL_MA.values()) / 1000
    ripple = i_load / (2 * HZ * C_AUX)
    v_min = vpk - ripple
    L += ['| 負載項（假設） | 電流 |', '|---|---:|']
    for k, v in COIL_MA.items():
        L.append(f'| {k} | {v}mA |')
    L.append(f'| **合計** | **{i_load*1000:.0f}mA** |')
    L.append('')
    L.append(f'- 全橋整流：標稱峰值 {vpk:.1f}V；高市電空載 {vpk_hi:.1f}V。{C_AUX*1e6:.0f}µF 濾波、{i_load*1000:.0f}mA 時紋波 {ripple:.2f}Vpp，'
             f'谷值 {v_min:.1f}V，對 7812（需 ≥{V_REG+V_REG_DROP:.0f}V）餘裕 {v_min-V_REG-V_REG_DROP:.1f}V——'
             + ('足夠。' if v_min > V_REG + V_REG_DROP else '**不足，要加大濾波或改 LDO**。'))
    L.append(f'- 穩壓器耗散最壞 ({vpk_hi:.1f}−{V_REG:.0f})×{i_load*1000:.0f}mA ≈ {(vpk_hi-V_REG)*i_load:.2f}W，TO-220 加小散熱片或鎖機殼。')
    L.append(f'- 12Vac 繞組需求：DC {i_load*1000:.0f}mA × 1.6（電容輸入整流換算）≈ {i_load*1.6*1000:.0f}mA rms，'
             f'約 {VAC_AUX*i_load*1.6:.1f}VA。**到貨後用已知負載量繞組壓降確認**；12Vac 直入 UPC1237 類模組時，模組自己的整流電容也算在這裡。')
    L.append('- 若繼電器改 DC24V 線圈或加第二組觸點，這張表要重算。')

    # 6. mute network
    L += section('6. 既有靜音支路能否交給控制板')
    for v in (V_RAIL_NOM, 25.0, V_RAIL_HIGH):
        L.append(f'- VEE = −{v:.1f}V：I_mute = ({v:.1f}−{V_MUTE_PIN})/22k = {(v-V_MUTE_PIN)/R8*1000:.2f}mA'
                 + ('（≥0.5mA，符合 TI 要求）' if (v - V_MUTE_PIN) / R8 >= 0.5e-3 else '（**不足**）'))
    L.append(f'- R8×C8 = {R8*C8:.1f}s：解除靜音的軟啟動時間常數，與喇叭繼電器 3～5s 延遲相容。')
    L.append('- 控制板取代 JP1／JP2 的方式：每聲道各一顆 NPN／光耦，集極接 R8 的 RUN 端、射極接 VEE，'
             f'耐壓 ≥{V_RAIL_HIGH:.0f}V（選 60V 級），開關電流僅 1.3mA。**左右兩顆各自獨立，兩個 MUTE 節點仍不相接。**'
             ' 板上 JP1／JP2 保留為手動測試位。')

    # 7. Z10 trigger
    L += section('7. Z10 12V trigger 直接驅動一次側繼電器')
    L.append('- 拓樸：Z10 trigger out（12VDC）→ 3.5mm 插座 → 串聯二極體（防反接）→ DC12V 繼電器線圈 ‖ 續流二極體；'
             '線圈另一端接 trigger 地。**線圈電源就是 Z10 的 12V**，因此後級關機時不需要任何待機電源，'
             '也不需要市電側常通電路，符合 01 號文件「不需額外 PCB」的預留。')
    L.append('- 手動總開關與繼電器觸點**並聯**（OR），總開關前另有 AC 入口保險絲與主開關。')
    L.append('- 線圈電流上限取決於 Z10 trigger 輸出能力，**原廠規格未取得**。門檻：線圈 ≤50mA（DC12V、≥240Ω）；'
             '若 Z10 只能供 ≤20mA，改用光耦＋輔助電源就會回到待機電源問題，那時改成「觸發鎖住」：'
             'trigger 只負責吸合，吸合後由 12Vac 輔助電源自保持，trigger 消失時由控制板釋放。')
    L.append('- 一次側繼電器觸點：AC250V、≥5A、阻性；串在軟啟動 R_s 之前。動作順序見 docs/14 §3。')

    L += section('8. 這份估算不能替代的量測')
    L += ['1. 變壓器三組繞組空載電壓、線色、彼此隔離、12Vac 帶載壓降（推 VA）。',
          '2. Z10 trigger 輸出電壓與可供電流（原廠手冊或以電阻負載實測）。',
          '3. 選定繼電器後的線圈電流與 DC 分斷曲線。',
          '4. 成機軌壓衰減曲線（示波器）對照 §4。', '',
          '參考：[TI LM3886 SNAS091](https://www.ti.com/lit/ds/symlink/lm3886.pdf) §Mute；'
          '[docs/05](../docs/05-內建電源與機構.md)；[docs/13](../docs/13-喇叭保護與啟停設計計畫.md)。', '']
    return '\n'.join(L)


if __name__ == '__main__':
    print(report(), end='')
