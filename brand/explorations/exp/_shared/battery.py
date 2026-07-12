#!/usr/bin/env python3
"""Shared Phase-2 battery: every exp/* branch renders its marks through the
SAME stations so the four directions compare apples-to-apples.

A branch calls emit_battery(branch_dir, manifest) with a manifest naming its
mark files (paths relative to the branch dir). Stations: hero, reduction
ladder, favicon strip 16/24/32/48 on light+dark, dark grounds (indigo +
charcoal), bilingual co-brand, circle avatar, poster header sim, receipt
header sim, 6 cm mono print sim, mini specimen. Missing optional keys render
as an explicit "not provided" cell — absence must be visible, not silent.

Manifest keys:
  name, claim                       str (short); claim = the hypothesis line
  hero                              path — the direction's flagship mark
  ladder                            [(path, label), ...] reduction steps
  favicon_light, favicon_dark       path — favicon-shaped mark per tab theme
  dark_indigo, dark_charcoal        path — dark-ground treatment
  avatar                            path — circle-crop candidate
  mono                              path — single-colour mark (print/embroidery)
  specimen                          [(path, label), ...] everything the branch ships
"""
from pathlib import Path

DIST = "../../../dist/outlined"


def _img(src, style=""):
    attr = ' style="' + style + '"' if style else ""
    return f'<img src="{src}"{attr}>'


def _cell(head, body, cls="cell"):
    return f'<div class="{cls}"><div class="head">{head}</div><div class="body">{body}</div></div>'


