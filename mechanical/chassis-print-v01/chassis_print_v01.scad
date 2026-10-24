// LM3886 3D 列印機殼 第一版（2026-10-25）
// 座標：x 向右（從機後看；從正面看 x=0 是右側，所以 x=0 側的零件叫 _R）（寬）、y 由後往前（深）、z 向上。原點＝機內左後下角、底板上表面。
// 散熱片 176×33×60（蝦皮小白的生活工場）當左右側牆的一部分：底板嵌在側牆外側凹槽，鰭片露在機外，
// LM3886 從機內穿過窗口直接鎖在散熱片底板上（沿用放大板 V0.6「IC 貼板邊」的方案 B）。
// 單檔多件：用 -D part="xxx" 匯出單件 STL；-D opt="A"（上下蓋全列印分 4 塊）或 "B"（上下蓋用 2 mm 鋁板）。

part = "all";
opt  = "B";
$fn = 24;

// ---------- 主要尺寸 ----------
W = 290;        // 內寬
D = 280;        // 內深
H = 78;         // 內高（底板上表面到上蓋下表面）
T = 4;          // 列印牆厚
RW = 49;        // 側件回折段外寬（含轉角）：前後中央面板因此只剩 298-2×49 = 200 寬，一般列印機放得下
SPLIT = 150;    // 側件前後分件位置（y）
LAP = 8;        // 半搭接長度
LIP = 6;        // 上下蓋承接唇寬
LIPT = 5;       // 承接唇厚
PT = 2;         // 鋁板厚（方案 B）
TT = 3;         // 列印蓋板厚（方案 A）
ZB = -LIPT - PT;   // 牆底 z（-7）
ZT = H + PT;       // 牆頂 z（80）

// 散熱片（賣場標示 176×33×60；底板厚 5 與鰭片 23 片是估的，到貨要量）
HSL = 176; HSH = 60; HST = 33; HSB = 5; NFIN = 23; FINT = 1.5;
HSY0 = 12;                 // 散熱片後端離後內牆
HSZ0 = (H - HSH) / 2;      // 9：上下置中
BOSS = 4;                  // 牆內側加厚（讓凹槽深 5 之後仍留 3 mm 唇）
LIPW = 6;                  // 散熱片窗口四周留的唇寬
HOLE_IN = 3;               // 固定螺絲離凹槽邊

// ---------- 小工具 ----------
module bx(x0, y0, z0, x1, y1, z1) { translate([x0, y0, z0]) cube([x1 - x0, y1 - y0, z1 - z0]); }
module cyl_x(x0, x1, y, z, d) { translate([x0, y, z]) rotate([0, 90, 0]) cylinder(h = x1 - x0, d = d); }
module cyl_y(y0, y1, x, z, d) { translate([x, y0, z]) rotate([-90, 0, 0]) cylinder(h = y1 - y0, d = d); }
module cyl_z(z0, z1, x, y, d) { translate([x, y, z0]) cylinder(h = z1 - z0, d = d); }

