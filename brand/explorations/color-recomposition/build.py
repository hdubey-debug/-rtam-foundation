#!/usr/bin/env python3
"""explorations/color-recomposition — the substances, not the stones.

Founder verdict on the ratified palette (2026-07-12): black and gold
yes; indigo terrible, teal terrible, ivory wash "chrome yellow-ish",
the whole thing "a government website"; icon blending into the poster
("where's the knife?"); liked individually: gold, deep bronze, bronze,
gray, charcoal; wants holy richness, matte or gloss finish thinking,
"colours as sophisticated as the philosophy".

The theological re-derivation: the old palette coloured the brand like
the ARCHITECTURE (lit stone, carved stone, night sky). Shaiva worship
has its own exact palette — the SUBSTANCES that touch the Lord:

  MAHAKALA black  #141414  the linga stone; the garbhagriha dark;
                           Shiva as Time. Black is not absence — it is
                           His colour. Ground of the brand.
  DIPA gold       #C8A15A  the lamp flame — the only light inside the
                           sanctum. God-points, display type on black,
                           foil in print.
  BHASMA ash      #C9C2B6 / #B8B1A4 / #8F887C
                           vibhuti — the sacred ash Shiva wears. Body
                           text and quiet marks on black. (The founder's
                           "gray" instinct is precisely Shaiva.)
  KANSYA bronze   #9B6A2F  bell-metal — the ghanta, panchaloha casting.
                           Warm secondary metal, large sizes on black.
  TAMRA copper    #7A5423  the abhisheka vessels — functional accent on
                           light (P1-proven 6.07/5.04, Pantone 1405C).
  CHANDRA moon    #EDEBE6  the moon on His crown; milk abhisheka. The
                           de-yellowed paper for reading surfaces.
  retired from brand surfaces: deepIndigo, jala teal, warmIvory-as-
  ground, sandstone-as-panel. (Documents may still print on white.)

Four compositions, all from the substances, judged on the criticized
surface (the city poster) plus icon tile and UI strip:

  1 GARBHAGRIHA  black leads; ash icon body + gold hub; gold display,
                 ash text. The sanctum at aarti. (proposed lead)
  2 GHANTA       black leads; two metals — bronze icon body + gold
                 hub; warmer, more ornamental.
  3 BHASMA-DAY   the reading register recomposed: moon paper, charcoal
                 ink, tamra accents, one gold rule. Kills the beige.
  4 KANAKA       all-gold icon on black; festival/invitation register;
                 matte soft-touch + gold foil ("mad finish").

    python3 build.py    # writes candidates/*.svg + gallery.html
"""
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent

BLACK = "#141414"      # mahakala ground
CHARCOAL = "#1A1A1A"   # ink on light (unchanged)
GOLD = "#C8A15A"       # dipa
ASH1 = "#C9C2B6"       # bhasma light — body on black
ASH = "#B8B1A4"        # bhasma — existing stoneGray, re-anchored
ASH2 = "#8F887C"       # bhasma deep — captions on black
BRONZE = "#9B6A2F"     # kansya
TAMRA = "#7A5423"      # copper accent (P1)
MOON = "#EDEBE6"       # chandra paper

VB = 512
C = 256.0
R = 230.0
LINGA = 0.22 * R
MED = 0.92 * R
MEDR = 0.045 * R
E3_GEO = ((73.6, 10.5), [((80.0, 17.0), (92.0, 25.5), (108.0, 28.5)),
                         ((126.0, 30.4), (148.0, 14.0), (161.0, 0))])