def emit_battery(branch_dir: Path, m: dict) -> Path:
    def station(key, head, body_fn, cls="cell"):
        if m.get(key):
            return _cell(head, body_fn(m[key]), cls)
        return _cell(head, '<span class="missing">not provided by this direction</span>', cls)

    fav_row_light = fav_row_dark = '<span class="missing">not provided</span>'
    if m.get("favicon_light"):
        fav_row_light = "".join(
            f'<span class="fav"><img src="{m["favicon_light"]}" width="{s}" height="{s}"><i>{s}</i></span>'
            for s in (16, 24, 32, 48))
    if m.get("favicon_dark"):
        fav_row_dark = "".join(
            f'<span class="fav"><img src="{m["favicon_dark"]}" width="{s}" height="{s}"><i>{s}</i></span>'
            for s in (16, 24, 32, 48))

    ladder = "".join(
        f'<figure><img src="{p}"><figcaption>{lab}</figcaption></figure>'
        for p, lab in m.get("ladder", []))
    specimen = "".join(
        f'<figure><img src="{p}"><figcaption>{lab}</figcaption></figure>'
        for p, lab in m.get("specimen", []))

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>exp/{m['name']} — Phase-2 battery</title>
<link rel="stylesheet" href="../../../palette/colors.css">
<style>
  @font-face {{ font-family:'Cinzel'; font-weight:500; src:url('../../../fonts/cinzel/cinzel-500.ttf'); }}
  @font-face {{ font-family:'Inter'; font-weight:400; src:url('../../../fonts/inter/inter-400.ttf'); }}
  @font-face {{ font-family:'Inter'; font-weight:300; src:url('../../../fonts/inter/inter-300.ttf'); }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:40px 56px 80px; background:var(--rtam-ivory); color:var(--rtam-charcoal);
         font-family:Inter,sans-serif; }}
  h1 {{ font-family:Cinzel,serif; font-weight:500; font-size:26px; letter-spacing:.05em; margin:0; }}
  .claim {{ font-size:14px; color:#555; margin:6px 0 30px; max-width:900px; line-height:1.6; }}
  .grid {{ display:grid; grid-template-columns:repeat(12, 1fr); gap:18px; }}
  .cell {{ border:1px solid var(--rtam-sandstone); background:#fffdf8; grid-column:span 6; }}
  .cell.third {{ grid-column:span 4; }}
  .cell.full {{ grid-column:span 12; }}
  .cell .head {{ font-size:10.5px; letter-spacing:.12em; text-transform:uppercase; color:#877;
                padding:8px 12px; border-bottom:1px solid var(--rtam-sandstone); }}
  .cell .body {{ padding:22px; display:flex; align-items:center; justify-content:center; gap:26px;
                min-height:150px; flex-wrap:wrap; }}
  .cell .body img {{ max-width:100%; }}
  .missing {{ color:#b66; font-size:12px; letter-spacing:.05em; }}
  .dark-i .body {{ background:var(--rtam-indigo); }}
  .dark-c .body {{ background:var(--rtam-charcoal); }}
  .fav {{ display:inline-flex; flex-direction:column; align-items:center; gap:6px; margin:0 14px; }}
  .fav i {{ font-style:normal; font-size:10px; color:#999; }}
  .hero-img {{ width:340px; }}
  figure {{ margin:0; text-align:center; }}
  figcaption {{ font-size:10.5px; color:#888; margin-top:8px; letter-spacing:.05em; }}
  .avatar {{ width:150px; height:150px; border-radius:50%; overflow:hidden; background:#fff;
            border:1px solid var(--rtam-sandstone); display:flex; align-items:center; justify-content:center; }}
  .avatar img {{ width:78%; }}
  .poster-sim .body {{ background:var(--rtam-indigo); flex-direction:column; padding:36px; }}
  .poster-sim img.mark {{ width:120px; margin-bottom:18px; }}
  .poster-sim img.wm {{ width:380px; }}
  .receipt-sim img.mark {{ width:74px; }}
  .receipt-sim img.wm {{ width:360px; }}
  .mono-sim .body {{ filter:grayscale(1); }}
  .mono-sim img {{ width:227px; }} /* 6 cm at 96 dpi */
  .co img {{ vertical-align:middle; }}
</style>
</head>
<body>
  <h1>exp/{m['name']}</h1>
  <p class="claim"><strong>Claim:</strong> {m['claim']}</p>
  <div class="grid">
    {station('hero', 'Hero — flagship mark on ivory', lambda p: _img(p, 'width:340px'))}
    {_cell('Reduction ladder', ladder or '<span class="missing">not provided</span>')}
    {_cell('Favicon — light tabs 16/24/32/48', fav_row_light, 'cell third')}
    {_cell('Favicon — dark tabs 16/24/32/48', fav_row_dark + '', 'cell third dark-c')}
    {station('avatar', 'Circle avatar crop', lambda p: f'<div class="avatar"><img src="{p}"></div>', 'cell third')}
    {station('dark_indigo', 'Sacred night — indigo ground', lambda p: _img(p, 'width:300px'), 'cell dark-i')}
    {station('dark_charcoal', 'Working dark — charcoal ground', lambda p: _img(p, 'width:300px'), 'cell dark-c')}
    {station('cobrand', 'Bilingual co-brand — mark + shipped lockup', lambda p: f'<span class="co">{_img(p, "width:120px")}</span><span class="co">{_img(DIST + "/lockups/rtam-bilingual-foundation.svg", "width:430px")}</span>', 'cell full')}
    {station('poster_mark', 'Donation-poster header simulation', lambda p: f'<img class="mark" src="{p}"><img class="wm" src="{DIST}/logos/rtam-wordmark-white-golddot.svg">', 'cell poster-sim')}
    {station('receipt_mark', 'Receipt / letterhead header simulation', lambda p: f'<img class="mark" src="{p}"><img class="wm" src="{DIST}/lockups/donation-lockup.svg">', 'cell receipt-sim')}
    {station('mono', '6 cm mono print / embroidery simulation', lambda p: _img(p), 'cell mono-sim')}
    {_cell('Mini specimen — everything this direction ships', specimen or '<span class="missing">none</span>', 'cell full')}
  </div>
</body>
</html>
"""
    out = branch_dir / "battery.html"
    out.write_text(html)
    return out
