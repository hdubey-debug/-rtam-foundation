#!/usr/bin/env python3
"""exp/lotus-medallion — the founder's direct brief, replacing directions A-D:

    top view · a 12-petal lotus at the centre · a circle of 12 medallions ·
    artistic, abstract.

Twelve candidates render that one concept in twelve registers (solid vs
stroke, medallions as beads/suns/rings/points, aligned vs 15deg-offset,
rimmed vs floating, positive vs negative space). All geometry derives from
iconography/geometry/grid.json (30deg spokes, medallion ring at 0.92R); the
gold centre dot is the linga-from-above = the brand bindu, everywhere.

Colorways per candidate:
    light  charcoal + gold on light grounds (the workhorse)
    night  ivory + gold on indigo/charcoal (the Phase-0 dark convention)

    python3 build.py    # writes candidates/*.svg + gallery.html
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent.parent / "tools"))
from brandlib import polar, petal_path  # noqa: E402

VB = 512
C = 256.0
R = 220.0          # rim reference radius (grid.json rimOuter = 1.0)
TIP_UP = -90.0     # a petal tip holds the vertical axis
STEP = 30.0        # grid.json anglesDeg.spoke
OFF = 15.0         # grid.json anglesDeg.tierOffset

COLORWAYS = {
    "light": {"ink": "#1A1A1A", "gold": "#C8A15A", "punch": "#F7F3E9"},
    "night": {"ink": "#F7F3E9", "gold": "#C8A15A", "punch": "#1C1A3D"},
}


def F(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def pt(rr, deg):
    return polar(C, C, rr * R, deg)


def dot(x, y, r, col):
    return f'<circle cx="{F(x)}" cy="{F(y)}" r="{F(r)}" fill="{col}"/>'


def ring(rr, sw, col, cx=None, cy=None, r_abs=None):
    x = C if cx is None else cx
    y = C if cy is None else cy
    rr_ = rr * R if r_abs is None else r_abs
    return (f'<circle cx="{F(x)}" cy="{F(y)}" r="{F(rr_)}" fill="none" '
            f'stroke="{col}" stroke-width="{sw}"/>')


def lotus_solid(col, tip, base, hw, belly=1.28, offset=0.0):
    els = []
    for k in range(12):
        a = TIP_UP + offset + k * STEP
        d = petal_path(C, C, tip * R, base * R, a, hw, belly)
        els.append(f'<path d="{d} Z" fill="{col}"/>')
    return els


def lotus_stroke(col, tip, base, hw, sw, belly=1.35, offset=0.0):
    els = []
    for k in range(12):
        a = TIP_UP + offset + k * STEP
        d = petal_path(C, C, tip * R, base * R, a, hw, belly)
        els.append(f'<path d="{d}" fill="none" stroke="{col}" '
                   f'stroke-width="{sw}" stroke-linecap="round"/>')
    return els


def dots_ring(col, rr, r, offset=False):
    els = []
    for k in range(12):
        a = TIP_UP + (OFF if offset else 0.0) + k * STEP
        x, y = pt(rr, a)
        els.append(dot(x, y, r, col))
    return els


def rings_ring(col, rr, r, sw, offset=False):
    els = []
    for k in range(12):
        a = TIP_UP + (OFF if offset else 0.0) + k * STEP
        x, y = pt(rr, a)
        els.append(ring(0, sw, col, cx=x, cy=y, r_abs=r))
    return els


# --- the twelve candidates ---------------------------------------------------
def c_mala(c):
    """Beads on the thread: rim ring as a japamala, gold medallion beads."""
    els = [ring(0.92, 3, c["ink"])]
    els += lotus_solid(c["ink"], 0.58, 0.24, 10.5)
    els += dots_ring(c["gold"], 0.92, 10.5, offset=True)
    els.append(dot(C, C, 15, c["gold"]))
    return els


def c_engraved(c):
    """Ceremonial control: all fine stroke, dot-in-ring suns, double court."""
    els = [ring(1.0, 2.5, c["ink"]), ring(0.155, 2.5, c["ink"])]
    els += lotus_stroke(c["ink"], 0.62, 0.27, 11.5, 3)
    for k in range(12):
        x, y = pt(0.92, TIP_UP + k * STEP)
        els.append(ring(0, 2.5, c["ink"], cx=x, cy=y, r_abs=10))
        els.append(dot(x, y, 3.5, c["gold"]))
    els.append(dot(C, C, 13, c["gold"]))
    return els


def c_suncourt(c):
    """Floating Adityas: disc-and-corona suns, no rim — whitespace is the water.
    (Rayed ticks fuzzed out below 64px on the first eye-check; the corona ring
    is the abstract sun that survives.)"""
    els = lotus_solid(c["ink"], 0.58, 0.24, 10.5)
    for k in range(12):
        x, y = pt(0.92, TIP_UP + OFF + k * STEP)
        els.append(dot(x, y, 7, c["gold"]))
        els.append(ring(0, 2, c["gold"], cx=x, cy=y, r_abs=11.5))
    els.append(dot(C, C, 15, c["gold"]))
    return els


def c_counterseal(c):
    """Negative space: solid disc, lotus + medallions punched out. Stamp/app-icon register."""
    els = [dot(C, C, 0.97 * R, c["ink"])]
    els += lotus_solid(c["punch"], 0.60, 0.22, 10.5, belly=1.25)
    els += dots_ring(c["punch"], 0.84, 9, offset=False)
    els.append(dot(C, C, 15, c["gold"]))
    return els


def c_interleave(c):
    """The 24 reading: 12 petals + 12 medallions interleaved = the tattvas around the centre."""
    els = lotus_solid(c["ink"], 0.66, 0.24, 10, belly=1.25)
    els += dots_ring(c["ink"], 0.78, 11, offset=True)
    els.append(dot(C, C, 15, c["gold"]))
    return els


def c_halo(c):
    """Wide water: small quiet lotus, far halo of gold petal-points (marquise)."""
    els = lotus_stroke(c["ink"], 0.52, 0.22, 12, 3.5)
    lens_r = 18.33  # lens 28 long x 13 wide: r = (L^2/4 + w^2) / 2w
    for k in range(12):
        a = TIP_UP + k * STEP
        x1, y1 = pt(0.93 - 14 / R, a)
        x2, y2 = pt(0.93 + 14 / R, a)
        els.append(f'<path d="M {F(x1)} {F(y1)} A {lens_r} {lens_r} 0 0 1 {F(x2)} {F(y2)} '
                   f'A {lens_r} {lens_r} 0 0 1 {F(x1)} {F(y1)} Z" fill="{c["gold"]}"/>')
    els.append(dot(C, C, 14, c["gold"]))
    return els


def c_raywheel(c):
    """Most abstract: petals as tapered rays — the rta-chakra as pure motion."""
    els = lotus_solid(c["ink"], 0.62, 0.16, 4.2, belly=1.05)
    els += dots_ring(c["gold"], 0.92, 8.5, offset=True)
    els.append(dot(C, C, 15, c["gold"]))
    return els


def c_archway(c):
    """Temple-arch petals: two circular arcs meet at each tip; ring medallions."""
    els = []
    for k in range(12):
        a = TIP_UP + k * STEP
        tx, ty = pt(0.62, a)
        b1x, b1y = pt(0.27, a - 13)
        b2x, b2y = pt(0.27, a + 13)
        r_arc = math.dist((b1x, b1y), (tx, ty)) * 0.92
        els.append(f'<path d="M {F(b1x)} {F(b1y)} A {F(r_arc)} {F(r_arc)} 0 0 1 {F(tx)} {F(ty)} '
                   f'A {F(r_arc)} {F(r_arc)} 0 0 1 {F(b2x)} {F(b2y)}" fill="none" '
                   f'stroke="{c["ink"]}" stroke-width="4" stroke-linecap="round"/>')
    els += rings_ring(c["ink"], 0.92, 9, 2.5, offset=True)
    els.append(dot(C, C, 14, c["gold"]))
    return els


def c_nalicourt(c):
    """Rotational serenity + one index: the water arc breaks at the nali, the drop returns."""
    els = lotus_solid(c["ink"], 0.58, 0.24, 10.5)
    a0, a1 = 103.0, 77.0  # gap centred on 90deg (toward the devotee)
    sx, sy = pt(0.76, a0)
    ex, ey = pt(0.76, a1)
    els.append(f'<path d="M {F(sx)} {F(sy)} A {F(0.76 * R)} {F(0.76 * R)} 0 1 1 {F(ex)} {F(ey)}" '
               f'fill="none" stroke="{c["ink"]}" stroke-width="2.5" stroke-linecap="round"/>')
    dx, dy = pt(0.82, 90.0)
    els.append(dot(dx, dy, 7.5, c["gold"]))
    els += dots_ring(c["ink"], 0.94, 10, offset=True)
    els.append(dot(C, C, 15, c["gold"]))
    return els


def c_orbit(c):
    """The water band: double rim holds the suns; outline lotus keeps it a seal."""
    els = [ring(0.85, 2, c["ink"]), ring(0.99, 3, c["ink"])]
    els += lotus_stroke(c["ink"], 0.56, 0.24, 12, 3)
    els += dots_ring(c["gold"], 0.92, 9.5, offset=False)
    els.append(dot(C, C, 14, c["gold"]))
    return els


def c_bloom(c):
    """Friendliest register: round-capped petal bars — community/devotee-facing."""
    els = []
    for k in range(12):
        a = TIP_UP + k * STEP
        x1, y1 = pt(0.28, a)
        x2, y2 = pt(0.55, a)
        els.append(f'<line x1="{F(x1)}" y1="{F(y1)}" x2="{F(x2)}" y2="{F(y2)}" '
                   f'stroke="{c["ink"]}" stroke-width="16" stroke-linecap="round"/>')
    els += dots_ring(c["ink"], 0.90, 9.5, offset=True)
    els.append(dot(C, C, 14, c["gold"]))
    return els


def c_tiered(c):
    """Honest to the murti: solid inner tier + outlined offset outer tier = 24 petals reading 12."""
    els = [ring(1.0, 2, c["ink"])]
    els += lotus_stroke(c["ink"], 0.62, 0.28, 12, 2.5, offset=OFF)
    els += lotus_solid(c["ink"], 0.48, 0.22, 10, belly=1.25)
    els += dots_ring(c["gold"], 0.92, 9.5, offset=False)
    els.append(dot(C, C, 13, c["gold"]))
    return els


CANDIDATES = [
    ("mala", "Beads on the thread — the medallion ring as a japamala; gold beads on an ink rim.", c_mala),
    ("engraved", "Ceremonial control — fine-stroke court, dot-in-ring suns; closest to the murti drawing.", c_engraved),
    ("suncourt", "Floating Adityas — disc-and-corona suns, no rim; the whitespace is the water.", c_suncourt),
    ("counterseal", "Negative space — lotus and medallions punched out of a solid disc; stamp / app-icon.", c_counterseal),
    ("interleave", "The 24 reading — petals and medallions interleave: 24 tattvas around the centre.", c_interleave),
    ("halo", "Wide water — a small quiet lotus, a far halo of gold petal-points.", c_halo),
    ("raywheel", "Most abstract — petals as tapered rays; the rta-chakra as pure motion.", c_raywheel),
    ("archway", "Temple-arch petals — each petal cut from two meeting arcs; ring medallions.", c_archway),
    ("nalicourt", "The index — water arc broken at the nali, the gold drop returns below.", c_nalicourt),
    ("orbit", "The water band — double rim holds the suns; outline lotus keeps it a seal.", c_orbit),
    ("bloom", "Friendliest — round-capped petal bars; community / devotee-facing register.", c_bloom),
    ("tiered", "Honest two-tier — solid inner + outlined offset outer = 24 petals reading 12.", c_tiered),
]


def emit(name, fn):
    outdir = HERE / "candidates"
    outdir.mkdir(exist_ok=True)
    for way, cols in COLORWAYS.items():
        els = fn(cols)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VB} {VB}">\n  '
               + "\n  ".join(els) + "\n</svg>\n")
        (outdir / f"{name}-{way}.svg").write_text(svg)


def gallery():
    cards = []
    for i, (name, claim, _) in enumerate(CANDIDATES, 1):
        cards.append(f"""
    <figure class="cand">
      <div class="hero"><img src="candidates/{name}-light.svg" width="210" height="210"></div>
      <div class="row">
        <span class="mini"><img src="candidates/{name}-light.svg" width="64" height="64"><i>64</i></span>
        <span class="mini"><img src="candidates/{name}-light.svg" width="32" height="32"><i>32</i></span>
        <span class="night"><img src="candidates/{name}-night.svg" width="118" height="118"></span>
      </div>
      <figcaption><b>{i} · {name}</b> — {claim}</figcaption>
    </figure>""")
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>exp/lotus-medallion — twelve treatments of one concept</title>
<link rel="stylesheet" href="../../../palette/colors.css">
<style>
  @font-face {{ font-family:'Cinzel'; font-weight:500; src:url('../../../fonts/cinzel/cinzel-500.ttf'); }}
  @font-face {{ font-family:'Inter'; font-weight:400; src:url('../../../fonts/inter/inter-400.ttf'); }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:40px 52px 80px; background:var(--rtam-ivory); color:var(--rtam-charcoal);
         font-family:Inter,sans-serif; }}
  h1 {{ font-family:Cinzel,serif; font-weight:500; font-size:26px; letter-spacing:.05em; margin:0 0 6px; }}
  .sub {{ font-size:13.5px; color:#555; max-width:960px; line-height:1.6; margin:0 0 30px; }}
  .grid {{ display:grid; grid-template-columns:repeat(3, 1fr); gap:22px; }}
  .cand {{ margin:0; border:1px solid var(--rtam-sandstone); background:#fffdf8; }}
  .hero {{ display:flex; justify-content:center; padding:24px 0 10px; }}
  .row {{ display:flex; align-items:center; justify-content:center; gap:22px; padding:8px 0 14px; }}
  .mini {{ display:inline-flex; flex-direction:column; align-items:center; gap:4px; }}
  .mini i {{ font-style:normal; font-size:10px; color:#999; }}
  .night {{ background:var(--rtam-indigo); padding:10px; line-height:0; }}
  figcaption {{ font-size:12px; line-height:1.55; padding:10px 14px 13px;
               border-top:1px solid var(--rtam-sandstone); color:#444; }}
  figcaption b {{ font-family:Cinzel,serif; font-size:13px; letter-spacing:.05em; color:var(--rtam-charcoal); }}
</style>
</head>
<body>
  <h1>exp/lotus-medallion — twelve treatments of one concept</h1>
  <p class="sub">Founder's brief: <b>top view — a 12-petal lotus at the centre, a circle of 12 medallions —
  artistic, abstract.</b> Same geometry canon under all twelve (grid.json: 30&deg; spokes, medallion ring at
  0.92R, vertical axis through a petal tip); what varies is the register: solid vs stroke, medallions as
  beads / suns / rings / points, aligned vs 15&deg;-offset, rimmed vs floating, positive vs negative space.
  Every centre dot is the linga seen from above — the brand bindu. Strips: 64/32&nbsp;px reduction; indigo
  tile = night colorway (ivory+gold).</p>
  <div class="grid">{"".join(cards)}
  </div>
</body>
</html>
"""
    (HERE / "gallery.html").write_text(html)


def main():
    for name, _, fn in CANDIDATES:
        emit(name, fn)
    gallery()
    print(f"wrote {len(CANDIDATES) * 2} candidate SVGs + gallery.html")


if __name__ == "__main__":
    main()
