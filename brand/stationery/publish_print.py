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
    # who is this for · what paper · what ink — every folder is one answer
    "letterhead/india-a4-paper": [
        (DIST / "letterhead.pdf", "letterhead-color.pdf"),
        (DIST / "letterhead-mono.pdf", "letterhead-black-only.pdf"),
    ],
    "letterhead/usa-letter-paper": [
        (DIST / "letterhead-us.pdf", "letterhead-color.pdf"),
        (DIST / "letterhead-us-mono.pdf", "letterhead-black-only.pdf"),
    ],
    "letterhead/cream-day-edition-a4": [
        (DIST / "letterhead-chandra.pdf", "letterhead-cream-color.pdf"),
        (DIST / "letterhead-chandra-mono.pdf", "letterhead-cream-black-only.pdf"),
    ],
    "letterhead": [
        (DIST / "letterhead.docx", "letterhead-typing-template.docx"),
    ],
    "receipt-book/give-to-printer": [
        (DIST / "receipt-a5-book.pdf", "receipt-page-black-only.pdf"),
        (DIST / "receipt-cover-a5-book.pdf", "receipt-cover-black-only.pdf"),
        (HERE / "receipt-press-spec.md", "printing-instructions.md"),
    ],
    "receipt-book/color-edition": [
        (DIST / "receipt-a5.pdf", "receipt-page-color.pdf"),
        (DIST / "receipt-cover-a5.pdf", "receipt-cover-color.pdf"),
    ],
    "stamps": [
        (DIST / "seal-chakra-round.pdf", "round-seal-50mm.pdf"),
        (DIST / "address-stamp.pdf", "address-stamp-75x38mm.pdf"),
        (HERE / "stamp-vendor-spec.md", "stamp-maker-instructions.md"),
    ],
    "address-labels": [
        (DIST / "labels-st8.pdf", "labels-8-per-sheet.pdf"),
        (DIST / "labels-alignment-test.pdf", "alignment-test-print-first.pdf"),
    ],
    "murti-plates": [
        (PLATES / "vertical-grammar-hi.pdf", "murti-dimensions-hindi.pdf"),
        (PLATES / "vertical-grammar.pdf", "murti-dimensions-english.pdf"),
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
