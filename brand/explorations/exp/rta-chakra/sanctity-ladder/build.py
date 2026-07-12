#!/usr/bin/env python3
"""exp/rta-chakra/sanctity-ladder — the recommendation made visible.

The founder re-stated the temple's core concept (2026-07-12): the same
divine consciousness present within the human heart also sustains the
order of the entire cosmos — immanent, sustaining, transcendent. Three
readings of one murti: front = 24 tattvas of Prakrti around Purusha;
top = the Rta Chakra (12 petals + 12 solar medallions, the Lord
sustaining cyclical order); inner = Anahata, the 12-petal heart lotus
with the Lord dwelling inside.

This study shows that the chosen geometry already carries all of it as
a LADDER — one drawing, three sanctity rungs, the same gold centre at
every scale:

  bindu       the Lord alone — the gold point in a plain ring;
              favicon / seal-dot / the dot under the R
  anahata     the Lord in the heart — the bare E3 corolla of twelve,
              gold at the centre; community / avatar register
  rta-chakra  the Lord bearing the cosmic order — the corolla seated
              in shila's pierced rim among the twelve Aditya windows;
              the Foundation icon

The front-view reading (24 tattvas, two tiers) is deliberately NOT
here: it belongs to the front elevation, reserved for the consecrated
ceremonial register (Phase 3).

Petal = E3 (mukta, founder's pick): narrow attachment, full E mass.
Frame = shila (founder's favourite craft). Nothing new is designed
here; the rungs are subsets of the approved mark.

    python3 build.py    # writes candidates/*.svg + gallery.html
"""
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent

COLORWAYS = {
    "light": {"ink": "#1A1A1A", "gold": "#C8A15A", "punch": "#F7F3E9"},
    "night": {"ink": "#F7F3E9", "gold": "#C8A15A", "punch": "#1C1A3D"},
}

VB = 512
C = 256.0
R = 230.0
LINGA = 0.22 * R
MED = 0.92 * R
MEDR = 0.045 * R

# E3 "mukta" petal, exactly as picked in petal-study-e.
E3_GEO = ((73.6, 10.5), [((80.0, 17.0), (92.0, 25.5), (108.0, 28.5)),
                         ((126.0, 30.4), (148.0, 14.0), (161.0, 0))])


def F(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def dot(x, y, r, col):
    return f'<circle cx="{F(x)}" cy="{F(y)}" r="{F(r)}" fill="{col}"/>'


def ring(x, y, r, col, sw):
    return (f'<circle cx="{F(x)}" cy="{F(y)}" r="{F(r)}" fill="none" '
            f'stroke="{col}" stroke-width="{F(sw)}"/>')


def petal_d(deg):
    a = math.radians(deg)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux

    def P(r, w):
        return f"{F(C + ux * r + nx * w)} {F(C + uy * r + ny * w)}"

    start, cubics = E3_GEO
    d = [f"M {P(start[0], -start[1])}"]
    for c1, c2, e in cubics:
        d.append(f"C {P(c1[0], -c1[1])} {P(c2[0], -c2[1])} {P(e[0], -e[1])}")
    anchors = [start] + [e for _, _, e in cubics]
    for i in range(len(cubics) - 1, -1, -1):
        c1, c2, _ = cubics[i]
        e_prev = anchors[i]
        d.append(f"C {P(c2[0], c2[1])} {P(c1[0], c1[1])} {P(e_prev[0], e_prev[1])}")
    return " ".join(d)


def corolla(c, seam_sw):
    return [f'<path d="{petal_d(a)} Z" fill="{c["ink"]}" stroke="{c["punch"]}" '
            f'stroke-width="{F(seam_sw)}" stroke-linejoin="round"/>'
            for a in range(-90, 270, 30)]


def g_bindu(c):
    """The Lord alone: the gold point, circled. Drawn large in its box —
    it is the smallest mark and never carries detail."""
    return [ring(C, C, 118, c["ink"], 9), dot(C, C, 76, c["gold"])]


def g_anahata(c):
    """The Lord in the heart: the bare corolla of twelve."""
    els = corolla(c, 4)
    els.append(dot(C, C, LINGA, c["gold"]))
    return els


def g_chakra(c):
    """The Lord bearing the cosmic order: the corolla seated in shila's
    pierced rim among the twelve Aditya windows. Medallions on the petal
    angles (founder-finalized 2026-07-12: aligned, bare hub) — each
    petal's ray runs tip-to-sun."""
    els = [ring(C, C, 213.5, c["ink"], 33)]
    for k in range(12):
        a = math.radians(-90 + k * 30)
        els.append(dot(C + MED * math.cos(a), C + MED * math.sin(a), MEDR, c["punch"]))
    els += corolla(c, 5)
    els.append(dot(C, C, LINGA, c["gold"]))
    return els


RUNGS = [
    ("bindu", "THE LORD ALONE", "Transcendent — beyond the universe He bears. The gold point that is the linga seen from above, the drop of abhisheka, and the dot under the R of RTAM. The favicon, the seal-dot, the smallest mark the brand will ever wear.", g_bindu),
    ("anahata", "THE LORD IN THE HEART", "Immanent — the inner view of the murti: the twelve-petal heart lotus, An&#257;hata, with the Lord dwelling at its centre. The petals attach without gripping. The community register: avatars, devotee-facing surfaces.", g_anahata),
    ("rta-chakra", "THE LORD BEARING THE COSMIC ORDER", "Sustaining — the top view of the murti: the &#7770;ta Chakra. The same heart-lotus now seated in the stone rim, the water between them, the twelve &#256;dityas as windows of light. The Foundation's icon.", g_chakra),
]


def emit_all():
    outdir = HERE / "candidates"
    outdir.mkdir(exist_ok=True)
    for stale in outdir.glob("*.svg"):
        stale.unlink()
    for name, _, _, fn in RUNGS:
        for way, cols in COLORWAYS.items():
            els = fn(cols)
            svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VB} {VB}">\n  '
                   + "\n  ".join(els) + "\n</svg>\n")
            (outdir / f"{name}-{way}.svg").write_text(svg)


