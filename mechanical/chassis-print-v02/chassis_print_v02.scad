// LM3886 3D 列印機殼 v0.2（2026-10-25）—— 給 Bambu Lab H2D（單噴頭 325×320×325）
// 和 v0.1 的差別：
//   1. 底板＋四面牆一體成型成一個「底殼」（298×288×81），不再拆 6 件；上蓋也是一整片列印。
//   2. 自製 CTRL／MAINS 板換成兩片現成板：UPC1237 保護器（約 52×31）與 AC110V 軟啟動板（95×58、孔距 84×47）。
//   3. 放大板 IC 窗口只開在 IC 位置（32 寬、尖頂免支撐），左右聲道 IC 都落在 y=94＝散熱片中心。
//   4. 底板內側加 40 mm 格狀肋、上蓋下側加 48 mm 格狀肋；四角與前後左右加上蓋螺柱（M3 熱熔螺母）。
//   5. 機腳 5 顆：四角＋變壓器正下方（M6 中心螺栓穿過變壓器、底板、中央機腳）。
// 座標：x 向右（從機後看；從正面看 x=0 是右側，所以 x=0 側叫 _R）、y 由後往前、z 向上；
// 原點＝機內右後角、底板上表面。
// 單檔多件：用 -D part="xxx" 匯出單件 STL。

part = "all";
$fn = 32;

// ---------- 主要尺寸 ----------
W = 290;  D = 280;  H = 78;     // 內寬、內深、內高（底板上表面到上蓋下表面）
T  = 4;                          // 牆厚
FT = 3;                          // 底板厚（z = -3..0）
LT = 3;                          // 上蓋板厚（z = 78..81）
RC = 6;                          // 外殼直角的外圓角
RIBH = 6;  RIBW = 2.4;  RIBP = 40;    // 底板肋：高、寬、間距
RIBH2 = 10; ZONE = [72, 225, 145];    // 變壓器區（x 72–225、y≥145，避開兩片現成板）肋加高到 10（剛性計算 tools/chassis_v02_stiffness.py）
LRIBH = 12; LRIBP = 40;              // 上蓋肋：高、間距（剛性計算：48 mm 時中央手壓 5 kg 撓度超標）
INS = 4.0;  INSD = 7;                 // M3 熱熔螺母孔徑、深

// 散熱片（賣場標 176×33×60；底板厚 5 是估的，到貨要量）
HSL = 176; HSH = 60; HST = 33; HSB = 5; NFIN = 23; FINT = 1.5;
HSY0 = 6;  HSZ0 = 4;             // 散熱片 y 起點、z 起點（底緣）
HSC = HSY0 + HSL / 2;            // 94：散熱片中心 y
BOSS = 4;                        // 散熱片區牆內加厚
LIPW = 6;                        // 凹槽外再留的牆
// IC 窗口（LM3886T 本體寬 20.02、厚 4.5，規格書 NDJ0011B；高度未量）
ICY = HSC;  WINW = 32;  WZ0 = 9;  WZ1 = 42;   // 窗口寬、底、直邊頂（再往上 45° 尖頂到 WZ1+WINW/2）
// 散熱片固定 M3 ×4：避開 IC 窗口與角柱，z 留給螺絲起子
HSSY = [HSY0 + 10, HSY0 + HSL - 10];
HSSZ = [HSZ0 + 18, HSZ0 + HSH - 8];