// ---------- 左側件（前後一體，之後再切成兩件） ----------
module side_full_R() {
  difference() {
    union() {
      bx(-T, -T, ZB, 0, D + T, ZT);                 // 側牆
      bx(-T, -T, ZB, RW - T, 0, ZT);                // 後回折
      bx(-T, D, ZB, RW - T, D + T, ZT);             // 前回折
      // 上下蓋承接唇
      for (z = [[ZB, ZB + LIPT], [H - LIPT, H]]) {
        bx(0, 0, z[0], LIP, D, z[1]);
        bx(0, 0, z[0], RW - T, LIP, z[1]);
        bx(0, D - LIP, z[0], RW - T, D, z[1]);
      }
      // 散熱片區牆內加厚
      bx(0, HSY0 - LIPW, HSZ0 - LIPW, BOSS, HSY0 + HSL + LIPW, HSZ0 + HSH + LIPW);
      // 與中央面板的半搭接（外半層伸出 LAP）
      bx(RW - T, -T, ZB, RW - T + LAP, -T / 2, ZT);
      bx(RW - T, D + T / 2, ZB, RW - T + LAP, D + T, ZT);
    }
    // 散熱片凹槽（從外側進，深＝底板厚）與窗口
    bx(-T - 1, HSY0 - 0.2, HSZ0 - 0.2, -T + HSB, HSY0 + HSL + 0.2, HSZ0 + HSH + 0.2);
    bx(-T - 1, HSY0 + LIPW, HSZ0 + LIPW, BOSS + 1, HSY0 + HSL - LIPW, HSZ0 + HSH - LIPW);
    // 散熱片固定螺絲 M3 ×4（從機內鎖進散熱片底板的攻牙孔）
    for (y = [HSY0 + HOLE_IN, HSY0 + HSL - HOLE_IN]) for (z = [HSZ0 + HOLE_IN, HSZ0 + HSH - HOLE_IN])
      cyl_x(-T - 1, BOSS + 1, y, z, 3.2);
    // 後回折：輸入端子（XLR 上、RCA 下）
    cyl_y(-T - 1, 1, 20.5, 55, 24);
    for (a = [0, 120, 240]) rotate([0, 0, 0]) translate([20.5 + 13 * cos(a + 90), 0, 55 + 13 * sin(a + 90)]) cyl_y(-T - 1, 1, 0, 0, 3.2);
    cyl_y(-T - 1, 1, 20.5, 22, 9.5);
    // 面板搭接螺絲（M3 熱熔螺母）
    for (z = [12, 66]) { cyl_y(-T - 1, 1, RW - T + LAP / 2, z, 2.8); cyl_y(D - 1, D + T + 1, RW - T + LAP / 2, z, 2.8); }
  }
}
// 前後分件：外半層半搭接（後件外半伸到 SPLIT+LAP，前件內半從 SPLIT-LAP 起）
module side_rear_R() {
  intersection() {
    side_full_R();
    union() { bx(-50, -50, -50, 100, SPLIT, 200); bx(-50, SPLIT, -50, -T / 2, SPLIT + LAP, 200); }
  }
}
module side_front_R() {
  intersection() {
    side_full_R();
    union() { bx(-50, SPLIT, -50, 100, D + 50, 200); bx(-T / 2, SPLIT - LAP, -50, 100, SPLIT, 200); }
  }
}
module mirror_L() { translate([W, 0, 0]) mirror([1, 0, 0]) children(); }

// ---------- 中央後面板（200 寬）：喇叭端子 ×4、IEC 電源座、trigger ----------
module rear_panel() {
  x0 = RW - T; x1 = W + T - RW;
  difference() {
    union() {
      bx(x0, -T, ZB, x1, 0, ZT);
      bx(x0 - LAP, -T / 2, ZB, x1 + LAP, 0, ZT);                     // 內半層伸進回折
      for (z = [[ZB, ZB + LIPT], [H - LIPT, H]]) bx(x0, 0, z[0], x1, LIP, z[1]);
    }
    for (x = [80, 99, 191, 210]) cyl_y(-T - 1, LIP + 1, x, 30, 8.5);   // 喇叭端子
    bx(W / 2 - 24, -T - 1, 20, W / 2 + 24, LIP + 1, 48);              // IEC C14 含保險絲座 48×28
    for (x = [W / 2 - 20, W / 2 + 20]) cyl_y(-T - 1, 1, x, 34, 3.2);
    cyl_y(-T - 1, 1, 112, 30, 8);                                      // 12 V trigger 3.5 mm 母座
    for (x = [x0 - LAP / 2, x1 + LAP / 2]) for (z = [12, 66]) cyl_y(-T - 1, 1, x, z, 3.2);
  }
}
// ---------- 中央前面板（200 寬）：電源鈕、LED ----------
module front_panel() {
  x0 = RW - T; x1 = W + T - RW;
  difference() {
    union() {
      bx(x0, D, ZB, x1, D + T, ZT);
      bx(x0 - LAP, D, ZB, x1 + LAP, D + T / 2, ZT);
      for (z = [[ZB, ZB + LIPT], [H - LIPT, H]]) bx(x0, D - LIP, z[0], x1, D, z[1]);
    }
    cyl_y(D - LIP - 1, D + T + 1, W / 2, 39, 16);
    cyl_y(D - LIP - 1, D + T + 1, W / 2 + 30, 39, 5.2);
    for (x = [x0 - LAP / 2, x1 + LAP / 2]) for (z = [12, 66]) cyl_y(D - 1, D + T + 1, x, z, 3.2);
  }
}

