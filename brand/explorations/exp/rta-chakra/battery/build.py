#!/usr/bin/env python3
"""exp/rta-chakra/battery — the finalized icon against the real world.

Icon finalized by the founder 2026-07-12 (b2f37f5): E3 corolla of
twelve, tip-aligned Aditya windows, bare hub, shila rim, gold
Shivalinga. This battery proves it (or finds its limits) on the
surfaces the brand will actually live on, and doubles as the evidence
base for the colour-ratification decision (task #14).

Stations:
  1  reduction ladder + the ladder rule (below 48 px the mark steps
     down to the bindu — the system's own reduction theology)
  2  favicon in browser chrome, light + dark tabs, 16 px
  3  circle avatars on platform grounds: YouTube dark #0F0F0F,
     X black #000000, Instagram white #FFFFFF — ivory and indigo
     discs, 80 px + 40 px
  4  YouTube channel banner at TRUE proportions: desktop crop of the
     2560x1440 art is a 2560x423 strip with a 1546x423 safe area —
     simulated to scale with the safe area outlined (founder asked
     whether the first sim's small lockup would scale: yes, and this
     station now shows the real geometry)
  5  YouTube thumbnail 480x270 (indigo, ivory display type; mark fully
     inside the frame, spelling per repo convention — founder fixes)
  6  donation poster header (ivory, stacked lockup, gold rule)
  7  receipt / letterhead header (quiet, small mark, charcoal text)
  8  six-centimetre embroidery simulation, single ink on sandstone
     (227 px ~ 6 cm at 96 dpi) + 128 px
  9  lockups: horizontal + stacked, light + night
 10  the four voices — two entities x two scripts: the icon locked up
     with Foundation EN, Foundation Devanagari (pratishthan), Mandir
     EN (diacritic), Mandir Devanagari. All four wordmarks are shipped
     Phase-0 masters; night variants of the Devanagari/temple voices
     do not exist yet (named Phase-3 gap).

Marks are regenerated here from the finalized geometry (single source
of truth for the study; Phase 3 moves it into brand.json).

    python3 build.py    # writes candidates/*.svg + gallery.html
"""
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent

WAYS = {
    "light": {"ink": "#1A1A1A", "gold": "#C8A15A", "punch": "#F7F3E9"},
    "night": {"ink": "#F7F3E9", "gold": "#C8A15A", "punch": "#1C1A3D"},
    "mono":  {"ink": "#1A1A1A", "gold": "#1A1A1A", "punch": "#E6DED1"},
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


def g_chakra(c):
    els = [ring(C, C, 213.5, c["ink"], 33)]
    for k in range(12):
        a = math.radians(-90 + k * 30)
        els.append(dot(C + MED * math.cos(a), C + MED * math.sin(a), MEDR, c["punch"]))
    els += corolla(c, 5)
    els.append(dot(C, C, LINGA, c["gold"]))
    return els


def g_anahata(c):
    els = corolla(c, 4)
    els.append(dot(C, C, LINGA, c["gold"]))
    return els


def g_bindu(c):
    return [ring(C, C, 118, c["ink"], 9), dot(C, C, 76, c["gold"])]


def emit_all():
    outdir = HERE / "candidates"
    outdir.mkdir(exist_ok=True)
    for stale in outdir.glob("*.svg"):
        stale.unlink()
    for name, fn in (("chakra", g_chakra), ("anahata", g_anahata), ("bindu", g_bindu)):
        for way, cols in WAYS.items():
            els = fn(cols)
            svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VB} {VB}">\n  '
                   + "\n  ".join(els) + "\n</svg>\n")
            (outdir / f"{name}-{way}.svg").write_text(svg)


