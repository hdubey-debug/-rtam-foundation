#!/usr/bin/env python3
"""Publish the print-ready set to the repo's public print/ area.

    python3 brand/stationery/publish_print.py

Copies the CURRENT masters from dist/ (build first: build.py && checks.py) and
the murti plates into print/ — the folder the mandir's people download from.
print/ is committed; dist/ is local build output. One direction only: dist → print.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DIST = HERE / "dist"
PLATES = REPO / "murti-3d" / "plates"
PRINT = REPO / "print"

SET = {
    "letterhead": [
        (DIST / "letterhead.pdf", "letterhead.pdf"),
        (DIST / "letterhead-mono.pdf", "letterhead-mono.pdf"),
        (DIST / "letterhead.docx", "letterhead.docx"),
    ],
    "receipt": [
        (DIST / "receipt-a5.pdf", "receipt-a5.pdf"),
        (DIST / "receipt-a5-color.pdf", "receipt-a5-color.pdf"),
        (DIST / "receipt-cover-a5.pdf", "receipt-cover-a5.pdf"),
        (HERE / "receipt-press-spec.md", "receipt-press-spec.md"),
    ],
    "seal": [
        (DIST / "seal-chakra-round.pdf", "seal-chakra-round.pdf"),
        (DIST / "address-stamp.pdf", "address-stamp.pdf"),
        (HERE / "stamp-vendor-spec.md", "stamp-vendor-spec.md"),
    ],
    "labels": [
        (DIST / "labels-st8.pdf", "labels-st8.pdf"),
        (DIST / "labels-alignment-test.pdf", "labels-alignment-test.pdf"),
    ],
    "plates": [
        (PLATES / "vertical-grammar.pdf", "vertical-grammar.pdf"),
        (PLATES / "vertical-grammar-hi.pdf", "vertical-grammar-hi.pdf"),
    ],
}


def main() -> int:
    missing = []
    for folder, files in SET.items():
        out = PRINT / folder
        out.mkdir(parents=True, exist_ok=True)
        for src, name in files:
            if not src.exists():
                missing.append(str(src))
                continue
            shutil.copy2(src, out / name)
            print(f"  print/{folder}/{name}")
    if missing:
        print("MISSING (build first):\n  " + "\n  ".join(missing))
        return 1
    print("print/ is current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
