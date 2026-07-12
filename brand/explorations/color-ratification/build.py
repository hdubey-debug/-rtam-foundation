#!/usr/bin/env python3
"""explorations/color-ratification — task #14: ratify, don't rethink.

Battery evidence (exp/rta-chakra/battery): the quartet held at all ten
stations; no surface forced a new colour. This study closes the colour
question formally:

  1  the ratified palette — tokens, sanctum anchors, roles
  2  contrast receipts — every governing pair, ratios computed here
     (not quoted), AA/AAA labelled
  3  the functional digital layer — deep bronze #7A5423 (Phase-1
     accent study) as link/CTA on light; gold as the functional accent
     on dark; sample UI strips both ways
  4  the jala experiment — the one open theological question: does
     water deserve its own token, or is indigo (sacred night + water)
     the water? A deep-water teal candidate beside indigo, same
     content, verdict argued
  5  ceremonial accents — kumkum #C41E3A and flame-ember #D98E32
     usage rules (festival surfaces only, never UI)
  6  CITY POSTER, Devanagari-led (founder requirement): day + night
     A-series sims for Rtambhareshvara Mandir — content plan made
     visible; Devanagari text set live in vendored Tiro (simulation;
     the governed masters land in Phase 3)
  7  street banner 3:1 sim, Devanagari-led, indigo
  8  print notes — CMYK proofing starts, Pantone where studied,
     gold-foil rule

Canon note: this study DECIDES; the baking (colors.json v2 tokens +
usage-contrast gate extensions + renames) happens once, in Phase 3,
per the one-breaking-change rule.

    python3 build.py    # writes candidates/*.svg + gallery.html
"""
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent

# canon + studied extensions
GOLD = "#C8A15A"
IVORY = "#F7F3E9"
CHARCOAL = "#1A1A1A"
SANDSTONE = "#E6DED1"
INDIGO = "#1C1A3D"
BRONZE = "#9B6A2F"
STONE = "#B8B1A4"
ACCENT = "#7A5423"      # deep bronze, P1 accent study
KUMKUM = "#C41E3A"
EMBER = "#D98E32"
JALA = "#1B3C42"        # the experiment: deep-water teal candidate

WAYS = {
    "light": {"ink": CHARCOAL, "gold": GOLD, "punch": IVORY},
    "night": {"ink": IVORY, "gold": GOLD, "punch": INDIGO},
}

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


def g_chakra(c):
    els = [ring(C, C, 213.5, c["ink"], 33)]
    for k in range(12):
        a = math.radians(-90 + k * 30)
        els.append(dot(C + MED * math.cos(a), C + MED * math.sin(a), MEDR, c["punch"]))
    els += [f'<path d="{petal_d(a)} Z" fill="{c["ink"]}" stroke="{c["punch"]}" '
            f'stroke-width="5" stroke-linejoin="round"/>' for a in range(-90, 270, 30)]
    els.append(dot(C, C, LINGA, c["gold"]))
    return els


def emit_all():
    outdir = HERE / "candidates"
    outdir.mkdir(exist_ok=True)
    for stale in outdir.glob("*.svg"):
        stale.unlink()
    for way, cols in WAYS.items():
        els = g_chakra(cols)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VB} {VB}">\n  '
               + "\n  ".join(els) + "\n</svg>\n")
        (outdir / f"chakra-{way}.svg").write_text(svg)


SWATCHES = [
    (GOLD, "gold / antiqueGold", "the lamp flame — the Lord's points only: bindu, suns, rules on dark"),
    (CHARCOAL, "charcoal (ink)", "the linga stone — primary ink, relief mass"),
    (IVORY, "ivory / warmIvory", "lit stone — the light ground"),
    (SANDSTONE, "sandstone", "carved stone — secondary ground, borders"),
    (INDIGO, "deepIndigo", "sacred night AND the water — ratified double duty"),
    (ACCENT, "deep bronze (accent)", "functional accent on light: links, CTAs (P1 study)"),
    (BRONZE, "bronze", "legacy support tone — Phase 3 folds into accent"),
    (STONE, "stoneGray", "muted support, captions on white only"),
]