// 放大板 V0.6.1：90（沿牆）×80，IC U1 在板邊 x=39（KiCad），固定孔距邊 4 mm
AZ0 = 10;                         // 放大板底面高度（2 mm 墊＋8 mm 銅柱）
AX0 = 1.5;                        // 放大板貼牆那一邊的 x：散熱片底板內面在 x=1，留 0.5 間隙（IC 背板凸出板邊 0.5，最後用長孔微調）
AY0R = HSC - 39;                  // 55：右聲道板 y 起點（板逆時針轉 90°，IC 在 39）
AY0L = HSC - 51;                  // 43：左聲道板 y 起點（板順時針轉 90°，IC 在 90-39=51）
// 電源板 V0.6.1：92×120，孔距邊 4
PX0 = 99; PY0 = 20; PZ0 = 10;
// 軟啟動板（才嘉 AC110V）：95×58，孔距 84×47（商品圖），長邊沿 y；放右前（靠電源開關）
SSX0 = 10; SSY0 = 170; SSW = 58; SSL = 95; SSZ0 = 8;
// 保護板（BB 音研 UPC1237）：約 52×31（商品圖），孔位未知，暫設離邊 3。
// 放右後、放大板 R 正後方（喇叭端子內側），長邊沿 x：右聲道輸出端子 J2 就在旁邊，四顆喇叭端子集中在它後面
PRX0 = 28; PRY0 = 23; PRW = 52; PRL = 31; PRZ0 = 8; PRIN = 3;
// 喇叭端子：四顆集中成 2×2，右聲道下排、左聲道上排（XLR 在旁邊的 x=22）
SPKX = [60, 79]; SPKZ = [30, 58];
// 變壓器：Ø120×50（含出線鼓起），中心孔，置於底板肋上加 3 mm 橡膠墊
TX = W / 2; TY = 210; TD = 120; TH = 50; TZ0 = RIBH2 + 3;
// 上蓋螺柱位置
LIDSCR = [[5, 5], [W - 5, 5], [5, D - 5], [W - 5, D - 5], [W / 2, 4.5], [W / 2, D - 4.5], [5, 165], [W - 5, 165]];
// 機腳
FEET = [[16, 16], [W - 16, 16], [16, D - 16], [W - 16, D - 16]];

// ---------- 小工具 ----------
module bx(x0, y0, z0, x1, y1, z1) { translate([x0, y0, z0]) cube([x1 - x0, y1 - y0, z1 - z0]); }
module cyl_x(x0, x1, y, z, d) { translate([x0, y, z]) rotate([0, 90, 0]) cylinder(h = x1 - x0, d = d); }
module cyl_y(y0, y1, x, z, d) { translate([x, y0, z]) rotate([-90, 0, 0]) cylinder(h = y1 - y0, d = d); }
module cyl_z(z0, z1, x, y, d) { translate([x, y, z0]) cylinder(h = z1 - z0, d = d); }
module rbox(x0, y0, z0, x1, y1, z1, r) {
  hull() for (x = [x0 + r, x1 - r]) for (y = [y0 + r, y1 - r]) cyl_z(z0, z1, x, y, 2 * r);
}
module slot_x(x, y, z0, z1, len, d) { hull() for (dx = [-len / 2, len / 2]) cyl_z(z0, z1, x + dx, y, d); }

// 放大板固定孔（機殼座標）
function amp_holes_R() = [for (kx = [4, 86]) for (ky = [4, 76]) [AX0 + ky, AY0R + kx]];
function amp_holes_L() = [for (kx = [4, 86]) for (ky = [4, 76]) [W - AX0 - ky, AY0L + 90 - kx]];
function psu_holes() = [for (x = [PX0 + 4, PX0 + 88]) for (y = [PY0 + 4, PY0 + 116]) [x, y]];
function ss_holes() = [for (dx = [-23.5, 23.5]) for (dy = [-42, 42]) [SSX0 + SSW / 2 + dx, SSY0 + SSL / 2 + dy]];
function pr_holes() = [for (x = [PRX0 + PRIN, PRX0 + PRW - PRIN]) for (y = [PRY0 + PRIN, PRY0 + PRL - PRIN]) [x, y]];
// 市電板護罩固定耳
MCX0 = SSX0 - 3; MCX1 = SSX0 + SSW + 3; MCY0 = SSY0 - 3; MCY1 = SSY0 + SSL + 3; MCZ0 = RIBH; MCZ1 = 46;
MCTAB = [[(MCX0 + MCX1) / 2, MCY0 - 4], [(MCX0 + MCX1) / 2, MCY1 + 4]];