// ---------- 方案 B：2 mm 鋁板上下蓋 ----------
module plate_holes() { $fn = 12;
  for (x = [LIP / 2 + 1, W / 2, W - LIP / 2 - 1]) for (y = [LIP / 2 + 1, D / 2, D - LIP / 2 - 1])
    if (!(x == W / 2 && y == D / 2)) cyl_z(-20, 100, x, y, 3.4);
}
module plate_bottom() { $fn = 12;
  difference() {
    bx(0.3, 0.3, -PT, W - 0.3, D - 0.3, 0);
    plate_holes();
    for (xs = [[12, 80], [W - 80, W - 12]]) for (x = [xs[0] : 10 : xs[1]]) for (y = [30 : 10 : 100]) cyl_z(-20, 100, x, y, 5);  // 放大板下通風
    cyl_z(-20, 100, W / 2, 210, 6.5);                                                                      // 變壓器中心螺栓
  }
}
module plate_top() { $fn = 12;
  difference() {
    bx(0.3, 0.3, H, W - 0.3, D - 0.3, H + PT);
    plate_holes();
    for (x = [95 : 10 : 195]) for (y = [30 : 10 : 130]) cyl_z(-20, 100, x, y, 5);     // 電源板上方
    for (x = [12 : 10 : 80]) for (y = [30 : 10 : 100]) cyl_z(-20, 100, x, y, 5);      // 放大板 L 上方
    for (x = [W - 80 : 10 : W - 12]) for (y = [30 : 10 : 100]) cyl_z(-20, 100, x, y, 5);
    for (a = [0 : 30 : 330]) for (r = [25, 40, 55]) cyl_z(-20, 100, W / 2 + r * cos(a), 210 + r * sin(a), 5);  // 變壓器上方
  }
}

// ---------- 方案 A：列印蓋板，各分 4 塊（145×140），邊緣半搭接，底板加肋 ----------
module tile(i, j, z0, z1, top) { $fn = 12;
  x0 = i == 0 ? 0.3 : W / 2;  x1 = i == 0 ? W / 2 : W - 0.3;
  y0 = j == 0 ? 0.3 : D / 2;  y1 = j == 0 ? D / 2 : D - 0.3;
  zm = (z0 + z1) / 2;
  difference() {
    union() {
      bx(x0, y0, z0, x1, y1, z1);
      // 半搭接：i==0 的塊在接縫伸出下半層，i==1 的塊伸出上半層（y 向同理）
      if (i == 0) bx(x1, y0, z0, x1 + LAP, y1, zm); else bx(x0 - LAP, y0, zm, x0, y1, z1);
      if (j == 0) bx(x0, y1, z0, x1, y1 + LAP, zm); else bx(x0, y0 - LAP, zm, x1, y0, z1);
      if (!top) for (x = [x0 + 20 : 45 : x1 - 10]) bx(x, y0, z1, x + 3, y1, z1 + 4);         // 底板肋
      if (!top) for (y = [y0 + 20 : 45 : y1 - 10]) bx(x0, y, z1, x1, y + 3, z1 + 4);
    }
    if (i == 0) bx(x1, y0 - 1, zm, x1 + LAP + 1, y1 + 1, z1 + 10); else bx(x0 - LAP - 1, y0 - 1, z0 - 10, x0, y1 + 1, zm);
    if (j == 0) bx(x0 - 1, y1, zm, x1 + 1, y1 + LAP + 1, z1 + 10); else bx(x0 - 1, y0 - LAP - 1, z0 - 10, x1 + 1, y0, zm);
    plate_holes();
    if (top) for (x = [x0 + 15 : 12 : x1 - 15]) bx(x, y0 + 15, z0 - 1, x + 4, y1 - 15, z1 + 1);   // 通風長條
    else { for (x = [x0 + 12 : 10 : x1 - 12]) for (y = [y0 + 12 : 10 : y1 - 12]) if (y < 105) cyl_z(-20, 100, x, y, 5); cyl_z(-20, 100, W / 2, 210, 6.5); }
  }
}
module tile_bottom(i, j) { tile(i, j, -PT, -PT + TT, false); }
module tile_top(i, j)    { tile(i, j, H + PT - TT, H + PT, true); }

// ---------- 機腳 ×5（4 角＋變壓器下） ----------
module foot() { difference() { cylinder(h = 8, d = 20); translate([0, 0, -1]) cylinder(h = 10, d = 3.2); } }
module feet() { for (p = [[20, 20], [W - 20, 20], [20, D - 20], [W - 20, D - 20], [W / 2, 210]]) translate([p[0], p[1], -PT - 8]) foot(); }

// ---------- 散熱片（左）：底板嵌在凹槽、鰭片朝外 ----------
module heatsink_R() {
  bx(-T, HSY0, HSZ0, -T + HSB, HSY0 + HSL, HSZ0 + HSH);
  for (k = [0 : NFIN - 1]) { y = HSY0 + 1 + k * (HSL - 2 - FINT) / (NFIN - 1); bx(-T - (HST - HSB), y, HSZ0, -T, y + FINT, HSZ0 + HSH); }
}

