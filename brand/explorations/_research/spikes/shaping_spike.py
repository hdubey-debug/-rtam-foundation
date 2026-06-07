#!/usr/bin/env python3
"""SPIKE 1 (GATING): Devanagari shaping -> outlined SVG paths.

Proves the outlined-master strategy: uharfbuzz shapes real shipped brand
strings with the vendored Tiro Devanagari Sanskrit TTF, fontTools extracts
the positioned glyph outlines, and the resulting path-only SVG must:

  A. contain correctly formed conjuncts (म्भ, श्व, प्र, ष्ठ) — checked on the
     glyph sequence: no dotted-circle glyph, standalone-halant count matches
     the linguistically expected explicit-virāma count per string;
  B. render IDENTICALLY in cairosvg and Chromium — structural_diff max
     blob <= 150px at the 1024 grid (renderer independence: the whole
     point of outlining). The metric is calibrated by negative_control.py:
     identical renders <= 10px, the smallest injected defect 256px.

Also reported (informational, not gating): comparison against Chromium's
own rendering of the same LIVE TEXT with the same TTF (@font-face) —
shaping fidelity vs the browser's HarfBuzz. Glyph identity is already
gated exactly by A; the residual strip/drift numbers only quantify
rasterizer advance-rounding (diagnosed at <= 3px per 1024px line).

Latin (Cinzel) goes through the same pipeline as SPIKE 2.
Exit nonzero on any gate failure.
"""

import sys
from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = Path(__file__).resolve().parent
BRAND = HERE.parent.parent.parent          # brand/
TOOLS = BRAND / "tools"
sys.path.insert(0, str(TOOLS))
import numpy as np  # noqa: E402
from render_diff import ink_mask, structural_diff, MAX_BLOB, SIZE  # noqa: E402


def strip_fidelity(a, b, strips=8, search=6):
    """Per-strip best-shift IoU + drift. Returns (min_strip_iou, max_drift_px,
    line_len_px). Strips are bands of the joint ink x-range."""
    cols = np.where(a.any(axis=0) | b.any(axis=0))[0]
    x0, x1 = cols.min(), cols.max()
    edges = np.linspace(x0, x1 + 1, strips + 1).astype(int)
    min_iou, max_drift = 1.0, 0
    for i in range(strips):
        sa = a[:, edges[i]:edges[i + 1]]
        best = (-1.0, 0)
        for dx in range(-search, search + 1):
            for dy in range(-3, 4):
                sb = np.roll(np.roll(b, dx, axis=1), dy, axis=0)[:, edges[i]:edges[i + 1]]
                inter = (sa & sb).sum()
                union = (sa | sb).sum()
                s = inter / union if union else 1.0
                if s > best[0]:
                    best = (s, dx)
        min_iou = min(min_iou, best[0])
        max_drift = max(max_drift, abs(best[1]))
    return min_iou, max_drift, int(x1 - x0 + 1)

TIRO = BRAND / "fonts/tiro-devanagari-sanskrit/tiro-devanagari-sanskrit-400.ttf"

# (label, text, expected standalone-halant count)
# ऋतम्भरेश्वर मंदिर: म्भ and श्व must conjoin -> 0 visible halants
# ऋतम् प्रतिष्ठान: word-final म् keeps an explicit halant -> 1; प्र, ष्ठ conjoin
# ऋतम् फाउंडेशन: word-final म् -> 1
# ऋ alone -> 0
CASES = [
    ("temple", "ऋतम्भरेश्वर मंदिर", 0),
    ("pratishthan", "ऋतम् प्रतिष्ठान", 1),
    ("foundation-hi", "ऋतम् फाउंडेशन", 1),
    ("ri", "ऋ", 0),
]

FS = 110          # font-size in viewBox units
BASELINE = 170
MARGIN = 60
RENDER_SCALE = 2  # render at 2x, ink_mask downsamples to SIZE — averages out
                  # cross-rasterizer antialiasing fringe before binarization


def shape(ttf: Path, text: str):
    """HarfBuzz-shape text; return (glyph names, positions, hb font, upem)."""
    blob = hb.Blob.from_file_path(str(ttf))
    face = hb.Face(blob)
    font = hb.Font(face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf)
    return buf.glyph_infos, buf.glyph_positions, face.upem


def outline_svg(ttf: Path, text: str, fs: float, x: float, y: float,
                letter_spacing: float = 0.0):
    """Shape + outline. Returns (svg_path_elements, glyph_names, end_x).

    letter_spacing mirrors SVG/CSS semantics: added once per typographic
    cluster (HarfBuzz cluster id), after the cluster — including the last,
    exactly as browsers do for SVG <text>."""
    infos, positions, upem = shape(ttf, text)
    tt = TTFont(ttf)
    glyph_set = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    s = fs / upem
    cx = x
    names, ds = [], []
    for i, (info, pos) in enumerate(zip(infos, positions)):
        gname = order[info.codepoint]
        names.append(gname)
        spen = SVGPathPen(glyph_set)
        tpen = TransformPen(spen, (s, 0, 0, -s,
                                   cx + pos.x_offset * s,
                                   y - pos.y_offset * s))
        glyph_set[gname].draw(tpen)
        d = spen.getCommands()
        if d:
            ds.append(d)
        cx += pos.x_advance * s
        last_of_cluster = (i + 1 == len(infos)
                           or infos[i + 1].cluster != info.cluster)
        if letter_spacing and last_of_cluster:
            cx += letter_spacing
    return ds, names, cx


