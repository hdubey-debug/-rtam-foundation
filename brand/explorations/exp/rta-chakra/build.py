#!/usr/bin/env python3
"""exp/rta-chakra v2 — the synthesis round, after the founder's first
positive read of v1 (commit 00a547f).

His verdict on v1: good direction. shila (relief) liked most; aditya's
gold medallions liked most as an element; the gold middle IS the
Shivalinga and stays; utkirna has aspects to keep and innovate from;
tanka mildly liked (kept for the physical register); jala rejected
outright; dvitala unmentioned (retired). The R-dot wordmark lockup in
every row is now a locked system requirement.

His one correction, now law: FROM THE TOP ONLY TWELVE PETALS ARE
VISIBLE. The 24 (two tiers) belong to the front elevation reading only.
So the plan-view icon carries a single 12-petal corolla — base at the
jaladhari (.32 R), tips at the lower tier's reach (.62 R), petals wide
enough (hw 13 deg) to close into a corolla, separated by ground-colour
seams. All other radii unchanged from iconography/geometry/grid.json.

Four candidates, converged from six:

  shila   his pick, corrected to twelve — pure relief, pierced rim,
          gold linga at true scale
  ratna   the synthesis he described: shila's relief + aditya's gold —
          the twelve suns shine THROUGH the rim's pierced windows
  mala    utkirna's aspects innovated: twin-line channel with seated
          gold beads, relief petals carrying a carved ivory vein,
          the god-point circled
  tanka   the struck coin, corrected to twelve — the emboss/foil/wax
          register, monochrome by nature, gold only at the hub

Gold at god-points only: the linga always; the Adityas where they are
set as stones (ratna, mala).

    python3 build.py    # writes candidates/*.svg + gallery.html
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent.parent / "tools"))
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
PB = JAL                       # petal base
PT = 0.62 * R                  # 142.6 — petal tips (lower tier's reach)
HW = 13.0                      # petal half-width, deg — closes the corolla
WATER = 0.84 * R               # 193.2 — waterline groove
MED = 0.92 * R                 # 211.6 — medallion centres
MEDR = 0.045 * R               # 10.35 — medallion radius


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


def fpetal(tip_r, base_r, deg, hw, fill, stroke=None, sw=0):
    """Closed solid petal; the ground-colour stroke is the seam that keeps
    neighbouring petals distinct where the corolla closes."""
    d = petal_path(C, C, tip_r, base_r, deg, hw) + " Z"
    s = (f' stroke="{stroke}" stroke-width="{F(sw)}" stroke-linejoin="round"'
         if stroke else "")
    return f'<path d="{d}" fill="{fill}"{s}/>'


def spetal(tip_r, base_r, deg, hw, col, sw):
    """Open engraved petal outline (base left open — the socket)."""
    d = petal_path(C, C, tip_r, base_r, deg, hw)
    return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{F(sw)}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def corolla(els, c, sw_seam, veins=None, vein_sw=2.6, vein_reach=0.62):
    """The single 12-petal corolla, optionally with a carved radial vein.
    On solid petals keep the vein short (a base groove) — a full midrib
    turns the petals into leaves; full length is for engraved outlines."""
    for k in range(12):
        els.append(fpetal(PT, PB, A1(k), HW, c["ink"], stroke=c["punch"], sw=sw_seam))
    if veins:
        for k in range(12):
            x0, y0 = polar(C, C, PB + 10, A1(k))
            x1, y1 = polar(C, C, PB + (PT - PB) * vein_reach, A1(k))
            els.append(path(f"M {F(x0)} {F(y0)} L {F(x1)} {F(y1)}", veins, vein_sw))


# ------------------------------------------------------------- candidates
def g_shila(c):
    """His pick, corrected to twelve. Pure relief: ink is stone, ivory is
    light; heavy rim pierced by twelve sun-windows; gold linga true scale."""
    els = []
    els.append(ring(C, C, 213.5, c["ink"], 33))     # heavy rim band 197..230
    for k in range(12):
        x, y = polar(C, C, MED, A2(k))
        els.append(dot(x, y, MEDR, c["punch"]))     # pierced sun-windows
    corolla(els, c, sw_seam=5)
    els.append(dot(C, C, LINGA, c["gold"]))
    return els, (VB, VB)


def g_ratna(c):
    """The synthesis: shila's relief + aditya's gold. The twelve Adityas
    shine through the pierced windows; a ring of window-light stays
    around each sun."""
    els = []
    els.append(ring(C, C, 213.5, c["ink"], 33))
    for k in range(12):
        x, y = polar(C, C, MED, A2(k))
        els.append(dot(x, y, MEDR, c["punch"]))
        els.append(dot(x, y, 7.4, c["gold"]))
    corolla(els, c, sw_seam=5)
    els.append(dot(C, C, LINGA, c["gold"]))
    return els, (VB, VB)


def g_mala(c):
    """utkirna's aspects, innovated: the twin-line channel now carries the
    twelve suns as set gold beads; the relief petals keep the carved vein;
    the god-point circled at the centre."""
    els = []
    els.append(ring(C, C, 230, c["ink"], 5))
    els.append(ring(C, C, 195, c["ink"], 2.5))
    for k in range(12):
        x, y = polar(C, C, MED, A2(k))
        els.append(ring(x, y, 12.2, c["ink"], 2.2))  # carved seat
        els.append(dot(x, y, 8.8, c["gold"]))        # set gold bead
    corolla(els, c, sw_seam=4, veins=c["punch"], vein_sw=2.2, vein_reach=0.42)
    els.append(ring(C, C, LINGA, c["ink"], 3))
    els.append(dot(C, C, 40, c["gold"]))
    return els, (VB, VB)


def g_tanka(c):
    """The struck coin, corrected to twelve: the plan chased into one solid
    disc — waterline groove, sun-seats, veined petals — gold at the hub.
    The emboss / foil / wax register, monochrome by nature."""
    els = [dot(C, C, R, c["ink"])]
    els.append(ring(C, C, WATER, c["punch"], 3))
    for k in range(12):
        x, y = polar(C, C, MED, A2(k))
        els.append(ring(x, y, MEDR, c["punch"], 3))
    els.append(ring(C, C, JAL, c["punch"], 3))
    corolla(els, c, sw_seam=3.5, veins=c["punch"], vein_sw=2.2)
    els.append(dot(C, C, 44, c["gold"]))
    return els, (VB, VB)


CANDIDATES = [
    ("shila", "Your pick, corrected — twelve petals only, exactly as the top view truly shows them (the twenty-four belong to the front elevation). Pure relief: ink is stone, ivory is light, the heavy rim pierced by twelve sun-windows, the Shivalinga gold at its true measured scale.", g_shila),
    ("ratna", "The synthesis you described — shila's stone relief carrying aditya's gold: the twelve Adityas now shine <i>through</i> the rim's pierced windows, each sun keeping a ring of window-light around it, the Shivalinga gold at the hub. Thirteen god-points, nothing else gilded.", g_ratna),
    ("mala", "Number two's craft, innovated — the twin-line channel now holds the twelve suns as gold beads set in carved seats; the petals stay solid relief but carry the mason's vein; the god-point circled at the centre. The most jewelled of the four.", g_mala),
    ("tanka", "The coin, corrected to twelve — kept for the physical register the others can't do: blind emboss, gold foil, the wax of the seal. The whole plan chased into one disc, gold only where the Lord stands.", g_tanka),
]


def emit_all():
    outdir = HERE / "candidates"
    outdir.mkdir(exist_ok=True)
    for stale in outdir.glob("*.svg"):
        stale.unlink()
    for name, _, fn in CANDIDATES:
        for way, cols in COLORWAYS.items():
            els, (w, h) = fn(cols)
            svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">\n  '
                   + "\n  ".join(els) + "\n</svg>\n")
            (outdir / f"{name}-{way}.svg").write_text(svg)


def gallery():
    dist = "../../../dist/outlined/logos"
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
<title>exp/rta-chakra v2 — twelve from above, the synthesis</title>
<link rel="stylesheet" href="../../../palette/colors.css">
<style>
  @font-face {{ font-family:'Cinzel'; font-weight:500; src:url('../../../fonts/cinzel/cinzel-500.ttf'); }}
  @font-face {{ font-family:'Inter'; font-weight:400; src:url('../../../fonts/inter/inter-400.ttf'); }}
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
  <h1>exp/rta-chakra v2 — twelve from above, the synthesis</h1>
  <p class="sub">Revision after your read of round one. Corrected everywhere: <b>the top view shows twelve petals
  only</b> — a single closed corolla from the jaladhari (.32&nbsp;R) to the lower tier's reach (.62&nbsp;R); the
  twenty-four stay in the front elevation, where they belong. Retired: jala (your call) and dvitala. Kept and
  fused: <b>shila's relief</b> (your pick) now carries <b>aditya's gold suns</b> in candidate two; <b>utkirna's
  carving</b> innovates into candidate three; <b>tanka</b> stays as the physical register. The Shivalinga is gold
  at the hub of all four, and every row locks up with the R-dot wordmark — both now fixed points of the system.</p>
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
