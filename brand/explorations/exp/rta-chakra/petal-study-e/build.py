#!/usr/bin/env python3
"""exp/rta-chakra/petal-study-e — the E branch: developing the winner.

Founder picked E (patra, the sector-filling shield) from petal-study/
and asked to innovate on it: "a different, more petal-ish, lotus-ish
shape in Number E." So every variant here keeps E's DNA — the petal
fills its whole twelfth of the circle, neighbours a seam apart, bold
mass that survives small sizes — and varies only how botanical the
outline becomes. The unchanged E leads the gallery as the anchor.

Six descendants:

  E1 padma    the broad marquise — E's mass on fully continuous curves,
              belly at the middle, no straight sides (most lotus)
  E2 agni     the flame — E's body finishing in an ogee tip: the line
              breathes inward before the point
  E3 mukta    the pinched base — petals attach narrow like real petals,
              swell fast to full width; dark rays open around the hub
  E4 hridaya  the folded tip — a soft shoulder-cusp before the point,
              like the folded edge of a floating petal
  E5 antara   E's exact silhouette carrying a carved inner echo —
              the petal-within-petal of temple stone
  E6 purna    the full bloom — E's mass under a rounded crown that
              closes in a small nib

Same frozen frame as petal-study/: base .32 R, tips .70 R, twelve at
30 deg, gold Shivalinga at .22 R. Same declaration pattern: (radius,
half-width) anchor/control cubic chains, right side mirrored.

    python3 build.py    # writes candidates/*.svg + gallery.html
"""
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent

INK = "#1A1A1A"
GOLD = "#C8A15A"
PUNCH = "#F7F3E9"

VB = 512
C = 256.0
R = 230.0
LINGA = 0.22 * R
JAL = 0.32 * R                 # 73.6  — petal base
PT = 0.70 * R                  # 161.0 — petal tip
MED = 0.92 * R
MEDR = 0.045 * R