PAIRS = [
    (CHARCOAL, IVORY, "body text on light ground"),
    (CHARCOAL, SANDSTONE, "text on secondary ground"),
    (IVORY, INDIGO, "text on sacred night"),
    (GOLD, INDIGO, "gold on night — functional accent on dark"),
    (GOLD, CHARCOAL, "gold on charcoal"),
    (ACCENT, IVORY, "links / CTA text on ivory"),
    (ACCENT, SANDSTONE, "links on sandstone"),
    (KUMKUM, IVORY, "kumkum ceremonial on light"),
    (EMBER, INDIGO, "flame-ember ceremonial on night"),
    (GOLD, IVORY, "gold on ivory — DECORATIVE ONLY, never text"),
    (IVORY, JALA, "text on jala teal (experiment)"),
    (GOLD, JALA, "gold on jala teal (experiment)"),
]


def pair_chip(fg, bg, label):
    r = ratio(fg, bg)
    if r >= 7:
        grade = "AAA"
    elif r >= 4.5:
        grade = "AA"
    elif r >= 3:
        grade = "AA-large"
    else:
        grade = "FAIL"
    return (f'<div class="pchip"><div class="pv" style="background:{bg}; color:{fg};">Aa {r:.2f}</div>'
            f'<div class="pl"><b>{grade}</b> · {label}<br><span>{fg} on {bg}</span></div></div>')


