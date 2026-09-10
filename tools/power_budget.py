"""Ideal class-B power/thermal estimates, not an LM3886 simulation."""
from math import pi, sqrt, log10

LOAD = 8.0
RF, RG, RB, RIN = 20000.0, 1000.0, 1000.0, 22000.0
CI, CF = 2.2e-6, 47e-6
IQ = 0.085  # Datasheet limit at its test conditions; extrapolated assumption here.
TA, RJC, RCS, RSA = 40.0, 1.0, 0.5, 0.5
GAIN = (1 + RF / RG) * RIN / (RIN + RB)


def response(frequency):
    s = 2j * pi * frequency
    return RIN / (RB + RIN + 1 / (s * CI)) * (1 + RF / (RG + 1 / (s * CF)))


def dissipation(rail, power):
    peak = sqrt(2 * LOAD * power)
    return 2 * rail * peak / (pi * LOAD) - power + 2 * rail * IQ


def worst_heat(rail):
    return 2 * rail * rail / (pi * pi * LOAD) + 2 * rail * IQ


def report():
    lines = ['# 功率、供電與散熱估算', '',
             '由 `python3 tools/power_budget.py` 產生。這是理想線性電路與 class-B 能量模型，不是 LM3886 SPICE 模擬或實測。', '',
             '## 計算假設', '',
             '- 負載為 8Ω 電阻，兩聲道相同。標稱每軌 35V，上界情境每軌 37V。',
             '- 每顆 IC 靜態電流採 85mA 作估算；原廠測試條件主要為 ±28V，外推到本設計電壓仍需實測。',
             '- LM3886T 的 θJC 採 1°C/W；絕緣介面 θCS=0.5°C/W、每顆獨立散熱器 θSA=0.5°C/W 為選型假設。',
             '- 環境為機內 40°C，設計接面溫度目標低於 125°C；不把熱保護作正常工作點。',
             '- 功率餘裕試算預留每側 6V 輸出壓降；此為專案假設，不能套用小電流 dropout 規格來保證大功率輸出。', '',
             '來源：[TI LM3886 datasheet，Electrical Characteristics／熱設計](https://www.ti.com/lit/ds/symlink/lm3886.pdf)。', '',
             '## 增益與低頻', '',
             f'- IC 中頻閉迴路增益：1+20k/1k = 21 V/V。含輸入 1k 串阻與 22k 負載：{GAIN:.3f} V/V（{20*log10(GAIN):.2f}dB）。',
             f'- 輸入隔直轉折估算：1/[2π×(1k+22k)×2.2µF] = {1/(2*pi*(RB+RIN)*CI):.2f}Hz。',
             f'- 回授下臂轉折：1/(2π×1k×47µF) = {1/(2*pi*RG*CF):.2f}Hz，DC 增益趨近 1。',
             f'- 理想網路 20Hz 相對 1kHz：{20*log10(abs(response(20)/response(1000))):.3f}dB；未含 IC 頻寬、訊源阻抗與輸出網路。', '',
             '## 每聲道輸出需求', '',
             '| 功率／8Ω | 輸出 Vrms | 輸出 Vpeak | 負載 Ipeak | 輸入 Vrms，按中頻增益 |',
             '|---|---:|---:|---:|---:|']
    for p in (1, 40, 50):
        vrms = sqrt(p * LOAD)
        lines.append(f'| {p}W | {vrms:.3f}V | {sqrt(2)*vrms:.3f}V | {sqrt(2)*vrms/LOAD:.3f}A | {vrms/GAIN:.3f}V |')
    lines += ['', '## 供電與耗散', '',
              '`Pdc = 2 × Vrail × Vpeak / (π × Rload) + 2 × Vrail × Iq`；`Pd = Pdc − Pout`。雙聲道總功率乘 2。', '',
              '| 每側電源 | 6V 壓降假設下功率上界／聲道 | 40W 時雙聲道 DC 需求 | 40W 時每軌平均電流 | 最大耗散／顆 | 最大耗散對應輸出／聲道 | 估計 Tj |',
              '|---|---:|---:|---:|---:|---:|---:|']
    for rail in (35, 37):
        heat = worst_heat(rail)
        dc = 2 * (40 + dissipation(rail, 40))
        temp = TA + heat * (RJC + RCS + RSA)
        lines.append(f'| ±{rail}V | {(rail-6)**2/(2*LOAD):.2f}W | {dc:.2f}W | {dc/(2*rail):.2f}A | {heat:.2f}W | {2*rail**2/(pi*pi*LOAD):.2f}W | {temp:.1f}°C |')
    lines += ['', '上表的功率上界是電壓幾何估算，不包含限流、SPiKe、失真或電源下陷，不能當額定輸出。', '',
              '`Pd,max = 2 × Vrail² / (π² × Rload) + 2 × Vrail × Iq`。耗散最大時的輸出功率不是滿功率；因此必須測試中等輸出。', '',
              '獨立散熱器：`Tj = Ta + Pd × (θJC + θCS + θSA)`。若兩顆共用散熱器，應改成 `Tj = Ta + 2×Pd×θSA,shared + Pd×(θJC+θCS)`；同等條件需共用散熱器約 ≤0.25°C/W。', '',
              '若絕緣介面熱阻升為 1°C/W，±37V 最壞模型的接面將約 142°C，原散熱選擇不再滿足本專案 125°C 目標。必須核對實際介面、通風及負載，尤其真實喇叭的相角。', '',
              '2×50W 同相正弦的每軌訊號峰值約 7.07A，另有靜態電流。每軌 ≥4A 連續只是初選容量；電源瞬態能力及電容儲能需一起驗證，不能只看電源銘牌。', '',
              '## 靜音電流', '',
              '依原廠近似關係：`I8 = (|VEE| − 2.6V) / 22kΩ`。電阻功耗為 `(VEE_abs−2.6)²/22k`，未含瞬態。', '',
              '| 負電源 | 解除靜音電流估算 | 22k 穩態耗散 |', '|---|---:|---:|']
    for rail in (20, 28, 35, 37):
        lines.append(f'| −{rail}V | {(rail-2.6)/22000*1000:.3f}mA | {(rail-2.6)**2/22000*1000:.2f}mW |')
    lines += ['', '採 0.25W、1% 電阻。22k×100µF=2.2s 是 RC 常數，實際解除／進入靜音時刻仍需量測。', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    print(report(), end='')
