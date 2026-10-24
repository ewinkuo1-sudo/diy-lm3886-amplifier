# -*- coding: utf-8 -*-
"""格狀梁（grillage）求解：把肋板當成 x、y 兩向交叉的梁網，節點 3 個自由度（w、θx、θy）。
給 chassis_v02_stiffness.py 用；手算等級，比單向梁準，但仍不是有限元素。

梁斷面＝一條肋＋分到的平板翼緣（寬＝肋距）。邊界節點（牆）w＝0，可選擇轉角也固定（固定端）。
"""
import numpy as np


def tsec(b, tf, n, w, h):
    Af, yf = b * tf, -tf / 2
    Ar, yr = n * w * h, h / 2
    yb = (Af * yf + Ar * yr) / (Af + Ar)
    I = b * tf ** 3 / 12 + Af * (yf - yb) ** 2 + n * w * h ** 3 / 12 + Ar * (yr - yb) ** 2
    J = (b * tf ** 3 + n * h * w ** 3) / 3
    return I, J, yb + tf, h - yb


def solve(xs, ys, E, G, sec, loads, fixed_edges=False):
    """xs、ys：網格線座標（含邊界）。sec(x0,y0,x1,y1)→(I,J,c_bot,c_top)。loads：{(i,j): P(N)}（向下為正）。
    回傳 (w 陣列 [i,j]、最大應力、最大撓度)。"""
    nx, ny = len(xs), len(ys)
    idx = lambda i, j: (j * nx + i) * 3
    N = nx * ny * 3
    K = np.zeros((N, N))
    members = []

    def add(i0, j0, i1, j1):
        x0, y0, x1, y1 = xs[i0], ys[j0], xs[i1], ys[j1]
        L = np.hypot(x1 - x0, y1 - y0)
        I, J, cb, ct = sec(x0, y0, x1, y1)
        # 區域座標：沿梁軸 s；DOF [w, θs(扭), θb(彎)]
        kb = E * I / L ** 3 * np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L],
                                        [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]])
        kt = G * J / L
        k = np.zeros((6, 6))
        # 順序：w0, θt0, θb0, w1, θt1, θb1
        bi = [0, 2, 3, 5]
        for a in range(4):
            for b in range(4):
                k[bi[a], bi[b]] += kb[a, b]
        k[1, 1] += kt; k[4, 4] += kt; k[1, 4] -= kt; k[4, 1] -= kt
        # 轉到整體：沿 x 的梁，扭轉轉角＝θx，彎曲轉角＝θy（w 對 x 的斜率，取 -θy 的慣例不影響結果，只要一致）
        T = np.zeros((6, 6))
        for n_ in (0, 3):
            T[n_, n_] = 1
            if x1 != x0:      # 沿 x：θt=θx、θb=θy
                T[n_ + 1, n_ + 1] = 1; T[n_ + 2, n_ + 2] = 1
            else:             # 沿 y：θt=θy、θb=θx
                T[n_ + 1, n_ + 2] = 1; T[n_ + 2, n_ + 1] = 1
        kg = T.T @ k @ T
        dofs = list(range(idx(i0, j0), idx(i0, j0) + 3)) + list(range(idx(i1, j1), idx(i1, j1) + 3))
        K[np.ix_(dofs, dofs)] += kg
        members.append((dofs, k, T, L, cb, ct, I, E))

    for j in range(ny):
        for i in range(nx - 1):
            add(i, j, i + 1, j)
    for i in range(nx):
        for j in range(ny - 1):
            add(i, j, i, j + 1)

    F = np.zeros(N)
    for (i, j), P in loads.items():
        F[idx(i, j)] += P
    fixed = []
    for j in range(ny):
        for i in range(nx):
            if i in (0, nx - 1) or j in (0, ny - 1):
                fixed.append(idx(i, j))
                if fixed_edges:
                    fixed += [idx(i, j) + 1, idx(i, j) + 2]
    free = np.setdiff1d(np.arange(N), fixed)
    u = np.zeros(N)
    u[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    smax = 0.0
    for dofs, k, T, L, cb, ct, I, E_ in members:
        ul = T @ u[dofs]
        f = k @ ul
        M = max(abs(f[2]), abs(f[5]))          # 兩端彎矩
        smax = max(smax, M * max(cb, ct) / I)
    w = u[0::3].reshape(ny, nx)
    return w, smax, float(np.abs(w).max())
