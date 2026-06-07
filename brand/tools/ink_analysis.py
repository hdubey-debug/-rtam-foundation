#!/usr/bin/env python3
"""Pixel-level ink analysis of the Cinzel R + bindu, and WCAG contrast math.

Renders an isolated Cinzel 'R' (fs=120) and Tiro 'ऋ' (fs=210) at exact viewBox
coords in Chromium, then computes ink bbox + ink centroid in viewBox units.
Compares against the shipped bindu cx=118 (wordmark) / 128 (icons).
"""

from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent / "_scratch"
SCALE = 4  # px per viewBox unit


def render_svg(markup: str, name: str, w: int, h: int) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"{name}.svg"
    p.write_text(markup)
    png = OUT / f"{name}.png"
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        ctx = b.new_context(viewport={"width": w * SCALE, "height": h * SCALE},
                            device_scale_factor=1)
        page = ctx.new_page()
        page.goto(p.resolve().as_uri(), wait_until="networkidle")
        page.evaluate("() => document.fonts.ready")
        page.wait_for_timeout(400)
        page.screenshot(path=str(png))
        b.close()
    return png


def ink_stats(png: Path, thresh=128):
    img = Image.open(png).convert("L")
    px = img.load()
    W, H = img.size
    xs_min, xs_max, ys_min, ys_max = W, -1, H, -1
    sx = n = 0
    for y in range(H):
        for x in range(W):
            if px[x, y] < thresh:  # dark ink on white
                if x < xs_min: xs_min = x
                if x > xs_max: xs_max = x
                if y < ys_min: ys_min = y
                if y > ys_max: ys_max = y
                sx += x
                n += 1
    if n == 0:
        return None
    return {
        "bbox_units": (xs_min / SCALE, xs_max / SCALE, ys_min / SCALE, ys_max / SCALE),
        "bbox_center_x": (xs_min + xs_max) / 2 / SCALE,
        "centroid_x": sx / n / SCALE,
        "ink_px": n,
    }


# --- isolated Cinzel R at wordmark metrics: x=80, y=160 baseline, fs=120 ---
R_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240">
<defs><style>@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500&amp;display=swap');</style></defs>
<rect width="240" height="240" fill="#fff"/>
<text x="80" y="160" font-family="Cinzel" font-size="120" font-weight="500" fill="#000">R</text>
</svg>"""

# --- isolated Tiro ऋ at icon metrics: anchor middle x=128, fs=210, y=200 (from icon svg) ---
RI_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 300">
<defs><style>@import url('https://fonts.googleapis.com/css2?family=Tiro+Devanagari+Sanskrit&amp;display=swap');</style></defs>
<rect width="256" height="300" fill="#fff"/>
<text x="128" y="200" font-family="'Tiro Devanagari Sanskrit'" font-size="210" text-anchor="middle" fill="#000">ऋ</text>
</svg>"""


def main():
    print("=== Cinzel R, wordmark metrics (x=80, fs=120, advance-center=119, bindu cx=118) ===")
    s = ink_stats(render_svg(R_SVG, "isolated-R", 240, 240))
    x0, x1, y0, y1 = s["bbox_units"]
    print(f"  ink bbox x: {x0:.1f}..{x1:.1f} (w {x1-x0:.1f}), y: {y0:.1f}..{y1:.1f}")
    print(f"  ink bbox CENTER x = {s['bbox_center_x']:.1f}")
    print(f"  ink mass CENTROID x = {s['centroid_x']:.1f}")
    print(f"  shipped bindu cx=118 -> off bbox-center {118 - s['bbox_center_x']:+.1f}, off centroid {118 - s['centroid_x']:+.1f}")

    print("\n=== Tiro ऋ, icon metrics (fs=210, viewBox extended to 300 to see full ink) ===")
    s2 = ink_stats(render_svg(RI_SVG, "isolated-RI", 256, 300))
    x0, x1, y0, y1 = s2["bbox_units"]
    print(f"  ink bbox x: {x0:.1f}..{x1:.1f}, y: {y0:.1f}..{y1:.1f}")
    print(f"  icon viewBox bottom = 256; ink bottom = {y1:.1f} -> {'CLIPPED by ' + format(y1-256, '.1f') + ' units' if y1 > 256 else 'fits'}")
    print(f"  (icon places baseline at y=200; this render used same)")


if __name__ == "__main__":
    main()