def F(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def _lum(hexcol):
    r, g, b = (int(hexcol[i:i + 2], 16) / 255.0 for i in (1, 3, 5))

    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def ratio(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


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


def g_chakra(body, gold, punch):
    els = [ring(C, C, 213.5, body, 33)]
    for k in range(12):
        a = math.radians(-90 + k * 30)
        els.append(dot(C + MED * math.cos(a), C + MED * math.sin(a), MEDR, punch))
    els += [f'<path d="{petal_d(a)} Z" fill="{body}" stroke="{punch}" '
            f'stroke-width="5" stroke-linejoin="round"/>' for a in range(-90, 270, 30)]
    els.append(dot(C, C, LINGA, gold))
    return els


ICONS = {
    "ash":    (ASH1, GOLD, BLACK),      # garbhagriha: ash body, gold hub
    "bronze": (BRONZE, GOLD, BLACK),    # ghanta: bell-metal body
    "day":    (CHARCOAL, GOLD, MOON),   # bhasma-day: ink on moon paper
    "gold":   (GOLD, GOLD, BLACK),      # kanaka: all-gold ceremonial
}


def emit_all():
    outdir = HERE / "candidates"
    outdir.mkdir(exist_ok=True)
    for stale in outdir.glob("*.svg"):
        stale.unlink()
    for name, (body, gold, punch) in ICONS.items():
        els = g_chakra(body, gold, punch)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VB} {VB}">\n  '
               + "\n  ".join(els) + "\n</svg>\n")
        (outdir / f"chakra-{name}.svg").write_text(svg)


def rlabel(fg, bg):
    r = ratio(fg, bg)
    grade = "AAA" if r >= 7 else ("AA" if r >= 4.5 else ("AA-large" if r >= 3 else "FAIL"))
    return f"{r:.2f} {grade}"


