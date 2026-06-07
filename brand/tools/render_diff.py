#!/usr/bin/env python3
"""Render-fidelity gate between two renders of the same SVG.

Used to prove an outlined SVG reproduces identically in a font-less renderer
(cairosvg) and a faithful one (Chromium). Both images are binarized to
ink/no-ink masks on a common grid; the BINDING metric is the largest
connected blob of the registered, antialiasing-tolerant symmetric
difference (structural_diff): AA fringe is diffuse, real defects are
concentrated. Registered IoU is reported as an informational secondary.

Gate: max blob <= 150 px (calibrated with injected-defect negative
controls — see brand/explorations/_research/spikes/negative_control.py).

Usage:
  render_diff.py a.png b.png [--max-blob 150]
  render_diff.py --svg path.svg [--max-blob 150]   # renders both ways itself
"""

import argparse
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

SIZE = 1024  # common comparison grid


def ink_mask(png: Path) -> np.ndarray:
    """Binarize: ink = pixels that differ meaningfully from the dominant
    (background) color. Works for dark-on-light and light-on-dark.

    The image is padded to a centered square with its own background value
    BEFORE resizing, so a tight render (cairosvg) and a letterboxed
    square-viewport render (Chromium screenshot) land on the same geometry."""
    img = Image.open(png).convert("L")
    a = np.asarray(img, dtype=np.int16)
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bg = int(np.bincount(border.clip(0, 255).astype(np.uint8)).argmax())
    side = max(img.size)
    sq = Image.new("L", (side, side), bg)
    sq.paste(img, ((side - img.size[0]) // 2, (side - img.size[1]) // 2))
    a = np.asarray(sq.resize((SIZE, SIZE), Image.LANCZOS), dtype=np.int16)
    return np.abs(a - bg) > 48


def dilate(m: np.ndarray, px: int = 1) -> np.ndarray:
    """Binary dilation by `px` pixels (square structuring element)."""
    out = m.copy()
    for _ in range(px):
        n = out.copy()
        n[1:, :] |= out[:-1, :]
        n[:-1, :] |= out[1:, :]
        n[:, 1:] |= out[:, :-1]
        n[:, :-1] |= out[:, 1:]
        out = n
    return out


def iou(a: np.ndarray, b: np.ndarray, tolerance_px: int = 1) -> float:
    """IoU with a small symmetric dilation tolerance: sub-pixel antialiasing
    and rasterizer rounding (±1px on stroke edges) are not portability
    failures, but missing glyphs, fallback fonts, or shifted advances still
    crater the score because every downstream glyph misaligns."""
    if tolerance_px:
        a, b = dilate(a, tolerance_px), dilate(b, tolerance_px)
    inter = np.logical_and(a, b).sum()
    union = np.logical_or(a, b).sum()
    return float(inter) / float(union) if union else 1.0


def best_shift(a: np.ndarray, b: np.ndarray, search_px: int = 4,
               tolerance_px: int = 1):
    """Best global translation of b (within ±search_px) by IoU.
    Returns (dx, dy, iou_at_best). Removes letterbox-centering arithmetic
    differences between renderers."""
    best = (0, 0, 0.0)
    for dx in range(-search_px, search_px + 1):
        for dy in range(-search_px, search_px + 1):
            s = iou(a, np.roll(np.roll(b, dx, axis=1), dy, axis=0), tolerance_px)
            if s > best[2]:
                best = (dx, dy, s)
    return best


def registered_iou(a: np.ndarray, b: np.ndarray, search_px: int = 4,
                   tolerance_px: int = 1) -> float:
    """IoU after global translation registration (informational metric —
    NOTE: scales with ink density, so it conflates composition sparseness
    with infidelity; the binding gate is structural_diff's max blob)."""
    return best_shift(a, b, search_px, tolerance_px)[2]


def largest_blob(mask: np.ndarray) -> int:
    """Area of the largest 8-connected component (sparse union-find)."""
    ys, xs = np.nonzero(mask)
    n = len(ys)
    if n == 0:
        return 0
    idx = {(int(y), int(x)): k for k, (y, x) in enumerate(zip(ys, xs))}
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for k, (y, x) in enumerate(zip(ys, xs)):
        for dy, dx in ((0, 1), (1, -1), (1, 0), (1, 1)):
            j = idx.get((int(y) + dy, int(x) + dx))
            if j is not None:
                ri, rj = find(k), find(j)
                if ri != rj:
                    parent[ri] = rj
    from collections import Counter
    return max(Counter(find(i) for i in range(n)).values())


def structural_diff(a: np.ndarray, b: np.ndarray, search_px: int = 4,
                    tolerance_px: int = 1) -> dict:
    """The binding fidelity metric: register b to a, dilate both by
    tolerance_px, take the symmetric difference, and measure its largest
    connected blob. Antialiasing fringe is DIFFUSE (many tiny fragments);
    any structural defect — wrong/missing glyph, shifted mark, filled
    counter — is CONCENTRATED into one blob. Scale-invariant: does not
    depend on how much ink the composition happens to have.

    Calibrated against injected defects (see spikes/negative_control.py):
    identical renders max-blob ~tens of px; a dropped anusvara-sized dot,
    a 5-unit mark shift, or a swapped glyph all exceed 200px at the 1024
    grid. Gate threshold: 150."""
    dx, dy, score = best_shift(a, b, search_px, tolerance_px)
    bb = np.roll(np.roll(b, dx, axis=1), dy, axis=0)
    da, db = dilate(a, tolerance_px), dilate(bb, tolerance_px)
    sym = (da & ~db) | (db & ~da)
    return {"max_blob": largest_blob(sym), "diff_px": int(sym.sum()),
            "iou": score, "shift": (dx, dy)}


MAX_BLOB = 150  # gate threshold at the 1024 comparison grid


def render_both(svg: Path, tmp: Path) -> tuple[Path, Path]:
    import cairosvg
    from playwright.sync_api import sync_playwright

    cairo_png = tmp / "cairo.png"
    cairosvg.svg2png(url=str(svg), write_to=str(cairo_png),
                     output_width=SIZE, background_color="#ffffff")

    chrome_png = tmp / "chrome.png"
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        ctx = b.new_context(viewport={"width": SIZE, "height": SIZE},
                            device_scale_factor=1)
        page = ctx.new_page()
        page.goto(svg.resolve().as_uri(), wait_until="networkidle")
        page.evaluate("() => document.fonts.ready")
        page.wait_for_timeout(300)
        page.screenshot(path=str(chrome_png))
        b.close()
    return cairo_png, chrome_png


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="*", help="two PNGs to compare")
    ap.add_argument("--svg", help="render this SVG via cairosvg AND Chromium, then compare")
    ap.add_argument("--max-blob", type=int, default=MAX_BLOB)
    args = ap.parse_args()

    if args.svg:
        with tempfile.TemporaryDirectory() as td:
            a, b = render_both(Path(args.svg), Path(td))
            d = structural_diff(ink_mask(a), ink_mask(b))
            label = args.svg
    elif len(args.images) == 2:
        d = structural_diff(ink_mask(Path(args.images[0])), ink_mask(Path(args.images[1])))
        label = f"{args.images[0]} vs {args.images[1]}"
    else:
        ap.error("give two PNGs or --svg")

    ok = d["max_blob"] <= args.max_blob
    print(f"max blob = {d['max_blob']}px (gate {args.max_blob})  "
          f"diff = {d['diff_px']}px  IoU = {d['iou']:.4f}  "
          f"{'PASS' if ok else 'FAIL'}  {label}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