// ================= 底殼 =================
module floor_ribs() {
  difference() {
    union() {
      for (x = [RIBP : RIBP : W - 1]) bx(x - RIBW / 2, 0, 0, x + RIBW / 2, D, RIBH);
      for (y = [RIBP : RIBP : D - 1]) bx(0, y - RIBW / 2, 0, W, y + RIBW / 2, RIBH);
      intersection() {                      // 變壓器區加高
        union() {
          for (x = [RIBP : RIBP : W - 1]) bx(x - RIBW / 2, 0, 0, x + RIBW / 2, D, RIBH2);
          for (y = [RIBP : RIBP : D - 1]) bx(0, y - RIBW / 2, 0, W, y + RIBW / 2, RIBH2);
        }
        bx(ZONE[0], ZONE[2], 0, ZONE[1], D, RIBH2);
      }
    }
    // 放大板銅柱位置讓開（銅柱站在 2 mm 墊上）
    for (p = concat(amp_holes_R(), amp_holes_L())) bx(p[0] - 8, p[1] - 6, 2, p[0] + 8, p[1] + 6, RIBH + 1);
  }
  // 變壓器承環（和肋同高，橡膠墊放在上面）
  difference() { cyl_z(0, RIBH2, TX, TY, TD - 4); cyl_z(-1, RIBH2 + 1, TX, TY, TD - 20); }
  cyl_z(0, RIBH2, TX, TY, 22);
  for (a = [0 : 45 : 315]) translate([TX, TY, 0]) rotate([0, 0, a]) bx(0, -RIBW / 2, 0, TD / 2 - 2, RIBW / 2, RIBH2);
}

module hs_boss(side) {   // side = 0 右（x=0）、1 左（x=W）
  x0 = side == 0 ? 0 : W - BOSS;
  bx(x0, max(HSY0 - LIPW, 0), 0, x0 + BOSS, HSY0 + HSL + LIPW, min(HSZ0 + HSH + LIPW, H));
}
module posts() {
  for (c = [[0, 0], [W - 10, 0], [0, D - 10], [W - 10, D - 10]]) bx(c[0], c[1], 0, c[0] + 10, c[1] + 10, H);
  for (y = [0, D]) {     // 前後中央：上半段才有，下緣 45° 免支撐
    s = y == 0 ? 1 : -1;
    hull() { bx(W / 2 - 6, min(y, y + s * 9), H - 14, W / 2 + 6, max(y, y + s * 9), H); bx(W / 2 - 6, min(y, y + s * 0.01), H - 23, W / 2 + 6, max(y, y + s * 0.01), H - 14); }
  }
  for (x = [0, W]) {     // 左右 y=165
    s = x == 0 ? 1 : -1;
    hull() { bx(min(x, x + s * 10), 159, H - 14, max(x, x + s * 10), 171, H); bx(min(x, x + s * 0.01), 159, H - 24, max(x, x + s * 0.01), 171, H - 14); }
  }
}
module board_bosses() {
  for (p = amp_holes_R()) bx(p[0] - 7, p[1] - 5, 0, p[0] + 7, p[1] + 5, 2);
  for (p = amp_holes_L()) bx(p[0] - 7, p[1] - 5, 0, p[0] + 7, p[1] + 5, 2);
  for (p = psu_holes()) cyl_z(0, PZ0, p[0], p[1], 9);
  for (p = ss_holes()) cyl_z(0, SSZ0, p[0], p[1], 8);
  for (p = pr_holes()) cyl_z(0, PRZ0, p[0], p[1], 7);
  for (p = MCTAB) cyl_z(0, MCZ0, p[0], p[1], 10);
  for (p = FEET) cyl_z(0, RIBH, p[0], p[1], 13);
}

