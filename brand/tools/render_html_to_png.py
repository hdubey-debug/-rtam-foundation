#!/usr/bin/env python3
"""Render an HTML file to PNG (full page) or PDF using Playwright Chromium.

Usage:
    python3 render_html_to_png.py <input.html> <output.png|pdf> [viewport_width] [scale] [css]

Output type is inferred from the extension (.png or .pdf).
viewport_width defaults to 1280 px (logical CSS pixels).
scale defaults to 2 — device_scale_factor for PNG (2 = retina, sharper on zoom).
PDF output ignores scale. A literal 5th arg `css` (page="css" in the API) makes
the document's own `@page { size: ... }` rule control the PDF sheet
(prefer_css_page_size) — for A5/true-size stationery masters; without it the
sheet stays the A4 default.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


def render(html_path: Path, out_path: Path, width: int, scale: float,
           page: str | None = None) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    url = html_path.resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": width, "height": 800},
            device_scale_factor=scale,
        )
        pg = ctx.new_page()
        pg.goto(url, wait_until="networkidle")
        # Give web fonts a final moment to settle after networkidle.
        pg.wait_for_timeout(500)
        if out_path.suffix.lower() == ".pdf":
            if page == "css":
                # Stationery masters: the document's @page { size } rule is the
                # sheet (A5 receipt, true-size stamp artwork, label sheets).
                pg.pdf(path=str(out_path), prefer_css_page_size=True,
                       print_background=True)
            else:
                # A4 is the foundation's document standard (Indian/international
                # trust correspondence); letterhead + receipt mockups are sized
                # to A4 794x1123 @96dpi.
                pg.pdf(path=str(out_path), format="A4", print_background=True)
        else:
            pg.screenshot(path=str(out_path), full_page=True)
        browser.close()


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    html_path = Path(argv[1])
    out_path = Path(argv[2])
    width = int(argv[3]) if len(argv) > 3 else 1280
    scale = float(argv[4]) if len(argv) > 4 else 2.0
    page = argv[5] if len(argv) > 5 else None
    if not html_path.exists():
        print(f"error: input not found: {html_path}", file=sys.stderr)
        return 1
    render(html_path, out_path, width, scale, page)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
