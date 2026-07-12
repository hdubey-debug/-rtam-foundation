#!/usr/bin/env python3
"""exp/symbolic — the founder's fourth brief, triangulated from three rejected
rounds: not flat geometry (read spa), not literal illustration (read like a
picture of a temple) — a SYMBOL: one distilled modern glyph that MEANS the
temple without depicting it. The vocabulary is the ritual, not the
architecture: the axis, the wheel, the falling drop, the receiving water,
the sheltering arch.

Five glyphs, each one theological statement:

  dhvaja     Rtam-bhara literally: the pillar BEARS the twelve-fold wheel
             at a single point of contact; the wheel holds the bindu
  abhisheka  grace descends from the crown-gap of the unbroken cycle toward
             the waiting water; the empty middle is where the Lord stands
  garbha     the sanctum arch shelters the seed of light — the same dot
             that lives under the R
  aksha      the world-axis pierces the twelve-fold year; the drop descends
             onto it, the water receives it
  mudra      the temple's seal struck like a coin: twelve rays of the
             Adityas cut into the field around the falling drop

Modern = thick confident strokes, generous emptiness, one or two elements.
Gold stays god-points only. Every glyph reduces to 32px unassisted (shown).

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


def dot(x, y, r, col):
    return f'<circle cx="{F(x)}" cy="{F(y)}" r="{F(r)}" fill="{col}"/>'


def path(d, col, sw, cap="round", fill="none"):
    return (f'<path d="{d}" fill="{fill}" stroke="{col}" stroke-width="{sw}" '
            f'stroke-linecap="{cap}" stroke-linejoin="round"/>')


def teardrop(cx, top_y, h, col):
    w = h * 0.62
    by = top_y + h * 0.70
    return (f'<path d="M {F(cx)} {F(top_y)} '
            f'C {F(cx - w * 0.22)} {F(top_y + h * 0.34)} {F(cx - w / 2)} {F(by - h * 0.24)} {F(cx - w / 2)} {F(by)} '
            f'A {F(w / 2)} {F(w / 2)} 0 1 0 {F(cx + w / 2)} {F(by)} '
            f'C {F(cx + w / 2)} {F(by - h * 0.24)} {F(cx + w * 0.22)} {F(top_y + h * 0.34)} {F(cx)} {F(top_y)} Z" '
            f'fill="{col}"/>')


def arc(cx, cy, r, a0, a1, col, sw, cap="butt"):
    p0 = (cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
    p1 = (cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)))
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return path(f"M {F(p0[0])} {F(p0[1])} A {F(r)} {F(r)} 0 {large} 1 {F(p1[0])} {F(p1[1])}",
                col, sw, cap=cap)


def water(cx, y, hw, col, sw):
    return path(f"M {F(cx - hw)} {F(y)} Q {F(cx)} {F(y + hw * 0.30)} {F(cx + hw)} {F(y)}", col, sw)


# ------------------------------------------------------------------ glyphs
def g_dhvaja(c):
    """The pillar bears the twelve-fold wheel at one point of contact."""
    cx, cy, r = 256.0, 190.0, 118.0
    els = []
    for k in range(12):
        a = 90 + k * 30
        els.append(arc(cx, cy, r, a - 13, a + 13, c["ink"], 10))
    els.append(dot(cx, cy, 16, c["gold"]))
    els.append(path(f"M {F(cx)} 324 L {F(cx)} 418", c["ink"], 22))
    els.append(water(cx, 440, 58, c["ink"], 9))
    return els, (512, 512)


def g_abhisheka(c):
    """Grace ENTERS the cycle: the drop pierces the crown-gap, straddling the
    ring line, and falls toward wide ground-water low in the bowl. (First cut
    kept drop + water fully inside mid-ring and read as a face.)"""
    cx, cy, r = 256.0, 240.0, 150.0
    els = []
    for k in range(12):
        a = 90 + k * 30
        a0, a1 = a - 13, a + 13
        if a == 240:
            a0, a1 = 227, 256
        if a == 300:
            a0, a1 = 284, 313
        els.append(arc(cx, cy, r, a0, a1, c["ink"], 9))
    els.append(teardrop(cx, 58, 62, c["gold"]))
    els.append(water(cx, 348, 74, c["ink"], 8))
    return els, (512, 512)


def g_garbha(c):
    """The sanctum arch shelters the seed of light."""
    els = []
    els.append(path("M 156 396 C 156 244 196 166 256 126 C 316 166 356 244 356 396",
                    c["ink"], 26))
    els.append(dot(256, 296, 24, c["gold"]))
    return els, (512, 512)


def g_aksha(c):
    """The axis pierces the twelve-fold wheel; the Lord's gold point sits at
    the crossing. (First cut — solid ring + on-ring beads + flame-drop above —
    read as the letter phi / a candlestick.)"""
    cx, cy, r = 256.0, 204.0, 112.0
    els = []
    for k in range(12):
        a = 90 + k * 30
        els.append(arc(cx, cy, r, a - 12, a + 12, c["ink"], 10))
    els.append(path(f"M {F(cx)} 76 L {F(cx)} 416", c["ink"], 20))
    els.append(dot(cx, cy, 17, c["gold"]))
    els.append(water(cx, 440, 58, c["ink"], 9))
    return els, (512, 512)


def g_mudra(c):
    """The seal struck like a coin: twelve rays cut into the field."""
    cx = cy = 256.0
    els = [dot(cx, cy, 168, c["ink"])]
    for k in range(12):
        a = 15 + k * 30
        pts = []
        for r_, w in ((168.0, 1.5), (120.0, 0.75)):
            for s in (-1, 1):
                b = math.radians(a + s * w)
                pts.append((cx + r_ * math.cos(b), cy + r_ * math.sin(b)))
        p0, p1, p2, p3 = pts[0], pts[1], pts[3], pts[2]
        els.append(f'<path d="M {F(p0[0])} {F(p0[1])} L {F(p1[0])} {F(p1[1])} '
                   f'L {F(p2[0])} {F(p2[1])} L {F(p3[0])} {F(p3[1])} Z" fill="{c["punch"]}"/>')
    els.append(f'<circle cx="{F(cx)}" cy="{F(cy)}" r="102" fill="none" '
               f'stroke="{c["punch"]}" stroke-width="3"/>')
    els.append(teardrop(cx, 202, 96, c["gold"]))
    return els, (512, 512)


CANDIDATES = [
    ("dhvaja", "The name itself as geometry — Rtam-<i>bhara</i>: the pillar BEARS the twelve-fold wheel at a single point of contact; the Lord's point holds the centre. Also the dhvaja-stambha, the standard raised before every sanctum.", g_dhvaja),
    ("abhisheka", "The temple's daily act, not its floor plan — the cycle opens at the crown and grace falls toward the waiting water. The middle is left empty: that is where the Lord stands.", g_abhisheka),
    ("garbha", "The sanctum reduced to one gesture — the arch shelters the seed of light. It is the same dot that lives under the R of the wordmark, now inside its shrine.", g_garbha),
    ("aksha", "The world-axis pierces the wheel of the year — twelve golden points around it; the drop descends onto the axis and the water below receives it.", g_aksha),
    ("mudra", "The seal, struck like a temple coin — twelve rays of the Adityas cut into the metal around the falling drop. The ceremonial one: foil, emboss, wax.", g_mudra),
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
          <img src="{dist}/rtam-wordmark-ivory-golddot.svg" style="height:26px"></div>
        </figure>
      </div>
    </section>""")
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>exp/symbolic — five symbols, not pictures</title>
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
  <h1>exp/symbolic — five symbols, not pictures</h1>
  <p class="sub">The reframe after three rejected rounds: flat geometry read <i>spa</i>, temple drawings read
  <i>literal</i>. A brand mark for a temple should work like the Om works — a <b>symbol that means, not a picture
  that depicts</b>. So the vocabulary here is the <b>ritual</b>, not the architecture: the axis, the wheel of
  twelve, the falling drop, the receiving water, the sheltering arch. One or two thick confident strokes each,
  generous emptiness, gold only at the god-points. Each row: the glyph &middot; its meaning &middot; a live lockup
  with the shipped wordmark &middot; 64/32/16&nbsp;px unassisted &middot; sacred night.</p>
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