module hs_cuts(side) {
  xo = side == 0 ? -T : W + T;              // 外表面
  s  = side == 0 ? 1 : -1;                   // 往機內的方向
  // 散熱片底板凹槽（從外側進，深＝底板厚）
  bx(min(xo - s, xo + s * HSB), HSY0 - 0.2, HSZ0 - 0.2, max(xo - s, xo + s * HSB), HSY0 + HSL + 0.2, HSZ0 + HSH + 0.2);
  // IC 窗口：直邊到 WZ1，往上 45° 尖頂（列印免支撐）
  xa = side == 0 ? -T - 1 : W - BOSS - 1;
  translate([xa, 0, 0]) rotate([90, 0, 90])
    linear_extrude(T + BOSS + 2)
      polygon([[ICY - WINW / 2, WZ0], [ICY + WINW / 2, WZ0], [ICY + WINW / 2, WZ1], [ICY, WZ1 + WINW / 2], [ICY - WINW / 2, WZ1]]);
  // 放大板板邊槽：板子要伸到散熱片底板內面（x=1），把加厚區在板厚高度挖開
  ay0 = side == 0 ? AY0R : AY0L;
  if (side == 0) bx(1, ay0 - 1, WZ0, BOSS + 1, ay0 + 91, AZ0 + 1.6 + 2);
  else           bx(W - BOSS - 1, ay0 - 1, WZ0, W - 1, ay0 + 91, AZ0 + 1.6 + 2);
  // 靠牆那排銅柱（離板邊 4 mm）會卡進加厚區：在銅柱高度挖缺口（含長孔 ±2.5 的移動量）
  for (p = side == 0 ? amp_holes_R() : amp_holes_L())
    if (p[0] < 20 || p[0] > W - 20) bx(side == 0 ? 1 : W - BOSS - 1, p[1] - 5, 2, side == 0 ? BOSS + 1 : W - 1, p[1] + 5, WZ0 + 0.5);
  // 散熱片固定螺絲 M3 ×4（從機內鎖進散熱片底板攻牙孔）
  for (y = HSSY) for (z = HSSZ) cyl_x(xa, xa + T + BOSS + 2, y, z, 3.4);
}

module rear_cuts() {     // 後牆：XLR＋RCA（左右）、喇叭端子 ×4、IEC
  for (x = [22, W - 22]) {
    cyl_y(-T - 1, 1, x, 52, 24);
    cyl_y(-T - 1, 1, x + 9.5, 64, 3.2); cyl_y(-T - 1, 1, x - 9.5, 40, 3.2);
    cyl_y(-T - 1, 1, x, 20, 9.5);
  }
  for (x = SPKX) for (z = SPKZ) cyl_y(-T - 1, 1, x, z, 8.5);
  // 後牆外側刻字（深 0.6）
  for (t = [["R", SPKZ[0]], ["L", SPKZ[1]]]) translate([SPKX[1] + 13, -T + 0.6, t[1] - 4]) rotate([90, 0, 0]) linear_extrude(1) text(t[0], size = 8, halign = "center", font = "Liberation Sans:style=Bold");
  translate([SPKX[0] - 13, -T + 0.6, (SPKZ[0] + SPKZ[1]) / 2 - 3]) rotate([90, 0, 0]) linear_extrude(1) text("SPK", size = 5, halign = "center", font = "Liberation Sans:style=Bold");
  bx(W / 2 - 23.75, -T - 1, 34 - 13.75, W / 2 + 23.75, 1, 34 + 13.75);       // IEC C14 含保險絲 47.5×27.5
  for (x = [W / 2 - 20, W / 2 + 20]) cyl_y(-T - 1, 1, x, 34, 3.2);
}
SWX = 85; LEDX = W - 85;   // 開關不能放正中（會撞變壓器），放在軟啟動板旁
module front_cuts() {    // 前牆：電源開關 Ø16、LED Ø5
  cyl_y(D - 1, D + T + 1, SWX, 39, 16);
  cyl_y(D - 1, D + T + 1, LEDX, 39, 5.2);
}
module floor_cuts() {
  // 放大板：底下穿螺絲進銅柱，x 方向長孔 ±2.5 mm
  for (p = concat(amp_holes_R(), amp_holes_L())) slot_x(p[0], p[1], -FT - 1, 2.5, 5, 3.4);
  // 熱熔螺母孔
  for (p = concat(psu_holes(), ss_holes(), pr_holes(), MCTAB)) cyl_z(2, 30, p[0], p[1], INS);
  for (p = FEET) cyl_z(-FT - 1, -FT + INSD, p[0], p[1], INS);
  // 變壓器中心螺栓 M6
  cyl_z(-FT - 1, RIBH2 + 1, TX, TY, 6.6);
  // 放大板下方通風孔（避開肋與銅柱）
  for (r = [[AX0 + 8, AX0 + 74, AY0R + 10, AY0R + 82], [W - AX0 - 74, W - AX0 - 8, AY0L + 8, AY0L + 80]])
    for (x = [r[0] : 9 : r[1]]) for (y = [r[2] : 9 : r[3]])
      if (abs(x - round(x / RIBP) * RIBP) > 5 && abs(y - round(y / RIBP) * RIBP) > 5
          && min([for (p = concat(amp_holes_R(), amp_holes_L())) norm([x - p[0], y - p[1]])]) > 10)
        cyl_z(-FT - 1, 1, x, y, 5);
}
module lid_screws() { for (p = LIDSCR) cyl_z(H - INSD, H + 1, p[0], p[1], INS); }