def gallery():
    receipts = "".join(
        f'<div class="pchip"><div class="pv" style="background:{bg}; color:{fg}; '
        f'{"border:1px solid #ddd;" if bg == MOON else ""}">Aa</div>'
        f'<div class="pl"><b>{rlabel(fg, bg)}</b> · {lab}<br><span>{fg} on {bg}</span></div></div>'
        for fg, bg, lab in [
            (GOLD, BLACK, "dipa display on mahakala"),
            (ASH1, BLACK, "bhasma body on mahakala"),
            (ASH2, BLACK, "bhasma captions on mahakala"),
            (BRONZE, BLACK, "kansya on mahakala — large/decor only"),
            (CHARCOAL, MOON, "ink on chandra paper"),
            (TAMRA, MOON, "tamra links on chandra"),
            (GOLD, MOON, "gold on chandra — DECORATIVE only"),
        ])

    def poster(icon, ground, name_c, en_c, rule_c, mot_c, ev_c, tithi_c, foot_c, qr_c, border=""):
        return f"""
      <div class="poster" style="background:{ground}; {border}">
        <img src="candidates/chakra-{icon}.svg" width="100" height="100">
        <div class="nm" style="color:{name_c};">&#2315;&#2340;&#2350;&#2381;&#2349;&#2352;&#2375;&#2358;&#2381;&#2357;&#2352;<br>&#2350;&#2306;&#2342;&#2367;&#2352;</div>
        <div class="ens" style="color:{en_c};">RTAMBHARESHVARA MANDIR</div>
        <div class="grule" style="background:{rule_c};"></div>
        <div class="mot" style="color:{mot_c};">&#2315;&#2340;&#2360;&#2381;&#2351; &#2346;&#2344;&#2381;&#2341;&#2366;&#2350;&#2381;</div>
        <div class="ev" style="color:{ev_c};">&#2350;&#2361;&#2366;&#2358;&#2367;&#2357;&#2352;&#2366;&#2340;&#2381;&#2352;&#2367; &#2350;&#2361;&#2379;&#2340;&#2381;&#2360;&#2357;</div>
        <div class="tithi" style="color:{tithi_c};">[&#2340;&#2367;&#2341;&#2367; &middot; date] &middot; [&#2360;&#2350;&#2351; &middot; time]</div>
        <div class="foot">
          <div class="addr" style="color:{foot_c};">[&#2360;&#2381;&#2341;&#2366;&#2344; &middot; venue, city]<br>rtamfoundation.org</div>
          <div class="qr" style="border-color:{qr_c}; color:{qr_c};">QR</div>
        </div>
      </div>"""

    def nav(bg, brand_c, link_c, btn_bg, btn_c, border=""):
        return f"""
      <div class="ui" style="background:{bg}; {border}">
        <div class="nav" style="color:{brand_c};"><b style="font-family:Cinzel,serif;">&#7770;TAM</b>
          <a href="#" style="color:{link_c};">Darshan</a><a href="#" style="color:{link_c};">Seva</a>
          <a href="#" style="color:{link_c};">Events</a><span style="flex:1"></span>
          <span class="btn" style="background:{btn_bg}; color:{btn_c};">Donate</span></div>
      </div>"""

    comps = f"""
  <h2>1 · GARBHAGRIHA — the sanctum at aarti <span class="rec">proposed lead register</span></h2>
  <div class="st"><div class="row">
    <div class="tile" style="background:{BLACK};"><img src="candidates/chakra-ash.svg" width="180" height="180"></div>
    {poster("ash", BLACK, GOLD, ASH2, GOLD, ASH1, GOLD, ASH1, ASH2, ASH2)}
    <div class="side">
      <p class="claim">Ash body, gold heart: the icon is <b>vibhuti and flame on the sanctum dark</b> — it can
      never blend into the ground again. Display type is the lamp (gold); reading text is the ash. One metal,
      one ash, one black: the quietest and the holiest.</p>
      {nav(BLACK, ASH1, GOLD, GOLD, CHARCOAL)}
    </div>
  </div></div>

  <h2>2 · GHANTA — bell-metal and flame</h2>
  <div class="st"><div class="row">
    <div class="tile" style="background:{BLACK};"><img src="candidates/chakra-bronze.svg" width="180" height="180"></div>
    {poster("bronze", BLACK, GOLD, ASH2, GOLD, ASH1, BRONZE, ASH1, ASH2, ASH2)}
    <div class="side">
      <p class="claim">Two metals: the corolla cast in <b>kansya bell-bronze</b>, the Lord in gold. Warmer and
      more ornamental than 1 — the temple's metalware register. Bronze stays at large sizes only (it is a
      3.9:1 colour); ash still carries the reading text.</p>
      {nav(BLACK, ASH1, GOLD, BRONZE, "#F4F1EA")}
    </div>
  </div></div>

  <h2>3 · BHASMA-DAY — the reading register, de-yellowed</h2>
  <div class="st"><div class="row">
    <div class="tile" style="background:{MOON}; border:1px solid #ddd;"><img src="candidates/chakra-day.svg" width="180" height="180"></div>
    {poster("day", MOON, CHARCOAL, ASH2, GOLD, TAMRA, TAMRA, ASH2, ASH2, ASH2, "border:1px solid #ddd;")}
    <div class="side">
      <p class="claim">Websites and letters still need a light page — but <b>chandra moon-paper, not chrome
      ivory</b>: the yellow is gone, the panels are gone, charcoal ink does the work, copper is the only accent,
      gold appears once as the rule. The government-website beige dies here; day surfaces become a gallery
      wall for the mark.</p>
      {nav(MOON, CHARCOAL, TAMRA, TAMRA, MOON, "border:1px solid #ddd;")}
    </div>
  </div></div>

  <h2>4 · KANAKA — the all-gold ceremonial</h2>
  <div class="st"><div class="row">
    <div class="tile" style="background:{BLACK};"><img src="candidates/chakra-gold.svg" width="180" height="180"></div>
    {poster("gold", BLACK, GOLD, ASH2, GOLD, ASH1, GOLD, ASH1, ASH2, ASH2)}
    <div class="side">
      <p class="claim">The festival dress: the whole mark in dipa gold on the sanctum black — in print this is
      <b>real gold foil on matte soft-touch black</b>, the "finished" richness you named. Reserved for
      invitations, festival posters, the temple drum: if everything is gold, nothing is.</p>
      {nav(BLACK, GOLD, GOLD, GOLD, CHARCOAL)}
    </div>
  </div></div>"""

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>colour recomposition — the substances, not the stones</title>
<style>
  @font-face {{ font-family:'Cinzel'; font-weight:500; src:url('../../fonts/cinzel/cinzel-500.ttf'); }}
  @font-face {{ font-family:'Inter'; font-weight:400; src:url('../../fonts/inter/inter-400.ttf'); }}
  @font-face {{ font-family:'Inter'; font-weight:600; src:url('../../fonts/inter/inter-600.ttf'); }}
  @font-face {{ font-family:'Tiro'; font-weight:400; src:url('../../fonts/tiro-devanagari-sanskrit/tiro-devanagari-sanskrit-400.ttf'); }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:40px 52px 80px; background:{MOON}; color:{CHARCOAL}; font-family:Inter,sans-serif; }}
  h1 {{ font-family:Cinzel,serif; font-weight:500; font-size:26px; letter-spacing:.05em; margin:0 0 6px; }}
  .sub {{ font-size:13.5px; color:#555; max-width:1040px; line-height:1.7; margin:0 0 22px; }}
  h2 {{ font-family:Cinzel,serif; font-weight:500; font-size:15px; letter-spacing:.08em; margin:34px 0 12px; }}
  .rec {{ font-family:Inter,sans-serif; font-size:10px; letter-spacing:.1em; background:{GOLD}; color:{CHARCOAL};
         padding:3px 8px; border-radius:2px; vertical-align:2px; margin-left:8px; }}
  .st {{ border:1px solid #ddd; background:#fbfaf7; padding:22px 26px; }}
  .row {{ display:flex; gap:26px; align-items:flex-start; flex-wrap:wrap; }}
  .tile {{ width:230px; height:230px; display:flex; align-items:center; justify-content:center; }}
  .side {{ flex:1; min-width:300px; }}
  .claim {{ font-size:12.5px; line-height:1.7; color:#444; margin:0 0 14px; max-width:430px; }}

  .subst {{ display:flex; gap:0; flex-wrap:wrap; margin:0 0 8px; }}
  .schip {{ width:132px; padding:10px 12px; color:#fff; font-size:10.5px; line-height:1.5; height:96px; }}
  .schip b {{ font-size:11.5px; letter-spacing:.06em; }}

  .pchip {{ width:230px; display:flex; gap:10px; align-items:center; margin:6px 24px 6px 0; float:left; }}
  .pv {{ width:56px; height:40px; border-radius:3px; display:flex; align-items:center; justify-content:center;
        font-weight:600; font-size:13px; }}
  .pl {{ font-size:10.5px; line-height:1.4; }}
  .pl span {{ color:#999; font-size:9.5px; }}

  .poster {{ width:300px; height:424px; padding:26px 22px 18px; display:flex; flex-direction:column;
            align-items:center; text-align:center; }}
  .poster .nm {{ font-family:Tiro,serif; font-size:30px; line-height:1.3; margin-top:14px; }}
  .poster .ens {{ font-size:9px; letter-spacing:.22em; margin-top:6px; }}
  .poster .grule {{ width:104px; height:1.5px; margin:14px auto; }}
  .poster .mot {{ font-family:Tiro,serif; font-size:16px; }}
  .poster .ev {{ font-family:Tiro,serif; font-size:17.5px; margin-top:18px; }}
  .poster .tithi {{ font-size:10.5px; margin-top:5px; }}
  .poster .foot {{ margin-top:auto; display:flex; align-items:center; gap:12px; width:100%; }}
  .poster .addr {{ font-size:9px; text-align:left; line-height:1.6; flex:1; }}
  .qr {{ width:46px; height:46px; border:1.5px solid; display:flex; align-items:center; justify-content:center;
        font-size:8.5px; letter-spacing:.08em; }}

  .ui {{ width:430px; border-radius:4px; overflow:hidden; }}
  .ui .nav {{ display:flex; align-items:center; gap:16px; padding:11px 16px; font-size:12.5px; }}
  .btn {{ display:inline-block; padding:6px 15px; border-radius:3px; font-weight:600; font-size:12px; }}
  a {{ text-decoration:none; }}
  table {{ border-collapse:collapse; font-size:12px; }}
  th, td {{ border-bottom:1px solid #ddd; padding:7px 14px 7px 0; text-align:left; }}
  th {{ font-size:10px; letter-spacing:.1em; color:#888; }}
</style>
</head>
<body>
  <h1>colour recomposition — the substances, not the stones</h1>
  <p class="sub">The reflection you asked for: the rejected palette coloured the brand like the
  <i>architecture</i> — lit stone, carved stone, night sky. That is why it read civic. Shaiva worship has its
  own palette: <b>the substances that actually touch the Lord</b>. The linga is black stone and the garbhagriha
  is dark — <b>black is His colour, not an absence</b>. The only light inside is the <b>dipa flame — gold</b>.
  Shiva wears <b>bhasma — ash</b>: your grey. The ghanta and the cast murti are <b>kansya — bell-bronze</b>;
  the abhisheka vessels are <b>tamra — copper</b>; the moon on His crown is the one white. Your liked list
  <i>is</i> this list. Retired from brand surfaces: indigo, teal, ivory-as-ground, sandstone panels. Below: the
  substance palette, its receipts, and <b>four complete compositions</b> judged on the surface you criticised.</p>

  <div class="subst">
    <div class="schip" style="background:{BLACK};"><b>MAHAKALA</b><br>{BLACK}<br>the linga; the sanctum dark; the ground</div>
    <div class="schip" style="background:{GOLD}; color:{CHARCOAL};"><b>DIPA</b><br>{GOLD}<br>the flame; god-points; display on black; foil</div>
    <div class="schip" style="background:{ASH1}; color:{CHARCOAL};"><b>BHASMA</b><br>{ASH1} / {ASH} / {ASH2}<br>vibhuti ash; body text on black</div>
    <div class="schip" style="background:{BRONZE};"><b>KANSYA</b><br>{BRONZE}<br>bell-metal; large/ornament on black</div>
    <div class="schip" style="background:{TAMRA};"><b>TAMRA</b><br>{TAMRA}<br>copper vessels; accent on light</div>
    <div class="schip" style="background:{MOON}; color:{CHARCOAL}; border:1px solid #ddd;"><b>CHANDRA</b><br>{MOON}<br>the moon-paper; reading ground</div>
  </div>

  <h2>receipts — computed on this page</h2>
  <div class="st" style="overflow:auto;">{receipts}<div style="clear:both;"></div></div>
  {comps}

  <h2>finish — the "mad finished" question</h2>
  <div class="st">
    <table>
      <tr><th>surface</th><th>finish</th><th>gold becomes</th></tr>
      <tr><td>city poster / invitation (ceremonial)</td><td><b>matte soft-touch black</b></td><td><b>hot-stamp gold foil</b> (gloss against matte — the knife in material form)</td></tr>
      <tr><td>street banner / flex</td><td>matte laminate</td><td>printed {GOLD} (foil not viable outdoors)</td></tr>
      <tr><td>letterhead / receipts</td><td>uncoated chandra stock</td><td>printed {GOLD}, used once per page</td></tr>
      <tr><td>embroidery</td><td>—</td><td>metallic gold thread on black or ash cloth</td></tr>
    </table>
    <p style="font-size:11px; color:#888; margin:12px 0 0;">Proposal: <b>1 GARBHAGRIHA leads the brand</b> (all
    dark surfaces, city print, video); <b>3 BHASMA-DAY</b> is the reading register (website body, documents);
    <b>4 KANAKA</b> is festival dress; <b>2 GHANTA</b> stands ready if you want the warmer two-metal voice
    instead of 1. Devanagari set live in vendored Tiro as simulation. Baking into colors.json v2 happens in
    Phase 3 after your pick.</p>
  </div>
</body>
</html>
"""
    (HERE / "gallery.html").write_text(html)


def main():
    emit_all()
    gallery()
    print("wrote 4 SVGs + gallery.html")


if __name__ == "__main__":
    main()
