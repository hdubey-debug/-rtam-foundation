#!/usr/bin/env python3
"""Render an HTML file to PNG (full page) or PDF using Playwright Chromium.

Usage:
    python3 render_html_to_png.py <input.html> <output.png|pdf> [viewport_width]

Output type is inferred from the extension (.png or .pdf).
Viewport width defaults to 1280px.
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


def render(html_path: Path, out_path: Path, width: int) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    url = html_path.resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": width, "height": 800})
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle")
        # Give web fonts a final moment to settle after networkidle.
        page.wait_for_timeout(500)
        if out_path.suffix.lower() == ".pdf":
            page.pdf(path=str(out_path), format="Letter", print_background=True)
        else:
            page.screenshot(path=str(out_path), full_page=True)
        browser.close()


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    html_path = Path(argv[1])
    out_path = Path(argv[2])
    width = int(argv[3]) if len(argv) > 3 else 1280
    if not html_path.exists():
        print(f"error: input not found: {html_path}", file=sys.stderr)
        return 1
    render(html_path, out_path, width)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