module tub() {
  difference() {
    union() {
      difference() { rbox(-T, -T, -FT, W + T, D + T, H, RC); bx(0, 0, 0, W, D, H + 1); }
      floor_ribs();
      hs_boss(0); hs_boss(1);
      posts();
      board_bosses();
    }
    hs_cuts(0); hs_cuts(1);
    rear_cuts(); front_cuts(); floor_cuts(); lid_screws();
  }
}

// ================= 上蓋（一整片，翻過來印：外表面貼平台） =================
module lid() {
  difference() {
    union() {
      rbox(-T, -T, H, W + T, D + T, H + LT, RC);
      intersection() {
        union() {
          for (x = [LRIBP : LRIBP : W - 1]) bx(x - RIBW / 2, 0, H - LRIBH, x + RIBW / 2, D, H);
          for (y = [LRIBP : LRIBP : D - 1]) bx(0, y - RIBW / 2, H - LRIBH, W, y + RIBW / 2, H);
        }
        difference() {
          bx(12, 12, H - LRIBH - 1, W - 12, D - 12, H + 1);
          cyl_z(H - LRIBH - 2, H - 7, TX, TY, 30);       // 讓開變壓器中心螺栓與螺帽（頂約 z=67）
        }
      }
      // 定位框：沿內牆一圈 1.6 厚、4 高，避開螺柱
      difference() {
        bx(0.4, 0.4, H - 4, W - 0.4, D - 0.4, H);
        bx(2.0, 2.0, H - 5, W - 2.0, D - 2.0, H + 1);
        for (p = LIDSCR) cyl_z(H - 6, H + 1, p[0], p[1], 26);
        bx(-1, HSY0 - LIPW - 1, H - 6, BOSS + 0.6, HSY0 + HSL + LIPW + 1, H + 1);          // 散熱片加厚區讓開
        bx(W - BOSS - 0.6, HSY0 - LIPW - 1, H - 6, W + 1, HSY0 + HSL + LIPW + 1, H + 1);
      }
    }
    // 沉頭螺絲孔
    for (p = LIDSCR) { cyl_z(H - 1, H + LT + 1, p[0], p[1], 3.4); translate([p[0], p[1], H + LT - 1.8]) cylinder(h = 1.81, d1 = 3.4, d2 = 6.8); }
    // 通風長孔（沿 y，避開肋）
    for (r = [[10, 76, 60, 140], [W - 76, W - 10, 50, 130], [105, 185, 30, 130], [SSX0 + 4, SSX0 + SSW - 4, SSY0 + 10, SSY0 + SSL - 10]])
      for (x = [r[0] : 7 : r[1]]) if (abs(x - round(x / LRIBP) * LRIBP) > 4)
        for (k = [0 : floor(D / LRIBP)]) {          // 在相鄰兩條肋之間分段，不切斷肋
          ya = max(r[2], k * LRIBP + 5); yb = min(r[3], (k + 1) * LRIBP - 5);
          if (yb - ya > 6) hull() { cyl_z(H - LRIBH - 1, H + LT + 1, x, ya, 3.5); cyl_z(H - LRIBH - 1, H + LT + 1, x, yb, 3.5); }
        }
    for (a = [0 : 20 : 340]) for (rr = [30, 46]) {
      x = TX + rr * cos(a); y = TY + rr * sin(a);
      if (abs(x - round(x / LRIBP) * LRIBP) > 4 && abs(y - round(y / LRIBP) * LRIBP) > 4) cyl_z(H - LRIBH - 1, H + LT + 1, x, y, 5);
    }
  }
}

