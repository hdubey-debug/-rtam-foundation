#!/usr/bin/env python3
"""exp/rta-chakra/jaladhari-study — the founder's two concerns on the
locked mark (E3 corolla in shila's rim):

1. "The jaladhari is missing." True: the murti's inner reading is
   explicitly "shivling AND jaladhari" in the heart, and grid.json
   carries the jaladhari at .32 R — but the drawn mark shows the gold
   linga in a bare void. Three treatments compared:
     bare    as locked — the void reads as water by absence
     lip     a hairline ring at .32 R threading the gaps between the
             pinched petal bases — water glimpsed between petals
             (borrows one line into the relief register)
     vessel  a solid ink annulus around the gold — the linga visibly
             SEATED in its vessel, relief-true, no hairlines
2. "The medallions need to be aligned with the tip of the petal."
   Applied: medallions move from the offset (between tips) to the
   petal angles — each petal's ray continues across the water into its
   Aditya window. The previously-locked offset mark leads the gallery,
   dimmed, as the anchor.

Every variant shown as: the rta-chakra hero, the anahata corolla (the
jaladhari belongs to the heart reading too), sacred night, 64/32.

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
LINGA = 0.22 * R               # 50.6
JAL = 0.32 * R                 # 73.6
MED = 0.92 * R
MEDR = 0.045 * R

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


def hub(c, jaladhari):
    """The centre: gold linga, optionally seated in its jaladhari."""
    els = []
    if jaladhari == "lip":
        els.append(ring(C, C, JAL, c["ink"], 3))       # under the petals
    if jaladhari == "vessel":
        els.append(ring(C, C, 61, c["ink"], 13))       # solid annulus 54.5..67.5
    els.append(dot(C, C, LINGA, c["gold"]))
    return els


def g_chakra(c, med_deg0, jaladhari):
    els = [ring(C, C, 213.5, c["ink"], 33)]
    for k in range(12):
        a = math.radians(med_deg0 + k * 30)
        els.append(dot(C + MED * math.cos(a), C + MED * math.sin(a), MEDR, c["punch"]))
    els += hub(c, jaladhari)[:1] if jaladhari == "lip" else []
    els += corolla(c, 5)
    els += hub(c, jaladhari)[1:] if jaladhari == "lip" else hub(c, jaladhari)
    return els


def g_anahata(c, jaladhari):
    els = []
    els += hub(c, jaladhari)[:1] if jaladhari == "lip" else []
    els += corolla(c, 4)
    els += hub(c, jaladhari)[1:] if jaladhari == "lip" else hub(c, jaladhari)
    return els


VARIANTS = [
    ("ref", -75, "bare", "AS LOCKED · medallions between tips, hub bare", "The anchor — yesterday's mark, unchanged, for calibration."),
    ("aligned-bare", -90, "bare", "ALIGNED · bare hub", "Your alignment applied: each petal's ray continues across the water into its own Aditya window — the spokes of the wheel complete. The hub stays bare: water read by absence."),
    ("aligned-lip", -90, "lip", "ALIGNED · the water-lip", "Alignment plus a hairline ring at the jaladhari radius, glimpsed through the twelve gaps between the pinched petal bases — the water surfacing between the petals. Borrows one fine line into the relief register."),
    ("aligned-vessel", -90, "vessel", "ALIGNED · the vessel", "Alignment plus the jaladhari as solid relief: a dark annulus in which the gold linga visibly sits — Purusha seated in the vessel, in the lotus, in the cosmos. No hairlines; the register stays pure stone."),
]


def emit_all():
    outdir = HERE / "candidates"
    outdir.mkdir(exist_ok=True)
    for stale in outdir.glob("*.svg"):
        stale.unlink()
    for key, med0, jal, _, _ in VARIANTS:
        for way, cols in COLORWAYS.items():
            for kind, els in (("chakra", g_chakra(cols, med0, jal)),
                              ("anahata", g_anahata(cols, jal))):
                svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VB} {VB}">\n  '
                       + "\n  ".join(els) + "\n</svg>\n")
                (outdir / f"{kind}-{key}-{way}.svg").write_text(svg)


def gallery():
    rows = []
    for key, _, _, title, claim in VARIANTS:
        cls = ' class="cand ref"' if key == "ref" else ' class="cand"'
        rows.append(f"""
    <section{cls}>
      <div class="strip">
        <figure><img src="candidates/chakra-{key}-light.svg" width="236" height="236"><figcaption>rta-chakra</figcaption></figure>
        <figure><img src="candidates/anahata-{key}-light.svg" width="188" height="188"><figcaption>anahata</figcaption></figure>
        <figure class="night"><img src="candidates/chakra-{key}-night.svg" width="188" height="188"></figure>
        <div class="minis">
          <span><img src="candidates/chakra-{key}-light.svg" width="64" height="64"><i>64</i></span>
          <span><img src="candidates/chakra-{key}-light.svg" width="32" height="32"><i>32</i></span>
        </div>
        <p class="claim"><b>{title}</b><br>{claim}</p>
      </div>
    </section>""")
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>jaladhari study — the hub, and the alignment of the suns</title>
<link rel="stylesheet" href="../../../../palette/colors.css">
<style>
  @font-face {{ font-family:'Cinzel'; font-weight:500; src:url('../../../../fonts/cinzel/cinzel-500.ttf'); }}
  @font-face {{ font-family:'Inter'; font-weight:400; src:url('../../../../fonts/inter/inter-400.ttf'); }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:40px 52px 80px; background:var(--rtam-ivory); color:var(--rtam-charcoal);
         font-family:Inter,sans-serif; }}
  h1 {{ font-family:Cinzel,serif; font-weight:500; font-size:26px; letter-spacing:.05em; margin:0 0 6px; }}
  .sub {{ font-size:13.5px; color:#555; max-width:1020px; line-height:1.65; margin:0 0 30px; }}
  .cand {{ border:1px solid var(--rtam-sandstone); background:#fffdf8; margin:0 0 22px; }}
  .cand.ref {{ opacity:.62; background:#f6f2e9; }}
  .strip {{ display:flex; align-items:center; gap:30px; padding:22px 30px; }}
  figure {{ margin:0; text-align:center; }}
  figure.night {{ background:var(--rtam-indigo); padding:14px; }}
  figcaption {{ font-size:10px; color:#999; margin-top:4px; letter-spacing:.08em; }}
  .minis {{ display:flex; flex-direction:column; gap:10px; }}
  .minis span {{ display:inline-flex; flex-direction:column; align-items:center; gap:3px; }}
  .minis i {{ font-style:normal; font-size:10px; color:#999; }}
  .claim {{ flex:1; font-size:13.5px; line-height:1.65; color:#444; margin:0; }}
  .claim b {{ font-family:Cinzel,serif; font-size:13.5px; letter-spacing:.08em; color:var(--rtam-charcoal); }}
</style>
</head>
<body>
  <h1>jaladhari study — the hub, and the alignment of the suns</h1>
  <p class="sub">Your two concerns on the locked mark, isolated. <b>Alignment</b>: the medallions move onto the
  petal angles, so every petal's ray runs tip-to-sun (the locked offset version leads, dimmed, for comparison).
  <b>The jaladhari</b>: your inner reading is "shivling <i>and jaladhari</i>" in the heart — the murti seats the
  Lord in a vessel, and the mark currently shows Him in a void. Three treatments: bare (water by absence), the
  water-lip (a hairline surfacing between the petal bases), the vessel (solid relief annulus). Each shown as
  &#7771;ta-chakra &middot; an&#257;hata &middot; night &middot; 64/32.</p>
  {"".join(rows)}
</body>
</html>
"""
    (HERE / "gallery.html").write_text(html)


def main():
    emit_all()
    gallery()
    print(f"wrote {len(VARIANTS) * 4} SVGs + gallery.html")


if __name__ == "__main__":
    main()
