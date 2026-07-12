#!/usr/bin/env python3
"""Composite ink-bbox centering audit (the 2026-07 audit method, made repeatable).

For every asset in brand.json: emit the livetext SVG for its first output,
swap the @import for file:// @font-face (parity.faithful — bare @import is
banned in proofs), inject the parity render ground, render in Chromium at
device_scale_factor=2, and measure the FULL COMPOSITE ink bbox (letters +
bindu + rules) in viewBox units. Reports the bbox-center offset from the
viewBox center and the four margins. Positive dy = ink sits LOW (shift the
content up by dy to center); positive dx = ink sits RIGHT.

Run before and after a recentering spec edit; the after-run is the proof.
    python3 center_audit.py
"""
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

TOOLS = Path(__file__).resolve().parents[3] / "tools"
sys.path.insert(0, str(TOOLS))
import brandlib as bl  # noqa: E402
from parity import faithful, inject_bg, render_bg  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

SS = 2  # device pixels per viewBox unit


def bg_lum(hexcol: str) -> float:
    h = hexcol.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return 0.299 * r + 0.587 * g + 0.114 * b


def main() -> int:
    brand = bl.load_brand()
    print(f"{'asset':34s} {'viewBox':>9s} {'dx':>6s} {'dy':>6s}   margins L/R/T/B (units)")
    print("-" * 92)
    with sync_playwright() as pw, tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        br = pw.chromium.launch()
        ctx = br.new_context(device_scale_factor=SS)
        page = ctx.new_page()
        for asset in brand["assets"]:
            output = asset["outputs"][0]
            w, h = asset["viewBox"]
            bg = render_bg(brand, output)
            svg = inject_bg(faithful(bl.emit_livetext(brand, asset, output)), bg)
            p = tmp / "a.svg"
            p.write_text(svg)
            page.set_viewport_size({"width": w, "height": h})
            page.goto(p.resolve().as_uri(), wait_until="networkidle")
            page.evaluate("() => document.fonts.ready")
            page.wait_for_timeout(250)
            png = tmp / "a.png"
            page.screenshot(path=str(png))
            a = np.asarray(Image.open(png).convert("L"), dtype=np.int16)
            mask = np.abs(a - bg_lum(bg)) > 48
            ys, xs = np.nonzero(mask)
            if len(ys) == 0:
                print(f"{asset['id']:34s} NO INK")
                continue
            x0, x1 = xs.min() / SS, xs.max() / SS
            y0, y1 = ys.min() / SS, ys.max() / SS
            dx = (x0 + x1) / 2 - w / 2
            dy = (y0 + y1) / 2 - h / 2
            print(f"{asset['id']:34s} {w:>4d}x{h:<4d} {dx:>+6.1f} {dy:>+6.1f}   "
                  f"{x0:.1f}/{w - x1:.1f}/{y0:.1f}/{h - y1:.1f}")
        br.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