// ================= 市電板護罩（翻過來印：頂面貼平台） =================
module mains_cover() {
  difference() {
    union() {
      bx(MCX0, MCY0, MCZ0, MCX1, MCY1, MCZ1);
      for (p = MCTAB) {
        s = p[1] < MCY0 ? 1 : -1;
        bx(p[0] - 7, min(p[1] - s * 5, p[1] + s * 4), MCZ0, p[0] + 7, max(p[1] - s * 5, p[1] + s * 4), MCZ0 + 3);
        hull() { bx(p[0] - 7, min(p[1] + s * 4, p[1] + s * 3.99), MCZ0 + 3, p[0] + 7, max(p[1] + s * 4, p[1] + s * 3.99), MCZ0 + 12);
                 bx(p[0] - 7, min(p[1] - s * 5, p[1] + s * 4), MCZ0 + 3, p[0] + 7, max(p[1] - s * 5, p[1] + s * 4), MCZ0 + 3.01); }
      }
    }
    bx(MCX0 + 2, MCY0 + 2, MCZ0 - 1, MCX1 - 2, MCY1 - 2, MCZ1 - 2);
    for (p = MCTAB) cyl_z(MCZ0 - 1, MCZ1, p[0], p[1], 3.4);
    for (y = [SSY0 + 20, SSY0 + SSL - 20]) bx(MCX0 - 1, y - 8, MCZ0 - 1, MCX0 + 3, y + 8, MCZ0 + 10);   // 出線缺口（朝變壓器）
    for (x = [MCX0 + 8 : 6 : MCX1 - 8]) bx(x - 1.5, MCY0 + 20, MCZ1 - 3, x + 1.5, MCY1 - 20, MCZ1 + 1); // 頂面散熱長孔
  }
}

// ================= 機腳 =================
module foot() { difference() { cylinder(h = 8, d = 22); translate([0, 0, -1]) cylinder(h = 10, d = 3.4); translate([0, 0, -1]) cylinder(h = 4, d = 6.5); } }
module foot_center() { difference() { cylinder(h = 8, d = 32); translate([0, 0, -1]) cylinder(h = 10, d = 6.6); translate([0, 0, -1]) cylinder(h = 6, d = 11.6, $fn = 6); } }
module feet() {
  for (p = FEET) translate([p[0], p[1], -FT - 8]) foot();
  translate([TX, TY, -FT - 8]) foot_center();
}