def gallery():
    dist = "../../../../dist/outlined/logos"

    def strip(way):
        figs = []
        for name, title, claim, _ in RUNGS:
            figs.append(f"""
        <figure>
          <img src="candidates/{name}-{way}.svg" width="236" height="236">
          <figcaption><b>{title}</b><br>{claim}</figcaption>
        </figure>""")
        return "".join(figs)

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>the sanctity ladder — one geometry, three rungs</title>
<link rel="stylesheet" href="../../../../palette/colors.css">
<style>
  @font-face {{ font-family:'Cinzel'; font-weight:500; src:url('../../../../fonts/cinzel/cinzel-500.ttf'); }}
  @font-face {{ font-family:'Inter'; font-weight:400; src:url('../../../../fonts/inter/inter-400.ttf'); }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:40px 52px 80px; background:var(--rtam-ivory); color:var(--rtam-charcoal);
         font-family:Inter,sans-serif; }}
  h1 {{ font-family:Cinzel,serif; font-weight:500; font-size:26px; letter-spacing:.05em; margin:0 0 6px; }}
  .sub {{ font-size:13.5px; color:#555; max-width:1020px; line-height:1.65; margin:0 0 30px; }}
  .strip {{ display:flex; gap:34px; align-items:flex-start; padding:30px 34px;
           border:1px solid var(--rtam-sandstone); background:#fffdf8; margin-bottom:24px; }}
  .strip.night {{ background:var(--rtam-indigo); border-color:var(--rtam-indigo); }}
  .strip.night figcaption {{ color:#cfcae0; }}
  .strip.night figcaption b {{ color:var(--rtam-ivory); }}
  figure {{ margin:0; flex:1; text-align:center; }}
  figcaption {{ font-size:12px; line-height:1.6; color:#555; margin-top:12px; text-align:left; }}
  figcaption b {{ font-family:Cinzel,serif; font-size:12.5px; letter-spacing:.09em; color:var(--rtam-charcoal); }}
  .lockrow {{ display:flex; align-items:center; gap:20px; padding:18px 24px;
             border:1px solid var(--rtam-sandstone); background:var(--rtam-ivory); width:fit-content; }}
  .note {{ font-size:12.5px; color:#777; max-width:1020px; line-height:1.65; margin-top:18px; }}
</style>
</head>
<body>
  <h1>the sanctity ladder — one geometry, three rungs</h1>
  <p class="sub">The temple's one idea: <b>the Lord who runs the world is the Lord dwelling in your heart, and He
  is transcendental to both.</b> The chosen mark carries that idea as a ladder — the same drawing at three
  zooms, the same gold centre at every scale. Zoom all the way in and only He remains. Petal E3
  (<i>mukta</i>) · frame shila · nothing designed here that you have not already approved.</p>
  <div class="strip">{strip("light")}</div>
  <div class="strip night">{strip("night")}</div>
  <div class="lockrow">
    <img src="candidates/rta-chakra-light.svg" width="58" height="58">
    <img src="{dist}/rtam-wordmark-sacred-RTAM-dot.svg" style="height:36px">
  </div>
  <p class="note">The fourth reading — the front elevation, the two tiers of 24 tattvas of Prakṛti around
  Puruṣa — is deliberately absent from this ladder: it belongs to the consecrated ceremonial register
  (certificates, the sanctum itself), to be drawn in Phase 3. The dot under the R in the lockup above and the
  centre of every rung are the same point.</p>
</body>
</html>
"""
    (HERE / "gallery.html").write_text(html)


def main():
    emit_all()
    gallery()
    print(f"wrote {len(RUNGS) * 2} SVGs + gallery.html")


if __name__ == "__main__":
    main()