def gallery():
    dist = "../../../../dist/outlined/logos"
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>battery — the finalized icon against the real world</title>
<link rel="stylesheet" href="../../../../palette/colors.css">
<style>
  @font-face {{ font-family:'Cinzel'; font-weight:500; src:url('../../../../fonts/cinzel/cinzel-500.ttf'); }}
  @font-face {{ font-family:'Inter'; font-weight:400; src:url('../../../../fonts/inter/inter-400.ttf'); }}
  @font-face {{ font-family:'Inter'; font-weight:600; src:url('../../../../fonts/inter/inter-600.ttf'); }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:40px 52px 80px; background:var(--rtam-ivory); color:var(--rtam-charcoal);
         font-family:Inter,sans-serif; }}
  h1 {{ font-family:Cinzel,serif; font-weight:500; font-size:26px; letter-spacing:.05em; margin:0 0 6px; }}
  .sub {{ font-size:13.5px; color:#555; max-width:1020px; line-height:1.65; margin:0 0 30px; }}
  h2 {{ font-family:Cinzel,serif; font-weight:500; font-size:15px; letter-spacing:.08em; margin:34px 0 12px; }}
  .st {{ border:1px solid var(--rtam-sandstone); background:#fffdf8; padding:22px 26px; }}
  .row {{ display:flex; align-items:center; gap:26px; flex-wrap:wrap; }}
  .lab {{ font-size:10px; color:#999; letter-spacing:.08em; text-align:center; margin-top:5px; }}
  .cell {{ text-align:center; }}

  .tabbar {{ width:430px; border-radius:8px 8px 0 0; padding:8px 10px 0; }}
  .tabbar.lightc {{ background:#DEE1E6; }}
  .tabbar.darkc {{ background:#202124; }}
  .tab {{ display:flex; align-items:center; gap:8px; width:230px; padding:7px 12px;
         border-radius:8px 8px 0 0; font-size:12px; }}
  .lightc .tab {{ background:#fff; color:#333; }}
  .darkc .tab {{ background:#35363A; color:#ddd; }}

  .plat {{ padding:26px 30px; display:flex; gap:30px; align-items:center; }}
  .plat.yt {{ background:#0F0F0F; }}
  .plat.x {{ background:#000; }}
  .plat.ig {{ background:#fff; border:1px solid #eee; }}
  .av {{ border-radius:50%; display:flex; align-items:center; justify-content:center; }}
  .av.ivory {{ background:var(--rtam-ivory); }}
  .av.indigo {{ background:var(--rtam-indigo); }}
  .plat .who {{ font-size:12px; }}
  .plat.yt .who, .plat.x .who {{ color:#ddd; }}
  .plat.ig .who {{ color:#333; }}

  .banner {{ width:968px; height:160px; background:var(--rtam-indigo); position:relative;
            display:flex; align-items:center; justify-content:center; }}
  .banner .safe {{ width:585px; height:160px; border-left:1px dashed rgba(247,243,233,.35);
                  border-right:1px dashed rgba(247,243,233,.35); display:flex;
                  align-items:center; justify-content:center; gap:20px; }}
  .banner .hint {{ position:absolute; right:10px; bottom:6px; font-size:9.5px; color:rgba(247,243,233,.45);
                  letter-spacing:.06em; }}
  .thumb {{ width:480px; height:270px; background:var(--rtam-indigo); position:relative;
           overflow:hidden; padding:26px 28px; }}
  .thumb .t1 {{ font-family:Cinzel,serif; font-size:30px; color:var(--rtam-ivory); line-height:1.25;
               width:250px; }}
  .thumb .t2 {{ font-size:12px; letter-spacing:.18em; color:var(--rtam-gold); margin-top:10px; }}
  .thumb img.mark {{ position:absolute; right:22px; bottom:22px; width:172px; height:172px; }}
  .thumb .chip {{ position:absolute; right:10px; top:10px; background:rgba(0,0,0,.7); color:#fff;
                 font-size:11px; padding:2px 6px; border-radius:3px; }}
  .voices {{ display:flex; flex-direction:column; gap:14px; }}
  .voices .lockup {{ background:var(--rtam-ivory); border:1px solid var(--rtam-sandstone); }}
  .voices .tag {{ font-size:10px; color:#999; letter-spacing:.08em; width:200px; }}

  .poster {{ width:640px; background:var(--rtam-ivory); border:1px solid var(--rtam-sandstone);
            text-align:center; padding:44px 30px 34px; }}
  .poster .rule {{ width:120px; height:1.5px; background:var(--rtam-gold); margin:20px auto; }}
  .poster .h {{ font-family:Cinzel,serif; font-size:15px; letter-spacing:.22em; }}

  .receipt {{ width:640px; background:#fff; border:1px solid var(--rtam-sandstone);
             display:flex; align-items:center; gap:16px; padding:16px 22px; }}
  .receipt .r1 {{ font-family:Cinzel,serif; font-size:14px; letter-spacing:.12em; }}
  .receipt .r2 {{ font-size:10.5px; color:#777; margin-top:2px; }}

  .fabric {{ background:var(--rtam-sandstone); padding:30px; display:flex; gap:40px; align-items:center; }}

  .lockup {{ display:flex; align-items:center; gap:18px; padding:16px 22px; width:fit-content; }}
  .lockup.l {{ background:var(--rtam-ivory); border:1px solid var(--rtam-sandstone); }}
  .lockup.n {{ background:var(--rtam-indigo); }}
  .stacked {{ text-align:center; padding:24px 34px; width:fit-content; }}
  .stacked.l {{ background:var(--rtam-ivory); border:1px solid var(--rtam-sandstone); }}
  .stacked.n {{ background:var(--rtam-indigo); }}
</style>
</head>
<body>
  <h1>battery — the finalized icon against the real world</h1>
  <p class="sub">Nine stations, every surface the brand will actually live on. Icon as finalized: E3 corolla,
  tip-aligned &#256;ditya windows, bare hub, gold Shivalinga. The ladder rule under test at station&nbsp;1:
  <b>below 48&nbsp;px the mark steps down a sanctity rung to the bindu</b> — reduction as theology, not
  compromise. This page is also the evidence base for the colour decision.</p>

  <h2>1 · reduction ladder</h2>
  <div class="st"><div class="row">
    <span class="cell"><img src="candidates/chakra-light.svg" width="270" height="270"><div class="lab">270</div></span>
    <span class="cell"><img src="candidates/chakra-light.svg" width="128" height="128"><div class="lab">128</div></span>
    <span class="cell"><img src="candidates/chakra-light.svg" width="64" height="64"><div class="lab">64</div></span>
    <span class="cell"><img src="candidates/chakra-light.svg" width="48" height="48"><div class="lab">48 — last chakra size</div></span>
    <span class="cell"><img src="candidates/bindu-light.svg" width="48" height="48"><div class="lab">48 bindu</div></span>
    <span class="cell"><img src="candidates/bindu-light.svg" width="32" height="32"><div class="lab">32</div></span>
    <span class="cell"><img src="candidates/bindu-light.svg" width="24" height="24"><div class="lab">24</div></span>
    <span class="cell"><img src="candidates/bindu-light.svg" width="16" height="16"><div class="lab">16</div></span>
  </div></div>

  <h2>2 · favicon in browser chrome</h2>
  <div class="st"><div class="row">
    <div class="tabbar lightc"><div class="tab"><img src="candidates/bindu-light.svg" width="16" height="16"> &#7770;TAM Foundation</div></div>
    <div class="tabbar darkc"><div class="tab"><img src="candidates/bindu-night.svg" width="16" height="16"> &#7770;TAM Foundation</div></div>
  </div></div>

  <h2>3 · avatars on platform grounds — YouTube dark · X black · Instagram white</h2>
  <div class="st" style="padding:0; overflow:hidden;">
    <div class="plat yt">
      <span class="av ivory" style="width:80px;height:80px;"><img src="candidates/chakra-light.svg" width="62" height="62"></span>
      <span class="av indigo" style="width:80px;height:80px;"><img src="candidates/chakra-night.svg" width="62" height="62"></span>
      <span class="av ivory" style="width:40px;height:40px;"><img src="candidates/chakra-light.svg" width="31" height="31"></span>
      <span class="av indigo" style="width:40px;height:40px;"><img src="candidates/bindu-night.svg" width="31" height="31"></span>
      <span class="who">&#7770;TAM Foundation &middot; @rtamfoundation &middot; YouTube #0F0F0F</span>
    </div>
    <div class="plat x">
      <span class="av ivory" style="width:80px;height:80px;"><img src="candidates/chakra-light.svg" width="62" height="62"></span>
      <span class="av indigo" style="width:80px;height:80px;"><img src="candidates/chakra-night.svg" width="62" height="62"></span>
      <span class="av ivory" style="width:40px;height:40px;"><img src="candidates/chakra-light.svg" width="31" height="31"></span>
      <span class="av indigo" style="width:40px;height:40px;"><img src="candidates/bindu-night.svg" width="31" height="31"></span>
      <span class="who">X / Twitter #000000</span>
    </div>
    <div class="plat ig">
      <span class="av ivory" style="width:80px;height:80px; border:1px solid #e5e5e5;"><img src="candidates/chakra-light.svg" width="62" height="62"></span>
      <span class="av indigo" style="width:80px;height:80px;"><img src="candidates/chakra-night.svg" width="62" height="62"></span>
      <span class="av ivory" style="width:40px;height:40px; border:1px solid #e5e5e5;"><img src="candidates/chakra-light.svg" width="31" height="31"></span>
      <span class="av indigo" style="width:40px;height:40px;"><img src="candidates/bindu-night.svg" width="31" height="31"></span>
      <span class="who">Instagram #FFFFFF</span>
    </div>
  </div>

  <h2>4 · YouTube channel banner — true desktop-crop geometry (2560&times;423 strip, 1546&times;423 safe area, scaled &times;0.378)</h2>
  <div class="st">
    <div class="banner">
      <div class="safe">
        <img src="candidates/chakra-night.svg" width="76" height="76">
        <img src="{dist}/rtam-wordmark-white-golddot.svg" style="height:34px">
      </div>
      <span class="hint">dashed = mobile/desktop safe area &middot; at real size this lockup is &asymp;2.6&times; larger than shown</span>
    </div>
  </div>

  <h2>5 · YouTube thumbnail 480&times;270 — mark whole, spelling per repo convention</h2>
  <div class="st"><div class="thumb">
    <div class="t1">Rudrabhisheka</div>
    <div class="t2">LIVE &middot; MAHA SHIVARATRI</div>
    <img class="mark" src="candidates/chakra-night.svg">
    <span class="chip">3:12:44</span>
  </div></div>

  <h2>6 · donation poster header</h2>
  <div class="st"><div class="poster">
    <img src="candidates/chakra-light.svg" width="92" height="92"><br>
    <img src="{dist}/rtam-wordmark-sacred-RTAM-dot.svg" style="height:40px; margin-top:16px;">
    <div class="rule"></div>
    <div class="h">RTAMBHARESHVARA MANDIR</div>
  </div></div>

  <h2>7 · receipt / letterhead header</h2>
  <div class="st"><div class="receipt">
    <img src="candidates/chakra-light.svg" width="48" height="48">
    <div>
      <div class="r1">RTAM FOUNDATION</div>
      <div class="r2">Donation receipt &middot; 501(c)(3) &middot; rtamfoundation.org</div>
    </div>
  </div></div>

  <h2>8 · embroidery, single ink, 6 cm on fabric</h2>
  <div class="st" style="padding:0;"><div class="fabric">
    <span class="cell"><img src="candidates/chakra-mono.svg" width="227" height="227"><div class="lab">6 cm</div></span>
    <span class="cell"><img src="candidates/chakra-mono.svg" width="128" height="128"><div class="lab">3.4 cm</div></span>
    <span class="cell"><img src="candidates/anahata-mono.svg" width="128" height="128"><div class="lab">anahata 3.4 cm</div></span>
  </div></div>

  <h2>9 · lockups — horizontal and stacked</h2>
  <div class="st"><div class="row">
    <div class="lockup l">
      <img src="candidates/chakra-light.svg" width="58" height="58">
      <img src="{dist}/rtam-wordmark-sacred-RTAM-dot.svg" style="height:36px">
    </div>
    <div class="lockup n">
      <img src="candidates/chakra-night.svg" width="58" height="58">
      <img src="{dist}/rtam-wordmark-white-golddot.svg" style="height:34px">
    </div>
    <div class="stacked l">
      <img src="candidates/chakra-light.svg" width="76" height="76"><br>
      <img src="{dist}/rtam-wordmark-sacred-RTAM-dot.svg" style="height:30px; margin-top:12px;">
    </div>
    <div class="stacked n">
      <img src="candidates/chakra-night.svg" width="76" height="76"><br>
      <img src="{dist}/rtam-wordmark-white-golddot.svg" style="height:28px; margin-top:12px;">
    </div>
  </div></div>

  <h2>10 · the four voices — two entities &times; two scripts, one icon</h2>
  <div class="st"><div class="voices">
    <div class="row">
      <div class="lockup">
        <img src="candidates/chakra-light.svg" width="54" height="54">
        <img src="{dist}/rtam-wordmark-sacred-RTAM-dot.svg" style="height:34px">
      </div>
      <span class="tag">FOUNDATION &middot; ENGLISH</span>
    </div>
    <div class="row">
      <div class="lockup">
        <img src="candidates/chakra-light.svg" width="54" height="54">
        <img src="{dist}/rtam-wordmark-devanagari-pratishthan.svg" style="height:34px">
      </div>
      <span class="tag">FOUNDATION &middot; DEVANAGARI</span>
    </div>
    <div class="row">
      <div class="lockup">
        <img src="candidates/chakra-light.svg" width="54" height="54">
        <img src="{dist}/rtam-temple-wordmark-diacritic.svg" style="height:42px">
      </div>
      <span class="tag">MANDIR &middot; ENGLISH</span>
    </div>
    <div class="row">
      <div class="lockup">
        <img src="candidates/chakra-light.svg" width="54" height="54">
        <img src="{dist}/rtam-temple-wordmark-devanagari.svg" style="height:46px">
      </div>
      <span class="tag">MANDIR &middot; DEVANAGARI</span>
    </div>
  </div>
  <p style="font-size:11.5px; color:#888; margin:14px 0 0; line-height:1.6;">All four wordmarks are shipped
  Phase-0 masters (font-free, outlined). Named gap for Phase&nbsp;3: night (ivory-ink) variants of the
  Devanagari and Mandir voices do not exist yet; and per the perspective-family architecture the Mandir may
  receive its own elevation mark — these lockups prove the chakra pairs with every voice meanwhile.</p>
  </div>
</body>
</html>
"""
    (HERE / "gallery.html").write_text(html)


def main():
    emit_all()
    gallery()
    print("wrote 9 SVGs + gallery.html")


if __name__ == "__main__":
    main()