def gallery():
    sw = "".join(
        f'<div class="swatch"><div class="sq" style="background:{hexv}; '
        f'{"border:1px solid #ddd;" if hexv in (IVORY, SANDSTONE) else ""}"></div>'
        f'<div class="sn">{name}<br><span>{hexv} — {anchor}</span></div></div>'
        for hexv, name, anchor in SWATCHES)
    pairs = "".join(pair_chip(*p) for p in PAIRS)

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>colour ratification — the sanctum palette, proven and extended</title>
<link rel="stylesheet" href="../../palette/colors.css">
<style>
  @font-face {{ font-family:'Cinzel'; font-weight:500; src:url('../../fonts/cinzel/cinzel-500.ttf'); }}
  @font-face {{ font-family:'Inter'; font-weight:400; src:url('../../fonts/inter/inter-400.ttf'); }}
  @font-face {{ font-family:'Inter'; font-weight:600; src:url('../../fonts/inter/inter-600.ttf'); }}
  @font-face {{ font-family:'Tiro'; font-weight:400; src:url('../../fonts/tiro-devanagari-sanskrit/tiro-devanagari-sanskrit-400.ttf'); }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:40px 52px 80px; background:var(--rtam-ivory); color:var(--rtam-charcoal);
         font-family:Inter,sans-serif; }}
  h1 {{ font-family:Cinzel,serif; font-weight:500; font-size:26px; letter-spacing:.05em; margin:0 0 6px; }}
  .sub {{ font-size:13.5px; color:#555; max-width:1020px; line-height:1.65; margin:0 0 30px; }}
  h2 {{ font-family:Cinzel,serif; font-weight:500; font-size:15px; letter-spacing:.08em; margin:34px 0 12px; }}
  .st {{ border:1px solid var(--rtam-sandstone); background:#fffdf8; padding:22px 26px; }}
  .row {{ display:flex; gap:22px; flex-wrap:wrap; align-items:flex-start; }}

  .swatch {{ width:225px; }}
  .sq {{ height:64px; border-radius:3px; }}
  .sn {{ font-size:12px; font-weight:600; margin-top:6px; }}
  .sn span {{ font-weight:400; color:#777; font-size:11px; line-height:1.5; }}

  .pchip {{ width:225px; display:flex; gap:10px; align-items:center; }}
  .pv {{ width:74px; height:48px; border-radius:3px; display:flex; align-items:center;
        justify-content:center; font-weight:600; font-size:13px; border:1px solid #e5e0d5; }}
  .pl {{ font-size:11px; line-height:1.45; }}
  .pl span {{ color:#999; font-size:10px; }}

  .ui {{ width:470px; border-radius:4px; overflow:hidden; border:1px solid var(--rtam-sandstone); }}
  .ui .nav {{ display:flex; align-items:center; gap:16px; padding:12px 16px; font-size:12.5px; }}
  .ui.light {{ background:var(--rtam-ivory); }}
  .ui.light .nav a {{ color:{ACCENT}; }}
  .ui.night {{ background:var(--rtam-indigo); }}
  .ui.night .nav {{ color:var(--rtam-ivory); }}
  .ui.night .nav a {{ color:var(--rtam-gold); }}
  .ui .body {{ padding:6px 16px 16px; font-size:12px; line-height:1.6; }}
  .ui.night .body {{ color:var(--rtam-ivory); }}
  .btn {{ display:inline-block; padding:7px 16px; border-radius:3px; font-weight:600; font-size:12px; }}
  a {{ text-decoration:none; }}

  .jala-tiles {{ display:flex; gap:22px; }}
  .jtile {{ width:330px; padding:24px; text-align:center; }}
  .jtile .dn {{ font-family:Tiro,serif; font-size:21px; color:var(--rtam-ivory); margin-top:12px; }}
  .jtile .en {{ font-size:10.5px; letter-spacing:.14em; color:var(--rtam-ivory); opacity:.75; margin-top:4px; }}
  .jtile .mot {{ font-family:Tiro,serif; font-size:14px; color:var(--rtam-gold); margin-top:10px; }}
  .jlab {{ font-size:11px; color:#777; margin-top:8px; text-align:center; }}

  .cer {{ display:flex; gap:22px; align-items:center; }}
  .cchip {{ width:120px; height:56px; border-radius:3px; display:flex; align-items:center; justify-content:center;
           color:#fff; font-size:11px; font-weight:600; }}
  .fest {{ flex:1; background:var(--rtam-ivory); border:1px solid var(--rtam-sandstone); text-align:center;
          padding:18px; }}
  .fest .fl {{ font-family:Tiro,serif; font-size:19px; color:{KUMKUM}; }}
  .fest .fr {{ width:90px; height:2px; background:{KUMKUM}; margin:8px auto; }}
  .fest .fs {{ font-size:10px; letter-spacing:.18em; color:#666; }}

  .posters {{ display:flex; gap:26px; align-items:flex-start; }}
  .poster {{ width:330px; height:467px; padding:30px 24px 20px; display:flex; flex-direction:column;
            align-items:center; text-align:center; }}
  .poster.day {{ background:var(--rtam-ivory); border:1px solid var(--rtam-sandstone); }}
  .poster.night {{ background:var(--rtam-indigo); }}
  .poster .nm {{ font-family:Tiro,serif; font-size:33px; line-height:1.3; margin-top:16px; }}
  .poster.day .nm {{ color:var(--rtam-charcoal); }}
  .poster.night .nm {{ color:var(--rtam-ivory); }}
  .poster .ens {{ font-size:9.5px; letter-spacing:.22em; margin-top:6px; }}
  .poster.day .ens {{ color:#666; }}
  .poster.night .ens {{ color:var(--rtam-ivory); opacity:.7; }}
  .poster .grule {{ width:110px; height:1.5px; background:var(--rtam-gold); margin:16px auto; }}
  .poster .mot {{ font-family:Tiro,serif; font-size:17px; }}
  .poster.day .mot {{ color:{ACCENT}; }}
  .poster.night .mot {{ color:var(--rtam-gold); }}
  .poster .ev {{ font-family:Tiro,serif; font-size:19px; margin-top:22px; }}
  .poster.day .ev {{ color:{KUMKUM}; }}
  .poster.night .ev {{ color:{EMBER}; }}
  .poster .tithi {{ font-size:11px; margin-top:6px; }}
  .poster.day .tithi {{ color:#555; }}
  .poster.night .tithi {{ color:var(--rtam-ivory); opacity:.8; }}
  .poster .foot {{ margin-top:auto; display:flex; align-items:center; gap:12px; width:100%; }}
  .poster .addr {{ font-size:9.5px; text-align:left; line-height:1.6; flex:1; }}
  .poster.day .addr {{ color:#666; }}
  .poster.night .addr {{ color:var(--rtam-ivory); opacity:.75; }}
  .qr {{ width:52px; height:52px; border:1.5px solid; display:flex; align-items:center; justify-content:center;
        font-size:9px; letter-spacing:.08em; }}
  .poster.day .qr {{ border-color:#999; color:#999; }}
  .poster.night .qr {{ border-color:rgba(247,243,233,.6); color:rgba(247,243,233,.7); }}
  .plan {{ width:300px; font-size:12px; line-height:1.7; color:#444; }}
  .plan b {{ font-family:Cinzel,serif; letter-spacing:.06em; }}
  .plan ol {{ padding-left:18px; margin:8px 0; }}

  .sbanner {{ width:936px; height:312px; background:var(--rtam-indigo); display:flex; align-items:center;
             gap:36px; padding:0 48px; }}
  .sbanner .t {{ text-align:left; }}
  .sbanner .dn {{ font-family:Tiro,serif; font-size:44px; color:var(--rtam-ivory); }}
  .sbanner .en {{ font-size:12px; letter-spacing:.26em; color:var(--rtam-ivory); opacity:.72; margin-top:8px; }}
  .sbanner .mot {{ font-family:Tiro,serif; font-size:19px; color:var(--rtam-gold); margin-top:14px; }}

  table {{ border-collapse:collapse; font-size:12px; }}
  th, td {{ border-bottom:1px solid var(--rtam-sandstone); padding:7px 14px 7px 0; text-align:left; }}
  th {{ font-size:10px; letter-spacing:.1em; color:#888; }}
</style>
</head>
<body>
  <h1>colour ratification — the sanctum palette, proven and extended</h1>
  <p class="sub">Task #14, on battery evidence: the quartet held at all ten stations, so nothing is rethought.
  This page ratifies the palette formally, adds the functional digital layer from the Phase-1 accent study,
  closes the water question with an experiment, sets the ceremonial-accent rules — and carries the founder's
  new requirement: the <b>Devanagari-led city poster and street banner</b> for Rtambhareshvara Mandir as the
  print-facing stations. Decisions here; the colors.json v2 baking happens once, in Phase&nbsp;3.</p>

  <h2>1 · the ratified palette — anchored to the sanctum</h2>
  <div class="st"><div class="row">{sw}</div></div>

  <h2>2 · contrast receipts — computed, not quoted</h2>
  <div class="st"><div class="row">{pairs}</div></div>

  <h2>3 · the functional digital layer</h2>
  <div class="st"><div class="row">
    <div class="ui light">
      <div class="nav"><b style="font-family:Cinzel,serif;">&#7770;TAM</b>
        <a href="#">Darshan</a><a href="#">Seva</a><a href="#">Events</a>
        <span style="flex:1"></span>
        <span class="btn" style="background:{ACCENT}; color:{IVORY};">Donate</span></div>
      <div class="body">On light grounds the functional accent is <a href="#" style="color:{ACCENT};
      font-weight:600;">deep bronze {ACCENT}</a> — links, buttons, focus. Gold stays decorative.</div>
    </div>
    <div class="ui night">
      <div class="nav"><b style="font-family:Cinzel,serif;">&#7770;TAM</b>
        <a href="#">Darshan</a><a href="#">Seva</a><a href="#">Events</a>
        <span style="flex:1"></span>
        <span class="btn" style="background:{GOLD}; color:{CHARCOAL};">Donate</span></div>
      <div class="body">On sacred night, <a href="#" style="color:{GOLD}; font-weight:600;">gold becomes
      functional</a> — the lamp is the light source after dark.</div>
    </div>
  </div></div>

  <h2>4 · the jala experiment — does water need its own colour?</h2>
  <div class="st">
    <div class="jala-tiles">
      <div>
        <div class="jtile" style="background:{INDIGO};">
          <img src="candidates/chakra-night.svg" width="132" height="132">
          <div class="dn">&#2315;&#2340;&#2350;&#2381;&#2349;&#2352;&#2375;&#2358;&#2381;&#2357;&#2352; &#2350;&#2306;&#2342;&#2367;&#2352;</div>
          <div class="en">SACRED NIGHT &middot; DEEP INDIGO {INDIGO}</div>
          <div class="mot">&#2315;&#2340;&#2360;&#2381;&#2351; &#2346;&#2344;&#2381;&#2341;&#2366;&#2350;&#2381;</div>
        </div>
        <div class="jlab">indigo — night sky AND the water the basin holds</div>
      </div>
      <div>
        <div class="jtile" style="background:{JALA};">
          <img src="candidates/chakra-night.svg" width="132" height="132">
          <div class="dn">&#2315;&#2340;&#2350;&#2381;&#2349;&#2352;&#2375;&#2358;&#2381;&#2357;&#2352; &#2350;&#2306;&#2342;&#2367;&#2352;</div>
          <div class="en">JALA TEAL CANDIDATE {JALA}</div>
          <div class="mot">&#2315;&#2340;&#2360;&#2381;&#2351; &#2346;&#2344;&#2381;&#2341;&#2366;&#2350;&#2381;</div>
        </div>
        <div class="jlab">the teal candidate — technically passable, tonally a spa</div>
      </div>
    </div>
    <p style="font-size:12px; color:#555; max-width:900px; line-height:1.65; margin:16px 0 0;"><b>Verdict —
    indigo is ratified as the water.</b> The teal clears contrast but drags the identity toward the
    wellness/aquatic register this project has rejected three times; and theologically the murti's water is
    <i>night-dark</i>, holding the lamp's reflection — which is exactly ivory-on-indigo with gold. One ground
    colour for night and water keeps the liturgy of the palette intact. No new token.</p>
  </div>

  <h2>5 · ceremonial accents — the tilaka of the system</h2>
  <div class="st"><div class="cer">
    <div>
      <div class="cchip" style="background:{KUMKUM};">kumkum {KUMKUM}</div>
      <div class="cchip" style="background:{EMBER}; margin-top:10px;">ember {EMBER}</div>
    </div>
    <div class="fest">
      <div class="fl">&#2350;&#2361;&#2366;&#2358;&#2367;&#2357;&#2352;&#2366;&#2340;&#2381;&#2352;&#2367; &#2350;&#2361;&#2379;&#2340;&#2381;&#2360;&#2357;</div>
      <div class="fr"></div>
      <div class="fs">FESTIVAL EDITION ONLY &middot; KUMKUM ON LIGHT, EMBER ON NIGHT</div>
    </div>
    <p style="width:300px; font-size:11.5px; line-height:1.65; color:#555; margin:0;">Rules: ceremonial accents
    appear only on festival/ritual surfaces — invitations, festival posters, prasad packaging. Never in UI,
    never as body text, never both at once with gold rules on the same surface except at festival scale.
    Kumkum is the light-ground voice (5.27 on ivory), ember the night voice (6.22 on indigo).</p>
  </div></div>

  <h2>6 · the city poster — Devanagari-led, both colourways (founder requirement)</h2>
  <div class="st"><div class="posters">
    <div class="poster day">
      <img src="candidates/chakra-light.svg" width="96" height="96">
      <div class="nm">&#2315;&#2340;&#2350;&#2381;&#2349;&#2352;&#2375;&#2358;&#2381;&#2357;&#2352;<br>&#2350;&#2306;&#2342;&#2367;&#2352;</div>
      <div class="ens">RTAMBHARESHVARA MANDIR</div>
      <div class="grule"></div>
      <div class="mot">&#2315;&#2340;&#2360;&#2381;&#2351; &#2346;&#2344;&#2381;&#2341;&#2366;&#2350;&#2381;</div>
      <div class="ev">&#2350;&#2361;&#2366;&#2358;&#2367;&#2357;&#2352;&#2366;&#2340;&#2381;&#2352;&#2367; &#2350;&#2361;&#2379;&#2340;&#2381;&#2360;&#2357;</div>
      <div class="tithi">[&#2340;&#2367;&#2341;&#2367; &middot; date] &middot; [&#2360;&#2350;&#2351; &middot; time]</div>
      <div class="foot">
        <div class="addr">[&#2360;&#2381;&#2341;&#2366;&#2344; &middot; venue, city]<br>rtamfoundation.org</div>
        <div class="qr">QR</div>
      </div>
    </div>
    <div class="poster night">
      <img src="candidates/chakra-night.svg" width="96" height="96">
      <div class="nm">&#2315;&#2340;&#2350;&#2381;&#2349;&#2352;&#2375;&#2358;&#2381;&#2357;&#2352;<br>&#2350;&#2306;&#2342;&#2367;&#2352;</div>
      <div class="ens">RTAMBHARESHVARA MANDIR</div>
      <div class="grule"></div>
      <div class="mot">&#2315;&#2340;&#2360;&#2381;&#2351; &#2346;&#2344;&#2381;&#2341;&#2366;&#2350;&#2381;</div>
      <div class="ev">&#2350;&#2361;&#2366;&#2358;&#2367;&#2357;&#2352;&#2366;&#2340;&#2381;&#2352;&#2367; &#2350;&#2361;&#2379;&#2340;&#2381;&#2360;&#2357;</div>
      <div class="tithi">[&#2340;&#2367;&#2341;&#2367; &middot; date] &middot; [&#2360;&#2350;&#2351; &middot; time]</div>
      <div class="foot">
        <div class="addr">[&#2360;&#2381;&#2341;&#2366;&#2344; &middot; venue, city]<br>rtamfoundation.org</div>
        <div class="qr">QR</div>
      </div>
    </div>
    <div class="plan">
      <b>WHAT GOES ON THE POSTER</b>
      <ol>
        <li><b>The mark</b> — chakra, top centre; gold at the hub is the first thing the eye finds.</li>
        <li><b>The name, Devanagari first</b> — at least 2&times; the English support line.</li>
        <li><b>Gold rule</b> — the one gold line; separates name from message.</li>
        <li><b>The motto</b> — &#2315;&#2340;&#2360;&#2381;&#2351; &#2346;&#2344;&#2381;&#2341;&#2366;&#2350;&#2381; (becomes a governed master in Phase&nbsp;3).</li>
        <li><b>Occasion</b> — festival name in ceremonial colour (kumkum by day, ember by night) + tithi/date/time.</li>
        <li><b>Ground zone</b> — venue, site, QR. Nothing else; emptiness is the register.</li>
      </ol>
      Bilingual rule: Devanagari leads on city surfaces; English leads on web. Same grid either way.
    </div>
  </div></div>

  <h2>7 · street banner 3:1 — the drive-past test</h2>
  <div class="st"><div class="sbanner">
    <img src="candidates/chakra-night.svg" width="150" height="150">
    <div class="t">
      <div class="dn">&#2315;&#2340;&#2350;&#2381;&#2349;&#2352;&#2375;&#2358;&#2381;&#2357;&#2352; &#2350;&#2306;&#2342;&#2367;&#2352;</div>
      <div class="en">RTAMBHARESHVARA MANDIR &middot; RTAMFOUNDATION.ORG</div>
      <div class="mot">&#2315;&#2340;&#2360;&#2381;&#2351; &#2346;&#2344;&#2381;&#2341;&#2366;&#2350;&#2381;</div>
    </div>
  </div></div>

  <h2>8 · print notes — proofing starts</h2>
  <div class="st">
    <table>
      <tr><th>token</th><th>hex</th><th>CMYK start</th><th>Pantone</th><th>note</th></tr>
      <tr><td>gold</td><td>{GOLD}</td><td>0 / 20 / 55 / 22</td><td>match at vendor</td><td><b>gold foil replaces it on premium ceremonial print</b></td></tr>
      <tr><td>charcoal</td><td>{CHARCOAL}</td><td>0 / 0 / 0 / 90</td><td>Black 6 C territory</td><td>never pure #000 in print either</td></tr>
      <tr><td>ivory</td><td>{IVORY}</td><td>0 / 2 / 6 / 3</td><td>—</td><td>prefer warm uncoated stock over printing ivory</td></tr>
      <tr><td>deep indigo</td><td>{INDIGO}</td><td>54 / 57 / 0 / 76</td><td>2765 C territory</td><td>flood-coat for night posters</td></tr>
      <tr><td>deep bronze</td><td>{ACCENT}</td><td>35 / 60 / 95 / 30</td><td>1405 C</td><td>from the Phase-1 accent study</td></tr>
      <tr><td>kumkum</td><td>{KUMKUM}</td><td>0 / 92 / 70 / 15</td><td>—</td><td>festival editions only</td></tr>
    </table>
    <p style="font-size:11px; color:#888; margin:12px 0 0;">CMYK values are proofing starting points, to be
    press-checked; Pantone matches confirmed at the print vendor. All Devanagari on this page is set live in
    vendored Tiro as simulation — the governed outlined masters (motto included) land in Phase&nbsp;3.</p>
  </div>
</body>
</html>
"""
    (HERE / "gallery.html").write_text(html)


def main():
    emit_all()
    gallery()
    print("wrote 2 SVGs + gallery.html")


if __name__ == "__main__":
    main()
