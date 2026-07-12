#!/usr/bin/env python3
"""exp/rta-chakra/v2-12petal — the five crafts, faithful to themselves,
with the true lotus corolla.

Founder rulings this version obeys (2026-07-12):
- NO mixing components between candidates (the ratna/mala synthesis
  iteration, git 78bd12e, is reverted). Candidates keep their v1 numbers
  and identities: 1 tanka, 2 utkirna, 3 shila, 4 dvitala, 6 aditya
  (5 jala stays retired).
- Twelve petals only from the top (the 24 belong to the front
  elevation). v1 with its two-tier reading is preserved in
  ../v1-24petal/ so versions stay browsable.
- The v2 single petals were "too skinny" and read rose, not lotus.

The lotus petal, redrawn (rose -> lotus): a rose petal is widest near
its rounded top; a lotus petal carries its belly LOW (34 percent of the
length), enters already broad at the base, and tapers long into a
sharp ogival point. Built as two cubics per side in a radial frame.

The podium, rebalanced so twelve fill what twenty-four used to: petal
tips extended from .62 R to .70 R (the reach the lower tier used to
provide) and the belly width set to near-touching (half-spacing minus a
seam). Every other radius stays on grid.json canon: linga .22,
jaladhari .32 (petal base), waterline .84, medallions .92 (r .045),
rim 1.0; petals at 30 deg, medallions offset 15 deg.

    python3 build.py    # writes candidates/*.svg + gallery.html
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent.parent.parent / "tools"))
from brandlib import polar  # noqa: E402

COLORWAYS = {
    "light": {"ink": "#1A1A1A", "gold": "#C8A15A", "punch": "#F7F3E9"},
    "night": {"ink": "#F7F3E9", "gold": "#C8A15A", "punch": "#1C1A3D"},
}

VB = 512
C = 256.0
R = 230.0                      # rim outer radius on the 512 canvas
LINGA = 0.22 * R               # 50.6  — the Shivalinga, gold
JAL = 0.32 * R                 # 73.6  — jaladhari ring = petal base
PT = 0.70 * R                  # 161.0 — petal tips (optical: fills what
                               #         the second tier used to)
WATER = 0.84 * R               # 193.2 — waterline
MED = 0.92 * R                 # 211.6 — medallion centres
MEDR = 0.045 * R               # 10.35 — medallion radius

PL = PT - JAL                  # petal length 87.4
BELLY_AT = 0.34                # belly sits low — the lotus signature
W_BELLY = 24.5                 # half-width at belly (13.7 deg of the 15)
W_BASE_F = 0.74                # base already broad, no stalk


def A1(k):
    return -90 + k * 30        # petals: one tip due north


def A2(k):
    return -75 + k * 30        # medallions: offset 15 deg, between tips


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


def _lotus_d(deg):
    """True lotus petal outline, base at JAL, tip at PT, along `deg`.
    Two cubics per side: base swells into the low belly, then a long
    ogival taper accelerates into a sharp point."""
    a = math.radians(deg)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux

    def P(r_along, w_off):
        return f"{F(C + ux * r_along + nx * w_off)} {F(C + uy * r_along + ny * w_off)}"

    rb = JAL + BELLY_AT * PL
    wb = W_BELLY * W_BASE_F
    return (f"M {P(JAL, -wb)} "
            f"C {P(JAL + 0.12 * PL, -(wb + (W_BELLY - wb) * 0.7))} "
            f"{P(rb - 0.10 * PL, -W_BELLY)} {P(rb, -W_BELLY)} "
            f"C {P(rb + 0.32 * PL, -W_BELLY * 0.84)} "
            f"{P(PT - 0.08 * PL, -W_BELLY * 0.10)} {P(PT, 0)} "
            f"C {P(PT - 0.08 * PL, W_BELLY * 0.10)} "
            f"{P(rb + 0.32 * PL, W_BELLY * 0.84)} {P(rb, W_BELLY)} "
            f"C {P(rb - 0.10 * PL, W_BELLY)} "
            f"{P(JAL + 0.12 * PL, wb + (W_BELLY - wb) * 0.7)} {P(JAL, wb)}")


def lotus_fill(deg, fill, seam, sw):
    """Solid petal; the ground-colour seam keeps neighbours distinct and
    masks whatever passes beneath the edges."""
    return (f'<path d="{_lotus_d(deg)} Z" fill="{fill}" stroke="{seam}" '
            f'stroke-width="{F(sw)}" stroke-linejoin="round"/>')


def vein(deg, col, sw, reach):
    x0, y0 = polar(C, C, JAL + 8, deg)
    x1, y1 = polar(C, C, JAL + PL * reach, deg)
    return path(f"M {F(x0)} {F(y0)} L {F(x1)} {F(y1)}", col, sw)


def corolla(els, fill, seam, sw):
    for k in range(12):
        els.append(lotus_fill(A1(k), fill, seam, sw))


# ------------------------------------------------------------- candidates
def g_tanka(c):
    """1 — struck coin, as in round one: the plan chased into a solid disc,
    gold only at the hub."""
    els = [dot(C, C, R, c["ink"])]
    els.append(ring(C, C, WATER, c["punch"], 3))
    for k in range(12):
        x, y = polar(C, C, MED, A2(k))
        els.append(ring(x, y, MEDR, c["punch"], 3))
    els.append(ring(C, C, JAL, c["punch"], 3))
    corolla(els, c["ink"], c["punch"], 3.5)
    els.append(dot(C, C, 44, c["gold"]))
    return els, (VB, VB)


def g_utkirna(c):
    """2 — mason's twin-line, as in round one: mala channel with ink beads,
    open petals cut with the heavy chisel, veined, god-point circled."""
    els = []
    els.append(ring(C, C, 226, c["ink"], 4.5))
    els.append(ring(C, C, 197, c["ink"], 2.5))
    for k in range(12):
        x, y = polar(C, C, MED, A2(k))
        els.append(dot(x, y, MEDR, c["ink"]))
    els.append(ring(C, C, JAL, c["ink"], 3))
    corolla(els, c["punch"], c["ink"], 5)
    for k in range(12):
        els.append(vein(A1(k), c["ink"], 1.8, 0.62))
    els.append(ring(C, C, LINGA, c["ink"], 3))
    els.append(dot(C, C, 33, c["gold"]))
    return els, (VB, VB)


def g_shila(c):
    """3 — pure relief, as in round one: ink is stone, ivory is light,
    the heavy rim pierced by twelve sun-windows, the linga gold at true
    scale. Nothing borrowed from any other candidate."""
    els = []
    els.append(ring(C, C, 213.5, c["ink"], 33))
    for k in range(12):
        x, y = polar(C, C, MED, A2(k))
        els.append(dot(x, y, MEDR, c["punch"]))
    corolla(els, c["ink"], c["punch"], 5)
    els.append(dot(C, C, LINGA, c["gold"]))
    return els, (VB, VB)


def g_dvitala(c):
    """4 — the faithful portrait, as in round one: the full ring set in
    fine line — rim, waterline, medallions, jaladhari — around the solid
    corolla."""
    els = []
    els.append(ring(C, C, R, c["ink"], 3.5))
    els.append(ring(C, C, WATER, c["ink"], 2.5))
    for k in range(12):
        x, y = polar(C, C, MED, A2(k))
        els.append(dot(x, y, MEDR, c["ink"]))
    els.append(ring(C, C, JAL, c["ink"], 3))
    corolla(els, c["ink"], c["punch"], 4)
    els.append(dot(C, C, 40, c["gold"]))
    return els, (VB, VB)


def g_aditya(c):
    """6 — ceremonial glory, as in round one: the twelve Adityas set as
    gold stones in carved seats, gold at hub and rim both."""
    els = []
    els.append(ring(C, C, R, c["ink"], 4))
    els.append(ring(C, C, 189, c["ink"], 2.5))
    for k in range(12):
        x, y = polar(C, C, 208.2, A2(k))
        els.append(ring(x, y, 13.0, c["ink"], 2.6))
        els.append(dot(x, y, 9.4, c["gold"]))
    els.append(ring(C, C, JAL, c["ink"], 3))
    corolla(els, c["ink"], c["punch"], 4)
    els.append(ring(C, C, LINGA, c["ink"], 3))
    els.append(dot(C, C, 40, c["gold"]))
    return els, (VB, VB)


CANDIDATES = [
    (1, "tanka", "The struck coin, exactly as round one had it — the whole sanctum plan chased into one solid disc: waterline groove, twelve sun-seats, the lotus engraved petal by petal, gold only where the Lord stands. The emboss / foil / wax register.", g_tanka),
    (2, "utkirna", "The mason's line, exactly as round one had it — twin-line channel holding the twelve suns like mala beads, petals cut open with the heavy chisel and veined down the middle, the god-point circled at the centre.", g_utkirna),
    (3, "shila", "Your favourite, pure again — nothing borrowed from six. Ink is stone, ivory is light: the heavy rim pierced by twelve sun-windows, the solid lotus, the Shivalinga gold at its true measured scale.", g_shila),
    (4, "dvitala", "The faithful portrait — the complete ring set drawn fine: rim, waterline, twelve medallions, jaladhari, all exactly where the murti puts them, around the solid corolla and the gold centre.", g_dvitala),
    (6, "aditya", "The ceremonial glory, exactly as round one had it — the twelve Adityas set as gold stones in carved seats, gold at hub and rim both: the top of the sanctity ladder, for night grounds and invitations.", g_aditya),
]


def emit_all():
    outdir = HERE / "candidates"
    outdir.mkdir(exist_ok=True)
    for stale in outdir.glob("*.svg"):
        stale.unlink()
    for _, name, _, fn in CANDIDATES:
        for way, cols in COLORWAYS.items():
            els, (w, h) = fn(cols)
            svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">\n  '
                   + "\n  ".join(els) + "\n</svg>\n")
            (outdir / f"{name}-{way}.svg").write_text(svg)


def gallery():
    dist = "../../../../dist/outlined/logos"
    rows = []
    for num, name, claim, _ in CANDIDATES:
        rows.append(f"""
    <section class="cand">
      <div class="strip">
        <figure class="hero"><img src="candidates/{name}-light.svg" width="270" height="270"></figure>
        <div class="mid">
          <p class="claim"><b>{num} · {name}</b><br>{claim}</p>
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
          <img src="{dist}/rtam-wordmark-ivory-golddot.svg" style="height:26px"></div>
        </figure>
      </div>
    </section>""")
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>exp/rta-chakra v2 — twelve true lotus petals, five faithful crafts</title>
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
  <h1>exp/rta-chakra v2 — twelve true lotus petals, five faithful crafts</h1>
  <p class="sub">Your three rulings, applied. <b>No mixing</b>: the synthesis iteration is reverted; each candidate
  is itself again, keeping its round-one number (5 stays retired). <b>Twelve from above</b>: one corolla, and the
  old two-tier originals are preserved untouched in <code>v1-24petal/</code> next door. <b>Lotus, not rose</b>:
  the petal is redrawn — it enters broad at the base, carries its belly low, and tapers long into a sharp ogival
  point — and the podium is rebalanced so twelve fill what twenty-four used to (tips reach .70&nbsp;R; every
  other radius stays on the grid). Gold untouched: the Shivalinga always; the Adityas only in&nbsp;6.</p>
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
