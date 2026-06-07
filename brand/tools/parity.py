#!/usr/bin/env python3
"""US-13 gate: prove generator + outliner reproduce the design. THREE checks per
(asset,output) — each isolating a different failure mode, so a pass means the
shipped + outlined files are both correct:

  1. COORD-PARITY    livetext-gen  vs  livetext-committed   blob <= 30px
     Emitter fidelity: attributes/coords/rounding. Skipped (informational, *)
     for assets flagged `changed` (geometry intentionally updated, e.g. F6).
  2. RENDERER-INDEP  outline cairosvg vs outline chromium   blob <= 150px
     The Phase-0-calibrated distribution gate (negative-controlled in
     spikes/negative_control.py): the outlined master renders identically in a
     font-less renderer (print/Office/cairo) and a faithful one.
  3. POSITION        outline chromium vs livetext-gen chromium   offset <= 4px
     Catches the text-anchor/letter-spacing resolution bug (outline shifted off
     the live text): ink-bbox-center offset. Robust for sparse single-glyph marks
     (per-strip drift locks onto noise in their near-empty edge strips) and
     ignores Chromium's hint-the-<text>-not-the-<path> sub-pixel fringe.

Bare @import is banned in proofs; live text renders via file:// @font-face.
Run before generate.py --write. Exit nonzero on any gate failure.
"""
import argparse
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import cairosvg
sys.path.insert(0, str(Path(__file__).resolve().parent))
import brandlib as bl  # noqa: E402
from render_diff import ink_mask, structural_diff, SIZE, MAX_BLOB  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

F = bl.FONTS
PARITY_MAX = 30
DRIFT_MAX = 4

FACE = f"""
@font-face {{ font-family:'Cinzel'; font-weight:400; src:url('file://{F}/cinzel/cinzel-400.ttf'); }}
@font-face {{ font-family:'Cinzel'; font-weight:500; src:url('file://{F}/cinzel/cinzel-500.ttf'); }}
@font-face {{ font-family:'Cinzel'; font-weight:600; src:url('file://{F}/cinzel/cinzel-600.ttf'); }}
@font-face {{ font-family:'Cinzel'; font-weight:700; src:url('file://{F}/cinzel/cinzel-700.ttf'); }}
@font-face {{ font-family:'Tiro Devanagari Sanskrit'; src:url('file://{F}/tiro-devanagari-sanskrit/tiro-devanagari-sanskrit-400.ttf'); }}
@font-face {{ font-family:'Inter'; font-weight:300; src:url('file://{F}/inter/inter-400.ttf'); }}
@font-face {{ font-family:'Inter'; font-weight:400; src:url('file://{F}/inter/inter-400.ttf'); }}
@font-face {{ font-family:'Inter'; font-weight:500; src:url('file://{F}/inter/inter-500.ttf'); }}
@font-face {{ font-family:'Inter'; font-weight:600; src:url('file://{F}/inter/inter-600.ttf'); }}
"""


def faithful(svg: str) -> str:
    if "<style" in svg:
        return re.sub(r"<style[^>]*>.*?</style>", f"<style>{FACE}</style>", svg, flags=re.S)
    return svg


def inject_bg(svg: str, hexcol: str) -> str:
    """Insert a full-bleed background rect (render-only) so ink_mask can see the
    glyph — light-on-transparent overlay variants are invisible on the default
    white canvas. All three renders of a variant get the same injected ground."""
    i = svg.index(">", svg.index("<svg")) + 1
    m = re.search(r'viewBox="0 0 (\S+) (\S+)"', svg)
    w, h = m.group(1), m.group(2)
    return f'{svg[:i]}<rect width="{w}" height="{h}" fill="{hexcol}"/>{svg[i:]}'


def render_bg(brand: dict, output: dict) -> str:
    """Dark ground for light (ivory) overlay variants; light ground otherwise."""
    vals = set(output.get("colors", {}).values())
    return "#1A1A1A" if "ivory" in vals else "#FFFFFF"


def normalize_geometry(svg: str) -> str:
    """For the renderer-independence check: strip any full-bleed ground rect and
    force every fill/stroke to black-on-white, so the comparison tests the
    OUTLINE GEOMETRY's portability (cairo vs chrome) independent of colour — dark
    grounds otherwise invert ink_mask's background detection."""
    svg = re.sub(r'\s*<rect x="0" y="0"[^>]*/>\s*', "\n", svg)
    svg = re.sub(r'fill="#[0-9A-Fa-f]{6}"', 'fill="#000000"', svg)
    svg = re.sub(r'stroke="#[0-9A-Fa-f]{6}"', 'stroke="#000000"', svg)
    return svg