// ================= 散熱片與機內零件（示意，不列印） =================
module heatsink(side) {
  module hs0() {
    bx(-T, HSY0, HSZ0, -T + HSB, HSY0 + HSL, HSZ0 + HSH);
    for (k = [0 : NFIN - 1]) { y = HSY0 + 1 + k * (HSL - 2 - FINT) / (NFIN - 1); bx(-T - (HST - HSB), y, HSZ0, -T, y + FINT, HSZ0 + HSH); }
  }
  if (side == 0) hs0(); else translate([W, 0, 0]) mirror([1, 0, 0]) hs0();
}
module amp(side) {
  x0 = side == 0 ? AX0 : W - AX0 - 80;
  y0 = side == 0 ? AY0R : AY0L;
  bx(x0, y0, AZ0, x0 + 80, y0 + 90, AZ0 + 1.6);
  xi = side == 0 ? 1 : W - 5.5;                                  // IC 背板貼散熱片底板內面（x=1 / W-1）
  bx(xi, ICY - 10, AZ0 + 1.6, xi + 4.5, ICY + 10, AZ0 + 1.6 + 24);
  xc = side == 0 ? x0 + 55 : x0 + 25;
  cyl_z(AZ0 + 1.6, AZ0 + 30, xc, y0 + 20, 12); cyl_z(AZ0 + 1.6, AZ0 + 30, xc, y0 + 70, 12);
  cyl_z(AZ0 + 1.6, AZ0 + 40, side == 0 ? x0 + 40 : x0 + 40, y0 + 45, 20);
  for (p = side == 0 ? amp_holes_R() : amp_holes_L()) translate([p[0], p[1], 2]) cylinder(h = AZ0 - 2, d = 5.5, $fn = 6);
}
module psu() {
  bx(PX0, PY0, PZ0, PX0 + 92, PY0 + 120, PZ0 + 1.6);
  for (x = [PX0 + 23, PX0 + 69]) for (y = [PY0 + 30, PY0 + 72]) cyl_z(PZ0 + 1.6, PZ0 + 51.6, x, y, 35);
  for (x = [PX0 + 13, PX0 + 79]) bx(x - 10, PY0 + 100, PZ0 + 1.6, x + 10, PY0 + 104, PZ0 + 21.6);
}
module softstart() {
  bx(SSX0, SSY0, SSZ0, SSX0 + SSW, SSY0 + SSL, SSZ0 + 1.6);
  bx(SSX0 + 12, SSY0 + 8, SSZ0 + 1.6, SSX0 + 46, SSY0 + 38, SSZ0 + 30);          // 100 A 繼電器
  for (y = [SSY0 + 50, SSY0 + 62, SSY0 + 74, SSY0 + 86]) translate([SSX0 + 29, y, SSZ0 + 1.6 + 12]) rotate([90, 0, 0]) cylinder(h = 4, d = 22, center = true); // NTC ×4（直立）
}
module protect() {
  bx(PRX0, PRY0, PRZ0, PRX0 + PRW, PRY0 + PRL, PRZ0 + 1.6);
  bx(PRX0 + 18, PRY0 + 6, PRZ0 + 1.6, PRX0 + 40, PRY0 + 25, PRZ0 + 22);         // 歐姆龍繼電器
}
module transformer() {
  translate([TX, TY, TZ0]) { difference() { cylinder(h = TH - 5, d = TD, $fn = 64); translate([0, 0, -1]) cylinder(h = TH, d = 40); }
    translate([0, 0, TH - 5]) cylinder(h = 3, d = 100); translate([0, 0, TH - 2]) cylinder(h = 6, d = 10); }
}
module connectors() {
  for (x = [22, W - 22]) { cyl_y(-14, -T, x, 52, 24); cyl_y(5, 25, x, 52, 20); cyl_y(-16, -T, x, 20, 9); cyl_y(0, 12, x, 20, 9); }
  for (x = SPKX) for (z = SPKZ) { cyl_y(-18, -T, x, z, 10); cyl_y(0, 22, x, z, 6); }
  bx(W / 2 - 25, -T - 3, 19, W / 2 + 25, -T, 49); bx(W / 2 - 22, 0, 21, W / 2 + 22, 30, 47);
  cyl_y(D + T, D + T + 3, SWX, 39, 18); cyl_y(D - 30, D, SWX, 39, 15); cyl_y(D - 10, D + T + 2, LEDX, 39, 5);
}
module internals() { amp(0); amp(1); psu(); softstart(); protect(); transformer(); connectors(); }

// ---------- 選件 ----------
if (part == "all")              { tub(); lid(); mains_cover(); feet(); heatsink(0); heatsink(1); internals(); }
else if (part == "tub")          tub();
else if (part == "lid")          lid();
else if (part == "mains_cover")  mains_cover();
else if (part == "foot")         foot();
else if (part == "foot_center")  foot_center();
else if (part == "feet")         feet();
else if (part == "heatsink_R")   heatsink(0);
else if (part == "heatsink_L")   heatsink(1);
else if (part == "amp_R")        amp(0);
else if (part == "amp_L")        amp(1);
else if (part == "psu")          psu();
else if (part == "softstart")    softstart();
else if (part == "protect")      protect();
else if (part == "transformer")  transformer();
else if (part == "connectors")   connectors();

