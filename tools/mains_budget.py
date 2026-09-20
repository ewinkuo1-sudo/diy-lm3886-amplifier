"""Plan C voltage scenarios; ordered transformer VA/current still unknown."""
from math import sqrt, pi, log
from power_budget import LOAD, IQ
VAC, HZ, CAP, BLEED = 22.0, 60.0, 0.020, 2200.0
def rail_case(line_factor, power):
    peak_load = sqrt(2 * power * LOAD)
    peak_rail = sqrt(2) * VAC * line_factor - 2.2
    current = 2 * (peak_load / (pi * LOAD) + IQ) + peak_rail / BLEED
    ripple = current / (2 * HZ * CAP)
    return current, ripple, peak_rail-ripple/2, peak_rail-ripple
def report():
    high=VAC*1.10*1.08*sqrt(2)-1.2
    lines=['# V0.3 C 方案電源估算', '',
    '由 tools/mains_budget.py 產生；沒有硬體量測。只知道賣場標示 200W、AC110V、兩組獨立 22Vac 加一組 12Vac。VA、各繞組電流、頻率額定與調整率均待確認，不推定 200VA 或可供電流。', '',
    '## 試算假設', '',
    '- 假設 22Vac 為額定負載電壓；若實際為空載值，以下負載電壓會高估，需重算。',
    '- 市電以 110V／60Hz、±10% 試算；空載調整率假設 +8%。均非供應商保證或量測。',
    '- 兩組獨立次級各接全橋，DC 輸出串接；AC 次級不互接。四顆 10,000µF／63V，每軌兩顆並聯。',
    '- 導通二極體帶載每顆 1.1V，空載每顆 0.6V；不含線阻、ESR、充電角、變壓器動態下陷。', '',
    '## 雙聲道負載情境', '',
    'Vpeak=√2×Vac−2Vf；紋波=Irail/(2×60×0.020)；平均值=峰值−紋波/2。30W、40W 是計算負載，不表示供電一定支持。', '',
    '| 市電 | 每聲道假設輸出 | 每軌平均電流 | 紋波 | 平均軌電壓 | 谷值 | 谷值減輸出峰值 |',
    '|---|---:|---:|---:|---:|---:|---:|']
    for factor,label in [(0.9,'−10%'),(1,'標稱'),(1.1,'+10%')]:
        for power in (30,40):
            i,r,a,t=rail_case(factor,power)
            lines.append(f'| {label} | {power}W | {i:.2f}A | {r:.2f}Vpp | ±{a:.2f}V | ±{t:.2f}V | {t-sqrt(2*power*LOAD):.2f}V |')
    lines += ['', '若沿用每側 6V 輸出壓降的保守假設，標稱市電下 40W 餘裕不足，低市電連 30W 也不保證。30～40W 只是探索範圍，先量削波與溫升，再定雙聲道連續額定。', '',
    '## 空載、放電與儲能', '',
    f'- +10% 市電、+8% 空載調整率：22×1.10×1.08×√2−1.2 = {high:.2f}V／軌。暫以 36V 作熱情境，不是硬體限壓。',
    f'- 36V 時每顆 2.2k 洩放電阻耗散 {36**2/BLEED:.3f}W；候選 2W，仍須機內降額。',
    f'- 每軌 RC={BLEED*CAP:.1f}s，僅靠洩放電阻從 36V 降至 5V 約 {BLEED*CAP*log(36/5):.1f}s；實際斷電後仍量測殘壓。',
    f'- 兩軌 36V 總儲能約 {CAP*36**2:.2f}J，浪湧限制需按充電與快速關開情境設計。', '',
    '## 尚不能定案的數字', '',
    '- 變壓器持續供電能力、一次側與次級保險絲額定：等待繞組電流、VA、熱與浪湧資料。',
    '- 電容紋波額定與整流橋散熱：依充電波形與實際元件核對。電容 −20% 容差會讓紋波增加為 1.25 倍。',
    '- 12Vac 全橋濾波約 15～16Vdc，空載可能更高。AC12V 與 DC12V 保護板不得混接，DC 模組可能需穩壓。', '',
    '參考：[TI LM3886](https://www.ti.com/lit/ds/symlink/lm3886.pdf)、[TI AN-1849](https://www.ti.com/lit/an/snaa057c/snaa057c.pdf)。實際採購狀態見 archive/08-採購狀態.md。', '']
    return '\n'.join(lines)
if __name__=='__main__': print(report(),end='')
