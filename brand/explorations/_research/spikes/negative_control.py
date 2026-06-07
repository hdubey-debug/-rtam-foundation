#!/usr/bin/env python3
"""Negative control for the render-fidelity gate (structural_diff max-blob).

A gate that only ever saw passing pairs proves nothing. This script renders
the temple string outlined, then injects three real defects:

  D1. drop the anusvara (the smallest plausibly-droppable element);
  D2. shift the i-matra (dSignI) by 5 viewBox units;
  D3. swap a glyph (second dRa -> dTa).

and the wordmark with:

  D4. drop the gold bindu circle.

PASS criteria for the *metric*: every identical pair scores max-blob well
BELOW the gate (150), every defect pair well ABOVE it.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRAND = HERE.parent.parent.parent
sys.path.insert(0, str(BRAND / "tools"))
sys.path.insert(0, str(HERE))

from render_diff import ink_mask, structural_diff, SIZE, MAX_BLOB  # noqa: E402
from shaping_spike import outline_svg, svg_doc, render_chromium, RENDER_SCALE, TIRO, FS, BASELINE, MARGIN  # noqa: E402


def render(page, svg_path, png_path):
    render_chromium(svg_path, png_path, page)


def paths_for(text, mutate=None):
    """Outline text; mutate(names, ds_by_glyph) may edit the per-glyph list."""
    import uharfbuzz  # noqa: F401  (ensures import error surfaces here)
    ds, names, end_x = outline_svg(TIRO, text, FS, MARGIN, BASELINE)
    # ds skips empty glyphs (space); rebuild aligned list
    return ds, names, end_x


def main() -> int:
    from playwright.sync_api import sync_playwright
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    import uharfbuzz as hb

    text = "ऋतम्भरेश्वर मंदिर"

    # Re-shape manually so each glyph keeps its own path + transform.
    blob = hb.Blob.from_file_path(str(TIRO))
    face = hb.Face(blob)
    font = hb.Font(face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf)
    tt = TTFont(TIRO)
    glyph_set = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    s = FS / face.upem

    def glyph_paths(drop=None, shift=None, swap=None):
        """Per-glyph outlined paths with optional defect injection.
        drop: glyph name to omit; shift: (glyph name, dx_units);
        swap: (glyph name, replacement name) — first occurrence each."""
        cx = MARGIN
        ds = []
        dropped = shifted = swapped = False
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            gname = order[info.codepoint]
            draw_name, extra_dx = gname, 0.0
            if drop and gname == drop and not dropped:
                dropped = True
                cx += pos.x_advance * s
                continue
            if shift and gname == shift[0] and not shifted:
                shifted = True
                extra_dx = shift[1]
            if swap and gname == swap[0] and not swapped:
                swapped = True
                draw_name = swap[1]
            spen = SVGPathPen(glyph_set)
            tpen = TransformPen(spen, (s, 0, 0, -s,
                                       cx + pos.x_offset * s + extra_dx,
                                       BASELINE - pos.y_offset * s))
            glyph_set[draw_name].draw(tpen)
            d = spen.getCommands()
            if d:
                ds.append(d)
            cx += pos.x_advance * s
        return ds, cx

    base_ds, end_x = glyph_paths()
    w, h = end_x + MARGIN, BASELINE + 90
    variants = {
        "control": base_ds,
        "D1-drop-anusvara": glyph_paths(drop="dAnusvara")[0],
        "D2-shift-imatra": glyph_paths(shift=("dSignI", 5.0))[0],
        "D3-swap-ra-ta": glyph_paths(swap=("dRa", "dTa"))[0],
    }

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": SIZE, "height": SIZE},
                                  device_scale_factor=RENDER_SCALE)
        page = ctx.new_page()

        pngs = {}
        for name, ds in variants.items():
            body = "".join(f'<path d="{d}" fill="#1A1A1A"/>' for d in ds)
            svg = HERE / f"negctl-{name}.svg"
            svg.write_text(svg_doc(body, w, h))
            png = HERE / f"negctl-{name}.png"
            render(page, svg, png)
            pngs[name] = png

        # identical pair (re-render the control a second time = fresh raster)
        png_again = HERE / "negctl-control-again.png"
        render(page, pngs.__getitem__("control").with_suffix(".svg"), png_again)

        # wordmark bindu-drop pair (uses spike-2 outputs)
        wm = HERE / "latin-wordmark-outlined.svg"
        wm_src = wm.read_text()
        wm_nodot = HERE / "negctl-D4-drop-bindu.svg"
        wm_nodot.write_text(wm_src.replace(
            '<circle cx="118" cy="188" r="10" fill="#C8A15A"/>', ""))
        png_wm = HERE / "negctl-wordmark.png"
        png_wm_nodot = HERE / "negctl-D4-drop-bindu.png"
        render(page, wm, png_wm)
        render(page, wm_nodot, png_wm_nodot)

        browser.close()

    # also bring in the cross-renderer pairs from the spikes as identical pairs
    import cairosvg
    cairo_ctl = HERE / "negctl-control-cairo.png"
    cairosvg.svg2png(url=str(HERE / "negctl-control.svg"), write_to=str(cairo_ctl),
                     output_width=SIZE * RENDER_SCALE, background_color="#ffffff")

    base = ink_mask(pngs["control"])
    cases = [
        ("IDENTICAL re-raster (chrome,chrome)", ink_mask(png_again), True),
        ("IDENTICAL cross-renderer (cairo,chrome)", ink_mask(cairo_ctl), True),
        ("D1 drop anusvara", ink_mask(pngs["D1-drop-anusvara"]), False),
        ("D2 shift i-matra 5u", ink_mask(pngs["D2-shift-imatra"]), False),
        ("D3 swap ra->ta", ink_mask(pngs["D3-swap-ra-ta"]), False),
    ]
    print(f"gate: max blob <= {MAX_BLOB}px\n")
    bad = []
    for name, m, should_pass in cases:
        d = structural_diff(base, m)
        verdict = d["max_blob"] <= MAX_BLOB
        ok = verdict == should_pass
        print(f"  {name:42s} max-blob={d['max_blob']:5d}  diff={d['diff_px']:5d}  "
              f"iou={d['iou']:.4f}  -> {'pass' if verdict else 'FAIL-gate'}  "
              f"[{'METRIC OK' if ok else 'METRIC BROKEN'}]")
        if not ok:
            bad.append(name)

    d = structural_diff(ink_mask(png_wm), ink_mask(png_wm_nodot))
    verdict = d["max_blob"] <= MAX_BLOB
    ok = not verdict
    print(f"  {'D4 drop bindu (wordmark)':42s} max-blob={d['max_blob']:5d}  diff={d['diff_px']:5d}  "
          f"iou={d['iou']:.4f}  -> {'pass' if verdict else 'FAIL-gate'}  "
          f"[{'METRIC OK' if ok else 'METRIC BROKEN'}]")
    if not ok:
        bad.append("D4")

    print()
    if bad:
        print("NEGATIVE CONTROL FAILED — metric cannot separate:", bad)
        return 1
    print("NEGATIVE CONTROL PASSED — gate separates identical from defective.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