def F(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def dot(x, y, r, col):
    return f'<circle cx="{F(x)}" cy="{F(y)}" r="{F(r)}" fill="{col}"/>'


def ring(x, y, r, col, sw):
    return (f'<circle cx="{F(x)}" cy="{F(y)}" r="{F(r)}" fill="none" '
            f'stroke="{col}" stroke-width="{F(sw)}"/>')


def _P(deg):
    a = math.radians(deg)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux

    def P(r, w):
        return f"{F(C + ux * r + nx * w)} {F(C + uy * r + ny * w)}"
    return P


def chain_d(deg, geo, close_mirror=True):
    """Left side base->tip from the declared cubics; right side mirrored."""
    P = _P(deg)
    start, cubics = geo
    d = [f"M {P(start[0], -start[1])}"]
    for c1, c2, e in cubics:
        d.append(f"C {P(c1[0], -c1[1])} {P(c2[0], -c2[1])} {P(e[0], -e[1])}")
    if close_mirror:
        anchors = [start] + [e for _, _, e in cubics]
        for i in range(len(cubics) - 1, -1, -1):
            c1, c2, _ = cubics[i]
            e_prev = anchors[i]
            d.append(f"C {P(c2[0], c2[1])} {P(c1[0], c1[1])} {P(e_prev[0], e_prev[1])}")
    return " ".join(d)


# E, the anchor (from petal-study).
E_GEO = ((73.6, 17.3), [((91.0, 21.6), (108.0, 25.6), (126.0, 29.6)),
                        ((140.0, 27.5), (152.5, 13.5), (161.0, 0))])

# Inner echo for E5: E's silhouette offset inward, drawn as an open
# carved groove (no base chord).
E_INNER = ((81.0, 11.8), [((95.0, 15.6), (110.0, 18.9), (124.5, 22.0)),
                          ((136.0, 20.4), (146.5, 9.5), (152.5, 0))])

VARIANTS = [
    ("E", "patra", "Your pick, unchanged — the anchor everything below is bred from. Fills its twelfth, a seam apart, crown of points.",
     E_GEO, None),
    ("E1", "padma", "The broad marquise — E's full mass but on completely continuous curves: no straight sides, belly at the middle, an even swell and an even taper. The most lotus of the family.",
     ((73.6, 14.0), [((88.0, 23.0), (102.0, 28.5), (117.3, 30.0)),
                     ((133.0, 29.0), (149.0, 16.0), (161.0, 0))]), None),
    ("E2", "agni", "The flame — E's body, but the tip finishes in an ogee: the line breathes inward before rising to the point, the way carved stone petals do. Bold below, sacred fire above.",
     ((73.6, 16.5), [((91.0, 21.5), (107.0, 26.0), (124.0, 29.3)),
                     ((139.0, 28.0), (147.5, 2.2), (161.0, 0))]), None),
    ("E3", "mukta", "The pinched base — petals attach narrow, as real petals do, then swell fast to E's full width. Around the hub, twelve dark rays open between the bases: the corolla starts to radiate.",
     ((73.6, 10.5), [((80.0, 17.0), (92.0, 25.5), (108.0, 28.5)),
                     ((126.0, 30.4), (148.0, 14.0), (161.0, 0))]), None),
    ("E4", "hridaya", "The folded tip — E's mass with a soft shoulder before the point, like the folded-over edge of a petal floating on water. The subtlest change; look at the crown.",
     ((73.6, 16.5), [((91.0, 21.0), (108.0, 25.8), (126.0, 29.0)),
                     ((136.0, 27.8), (144.0, 22.0), (149.5, 15.5)),
                     ((155.5, 11.5), (160.0, 4.5), (161.0, 0))]), None),
    ("E5", "antara", "E's exact silhouette, carrying a carved inner echo — the petal-within-petal cut into every temple lotus plinth. The silhouette you already chose; the craft added inside it.",
     E_GEO, E_INNER),
    ("E6", "purna", "The full bloom — E's mass under a rounded crown that closes in a small nib instead of a spike. The softest of the family while staying just as heavy.",
     ((73.6, 17.3), [((91.0, 21.6), (108.0, 25.6), (126.0, 29.3)),
                     ((141.0, 27.5), (152.0, 18.5), (156.5, 10.5)),
                     ((159.0, 5.5), (160.5, 2.0), (161.0, 0))]), None),
]


def svg(els, viewbox):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}">\n  '
            + "\n  ".join(els) + "\n</svg>\n")


