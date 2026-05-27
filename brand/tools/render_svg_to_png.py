#!/usr/bin/env python3
"""Rasterize an SVG to PNG at a given pixel width.

Usage:
    python3 render_svg_to_png.py <input.svg> <output.png> [width_px]

Width defaults to 1024. Aspect ratio is preserved from the SVG viewBox.
"""

import sys
from pathlib import Path

import cairosvg


def render(svg_path: Path, png_path: Path, width: int) -> None:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(
        url=str(svg_path),
        write_to=str(png_path),
        output_width=width,
    )


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    svg_path = Path(argv[1])
    png_path = Path(argv[2])
    width = int(argv[3]) if len(argv) > 3 else 1024
    if not svg_path.exists():
        print(f"error: input not found: {svg_path}", file=sys.stderr)
        return 1
    render(svg_path, png_path, width)
    print(f"wrote {png_path} ({width}px wide)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