// ---------- 機內零件示意（不列印） ----------
Z0 = 8; PCB = 1.6;
module pcb(x0, y0, x1, y1) { bx(x0, y0, Z0, x1, y1, Z0 + PCB); }
module amp_R() {                                  // 放大板 V0.6.1：90（沿牆）×80，IC 貼板邊直接鎖散熱片
  pcb(1, 20, 81, 110);
  bx(1, 55, Z0 + PCB, 5.5, 75, Z0 + PCB + 21);   // LM3886T 直立
  for (y = [30, 95]) cyl_z(Z0 + PCB, Z0 + PCB + 25, 60, y, 12);
  cyl_z(Z0 + PCB, Z0 + PCB + 40, 40, 65, 20);
}
module psu() {                                   // 電源板 V0.6.1 92×120：4 顆 Ø35×50、GBJ×2
  pcb(99, 20, 191, 140);
  for (x = [122, 168]) for (y = [50, 92]) cyl_z(Z0 + PCB, Z0 + PCB + 50, x, y, 35);
  for (x = [112, 178]) bx(x - 10, 120, Z0 + PCB, x + 10, 124, Z0 + PCB + 20);
}
module ctrl()  { pcb(5, 150, 75, 270); for (y = [165, 195, 225, 255]) bx(20, y - 6, Z0 + PCB, 49, y + 6, Z0 + PCB + 16); }
module mains() { pcb(215, 170, 285, 270); bx(230, 200, Z0 + PCB, 259, 212, Z0 + PCB + 16); cyl_z(Z0 + PCB, Z0 + PCB + 20, 250, 240, 20); }
module transformer() {
  translate([W / 2, 210, 0]) { cylinder(h = 50, d = 120); translate([0, 0, 50]) cylinder(h = 3, d = 100); translate([0, 0, 53]) cylinder(h = 8, d = 10); }
}
module connectors() {
  for (x = [20.5, W - 20.5]) { cyl_y(-14, -T, x, 55, 24); cyl_y(-16, -T, x, 22, 9); }
  for (x = [80, 99, 191, 210]) cyl_y(-16, -T, x, 30, 8);
  bx(W / 2 - 25, -T - 3, 19, W / 2 + 25, -T, 49);
  cyl_y(D + T, D + T + 3, W / 2, 39, 16);
}
module internals() { amp_R(); mirror_L() amp_R(); psu(); ctrl(); mains(); transformer(); connectors(); }

// ---------- 選件 ----------
module printed_shell() { side_rear_R(); side_front_R(); mirror_L() side_rear_R(); mirror_L() side_front_R(); rear_panel(); front_panel(); feet(); }
module covers() {
  if (opt == "B") { plate_bottom(); plate_top(); }
  else { for (i = [0, 1]) for (j = [0, 1]) { tile_bottom(i, j); tile_top(i, j); } }
}

if (part == "all")              { printed_shell(); covers(); heatsink_R(); mirror_L() heatsink_R(); internals(); }
else if (part == "side_rear_R")  side_rear_R();
else if (part == "side_front_R") side_front_R();
else if (part == "side_rear_L")  mirror_L() side_rear_R();
else if (part == "side_front_L") mirror_L() side_front_R();
else if (part == "rear_panel")   rear_panel();
else if (part == "front_panel")  front_panel();
else if (part == "foot")         foot();
else if (part == "feet")         feet();
else if (part == "plate_bottom") plate_bottom();
else if (part == "plate_top")    plate_top();
else if (part == "tile_bottom_0") tile_bottom(0, 0);
else if (part == "tile_bottom_1") tile_bottom(1, 0);
else if (part == "tile_bottom_2") tile_bottom(0, 1);
else if (part == "tile_bottom_3") tile_bottom(1, 1);
else if (part == "tile_top_0")   tile_top(0, 0);
else if (part == "tile_top_1")   tile_top(1, 0);
else if (part == "tile_top_2")   tile_top(0, 1);
else if (part == "tile_top_3")   tile_top(1, 1);
else if (part == "heatsink_R")   heatsink_R();
else if (part == "heatsink_L")   mirror_L() heatsink_R();
else if (part == "amp_R")        amp_R();
else if (part == "amp_L")        mirror_L() amp_R();
else if (part == "psu")          psu();
else if (part == "ctrl")         ctrl();
else if (part == "mains")        mains();
else if (part == "transformer")  transformer();
else if (part == "connectors")   connectors();
