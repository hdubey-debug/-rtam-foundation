#!/usr/bin/env python3
"""Emit renderer-independent *-outlined.svg distribution masters from brand.json.

Each glyph run is shaped (uharfbuzz) and converted to <path> geometry (fontTools
-> SVGPathPen, the Phase-0-proven pipeline); shapes (bindu, rules) pass through.
The masters render correctly in font-less engines — cairosvg, print RIPs, Office,
older SVG consumers — where the live-text @import would fall back to a system
font. Mirrors the source tree under brand/dist/outlined/.

  outline.py            dry-run
  outline.py --write    write masters under brand/dist/outlined/
parity.py gates these (renderer-independence <= 150px blob, position <= 4px).
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import brandlib as bl  # noqa: E402

DIST = bl.BRAND / "dist" / "outlined"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    brand = bl.load_brand()
    n = 0
    for asset, output in bl.all_outputs(brand):
        svg = bl.emit_outlined(brand, asset, output)
        dest = DIST / output["path"]
        if args.write:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(svg)
        n += 1
        print(f"  {'wrote' if args.write else 'would write'}  dist/outlined/{output['path']}")
    print(f"\n{n} outlined masters{' written' if args.write else ' (dry-run; pass --write)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
