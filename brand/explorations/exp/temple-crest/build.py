#!/usr/bin/env python3
"""exp/temple-crest — the founder's third brief: drop "wholly minimal";
make it unmistakably a TEMPLE, remarkable, while keeping logo/icon/symbol
craft (reduction by DERIVATION, not shrinking).

Three marks, each in full + icon + glyph registers, all from the murti canon
(grid.json numbers; bindu = linga-from-above; gold = god-points only):

  jyotirlinga  the emblem: tripundra-marked linga in the two-tier lotus cup,
               basin with waterline + carved sun medallions, abhisheka
               teardrop under a 12-sun prabhavali halo
  rtayantra    the seal: square bhupura with four T-gates, 24-bead mala,
               12 carved sun medallions, two-tier lotus, and the nali channel
               leaving through the south gate
  garbhagriha  the crest: sanctum doorway — pillars, ogee prabhavali arch
               garlanded with 12 gold buds (Adityas), kalasha finial, the
               linga-in-basin inside, threshold steps below

Temple vocabulary used deliberately: tripundra (Shaiva signature), prabhavali,
kalasha, bhupura, mala beading, twin-line "carved groove" strokes.

    python3 build.py    # writes candidates/*.svg + gallery.html
"""
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent

COLORWAYS = {
    "light": {"ink": "#1A1A1A", "gold": "#C8A15A", "punch": "#F7F3E9"},
    "night": {"ink": "#F7F3E9", "gold": "#C8A15A", "punch": "#1C1A3D"},
}


