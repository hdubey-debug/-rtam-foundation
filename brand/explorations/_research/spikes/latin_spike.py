#!/usr/bin/env python3
"""SPIKE 2 + SPIKE 3.

SPIKE 2 (Latin outlining): the exact wordmark composition — Cinzel 500
'RTAM' fs=120 ls=12 + Cinzel 400 'Foundation' fs=62 ls=8, at the shipped
coordinates — through the same uharfbuzz->fontTools pipeline proven for
Devanagari. Gate:
  B. structural_diff max blob <= 150px between cairosvg and Chromium
     renders of the outlined SVG (calibrated by negative_control.py).
  (informational: strip fidelity vs Chromium live text with the same
   local TTFs and letter-spacing.)

SPIKE 3 (negative-space feasibility, concept e): skia-pathops boolean
difference — punch a circular counter out of the Cinzel R outline — must
  1. actually remove ink (punched-vs-plain max blob >= 300: the bite is
     a real concentrated difference), and
  2. render identically in cairosvg and Chromium (max blob <= 150).
Placement is arbitrary here; this is an engineering feasibility proof,
not a design.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRAND = HERE.parent.parent.parent
sys.path.insert(0, str(BRAND / "tools"))
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402
from render_diff import ink_mask, structural_diff, MAX_BLOB, SIZE  # noqa: E402
from shaping_spike import outline_svg, strip_fidelity, svg_doc, render_chromium, RENDER_SCALE  # noqa: E402

CINZEL = {w: BRAND / f"fonts/cinzel/cinzel-{w}.ttf" for w in (400, 500, 600, 700)}


def main() -> int:
    import cairosvg
    from pathops import Path as SkPath, op, PathOp
    from playwright.sync_api import sync_playwright
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen

    failures = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": SIZE, "height": SIZE},
                                  device_scale_factor=RENDER_SCALE)
        page = ctx.new_page()

        # ---------------- SPIKE 2: wordmark composition ----------------
        # shipped: <text x=80 y=160 fs=120 wght=500 ls=12>RTAM</text>
        #          <text x=540 y=160 fs=62 wght=400 ls=8>Foundation</text>
        ds1, n1, _ = outline_svg(CINZEL[500], "RTAM", 120, 80, 160, letter_spacing=12)
        ds2, n2, _ = outline_svg(CINZEL[400], "Foundation", 62, 540, 160, letter_spacing=8)
        w, h = 1080, 240
        body = ("".join(f'<path d="{d}" fill="#1A1A1A"/>' for d in ds1 + ds2)
                + '<circle cx="118" cy="188" r="10" fill="#C8A15A"/>')
        out_svg = HERE / "latin-wordmark-outlined.svg"
        out_svg.write_text(svg_doc(body, w, h))
        print(f"[wordmark] RTAM glyphs: {n1}; Foundation glyphs: {n2}")

        ref_svg = HERE / "latin-wordmark-livetext.svg"
        ref_svg.write_text(svg_doc(
            "<defs><style>"
            f"@font-face{{font-family:'C500';src:url('{CINZEL[500].resolve().as_uri()}');}}"
            f"@font-face{{font-family:'C400';src:url('{CINZEL[400].resolve().as_uri()}');}}"
            "</style></defs>"
            '<text x="80" y="160" font-family="C500" font-size="120" letter-spacing="12" fill="#1A1A1A">RTAM</text>'
            '<text x="540" y="160" font-family="C400" font-size="62" letter-spacing="8" fill="#1A1A1A">Foundation</text>'
            '<circle cx="118" cy="188" r="10" fill="#C8A15A"/>', w, h))

        p_out_chrome = HERE / "latin-wordmark-outlined-chrome.png"
        p_ref_chrome = HERE / "latin-wordmark-livetext-chrome.png"
        render_chromium(out_svg, p_out_chrome, page)
        render_chromium(ref_svg, p_ref_chrome, page)
        p_out_cairo = HERE / "latin-wordmark-outlined-cairo.png"
        cairosvg.svg2png(url=str(out_svg), write_to=str(p_out_cairo),
                         output_width=SIZE * RENDER_SCALE, background_color="#ffffff")

        db = structural_diff(ink_mask(p_out_cairo), ink_mask(p_out_chrome))
        gb = db["max_blob"] <= MAX_BLOB
        c1, drift, line = strip_fidelity(ink_mask(p_out_chrome), ink_mask(p_ref_chrome))
        drift_pct = 100.0 * drift / line
        print(f"  Gate B max-blob(cairo,chrome) = {db['max_blob']}px (gate {MAX_BLOB}), "
              f"diff={db['diff_px']}px, iou={db['iou']:.4f} -> {'PASS' if gb else 'FAIL'}")
        print(f"  info: vs livetext min strip IoU = {c1:.4f}, "
              f"drift = {drift}px/{line}px ({drift_pct:.2f}%)\n")
        if not gb:
            failures.append(f"wordmark: gate B max-blob {db['max_blob']} > {MAX_BLOB}")

        # ---------------- SPIKE 3: negative-space bindu ----------------
        # Outline the R alone (fs=120 at x=80/y=160), punch a circle r=12
        # near the bowl/leg junction (~140,118) with skia-pathops.
        tt = TTFont(CINZEL[500])
        glyph_set = tt.getGlyphSet()
        cmap = tt.getBestCmap()
        rname = cmap[ord("R")]
        upem = tt["head"].unitsPerEm
        s = 120 / upem

        sk_r = SkPath()
        tpen = TransformPen(sk_r.getPen(glyphSet=glyph_set), (s, 0, 0, -s, 80, 160))
        glyph_set[rname].draw(tpen)

        k = 0.5523
        cxc, cyc, r = 140.0, 118.0, 12.0
        sk_c = SkPath()
        pen_c = sk_c.getPen()
        pen_c.moveTo((cxc + r, cyc))
        pen_c.curveTo((cxc + r, cyc + k * r), (cxc + k * r, cyc + r), (cxc, cyc + r))
        pen_c.curveTo((cxc - k * r, cyc + r), (cxc - r, cyc + k * r), (cxc - r, cyc))
        pen_c.curveTo((cxc - r, cyc - k * r), (cxc - k * r, cyc - r), (cxc, cyc - r))
        pen_c.curveTo((cxc + k * r, cyc - r), (cxc + r, cyc - k * r), (cxc + r, cyc))
        pen_c.closePath()

        punched = op(sk_r, sk_c, PathOp.DIFFERENCE)
        spen = SVGPathPen(None)
        punched.draw(spen)
        d = spen.getCommands()
        spen_plain = SVGPathPen(None)
        sk_r.draw(spen_plain)
        d_plain = spen_plain.getCommands()
        print(f"[negative-space] punched path: {len(d)} chars")

        neg_svg = HERE / "negative-space-R.svg"
        neg_svg.write_text(svg_doc(f'<path d="{d}" fill="#1A1A1A"/>', 240, 240))
        plain_svg = HERE / "negative-space-R-plain.svg"
        plain_svg.write_text(svg_doc(f'<path d="{d_plain}" fill="#1A1A1A"/>', 240, 240))
        # side-by-side proof image for the eye-check
        (HERE / "negative-space-R-sidebyside.svg").write_text(svg_doc(
            f'<path d="{d}" fill="#1A1A1A"/>'
            f'<g transform="translate(140,0)"><path d="{d_plain}" fill="#1A1A1A"/></g>',
            420, 240))

        p_neg_chrome = HERE / "negative-space-R-chrome.png"
        p_plain_chrome = HERE / "negative-space-R-plain-chrome.png"
        render_chromium(neg_svg, p_neg_chrome, page)
        render_chromium(plain_svg, p_plain_chrome, page)
        render_chromium(HERE / "negative-space-R-sidebyside.svg",
                        HERE / "negative-space-R-sidebyside.png", page)
        p_neg_cairo = HERE / "negative-space-R-cairo.png"
        cairosvg.svg2png(url=str(neg_svg), write_to=str(p_neg_cairo),
                         output_width=SIZE * RENDER_SCALE, background_color="#ffffff")

        d_bite = structural_diff(ink_mask(p_plain_chrome), ink_mask(p_neg_chrome))
        d_xrend = structural_diff(ink_mask(p_neg_cairo), ink_mask(p_neg_chrome))
        g_bite = d_bite["max_blob"] >= 300       # the punch removed real ink
        g_xrend = d_xrend["max_blob"] <= MAX_BLOB  # result is renderer-independent
        print(f"  bite blob (plain vs punched) = {d_bite['max_blob']}px (need >= 300)"
              f" -> {'PASS' if g_bite else 'FAIL'}")
        print(f"  cross-renderer max-blob = {d_xrend['max_blob']}px (gate {MAX_BLOB})"
              f" -> {'PASS' if g_xrend else 'FAIL'}")
        if not (g_bite and g_xrend):
            failures.append(f"negative-space: bite {d_bite['max_blob']} / xrend {d_xrend['max_blob']}")

        browser.close()

    print("=" * 70)
    if failures:
        print("SPIKE FAILED:")
        for f in failures:
            print("  -", f)
        return 1
    print("SPIKES 2+3 PASSED — Latin outlining + pathops negative space viable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