def petal_els(deg, geo, inner, seam_sw):
    els = [f'<path d="{chain_d(deg, geo)} Z" fill="{INK}" stroke="{PUNCH}" '
           f'stroke-width="{F(seam_sw)}" stroke-linejoin="round"/>']
    if inner:
        els.append(f'<path d="{chain_d(deg, inner)}" fill="none" stroke="{PUNCH}" '
                   f'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
    return els


def emit_all():
    outdir = HERE / "candidates"
    outdir.mkdir(exist_ok=True)
    for stale in outdir.glob("*.svg"):
        stale.unlink()
    for key, _, _, geo, inner in VARIANTS:
        single = [f'<path d="{chain_d(-90, geo)} Z" fill="{INK}"/>']
        if inner:
            single.append(f'<path d="{chain_d(-90, inner)}" fill="none" stroke="{PUNCH}" '
                          f'stroke-width="2.4" stroke-linecap="round"/>')
        (outdir / f"petal-{key}.svg").write_text(svg(single, "198 77 116 118"))

        corolla = []
        for a in range(-90, 270, 30):
            corolla += petal_els(a, geo, inner, 4)
        corolla.append(dot(C, C, LINGA, GOLD))
        (outdir / f"corolla-{key}.svg").write_text(svg(corolla, f"0 0 {VB} {VB}"))

        shila = [ring(C, C, 213.5, INK, 33)]
        for k in range(12):
            a = math.radians(-75 + k * 30)
            shila.append(dot(C + MED * math.cos(a), C + MED * math.sin(a), MEDR, PUNCH))
        for a in range(-90, 270, 30):
            shila += petal_els(a, geo, inner, 5)
        shila.append(dot(C, C, LINGA, GOLD))
        (outdir / f"shila-{key}.svg").write_text(svg(shila, f"0 0 {VB} {VB}"))


def gallery():
    rows = []
    for key, name, claim, _, _ in VARIANTS:
        cls = ' class="cand base"' if key == "E" else ' class="cand"'
        rows.append(f"""
    <section{cls}>
      <div class="strip">
        <figure><img src="candidates/petal-{key}.svg" style="height:150px"><figcaption>the petal</figcaption></figure>
        <figure><img src="candidates/corolla-{key}.svg" width="216" height="216"><figcaption>the twelve</figcaption></figure>
        <figure><img src="candidates/shila-{key}.svg" width="216" height="216"><figcaption>in shila</figcaption></figure>
        <div class="minis">
          <span><img src="candidates/shila-{key}.svg" width="64" height="64"><i>64</i></span>
          <span><img src="candidates/shila-{key}.svg" width="32" height="32"><i>32</i></span>
        </div>
        <p class="claim"><b>{key} · {name}</b><br>{claim}</p>
      </div>
    </section>""")
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>petal study, branch E — six descendants of the shield</title>
<link rel="stylesheet" href="../../../../palette/colors.css">
<style>
  @font-face {{ font-family:'Cinzel'; font-weight:500; src:url('../../../../fonts/cinzel/cinzel-500.ttf'); }}
  @font-face {{ font-family:'Inter'; font-weight:400; src:url('../../../../fonts/inter/inter-400.ttf'); }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:40px 52px 80px; background:var(--rtam-ivory); color:var(--rtam-charcoal);
         font-family:Inter,sans-serif; }}
  h1 {{ font-family:Cinzel,serif; font-weight:500; font-size:26px; letter-spacing:.05em; margin:0 0 6px; }}
  .sub {{ font-size:13.5px; color:#555; max-width:1000px; line-height:1.65; margin:0 0 30px; }}
  .cand {{ border:1px solid var(--rtam-sandstone); background:#fffdf8; margin:0 0 22px; }}
  .cand.base {{ border:1.5px solid var(--rtam-gold); }}
  .strip {{ display:flex; align-items:center; gap:30px; padding:22px 30px; }}
  figure {{ margin:0; text-align:center; }}
  figcaption {{ font-size:10px; color:#999; margin-top:4px; letter-spacing:.08em; }}
  .minis {{ display:flex; flex-direction:column; gap:10px; }}
  .minis span {{ display:inline-flex; flex-direction:column; align-items:center; gap:3px; }}
  .minis i {{ font-style:normal; font-size:10px; color:#999; }}
  .claim {{ flex:1; font-size:13.5px; line-height:1.65; color:#444; margin:0; }}
  .claim b {{ font-family:Cinzel,serif; font-size:15px; letter-spacing:.06em; color:var(--rtam-charcoal); }}
</style>
</head>
<body>
  <h1>petal study, branch E — six descendants of the shield</h1>
  <p class="sub">Your pick, developed. Every variant keeps E's DNA — <b>the petal fills its whole twelfth, a seam
  apart, heavy enough to survive 32&nbsp;px</b> — and varies only how botanical the outline becomes. E itself
  leads, gold-framed, unchanged. Same frozen frame throughout: base on the jaladhari, tips at .70&nbsp;R, twelve
  at 30&deg;, the Shivalinga gold at the hub. Single petal &middot; the twelve &middot; in shila &middot;
  64/32&nbsp;px.</p>
  {"".join(rows)}
</body>
</html>
"""
    (HERE / "gallery.html").write_text(html)


def main():
    emit_all()
    gallery()
    print(f"wrote {len(VARIANTS) * 3} SVGs + gallery.html")


if __name__ == "__main__":
    main()