def F(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def line(x1, y1, x2, y2, col, sw, cap="round"):
    return (f'<line x1="{F(x1)}" y1="{F(y1)}" x2="{F(x2)}" y2="{F(y2)}" '
            f'stroke="{col}" stroke-width="{sw}" stroke-linecap="{cap}"/>')


def dot(x, y, r, col):
    return f'<circle cx="{F(x)}" cy="{F(y)}" r="{F(r)}" fill="{col}"/>'


def circ(x, y, r, col, sw):
    return (f'<circle cx="{F(x)}" cy="{F(y)}" r="{F(r)}" fill="none" '
            f'stroke="{col}" stroke-width="{sw}"/>')


def path(d, col, sw, fill="none", cap="round"):
    return (f'<path d="{d}" fill="{fill}" stroke="{col}" stroke-width="{sw}" '
            f'stroke-linecap="{cap}" stroke-linejoin="round"/>')


def fpath(d, col):
    return f'<path d="{d}" fill="{col}"/>'


def teardrop(cx, top_y, h, col):
    """The abhisheka drop: point up, round belly below."""
    w = h * 0.62
    by = top_y + h * 0.70
    return fpath(f"M {F(cx)} {F(top_y)} "
                 f"C {F(cx - w * 0.22)} {F(top_y + h * 0.34)} {F(cx - w / 2)} {F(by - h * 0.24)} {F(cx - w / 2)} {F(by)} "
                 f"A {F(w / 2)} {F(w / 2)} 0 1 0 {F(cx + w / 2)} {F(by)} "
                 f"C {F(cx + w / 2)} {F(by - h * 0.24)} {F(cx + w * 0.22)} {F(top_y + h * 0.34)} {F(cx)} {F(top_y)} Z", col)


def tripundra(cx, dome_cy, dome_r, col, sw=5):
    """Three vibhuti arcs across the dome, bowing gently down, shorter upward."""
    els = []
    for i, (dy, hw) in enumerate([(-0.42, 0.60), (-0.16, 0.76), (0.10, 0.84)]):
        y = dome_cy + dy * dome_r
        w = hw * dome_r
        els.append(path(f"M {F(cx - w)} {F(y)} Q {F(cx)} {F(y + dome_r * 0.16)} {F(cx + w)} {F(y)}",
                        col, sw))
    return els


def cubic(p0, p1, p2, p3, t):
    mt = 1 - t
    x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
    y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
    dx = 3 * mt**2 * (p1[0] - p0[0]) + 6 * mt * t * (p2[0] - p1[0]) + 3 * t**2 * (p3[0] - p2[0])
    dy = 3 * mt**2 * (p1[1] - p0[1]) + 6 * mt * t * (p2[1] - p1[1]) + 3 * t**2 * (p3[1] - p2[1])
    return (x, y), (dx, dy)


def bud(x, y, out_deg, size, col):
    """Lotus bud / flame of the prabhavali garland, pointing along out_deg."""
    s = size
    d = (f"M 0 0 C {F(-s * 0.34)} {F(-s * 0.26)} {F(-s * 0.30)} {F(-s * 0.68)} 0 {F(-s)} "
         f"C {F(s * 0.30)} {F(-s * 0.68)} {F(s * 0.34)} {F(-s * 0.26)} 0 0 Z")
    return (f'<g transform="translate({F(x)} {F(y)}) rotate({F(out_deg + 90)})">'
            f'<path d="{d}" fill="{col}"/></g>')


def elev_lotus_cup(c, cx, seat_y, hw, petal_h, punch=True):
    """Elevation lotus cup: back tips peeking + front pointed petals with real
    ogive bellies and varied heights (centre tallest), punch-filled so they
    occlude what sits behind (carved relief order)."""
    els = []
    n_front = 5
    step = 2 * hw / n_front
    heights = [0.84, 0.95, 1.08, 0.95, 0.84]
    fill = c["punch"] if punch else "none"
    for k in range(n_front - 1):
        x = cx - hw + (k + 1) * step
        tip_y = seat_y - petal_h * 1.18
        els.append(path(f"M {F(x - step * 0.36)} {F(seat_y - petal_h * 0.50)} "
                        f"Q {F(x - step * 0.26)} {F(tip_y + petal_h * 0.30)} {F(x)} {F(tip_y)} "
                        f"Q {F(x + step * 0.26)} {F(tip_y + petal_h * 0.30)} {F(x + step * 0.36)} {F(seat_y - petal_h * 0.50)}",
                        c["ink"], 2.2))
    for k in range(n_front):
        x = cx - hw + (k + 0.5) * step
        ph = petal_h * heights[k]
        tip_y = seat_y - ph
        d = (f"M {F(x - step * 0.50)} {F(seat_y)} "
             f"C {F(x - step * 0.66)} {F(seat_y - ph * 0.44)} {F(x - step * 0.30)} {F(tip_y + ph * 0.26)} {F(x)} {F(tip_y)} "
             f"C {F(x + step * 0.30)} {F(tip_y + ph * 0.26)} {F(x + step * 0.66)} {F(seat_y - ph * 0.44)} {F(x + step * 0.50)} {F(seat_y)} Z")
        els.append(f'<path d="{d}" fill="{fill}" stroke="{c["ink"]}" stroke-width="2.6" stroke-linejoin="round"/>')
        els.append(path(f"M {F(x)} {F(tip_y + ph * 0.24)} L {F(x)} {F(seat_y - ph * 0.18)}",
                        c["ink"], 1.3))
    return els


def wave(x0, x1, y, col, sw, n=9):
    seg = (x1 - x0) / n
    d = [f"M {F(x0)} {F(y)}"]
    for i in range(n):
        d.append(f"q {F(seg / 2)} {F(-seg * 0.42)} {F(seg)} 0")
    return path(" ".join(d), col, sw)


# =============================================================== jyotirlinga
def jyotir_full(c):
    W = 640
    cx = 320.0
    els = []
    hcx, hcy, hr = cx, 316.0, 214.0
    for r_, sw in ((hr - 9, 2.0), (hr + 9, 2.0)):
        p0 = (hcx + r_ * math.cos(math.radians(-166)), hcy + r_ * math.sin(math.radians(-166)))
        p1 = (hcx + r_ * math.cos(math.radians(-14)), hcy + r_ * math.sin(math.radians(-14)))
        els.append(path(f"M {F(p0[0])} {F(p0[1])} A {F(r_)} {F(r_)} 0 0 1 {F(p1[0])} {F(p1[1])}",
                        c["ink"], sw))
    for a in (-166, -14):
        x = hcx + hr * math.cos(math.radians(a))
        y = hcy + hr * math.sin(math.radians(a))
        els.append(dot(x, y, 5, c["gold"]))
    for k in range(12):
        a = -159 + k * (138 / 11)
        x = hcx + hr * math.cos(math.radians(a))
        y = hcy + hr * math.sin(math.radians(a))
        els.append(dot(x, y, 6, c["gold"]))

    els.append(teardrop(cx, 128, 62, c["gold"]))

    dome_r = 75.0
    dome_cy = 285.0
    els.append(path(f"M {F(cx - dome_r)} {F(330)} L {F(cx - dome_r)} {F(dome_cy)} "
                    f"A {F(dome_r)} {F(dome_r)} 0 0 1 {F(cx + dome_r)} {F(dome_cy)} L {F(cx + dome_r)} {F(330)}",
                    c["ink"], 4))
    els += tripundra(cx, dome_cy, dome_r, c["ink"])

    els += elev_lotus_cup(c, cx, 400.0, 132.0, 66.0)

    els.append(path(f"M {F(cx - 150)} 406 C {F(cx - 140)} 452 {F(cx - 90)} 478 {F(cx)} 478 "
                    f"C {F(cx + 90)} 478 {F(cx + 140)} 452 {F(cx + 150)} 406", c["ink"], 4))
    els.append(path(f"M {F(cx - 150)} 406 L {F(cx + 150)} 406", c["ink"], 2.2))
    els.append(wave(cx - 126, cx + 126, 422, c["gold"], 2.4, n=8))
    for sx, sy, r_ in ((0, 460, 8.5), (58, 455, 8), (112, 440, 7)):
        for s in ((1,) if sx == 0 else (-1, 1)):
            els.append(circ(cx + s * sx, sy, r_, c["ink"], 2))
            els.append(dot(cx + s * sx, sy, r_ * 0.42, c["gold"]))

    els.append(line(cx - 9, 479, cx - 9, 502, c["ink"], 2.5))
    els.append(line(cx + 9, 479, cx + 9, 502, c["ink"], 2.5))
    els.append(dot(cx, 516, 5.5, c["gold"]))
    els.append(path(f"M {F(cx - 34)} 528 Q {F(cx)} 542 {F(cx + 34)} 528", c["ink"], 2.5))
    return els, (W, 590)


def jyotir_icon(c):
    cx = 256.0
    els = []
    els.append(teardrop(cx, 52, 46, c["gold"]))
    dome_r = 74.0
    dome_cy = 210.0
    els.append(path(f"M {F(cx - dome_r)} {F(246)} L {F(cx - dome_r)} {F(dome_cy)} "
                    f"A {F(dome_r)} {F(dome_r)} 0 0 1 {F(cx + dome_r)} {F(dome_cy)} L {F(cx + dome_r)} {F(246)}",
                    c["ink"], 7))
    els += tripundra(cx, dome_cy, dome_r, c["ink"], sw=7)
    els += elev_lotus_cup(c, cx, 318.0, 118.0, 62.0)
    els.append(path(f"M {F(cx - 140)} 322 C {F(cx - 130)} 366 {F(cx - 84)} 390 {F(cx)} 390 "
                    f"C {F(cx + 84)} 390 {F(cx + 130)} 366 {F(cx + 140)} 322", c["ink"], 7))
    els.append(wave(cx - 96, cx + 96, 348, c["gold"], 4, n=6))
    return els, (512, 448)


def jyotir_glyph(c):
    cx = 256.0
    els = []
    els.append(teardrop(cx, 58, 64, c["gold"]))
    dome_r = 120.0
    dome_cy = 290.0
    els.append(path(f"M {F(cx - dome_r)} {F(360)} L {F(cx - dome_r)} {F(dome_cy)} "
                    f"A {F(dome_r)} {F(dome_r)} 0 0 1 {F(cx + dome_r)} {F(dome_cy)} L {F(cx + dome_r)} {F(360)}",
                    c["ink"], 13))
    els += tripundra(cx, dome_cy, dome_r, c["ink"], sw=13)
    els.append(path(f"M {F(cx - 168)} 372 Q {F(cx)} 452 {F(cx + 168)} 372", c["ink"], 13))
    return els, (512, 470)


# ================================================================= rtayantra
def _square_with_gaps(cx, cy, half, gap, col, sw):
    """Square outline with a centred gap in each side (for the gates)."""
    els = []
    for rot in range(4):
        a = math.radians(rot * 90)
        ca, sa = math.cos(a), math.sin(a)

        def T(x, y):
            return (cx + x * ca - y * sa, cy + x * sa + y * ca)

        for x0, x1 in ((-half, -gap), (gap, half)):
            p, q = T(x0, -half), T(x1, -half)
            els.append(line(p[0], p[1], q[0], q[1], col, sw, cap="square"))
    return els


def _gate(cx, cy, half_in, half_out, col, sw):
    """One T-gate per side: stepped portal breaking both squares."""
    els = []
    for rot in range(4):
        a = math.radians(rot * 90)
        ca, sa = math.cos(a), math.sin(a)

        def T(x, y):
            return (cx + x * ca - y * sa, cy + x * sa + y * ca)

        pts = [(-32, -half_out), (-32, -half_out - 18), (-48, -half_out - 18),
               (-48, -half_out - 32), (48, -half_out - 32), (48, -half_out - 18),
               (32, -half_out - 18), (32, -half_out)]
        d = "M " + " L ".join(f"{F(T(x, y)[0])} {F(T(x, y)[1])}" for x, y in pts)
        els.append(path(d, col, sw, cap="square"))
        for jx in (-22, 22):
            p, q = T(jx, -half_in), T(jx, -half_out)
            els.append(line(p[0], p[1], q[0], q[1], col, sw * 0.7, cap="square"))
    return els


def yantra_petal(cx, cy, tip_r, base_r, deg, hw_deg, col, sw, inner=True, fill="none"):
    def P(r_, d_):
        return (cx + r_ * math.cos(math.radians(d_)), cy + r_ * math.sin(math.radians(d_)))

    els = []
    tx, ty = P(tip_r, deg)
    b1 = P(base_r, deg - hw_deg)
    b2 = P(base_r, deg + hw_deg)
    mid = base_r + (tip_r - base_r) * 0.55
    c1 = P(mid, deg - hw_deg * 1.32)
    c2 = P(tip_r * 0.97, deg - hw_deg * 0.35)
    c3 = P(tip_r * 0.97, deg + hw_deg * 0.35)
    c4 = P(mid, deg + hw_deg * 1.32)
    d = (f"M {F(b1[0])} {F(b1[1])} C {F(c1[0])} {F(c1[1])} {F(c2[0])} {F(c2[1])} {F(tx)} {F(ty)} "
         f"C {F(c3[0])} {F(c3[1])} {F(c4[0])} {F(c4[1])} {F(b2[0])} {F(b2[1])}")
    els.append(f'<path d="{d} Z" fill="{fill}" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round"/>')
    if inner:
        it = P(tip_r * 0.86, deg)
        i1 = P(base_r + 8, deg - hw_deg * 0.5)
        i2 = P(base_r + 8, deg + hw_deg * 0.5)
        m1 = P(mid, deg - hw_deg * 0.62)
        m2 = P(mid, deg + hw_deg * 0.62)
        els.append(path(f"M {F(i1[0])} {F(i1[1])} Q {F(m1[0])} {F(m1[1])} {F(it[0])} {F(it[1])} "
                        f"Q {F(m2[0])} {F(m2[1])} {F(i2[0])} {F(i2[1])}", col, 1.3))
    return els


def yantra_full(c):
    cx = cy = 320.0
    els = []
    els += _square_with_gaps(cx, cy, 252, 32, c["ink"], 3)
    els += _square_with_gaps(cx, cy, 234, 22, c["ink"], 1.6)
    els += _gate(cx, cy, 234, 252, c["ink"], 3)
    for k in range(24):
        a = k * 15 + 7.5
        els.append(dot(cx + 216 * math.cos(math.radians(a)),
                       cy + 216 * math.sin(math.radians(a)), 3.2, c["ink"]))
    els.append(circ(cx, cy, 200, c["ink"], 1.6))
    els.append(circ(cx, cy, 164, c["ink"], 1.6))
    for k in range(12):
        a = math.radians(-90 + k * 30)
        mx, my = cx + 182 * math.cos(a), cy + 182 * math.sin(a)
        els.append(circ(mx, my, 13, c["ink"], 2.4))
        els.append(dot(mx, my, 5.5, c["gold"]))
        for j in range(8):
            b = math.radians(j * 45 + 22.5)
            els.append(dot(mx + 9.5 * math.cos(b), my + 9.5 * math.sin(b), 1.5, c["ink"]))
    for k in range(12):
        els += yantra_petal(cx, cy, 150, 58, -90 + 15 + k * 30, 12.5, c["ink"], 2.4)
    for k in range(12):
        els += yantra_petal(cx, cy, 104, 48, -90 + k * 30, 10, c["ink"], 0, inner=False, fill=c["ink"])
    els.append(circ(cx, cy, 44, c["ink"], 2.5))
    els.append(circ(cx, cy, 38, c["ink"], 1.3))
    els.append(dot(cx, cy, 15, c["gold"]))
    els.append(f'<rect x="{F(cx - 7)}" y="366" width="14" height="204" fill="{c["punch"]}"/>')
    els.append(line(cx - 7, 366, cx - 7, 570, c["ink"], 2.4, cap="butt"))
    els.append(line(cx + 7, 366, cx + 7, 570, c["ink"], 2.4, cap="butt"))
    els.append(dot(cx, 584, 5.5, c["gold"]))
    return els, (640, 640)


def yantra_icon(c):
    cx = cy = 256.0
    els = [circ(cx, cy, 236, c["ink"], 4), circ(cx, cy, 196, c["ink"], 2)]
    for k in range(12):
        a = math.radians(-90 + 15 + k * 30)
        els.append(dot(cx + 216 * math.cos(a), cy + 216 * math.sin(a), 10, c["gold"]))
    for k in range(12):
        els += yantra_petal(cx, cy, 170, 56, -90 + k * 30, 11, c["ink"], 0, inner=False, fill=c["ink"])
    els.append(circ(cx, cy, 46, c["ink"], 3.5))
    els.append(dot(cx, cy, 17, c["gold"]))
    els.append(f'<rect x="{F(cx - 8)}" y="{F(cy + 40)}" width="16" height="162" fill="{c["punch"]}"/>')
    els.append(line(cx - 8, cy + 40, cx - 8, cy + 202, c["ink"], 3, cap="butt"))
    els.append(line(cx + 8, cy + 40, cx + 8, cy + 202, c["ink"], 3, cap="butt"))
    els.append(dot(cx, cy + 214, 8, c["gold"]))
    return els, (512, 512)


def yantra_glyph(c):
    cx = cy = 256.0
    els = [circ(cx, cy, 150, c["ink"], 22)]
    els.append(dot(cx, cy, 62, c["gold"]))
    els.append(f'<rect x="{F(cx - 24)}" y="{F(cy + 118)}" width="48" height="92" fill="{c["punch"]}"/>')
    els.append(line(cx - 24, cy + 118, cx - 24, cy + 208, c["ink"], 20, cap="butt"))
    els.append(line(cx + 24, cy + 118, cx + 24, cy + 208, c["ink"], 20, cap="butt"))
    return els, (512, 512)


# =============================================================== garbhagriha
ARCH_L = [((148.0, 300.0), (148.0, 216.0), (230.0, 186.0), (276.0, 150.0)),
          ((276.0, 150.0), (300.0, 132.0), (312.0, 124.0), (320.0, 104.0))]


def _arch_d(chain):
    (p0, c1, c2, p1), (q0, d1, d2, q1) = chain
    return (f"M {F(p0[0])} {F(p0[1])} C {F(c1[0])} {F(c1[1])} {F(c2[0])} {F(c2[1])} {F(p1[0])} {F(p1[1])} "
            f"C {F(d1[0])} {F(d1[1])} {F(d2[0])} {F(d2[1])} {F(q1[0])} {F(q1[1])}")


def _mirror_chain(chain):
    return [tuple((640 - p[0], p[1]) for p in seg) for seg in chain]


def door_full(c):
    els = []
    inner = [((162.0, 300.0), (162.0, 226.0), (240.0, 196.0), (284.0, 160.0)),
             ((284.0, 160.0), (304.0, 144.0), (313.0, 136.0), (320.0, 122.0))]
    for chain in (ARCH_L, _mirror_chain(ARCH_L)):
        els.append(path(_arch_d(chain), c["ink"], 3.2))
    for chain in (inner, _mirror_chain(inner)):
        els.append(path(_arch_d(chain), c["ink"], 1.6))
    for chain, sgn in ((ARCH_L, -1), (_mirror_chain(ARCH_L), 1)):
        for i, t in enumerate((0.18, 0.40, 0.62, 0.82, 0.96, 1.18)):
            seg, tt = (chain[0], t) if t <= 1 else (chain[1], t - 1)
            (x, y), (dx, dy) = cubic(*seg, tt)
            n = math.degrees(math.atan2(dy, dx)) + (90 if sgn < 0 else -90)
            nx, ny = math.cos(math.radians(n)), math.sin(math.radians(n))
            els.append(bud(x + nx * 10, y + ny * 10, n, 21, c["gold"]))
    els.append(circ(320, 84, 11, c["ink"], 2.6))
    els.append(line(308, 70, 332, 70, c["ink"], 2.6))
    els.append(path("M 320 70 C 314 62 315 56 320 50 C 325 56 326 62 320 70", c["ink"], 2))
    for px in (148, 492):
        els.append(line(px - 8, 300, px - 8, 500, c["ink"], 3.2))
        els.append(line(px + 8, 300, px + 8, 500, c["ink"], 3.2))
        els.append(line(px - 15, 300, px + 15, 300, c["ink"], 3.2))
        els.append(line(px - 15, 290, px + 15, 290, c["ink"], 2))
        els.append(line(px - 18, 500, px + 18, 500, c["ink"], 3.2))
        els.append(line(px - 24, 512, px + 24, 512, c["ink"], 2.4))
    els.append(teardrop(320, 176, 44, c["gold"]))
    dome_r = 52.0
    dome_cy = 268.0
    els.append(path(f"M {F(320 - dome_r)} {F(300)} L {F(320 - dome_r)} {F(dome_cy)} "
                    f"A {F(dome_r)} {F(dome_r)} 0 0 1 {F(320 + dome_r)} {F(dome_cy)} L {F(320 + dome_r)} {F(300)}",
                    c["ink"], 3.4))
    els += tripundra(320, dome_cy, dome_r, c["ink"], sw=3.6)
    els += elev_lotus_cup(c, 320, 352.0, 84.0, 46.0)
    els.append(path("M 216 356 C 224 392 258 410 320 410 C 382 410 416 392 424 356", c["ink"], 3.2))
    els.append(wave(238, 402, 374, c["gold"], 2.2, n=6))
    for hw, y in ((80, 434), (104, 452), (128, 470)):
        els.append(line(320 - hw, y, 320 + hw, y, c["ink"], 2.6))
    return els, (640, 560)


def door_icon(c):
    els = []
    outer = [((100.0, 320.0), (100.0, 210.0), (196.0, 168.0), (238.0, 128.0)),
             ((238.0, 128.0), (258.0, 108.0), (250.0, 92.0), (256.0, 66.0))]
    for chain in (outer, [tuple((512 - p[0], p[1]) for p in seg) for seg in outer]):
        els.append(path(_arch_d(chain), c["ink"], 9))
    els.append(line(100, 320, 100, 420, c["ink"], 9))
    els.append(line(412, 320, 412, 420, c["ink"], 9))
    els.append(line(74, 430, 438, 430, c["ink"], 9))
    els.append(teardrop(256, 148, 52, c["gold"]))
    dome_r = 78.0
    dome_cy = 320.0
    els.append(path(f"M {F(256 - dome_r)} {F(368)} L {F(256 - dome_r)} {F(dome_cy)} "
                    f"A {F(dome_r)} {F(dome_r)} 0 0 1 {F(256 + dome_r)} {F(dome_cy)} L {F(256 + dome_r)} {F(368)}",
                    c["ink"], 8))
    els += tripundra(256, dome_cy, dome_r, c["ink"], sw=8)
    els.append(circ(256, 56, 9, c["ink"], 6))
    return els, (512, 470)


def door_glyph(c):
    els = []
    outer = [((110.0, 330.0), (110.0, 212.0), (206.0, 176.0), (242.0, 134.0)),
             ((242.0, 134.0), (258.0, 116.0), (252.0, 100.0), (256.0, 76.0))]
    for chain in (outer, [tuple((512 - p[0], p[1]) for p in seg) for seg in outer]):
        els.append(path(_arch_d(chain), c["ink"], 20))
    els.append(line(110, 330, 110, 400, c["ink"], 20))
    els.append(line(402, 330, 402, 400, c["ink"], 20))
    els.append(line(84, 418, 428, 418, c["ink"], 20))
    els.append(teardrop(256, 200, 96, c["gold"]))
    return els, (512, 470)


CANDIDATES = [
    ("jyotirlinga", "The emblem — tripundra-marked linga in the lotus cup; basin, waterline, carved sun medallions, the nali and the returned drop; a 12-sun prabhavali halo above.",
     [("full", jyotir_full), ("icon", jyotir_icon), ("glyph", jyotir_glyph)]),
    ("rtayantra", "The seal — square bhupura with four T-gates, 24-bead mala, 12 carved suns, two-tier lotus (outlined over solid), and the nali channel leaving through the south gate.",
     [("full", yantra_full), ("icon", yantra_icon), ("glyph", yantra_glyph)]),
    ("garbhagriha", "The crest — the sanctum doorway: pillars, ogee prabhavali arch garlanded with 12 gold buds (the Adityas), kalasha finial, the Lord in his basin inside, threshold steps.",
     [("full", door_full), ("icon", door_icon), ("glyph", door_glyph)]),
]


def emit_all():
    outdir = HERE / "candidates"
    outdir.mkdir(exist_ok=True)
    for name, _, regs in CANDIDATES:
        for reg, fn in regs:
            for way, cols in COLORWAYS.items():
                els, (w, h) = fn(cols)
                svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">\n  '
                       + "\n  ".join(els) + "\n</svg>\n")
                (outdir / f"{name}-{reg}-{way}.svg").write_text(svg)