def bbox_center_offset(a, b):
    """Max axis ink-bbox-center offset (px) between two masks. Robust for sparse
    AND dense compositions (unlike per-strip drift, which locks onto noise in
    near-empty edge strips of single-glyph marks). A uniform anchor-resolution
    error shifts every centred run the same way -> the whole bbox moves -> caught;
    Chromium's hint-the-<text>-not-the-<path> fringe moves the center sub-pixel."""
    def center(m):
        ys, xs = np.nonzero(m)
        return (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    ax, ay = center(a); bx, by = center(b)
    return max(abs(ax - bx), abs(ay - by))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    args = ap.parse_args()
    brand = bl.load_brand()
    rows, fails = [], []
    SS = 2  # supersample: render at 2x then ink_mask averages AA -> matches the
            # Phase-0 calibration (spikes render device_scale_factor=2 before the gate)
    with sync_playwright() as pw, tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        br = pw.chromium.launch()
        ctx = br.new_context(device_scale_factor=SS)
        page = ctx.new_page()

        def chrome(svg, tag, vb):
            # viewport matches the SVG aspect -> no letterbox border (which would
            # invert ink_mask's background detection on dark-ground variants)
            w, h = vb
            page.set_viewport_size({"width": SIZE, "height": max(1, round(SIZE * h / w))})
            p = tmp / f"{tag}.svg"; p.write_text(svg)
            png = tmp / f"{tag}.png"
            page.goto(p.resolve().as_uri(), wait_until="networkidle")
            page.evaluate("() => document.fonts.ready"); page.wait_for_timeout(250)
            page.screenshot(path=str(png))
            return ink_mask(png)

        for asset, output in bl.all_outputs(brand):
            if args.only and asset["id"] != args.only:
                continue
            rel = output["path"]
            vb = asset["viewBox"]
            committed = bl.BRAND / rel
            gen_live = bl.emit_livetext(brand, asset, output)
            gen_outl = bl.emit_outlined(brand, asset, output)
            bg = render_bg(brand, output)
            m_gen = chrome(inject_bg(faithful(gen_live), bg), "gen", vb)
            norm = normalize_geometry(gen_outl)
            m_outl_c = chrome(norm, "outlc", vb)        # for r-indep (black-on-white)
            m_outl_pos = chrome(inject_bg(gen_outl, bg), "outlp", vb)  # for drift
            op = tmp / "outl_cairo.png"
            # match chrome's exact pixel dims (it rounds the CSS viewport then x SS);
            # a 1px height mismatch causes sub-pixel global misregistration -> fringe
            ch_h = max(1, round(SIZE * vb[1] / vb[0]))
            cairosvg.svg2png(bytestring=norm.encode(), write_to=str(op),
                             output_width=SIZE * SS, output_height=ch_h * SS,
                             background_color="#ffffff")
            m_outl_cairo = ink_mask(op)

            changed = bool(output.get("changed") or asset.get("changed"))
            # 1 coord-parity
            if committed.exists():
                m_comm = chrome(inject_bg(faithful(committed.read_text()), bg), "comm", vb)
                parity = structural_diff(m_comm, m_gen)["max_blob"]
            else:
                parity = None
            # 2 renderer-independence (distribution gate)
            rind = structural_diff(m_outl_cairo, m_outl_c)["max_blob"]
            # 3 position fidelity (actual-colour outline vs live text)
            drift = round(bbox_center_offset(m_outl_pos, m_gen), 1)

            ok_p = parity is None or changed or parity <= PARITY_MAX
            ok_r = rind <= MAX_BLOB
            ok_d = drift <= DRIFT_MAX
            if not ok_p:
                fails.append(f"{rel}: coord-parity blob {parity} > {PARITY_MAX}")
            if not ok_r:
                fails.append(f"{rel}: renderer-indep blob {rind} > {MAX_BLOB}")
            if not ok_d:
                fails.append(f"{rel}: outline position drift {drift} > {DRIFT_MAX}px")
            pstr = ("—" if parity is None else (f"{parity}*" if changed else str(parity)))
            rows.append((rel, pstr, str(rind), f"{drift}", "PASS" if (ok_p and ok_r and ok_d) else "FAIL"))
        br.close()

    print(f"{'asset':50s} {'parity':>7s} {'r-indep':>8s} {'drift':>6s}  status")
    print("-" * 88)
    for rel, p, r, d, s in rows:
        print(f"{rel:50s} {p:>7s} {r:>8s} {d:>6s}  {s}")
    if fails:
        print("\nGATE FAILED:")
        for f in fails:
            print("  -", f)
        return 1
    print(f"\nALL PASS  (parity<={PARITY_MAX}px blob · r-indep<={MAX_BLOB}px blob · drift<={DRIFT_MAX}px)")
    print("* = changed asset (geometry intentionally updated; coord-parity informational, eye-check)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
