#!/usr/bin/env python3
"""Emit every live-text source SVG in the brand asset tree from brand.json.

This is the single source of truth: hand-editing the icons/logos/lockups is no
longer the workflow — edit brand/spec/brand.json and regenerate. Kills the
copy-paste drift that caused the original defects. Pure data->string (no browser;
all positions are baked literals in brand.json).

  generate.py            dry-run: list what would be written, flag diffs
  generate.py --write    write the source SVGs in place
Run parity.py first (build.sh does) to prove the output reproduces the design.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import brandlib as bl  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write files (default: dry-run)")
    args = ap.parse_args()
    brand = bl.load_brand()
    n_new = n_chg = n_same = 0
    for asset, output in bl.all_outputs(brand):
        svg = bl.emit_livetext(brand, asset, output)
        dest = bl.BRAND / output["path"]
        old = dest.read_text() if dest.exists() else None
        state = "new" if old is None else ("unchanged" if old == svg else "changed")
        if state == "new":
            n_new += 1
        elif state == "changed":
            n_chg += 1
        else:
            n_same += 1
        if args.write:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(svg)
        print(f"  [{state:9s}] {output['path']}")
    verb = "wrote" if args.write else "would write"
    print(f"\n{verb}: {n_new} new, {n_chg} changed, {n_same} unchanged "
          f"({n_new + n_chg + n_same} source SVGs)")
    if not args.write:
        print("(dry-run — pass --write to apply; run parity.py to verify first)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