def svg_doc(body: str, w: float, h: float) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}">'
            f'<rect width="{w:g}" height="{h:g}" fill="#fff"/>{body}</svg>')


def render_chromium(svg_path: Path, png_path: Path, page):
    page.goto(svg_path.resolve().as_uri(), wait_until="networkidle")
    page.evaluate("() => document.fonts.ready")
    page.wait_for_timeout(300)
    page.screenshot(path=str(png_path))


def main() -> int:
    import cairosvg
    from playwright.sync_api import sync_playwright

    tt = TTFont(TIRO)
    cmap = tt.getBestCmap()
    order = tt.getGlyphOrder()
    halant_gname = order[0]  # placeholder; resolve via cmap below
    halant_gname = cmap.get(0x094D)
    dotted_circle = cmap.get(0x25CC)
    print(f"halant glyph = {halant_gname!r}, dotted-circle glyph = {dotted_circle!r}\n")

    failures = []
    results = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": SIZE, "height": SIZE},
                                  device_scale_factor=RENDER_SCALE)
        page = ctx.new_page()

        for label, text, expect_halants in CASES:
            ds, names, end_x = outline_svg(TIRO, text, FS, MARGIN, BASELINE)
            w = end_x + MARGIN
            h = BASELINE + 90

            # --- Gate A: glyph-sequence sanity ---
            n_halant = sum(1 for n in names if n == halant_gname)
            n_dotted = sum(1 for n in names if dotted_circle and n == dotted_circle)
            conjoined = len(names) < len(text.replace(" ", "")) + text.count(" ")
            ga = (n_dotted == 0) and (n_halant == expect_halants)
            print(f"[{label}] '{text}'")
            print(f"  codepoints={len(text)} -> glyphs={len(names)}")
            print(f"  glyph names: {' '.join(names)}")
            print(f"  halants={n_halant} (expected {expect_halants}), dotted-circles={n_dotted}"
                  f" -> Gate A {'PASS' if ga else 'FAIL'}")
            if not ga:
                failures.append(f"{label}: gate A (halants {n_halant}!={expect_halants} or dotted circle)")

            # --- outlined SVG ---
            body = "".join(f'<path d="{d}" fill="#1A1A1A"/>' for d in ds)
            out_svg = HERE / f"shaping-{label}-outlined.svg"
            out_svg.write_text(svg_doc(body, w, h))

            # --- live-text reference with the SAME local TTF ---
            ref_svg = HERE / f"shaping-{label}-livetext.svg"
            ref_svg.write_text(svg_doc(
                f"<defs><style>@font-face{{font-family:'TiroLocal';"
                f"src:url('{TIRO.resolve().as_uri()}');}}</style></defs>"
                f'<text x="{MARGIN}" y="{BASELINE}" font-family="TiroLocal" '
                f'font-size="{FS}" fill="#1A1A1A">{text}</text>', w, h))

            # --- renders ---
            png_outline_chrome = HERE / f"shaping-{label}-outlined-chrome.png"
            png_ref_chrome = HERE / f"shaping-{label}-livetext-chrome.png"
            render_chromium(out_svg, png_outline_chrome, page)
            render_chromium(ref_svg, png_ref_chrome, page)
            png_outline_cairo = HERE / f"shaping-{label}-outlined-cairo.png"
            cairosvg.svg2png(url=str(out_svg), write_to=str(png_outline_cairo),
                             output_width=SIZE * RENDER_SCALE,
                             background_color="#ffffff")

            # --- Gate B: renderer independence of the outlined SVG ---
            db = structural_diff(ink_mask(png_outline_cairo), ink_mask(png_outline_chrome))
            gb = db["max_blob"] <= MAX_BLOB
            # --- informational: shaping fidelity vs browser HarfBuzz ---
            ma, mb = ink_mask(png_outline_chrome), ink_mask(png_ref_chrome)
            c1, drift, line = strip_fidelity(ma, mb)
            drift_pct = 100.0 * drift / line
            print(f"  Gate B max-blob(cairo,chrome) = {db['max_blob']}px (gate {MAX_BLOB}), "
                  f"diff={db['diff_px']}px, iou={db['iou']:.4f} -> {'PASS' if gb else 'FAIL'}")
            print(f"  info: vs livetext min strip IoU = {c1:.4f}, "
                  f"drift = {drift}px/{line}px ({drift_pct:.2f}%)\n")
            if not gb:
                failures.append(f"{label}: gate B max-blob {db['max_blob']} > {MAX_BLOB}")
            results.append((label, text, len(names), n_halant, db["max_blob"], c1, drift_pct))

        browser.close()

    print("=" * 70)
    for label, text, ng, nh, mblob, c1, dp in results:
        print(f"  {label:14s} glyphs={ng:2d} halants={nh}  B-blob={mblob:4d}px  "
              f"strip={c1:.4f}  drift={dp:.2f}%")
    if failures:
        print("\nSPIKE FAILED:")
        for f in failures:
            print("  -", f)
        return 1
    print("\nSPIKE PASSED — outlined-master strategy is viable for Devanagari.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
