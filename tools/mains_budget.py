"""First-order unregulated PSU estimates; component candidates are not selected."""
from math import sqrt, pi, log
from power_budget import LOAD, IQ

VAC, VA, HZ, CAP, BLEED = 25.0, 300.0, 60.0, 0.020, 2200.0


def rail_case(line_factor, power):
    peak_load = sqrt(2 * power * LOAD)
    peak_rail = sqrt(2) * VAC * line_factor - 2 * 1.1
    current = 2 * (peak_load / (pi * LOAD) + IQ) + peak_rail / BLEED
    ripple = current / (2 * HZ * CAP)
    return current, ripple, peak_rail-ripple/2, peak_rail-ripple


def report():
    winding_current = VA / (2 * VAC)
    no_load_high = VAC * 1.10 * 1.08 * sqrt(2) - 2 * 0.6
    lines = ['# 內建電源估算', '',
             '由 `python3 tools/mains_budget.py` 產生；未穩壓電源的第一階估算，沒有電路模擬或實測。', '',
             '## 候選與假設', '',
             '- 變壓器總容量 300VA，兩組彼此獨立的 25Vac 次級，額定值均對應實際選定的一次側額定電壓。',
             '- 市電暫按 110V／60Hz，99–121V 為 ±10% 設計情境，並非本次量測或供電公司保證。115V 一次側料件須改算變比。',
             '- 每次級各接一個全橋；輸出串接成正負電源，次級 AC 端不預先接地或互連。每軌 20,000µF。',
             '- 負載時每顆導通二極體壓降假設 1.1V，空載假設 0.6V。變壓器空載調整率假設 +8%，待原廠數據替換。',
             '- 50W 仍是延伸目標；滿載電壓、失真與散熱決定最後額定。', '',
             '## 負載情境', '',
             '`Vpk ≈ √2×Vac−2Vf`，`ΔVpp≈Irail/(2×fline×Crail)`，`Vavg≈Vpk−ΔVpp/2`。',
             '雙聲道平均每軌電流使用理想 class-B 訊號電流加 IC 靜態及洩放電流。忽略線阻／ESR／充電角與變壓器動態下陷；表格不是保證下限。', '',
             '| 市電情境 | 每聲道目標 | 每軌平均電流 | 紋波估算 | 每軌平均電壓 | 每軌谷值 | 谷值扣除所需輸出峰值 |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for factor, name in [(0.9, '−10%'), (1.0, '標稱'), (1.1, '+10%')]:
        for power in (40, 50):
            current, ripple, average, trough = rail_case(factor, power)
            margin = trough - sqrt(2 * power * LOAD)
            lines.append(f'| {name} | {power}W | {current:.2f}A | {ripple:.2f}Vpp | ±{average:.2f}V | ±{trough:.2f}V | {margin:.2f}V |')
    lines += ['', '本專案以 6V 大電流輸出壓降作保守功率試算。標稱市電下 40W 尚有初步電壓餘裕；低市電不保證 40W，50W 也不可直接列為額定。最後一欄並非元件保證的 dropout。', '',
              '## 變壓器、整流與儲能', '',
              f'- 候選每組次級額定電流：300VA/(2×25V) = {winding_current:.2f}Arms。',
              f'- 全橋電容輸入的粗估 DC 能力：0.62×{winding_current:.2f} = {0.62*winding_current:.2f}A／軌；僅為初選，仍須檢查溫升與峰值充電。',
              '- 2×50W 同相正弦的每軌訊號峰值約 7.07A，另加靜態負載，短時間由電源與濾波電容共同承擔。',
              '- 電解紋波電流先以每軌 DC 電流的 2–3 倍檢查，再依實際充電波形選料；兩顆並聯不保證精確均流。',
              '- 若電容容差為 −20%，紋波估算增為上表的 1.25 倍；ESR／配線壓降另計。', '',
              '初選方法參考 [Hammond 整流設計指南](https://www.hammfg.com/pdf/5c007.pdf)。', '',
              '## 高市電空載與放電', '',
              f'- +10% 市電、+8% 空載調整率情境：25×1.10×1.08×√2−1.2 = {no_load_high:.2f}V／軌，總軌間約 {2*no_load_high:.2f}V。',
              '- 專案暫用 ±41V 作元件／散熱上界試算；這不是過壓箝位。LM3886 的工作總電壓上限為 84V，實際峰值及公差必須留有餘裕，不能以空載計算當過壓保護。',
              f'- 41V 時每軌 2.2k 洩放電阻功耗 = {41**2/BLEED:.3f}W；初選 2W 並檢查機內降額。',
              f'- 每軌 RC 常數 = {BLEED*CAP:.1f}s；只有洩放電阻時 41V→5V 理想時間 = {BLEED*CAP*log(41/5):.1f}s。',
              f'- 兩軌 41V 儲能總計 = {CAP*41**2:.2f}J。放電時間會受容差、電阻失效與負載影響，斷電後仍須量測電容殘壓。', '',
              '高市電及浪湧／啟停規劃參考 [TI AN-1849](https://www.ti.com/lit/an/snaa057c/snaa057c.pdf)；IC 電壓限制見 [LM3886 datasheet](https://www.ti.com/lit/ds/symlink/lm3886.pdf)。', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    print(report(), end='')
