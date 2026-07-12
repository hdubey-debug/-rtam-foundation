#!/usr/bin/env python3
"""One command -> every rendered export. This is the driver whose absence let
the exports/ tree go stale (each PNG had been a manual invocation; F11's diff
method re-rendered the same HTML twice, so a missing-stylesheet regression
diffed to zero). After it runs, verify_export.py probes the pixels.

  export_all.py            render everything into brand/exports/
  export_all.py --only X   substring filter on output path (faster iteration)

Covers: preview/mockup/specimen HTML -> PNG (Chromium, the sizes the kit has
always shipped), overlay-variant SVG proofs on charcoal (cairosvg), platform
rasters (export_platform), and the two guideline PDFs (render_md_to_pdf).
"""
import argparse
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
BRAND = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import cairosvg  # noqa: E402
import export_platform  # noqa: E402
from render_html_to_png import render as render_html  # noqa: E402
from render_md_to_pdf import render as render_md  # noqa: E402

# (source html, output png, viewport width, device scale)
HTML_JOBS = [
    ("previews/index.html",                     "exports/mockups/index.png",              1280, 2),
    ("previews/mockups/website-header.html",    "exports/mockups/website-header.png",     1280, 2),
    ("previews/mockups/donation-poster.html",   "exports/mockups/donation-poster.png",    1080, 2),
    ("previews/mockups/certificate.html",       "exports/mockups/certificate.png",        1100, 2),
    ("previews/mockups/favicon-scale-test.html","exports/mockups/favicon-scale-test.png", 1100, 2),
    ("previews/mockups/instagram-avatar.html",  "exports/mockups/instagram-avatar.png",   1100, 2),
    ("previews/mockups/letterhead.html",        "exports/mockups/letterhead.png",          794, 2),
    ("previews/mockups/donation-receipt.html",  "exports/mockups/donation-receipt.png",    794, 2),
    ("previews/mockups/youtube-banner.html",    "exports/mockups/youtube-banner.png",     2560, 2),
    ("previews/wordmark-specimen.html",             "exports/png/wordmark-specimen.png",             1200, 2),
    ("previews/monogram-specimen.html",             "exports/png/monogram-specimen.png",             1200, 2),
    ("previews/devanagari-monogram-specimen.html",  "exports/png/devanagari-monogram-specimen.png",  1200, 2),
    ("previews/lockups-specimen.html",              "exports/png/lockups-specimen.png",              1200, 2),
    ("previews/typography-specimen.html",           "exports/png/typography-specimen.png",           1200, 2),
]

# overlay variants proven on their intended dark ground (charcoal)
SVG_JOBS = [
    ("dist/outlined/icons/rtam-rdot-icon-white.svg", "exports/png/rtam-rdot-icon-white.png", 512),
    ("dist/outlined/logos/rtam-wordmark-white.svg",  "exports/png/rtam-wordmark-white.png", 1080),
]

PDF_JOBS = [
    ("guidelines/brand-book.md",  "exports/pdf/brand-book.pdf"),
    ("guidelines/usage-rules.md", "exports/pdf/usage-rules.pdf"),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="substring filter on the output path")
    args = ap.parse_args()

    def want(out: str) -> bool:
        return not args.only or args.only in out

    for src, out, width, scale in HTML_JOBS:
        if want(out):
            render_html(BRAND / src, BRAND / out, width, scale)
            print(f"  html  {out}")
    for src, out, width in SVG_JOBS:
        if want(out):
            (BRAND / out).parent.mkdir(parents=True, exist_ok=True)
            cairosvg.svg2png(url=str(BRAND / src), write_to=str(BRAND / out),
                             output_width=width, background_color="#1A1A1A")
            print(f"  svg   {out}")
    if want("exports/platform/"):
        export_platform.main()
    for src, out in PDF_JOBS:
        if want(out):
            render_md(BRAND / src, BRAND / out)
            print(f"  pdf   {out}")
    print("export_all: done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