def gallery():
    rows = []
    for i, (name, claim, _) in enumerate(CANDIDATES, 1):
        rows.append(f"""
    <section class="cand">
      <div class="strip">
        <figure class="hero"><img src="candidates/{name}-full-light.svg" style="height:330px"><figcaption>full — the {['emblem', 'seal', 'crest'][i - 1]}</figcaption></figure>
        <figure><img src="candidates/{name}-icon-light.svg" style="height:150px"><figcaption>icon (derived)</figcaption></figure>
        <figure class="glyphs">
          <span><img src="candidates/{name}-glyph-light.svg" width="64" height="64"><i>64</i></span>
          <span><img src="candidates/{name}-glyph-light.svg" width="32" height="32"><i>32</i></span>
          <figcaption>glyph / favicon</figcaption>
        </figure>
        <figure class="night"><img src="candidates/{name}-full-night.svg" style="height:280px"><figcaption class="nc">sacred night</figcaption></figure>
      </div>
      <p class="claim"><b>{i} · {name}</b> — {claim}</p>
    </section>""")
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>exp/temple-crest — three marks in temple language</title>
<link rel="stylesheet" href="../../../palette/colors.css">
<style>
  @font-face {{ font-family:'Cinzel'; font-weight:500; src:url('../../../fonts/cinzel/cinzel-500.ttf'); }}
  @font-face {{ font-family:'Inter'; font-weight:400; src:url('../../../fonts/inter/inter-400.ttf'); }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:40px 52px 80px; background:var(--rtam-ivory); color:var(--rtam-charcoal);
         font-family:Inter,sans-serif; }}
  h1 {{ font-family:Cinzel,serif; font-weight:500; font-size:26px; letter-spacing:.05em; margin:0 0 6px; }}
  .sub {{ font-size:13.5px; color:#555; max-width:980px; line-height:1.6; margin:0 0 30px; }}
  .cand {{ border:1px solid var(--rtam-sandstone); background:#fffdf8; margin:0 0 26px; }}
  .strip {{ display:flex; align-items:center; justify-content:space-between; gap:26px; padding:30px 34px; flex-wrap:wrap; }}
  figure {{ margin:0; text-align:center; }}
  figcaption {{ font-size:10.5px; color:#888; margin-top:10px; letter-spacing:.08em; text-transform:uppercase; }}
  .glyphs span {{ display:inline-flex; flex-direction:column; align-items:center; gap:5px; margin:0 12px; }}
  .glyphs i {{ font-style:normal; font-size:10px; color:#999; }}
  .night {{ background:var(--rtam-indigo); padding:22px 30px 12px; }}
  .night .nc {{ color:#8b87b8; }}
  .claim {{ font-size:13px; line-height:1.6; padding:12px 18px 15px; margin:0;
           border-top:1px solid var(--rtam-sandstone); color:#444; }}
  .claim b {{ font-family:Cinzel,serif; font-size:14px; letter-spacing:.05em; color:var(--rtam-charcoal); }}
</style>
</head>
<body>
  <h1>exp/temple-crest — three marks in temple language</h1>
  <p class="sub">Founder's brief: <b>drop "wholly minimal" — make it unmistakably a temple; remarkable; keep
  logo / icon / symbol craft.</b> The vocabulary is now the temple's own: <b>tripundra</b> (the three vibhuti
  lines — the Shaiva signature), <b>prabhavali</b> (the garland-arch), <b>kalasha</b>, <b>bhupura</b> (the yantra's
  four-gated square court), mala beading, twin-line carved strokes. Gold stays reserved for god-points: bindu,
  drop, suns, buds. Each mark is a three-register system — the full mark, a <i>derived</i> icon, a <i>derived</i>
  glyph (64/32&nbsp;px shown) — reduction by redrawing, never by shrinking. All geometry still obeys the
  rta-grid (12 / 24 / 30&deg; / 15&deg;).</p>
  {"".join(rows)}
</body>
</html>
"""
    (HERE / "gallery.html").write_text(html)


def main():
    emit_all()
    gallery()
    n = sum(len(r) for _, _, r in CANDIDATES) * 2
    print(f"wrote {n} SVGs + gallery.html")


if __name__ == "__main__":
    main()
