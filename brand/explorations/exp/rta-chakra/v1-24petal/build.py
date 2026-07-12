#!/usr/bin/env python3
"""exp/rta-chakra — round five, after the founder converged: keep the R-dot
wordmark (the name) and make the icon the murti's own plan view — 12 petals,
12 medallions, the Lord at the hub. The verdict of four rejected rounds is
that the 12+12 GEOMETRY was never the problem — the CRAFT was: flat
equal-weight hairlines read spa (round P2b); architectural drawing read
literal (P2c); ritual metaphors dropped the 12+12 (P2d).

So this round holds the geometry constant and varies only the craft.
Every radius is the murti's own, from iconography/geometry/grid.json
(normalized to rim R): linga .22 · jaladhari .32 · tier-1 tips .48 ·
tier-2 tips .62 · water to .84 · medallions at .92 (r .045) · rim 1.0.
Petals at 30 deg, tiers and medallions offset 15 deg. Gold at god-points
only: the linga-bindu always; the twelve Adityas only in the ceremonial
candidate.

Six craft registers:

  tanka     struck coin — the plan engraved into one solid disc
  utkirna   mason's twin-line — mala rim channel, heavy/light chisel tiers
  shila     pure relief — ink is stone, ivory is light, no outlines
  dvitala   the faithful portrait — solid upper tier, fine lower tier
  jala      water is space — rim broken at the nali, the drop leaves
  aditya    ceremonial glory — twelve gold suns set in carved seats

The tier-1 petals carry a ground-colour masking stroke so the lower tier
reads as passing BENEATH them (depth without literal shading).

    python3 build.py    # writes candidates/*.svg + gallery.html
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent.parent.parent / "tools"))
from brandlib import polar, petal_path  # noqa: E402

COLORWAYS = {
    "light": {"ink": "#1A1A1A", "gold": "#C8A15A", "punch": "#F7F3E9"},
    "night": {"ink": "#F7F3E9", "gold": "#C8A15A", "punch": "#1C1A3D"},
}

VB = 512
C = 256.0
R = 230.0                      # rim outer radius on the 512 canvas
LINGA = 0.22 * R               # 50.6  — gold bindu at true scale
JAL = 0.32 * R                 # 73.6  — jaladhari ring / petal bases
T1 = 0.48 * R                  # 110.4 — upper-tier petal tips
T2 = 0.62 * R                  # 142.6 — lower-tier petal tips
WATER = 0.84 * R               # 193.2 — waterline (outer edge of water)
MED = 0.92 * R                 # 211.6 — medallion centres
MEDR = 0.045 * R               # 10.35 — medallion radius
T2B = 96.0                     # lower-tier visible base (tucks under tier 1)


def A1(k):
    return -90 + k * 30        # tier-1 petals: one tip due north


def A2(k):
    return -75 + k * 30        # tier-2 petals + medallions: offset 15 deg


def F(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def dot(x, y, r, col):
    return f'<circle cx="{F(x)}" cy="{F(y)}" r="{F(r)}" fill="{col}"/>'


def ring(x, y, r, col, sw):
    return (f'<circle cx="{F(x)}" cy="{F(y)}" r="{F(r)}" fill="none" '
            f'stroke="{col}" stroke-width="{F(sw)}"/>')


def path(d, col, sw, cap="round", fill="none"):
    return (f'<path d="{d}" fill="{fill}" stroke="{col}" stroke-width="{F(sw)}" '
            f'stroke-linecap="{cap}" stroke-linejoin="round"/>')


def arc(cx, cy, r, a0, a1, col, sw, cap="butt"):
    p0 = (cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
    p1 = (cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)))
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return path(f"M {F(p0[0])} {F(p0[1])} A {F(r)} {F(r)} 0 {large} 1 {F(p1[0])} {F(p1[1])}",
                col, sw, cap=cap)


def teardrop(cx, top_y, h, col):
    w = h * 0.62
    by = top_y + h * 0.70
    return (f'<path d="M {F(cx)} {F(top_y)} '
            f'C {F(cx - w * 0.22)} {F(top_y + h * 0.34)} {F(cx - w / 2)} {F(by - h * 0.24)} {F(cx - w / 2)} {F(by)} '
            f'A {F(w / 2)} {F(w / 2)} 0 1 0 {F(cx + w / 2)} {F(by)} '
            f'C {F(cx + w / 2)} {F(by - h * 0.24)} {F(cx + w * 0.22)} {F(top_y + h * 0.34)} {F(cx)} {F(top_y)} Z" '
            f'fill="{col}"/>')


def fpetal(tip_r, base_r, deg, hw, fill, stroke=None, sw=0):
    """Closed solid petal; the optional ground-colour stroke masks whatever
    passes beneath its edges (how tier 1 sits OVER tier 2)."""
    d = petal_path(C, C, tip_r, base_r, deg, hw) + " Z"
    s = (f' stroke="{stroke}" stroke-width="{F(sw)}" stroke-linejoin="round"'
         if stroke else "")
    return f'<path d="{d}" fill="{fill}"{s}/>'


def spetal(tip_r, base_r, deg, hw, col, sw):
    """Open engraved petal outline (base left open — the socket)."""
    d = petal_path(C, C, tip_r, base_r, deg, hw)
    return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{F(sw)}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def med_dots(els, col, r_med=MED, r_dot=MEDR):
    for k in range(12):
        x, y = polar(C, C, r_med, A2(k))
        els.append(dot(x, y, r_dot, col))


# ------------------------------------------------------------- candidates
def g_tanka(c):
    """Struck coin: solid disc, the whole plan engraved as punched lines."""
    els = [dot(C, C, R, c["ink"])]
    els.append(ring(C, C, WATER, c["punch"], 3))
    for k in range(12):
        x, y = polar(C, C, MED, A2(k))
        els.append(ring(x, y, MEDR, c["punch"], 3))
    els.append(ring(C, C, JAL, c["punch"], 3))
    for k in range(12):
        els.append(spetal(T2, T2B, A2(k), 12.0, c["punch"], 2.5))
    for k in range(12):
        els.append(fpetal(T1, JAL, A1(k), 11.5, c["ink"], stroke=c["punch"], sw=3.5))
    els.append(dot(C, C, 44, c["gold"]))
    return els, (VB, VB)


def g_utkirna(c):
    """Mason's twin-line: mala rim channel, heavy/light chisel tiers.
    Midrib veins on the upper petals are the carving signature — without
    them the outlined petals read daisy, not carved lotus."""
    els = []
    els.append(ring(C, C, 226, c["ink"], 4.5))
    els.append(ring(C, C, 197, c["ink"], 2.5))
    med_dots(els, c["ink"])
    els.append(ring(C, C, JAL, c["ink"], 3))
    for k in range(12):
        els.append(spetal(T2, T2B, A2(k), 12.0, c["ink"], 2.5))
    for k in range(12):
        els.append(fpetal(T1, JAL, A1(k), 11.5, c["punch"], stroke=c["ink"], sw=5))
    for k in range(12):
        x0, y0 = polar(C, C, JAL + 6, A1(k))
        x1, y1 = polar(C, C, JAL + (T1 - JAL) * 0.68, A1(k))
        els.append(path(f"M {F(x0)} {F(y0)} L {F(x1)} {F(y1)}", c["ink"], 1.8))
    els.append(ring(C, C, LINGA, c["ink"], 3))
    els.append(dot(C, C, 33, c["gold"]))
    return els, (VB, VB)


def g_shila(c):
    """Pure relief: solid shapes only; ivory gaps are the carving light."""
    els = []
    els.append(ring(C, C, 213.5, c["ink"], 33))     # heavy rim band 197..230
    med_dots(els, c["punch"])                       # pierced sun-windows
    for k in range(12):
        els.append(fpetal(T2, 84, A2(k), 12.5, c["ink"]))
    for k in range(12):
        els.append(fpetal(T1, JAL, A1(k), 11.5, c["ink"], stroke=c["punch"], sw=5))
    els.append(dot(C, C, LINGA, c["gold"]))         # gold at true linga scale
    return els, (VB, VB)


def g_dvitala(c):
    """The faithful portrait: everything where the murti puts it."""
    els = []
    els.append(ring(C, C, R, c["ink"], 3.5))
    els.append(ring(C, C, WATER, c["ink"], 2.5))
    med_dots(els, c["ink"])
    els.append(ring(C, C, JAL, c["ink"], 3))
    for k in range(12):
        els.append(spetal(T2, T2B, A2(k), 12.0, c["ink"], 3))
    for k in range(12):
        els.append(fpetal(T1, JAL, A1(k), 11.5, c["ink"], stroke=c["punch"], sw=4))
    els.append(dot(C, C, 40, c["gold"]))
    return els, (VB, VB)


def g_jala(c):
    """Water is space: the rim opens at the nali; the drop leaves the mark."""
    R2 = 210.0
    jl, t1 = 0.32 * R2, 0.48 * R2
    med, mr = 0.92 * R2, 0.045 * R2
    els = []
    els.append(arc(C, C, R2, 95.2, 444.8, c["ink"], 5))     # gap at 6 o'clock
    hw = 0.09 * R2                                           # nali half-width
    y0 = C + math.sqrt(R2 * R2 - hw * hw)
    y1 = C + R2 + 0.14 * R2
    for s in (-1, 1):
        x = C + s * hw
        els.append(path(f"M {F(x)} {F(y0)} L {F(x)} {F(y1)}", c["ink"], 5, cap="butt"))
    for k in range(12):
        els.append(fpetal(t1, jl, A1(k), 13.0, c["ink"], stroke=c["punch"], sw=3))
    els.append(ring(C, C, jl, c["ink"], 3))
    for k in range(12):
        x, y = polar(C, C, med, A2(k))
        els.append(dot(x, y, mr, c["ink"]))
    els.append(dot(C, C, 33, c["gold"]))
    els.append(teardrop(C, y0 + 6, 24, c["gold"]))
    return els, (VB, VB)


def g_aditya(c):
    """Ceremonial glory: the twelve Adityas as gold stones in carved seats."""
    els = []
    els.append(ring(C, C, R, c["ink"], 4))
    els.append(ring(C, C, 189, c["ink"], 2.5))
    for k in range(12):
        x, y = polar(C, C, 208.2, A2(k))
        els.append(ring(x, y, 13.0, c["ink"], 2.6))
        els.append(dot(x, y, 9.4, c["gold"]))
    els.append(ring(C, C, JAL, c["ink"], 3))
    for k in range(12):
        els.append(spetal(T2, T2B, A2(k), 12.0, c["ink"], 3))
    for k in range(12):
        els.append(fpetal(T1, JAL, A1(k), 11.5, c["ink"], stroke=c["punch"], sw=4))
    els.append(ring(C, C, LINGA, c["ink"], 3))
    els.append(dot(C, C, 40, c["gold"]))
    return els, (VB, VB)


CANDIDATES = [
    ("tanka", "Struck like a coin — the whole sanctum plan engraved into one solid disc: waterline groove, twelve sun-seats cut around the rim, both petal tiers chased into the metal, the Lord solid gold at the hub. The emboss / foil / wax register.", g_tanka),
    ("utkirna", "The mason's line — a twin-line rim channel holds the twelve suns like beads of a mala; the upper petals cut with the heavy chisel, the lower tier with the light one; the god-point circled at the centre.", g_utkirna),
    ("shila", "Pure relief — ink is stone, ivory is light, no outlines anywhere. The heavy rim is pierced by twelve sun-windows; the lotus stands in two solid tiers; the linga is gold at its true measured scale.", g_shila),
    ("dvitala", "The faithful portrait — everything exactly where the murti puts it: twelve upper petals solid, twelve lower in fine line behind them, the waterline, and the twelve medallions riding between water and rim.", g_dvitala),
    ("jala", "Water is space, not a line — the emptiest one. The rim opens at the nali: the circle is deliberately broken toward the devotee, and the golden drop leaves the sanctum, carrying grace out of the mark.", g_jala),
    ("aditya", "The ceremonial glory — the twelve Adityas set as gold stones in carved seats, gold at hub and rim both: the top of the sanctity ladder. For night grounds, invitations, the drum of the temple.", g_aditya),
]


def emit_all():
    outdir = HERE / "candidates"
    outdir.mkdir(exist_ok=True)
    for name, _, fn in CANDIDATES:
        for way, cols in COLORWAYS.items():
            els, (w, h) = fn(cols)
            svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">\n  '
                   + "\n  ".join(els) + "\n</svg>\n")
            (outdir / f"{name}-{way}.svg").write_text(svg)


def gallery():
    dist = "../../../../dist/outlined/logos"
    rows = []
    for i, (name, claim, _) in enumerate(CANDIDATES, 1):
        rows.append(f"""
    <section class="cand">
      <div class="strip">
        <figure class="hero"><img src="candidates/{name}-light.svg" width="270" height="270"></figure>
        <div class="mid">
          <p class="claim"><b>{i} · {name}</b><br>{claim}</p>
          <div class="lockup">
            <img src="candidates/{name}-light.svg" width="58" height="58">
            <img src="{dist}/rtam-wordmark-sacred-RTAM-dot.svg" style="height:36px">
          </div>
          <div class="minis">
            <span><img src="candidates/{name}-light.svg" width="64" height="64"><i>64</i></span>
            <span><img src="candidates/{name}-light.svg" width="32" height="32"><i>32</i></span>
            <span><img src="candidates/{name}-light.svg" width="16" height="16"><i>16</i></span>
          </div>
        </div>
        <figure class="night">
          <img src="candidates/{name}-night.svg" width="210" height="210">
          <div class="nlock"><img src="candidates/{name}-night.svg" width="40" height="40">
          <img src="{dist}/rtam-wordmark-white-golddot.svg" style="height:26px"></div>
        </figure>
      </div>
    </section>""")
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>exp/rta-chakra — one geometry, six crafts</title>
<link rel="stylesheet" href="../../../../palette/colors.css">
<style>
  @font-face {{ font-family:'Cinzel'; font-weight:500; src:url('../../../../fonts/cinzel/cinzel-500.ttf'); }}
  @font-face {{ font-family:'Inter'; font-weight:400; src:url('../../../../fonts/inter/inter-400.ttf'); }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:40px 52px 80px; background:var(--rtam-ivory); color:var(--rtam-charcoal);
         font-family:Inter,sans-serif; }}
  h1 {{ font-family:Cinzel,serif; font-weight:500; font-size:26px; letter-spacing:.05em; margin:0 0 6px; }}
  .sub {{ font-size:13.5px; color:#555; max-width:1000px; line-height:1.65; margin:0 0 30px; }}
  .cand {{ border:1px solid var(--rtam-sandstone); background:#fffdf8; margin:0 0 24px; }}
  .strip {{ display:flex; align-items:center; gap:34px; padding:26px 34px; }}
  figure {{ margin:0; text-align:center; }}
  .mid {{ flex:1; min-width:0; }}
  .claim {{ font-size:13.5px; line-height:1.65; color:#444; margin:0 0 16px; }}
  .claim b {{ font-family:Cinzel,serif; font-size:16px; letter-spacing:.06em; color:var(--rtam-charcoal); }}
  .lockup {{ display:flex; align-items:center; gap:18px; padding:14px 18px; border:1px solid var(--rtam-sandstone);
            background:var(--rtam-ivory); width:fit-content; margin-bottom:14px; }}
  .minis span {{ display:inline-flex; flex-direction:column; align-items:center; gap:4px; margin-right:20px; }}
  .minis i {{ font-style:normal; font-size:10px; color:#999; }}
  .night {{ background:var(--rtam-indigo); padding:20px 26px; }}
  .nlock {{ display:flex; align-items:center; gap:12px; justify-content:center; margin-top:10px; }}
</style>
</head>
<body>
  <h1>exp/rta-chakra — one geometry, six crafts</h1>
  <p class="sub">Round five, and the lesson of the four before it: the <b>12-petal + 12-medallion geometry was
  never the problem — the craft was</b>. Flat equal hairlines read <i>spa</i>; architectural drawing read
  <i>literal</i>. So this round holds the geometry constant — every radius is the murti's own, from
  <code>iconography/geometry/grid.json</code>: linga at .22, jaladhari at .32, petal tiers at .48/.62,
  the water's calm to .84, the twelve medallions at .92 — and varies <b>only the craft register</b>:
  struck, carved, relieved, drawn, broken, jewelled. Gold stays at god-points: the linga always,
  the Adityas only in the ceremonial one. Each row: mark &middot; register &middot; live lockup with the
  shipped R-dot wordmark &middot; 64/32/16&nbsp;px unassisted &middot; sacred night.</p>
  {"".join(rows)}
</body>
</html>
"""
    (HERE / "gallery.html").write_text(html)


def main():
    emit_all()
    gallery()
    print(f"wrote {len(CANDIDATES) * 2} SVGs + gallery.html")


if __name__ == "__main__":
    main()
