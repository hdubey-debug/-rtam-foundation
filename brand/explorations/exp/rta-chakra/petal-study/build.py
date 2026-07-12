#!/usr/bin/env python3
"""exp/rta-chakra/petal-study — the petal silhouette, isolated.

Founder on the v2-12petal corolla: "the leaves are terrible... come up
with multiple leaf designs." So this study freezes everything else —
base at the jaladhari (.32 R), tips at .70 R, twelve at 30 deg, the
gold Shivalinga at .22 R — and varies ONLY the petal outline.

Six silhouettes, each from a real lotus-drawing tradition, each shown
three ways: the single petal enlarged, the bare corolla of twelve, and
seated in shila's frame (the leading candidate). The rejected v2 petal
is shown first as calibration.

Petal geometry is declared as anchor/control chains of (radius, width)
pairs in a radial frame; the right side is the mirror of the left, so
every silhouette is symmetric by construction.

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
LINGA = 0.22 * R               # 50.6
JAL = 0.32 * R                 # 73.6  — petal base
PT = 0.70 * R                  # 161.0 — petal tip
MED = 0.92 * R                 # 211.6
MEDR = 0.045 * R               # 10.35


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


def petal_d(deg, geo):
    """Left side base->tip from the declared cubics, right side mirrored."""
    P = _P(deg)
    start, cubics = geo
    d = [f"M {P(start[0], -start[1])}"]
    for c1, c2, e in cubics:
        d.append(f"C {P(c1[0], -c1[1])} {P(c2[0], -c2[1])} {P(e[0], -e[1])}")
    anchors = [start] + [e for _, _, e in cubics]
    for i in range(len(cubics) - 1, -1, -1):
        c1, c2, _ = cubics[i]
        e_prev = anchors[i]
        d.append(f"C {P(c2[0], c2[1])} {P(c1[0], c1[1])} {P(e_prev[0], e_prev[1])}")
    return " ".join(d)


# (radius, half-width) anchor/control chains, base 73.6 -> tip 161.
PETALS = [
    ("cal", "current", "The rejected one, for calibration only — belly at a third, long thin taper. What the options below are measured against.",
     ((73.6, 18.1), [((84.1, 22.6), (94.5, 24.5), (103.3, 24.5)),
                     ((131.3, 20.6), (154.0, 2.45), (161.0, 0))])),
    ("A", "shastra", "The temple flame — a full convex belly carried low, then the ogee: the line breathes inward before rising to the point. The petal carved on stone plinths (padma-pitha).",
     ((73.6, 17.0), [((82.3, 21.5), (91.0, 24.5), (99.8, 24.5)),
                     ((124.0, 21.5), (144.5, 1.0), (161.0, 0))])),
    ("B", "marquise", "The yantra petal — a serene pointed oval, belly at the very middle, both curves calm and equal. The petal of manuscript mandalas and mehndi lotuses.",
     ((73.6, 12.5), [((88.0, 19.5), (103.0, 23.5), (117.3, 23.5)),
                     ((131.5, 23.5), (147.0, 13.5), (161.0, 0))])),
    ("C", "mukula", "The bud — plump, soft-shouldered, closing to a small nib rather than a spike. The gentlest of the six; the lotus of Ajanta's painted ceilings.",
     ((73.6, 18.0), [((85.0, 23.0), (97.0, 25.0), (110.3, 25.0)),
                     ((128.0, 24.5), (147.5, 17.0), (155.5, 8.0)),
                     ((158.5, 4.2), (160.2, 1.6), (161.0, 0))])),
    ("D", "kalasha", "The dome — a full bulb gathered in by a true waist, then finishing like a finial. Each petal a tiny kalasha; the most ornamental.",
     ((73.6, 15.0), [((85.0, 21.5), (94.0, 25.0), (105.0, 25.0)),
                     ((119.0, 24.5), (133.5, 16.0), (141.8, 8.5)),
                     ((147.5, 10.2), (155.0, 4.2), (161.0, 0))])),
    ("E", "patra", "The shield — each petal fills its whole twelfth of the circle, only a seam apart, tips forming a crown. The boldest and most modern; strongest at small sizes.",
     ((73.6, 17.3), [((91.0, 21.6), (108.0, 25.6), (126.0, 29.6)),
                     ((140.0, 27.5), (152.5, 13.5), (161.0, 0))])),
    ("F", "shikhara", "The lancet — sides nearly parallel, then a decisive pointed arch, like a spire window. The most architectural and upright.",
     ((73.6, 16.5), [((95.0, 17.6), (113.0, 18.2), (131.3, 18.2)),
                     ((146.0, 15.8), (155.5, 7.2), (161.0, 0))])),
]


def svg(els, viewbox):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}">\n  '
            + "\n  ".join(els) + "\n</svg>\n")


def emit_all():
    outdir = HERE / "candidates"
    outdir.mkdir(exist_ok=True)
    for stale in outdir.glob("*.svg"):
        stale.unlink()
    for key, _, _, geo in PETALS:
        petal = f'<path d="{petal_d(-90, geo)} Z" fill="{INK}"/>'
        (outdir / f"petal-{key}.svg").write_text(svg([petal], "198 77 116 118"))

        corolla = [f'<path d="{petal_d(a, geo)} Z" fill="{INK}" stroke="{PUNCH}" '
                   f'stroke-width="4" stroke-linejoin="round"/>'
                   for a in range(-90, 270, 30)]
        corolla.append(dot(C, C, LINGA, GOLD))
        (outdir / f"corolla-{key}.svg").write_text(svg(corolla, f"0 0 {VB} {VB}"))

        shila = [ring(C, C, 213.5, INK, 33)]
        for k in range(12):
            a = math.radians(-75 + k * 30)
            shila.append(dot(C + MED * math.cos(a), C + MED * math.sin(a), MEDR, PUNCH))
        shila += [f'<path d="{petal_d(a, geo)} Z" fill="{INK}" stroke="{PUNCH}" '
                  f'stroke-width="5" stroke-linejoin="round"/>'
                  for a in range(-90, 270, 30)]
        shila.append(dot(C, C, LINGA, GOLD))
        (outdir / f"shila-{key}.svg").write_text(svg(shila, f"0 0 {VB} {VB}"))


def gallery():
    rows = []
    for key, name, claim, _ in PETALS:
        label = "reference · the rejected petal" if key == "cal" else f"{key} · {name}"
        cls = ' class="cand ref"' if key == "cal" else ' class="cand"'
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
        <p class="claim"><b>{label}</b><br>{claim}</p>
      </div>
    </section>""")
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>petal study — six silhouettes for the twelve</title>
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
  .cand.ref {{ opacity:.62; background:#f6f2e9; }}
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
  <h1>petal study — six silhouettes for the twelve</h1>
  <p class="sub">Everything frozen except the petal outline: base on the jaladhari, tips at .70&nbsp;R, twelve at
  30&deg;, the Shivalinga gold at the hub. Each silhouette shown as the single petal &middot; the bare corolla
  &middot; seated in shila (the leading frame) &middot; 64/32&nbsp;px. The petal you rejected sits at top, dimmed,
  purely for calibration. Whichever wins gets applied across all five candidates — the petal is a system-wide
  decision, not a per-design one.</p>
  {"".join(rows)}
</body>
</html>
"""
    (HERE / "gallery.html").write_text(html)


def main():
    emit_all()
    gallery()
    print(f"wrote {len(PETALS) * 3} SVGs + gallery.html")


if __name__ == "__main__":
    main()
