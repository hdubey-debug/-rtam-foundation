#!/usr/bin/env python3
"""WCAG 2.x contrast check for the brand palette.

Reads brand/palette/colors.json, computes the contrast ratio for every
documented foreground/background pairing, and flags failures against the
3:1 (graphics / large text) and 4.5:1 (body text) thresholds.

Exit code 1 if any pairing documented as body-text-safe fails 4.5:1.
"""

import json
import sys
from pathlib import Path

PALETTE = Path(__file__).resolve().parent.parent / "palette" / "colors.json"


def lum(hexc: str) -> float:
    c = [int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a: str, b: str) -> float:
    la, lb = lum(a), lum(b)
    lo, hi = min(la, lb), max(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def main() -> int:
    tokens = json.loads(PALETTE.read_text())
    hexes = {}
    for group in ("primary", "secondary"):
        for name, t in tokens.get(group, {}).items():
            hexes[name] = t["hex"]

    # (fg, bg, claimed_use): claimed_use 'body' must clear 4.5, 'graphics' 3.0,
    # 'decorative' has no minimum but is reported.
    pairs = [
        ("antiqueGold", "warmIvory", "decorative"),
        ("antiqueGold", "charcoalBlack", "graphics"),
        ("antiqueGold", "deepIndigo", "graphics"),
        ("charcoalBlack", "warmIvory", "body"),
        ("bronze", "warmIvory", "graphics"),
        ("stoneGray", "warmIvory", "decorative"),
        ("antiqueGold", "sandstone", "decorative"),
        ("warmIvory", "charcoalBlack", "body"),
        ("warmIvory", "deepIndigo", "body"),
    ]
    minimum = {"body": 4.5, "graphics": 3.0, "decorative": 0.0}

    failures = 0
    print("=== WCAG contrast (3:1 graphics/large text, 4.5:1 body text) ===")
    for fg, bg, use in pairs:
        r = ratio(hexes[fg], hexes[bg])
        need = minimum[use]
        ok = r >= need
        grade = ("ok" if r >= 4.5 else "ok graphics, FAIL body" if r >= 3 else "FAIL both")
        verdict = "PASS" if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"  {fg} on {bg}: {r:.2f}:1  [{grade}]  claimed use={use} -> {verdict}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
