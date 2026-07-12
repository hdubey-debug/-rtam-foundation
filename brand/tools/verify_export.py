#!/usr/bin/env python3
"""Colour-probe gate for brand/exports/ — the check that would have caught the
poisoned exports (HTML rendered without colors.css: every var() fell back to
black, and nothing noticed because the old parity method re-rendered the same
broken HTML and diffed zero).

Each managed export gets pixel-level expectations against the palette canon:

  point    (fx, fy) token          the pixel at that fraction of the image is
                                   within TOL of the token (grounds)
  contains (fx0,fy0,fx1,fy1) token N   the region holds >= N pixels within TOL
                                   of the token (ink/accent presence)

A missing file fails. PDFs get an existence + size floor. Exit 1 on any miss.
Run after export_all.py; build.sh wires both.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

TOOLS = Path(__file__).resolve().parent
BRAND = TOOLS.parent
sys.path.insert(0, str(TOOLS))
from palette_sync import load_canon  # noqa: E402

TOL = 30  # per-channel

_canon = load_canon()
C = {
    "gold": _canon["antiqueGold"],
    "ivory": _canon["warmIvory"],
    "charcoal": _canon["charcoalBlack"],
    "sandstone": _canon["sandstone"],
    "indigo": _canon["deepIndigo"],
}

PROBES = {
    "exports/mockups/donation-poster.png": [
        ("point", (0.03, 0.50), "indigo"),
        ("contains", (0.15, 0.28, 0.85, 0.55), "ivory", 500),
        ("contains", (0.20, 0.80, 0.80, 0.95), "gold", 150),
    ],
    "exports/mockups/website-header.png": [
        ("point", (0.50, 0.55), "ivory"),
        ("contains", (0.02, 0.00, 0.40, 0.10), "charcoal", 200),
    ],
    "exports/mockups/index.png": [
        ("point", (0.50, 0.999), "ivory"),
        ("contains", (0.00, 0.00, 1.00, 0.08), "charcoal", 200),
        ("contains", (0.00, 0.00, 1.00, 0.30), "gold", 100),
    ],
    "exports/mockups/letterhead.png": [
        ("point", (0.50, 0.50), "ivory"),
        ("contains", (0.05, 0.03, 0.70, 0.20), "charcoal", 150),
    ],
    "exports/mockups/donation-receipt.png": [
        ("point", (0.50, 0.60), "ivory"),
        ("contains", (0.05, 0.03, 0.70, 0.22), "charcoal", 150),
    ],
    "exports/mockups/certificate.png": [
        ("point", (0.50, 0.55), "ivory"),
        ("contains", (0.10, 0.05, 0.90, 0.60), "charcoal", 200),
    ],
    "exports/mockups/instagram-avatar.png": [
        ("point", (0.02, 0.50), "sandstone"),
        ("contains", (0.00, 0.00, 1.00, 1.00), "gold", 100),
    ],
    "exports/mockups/favicon-scale-test.png": [
        ("contains", (0.00, 0.55, 1.00, 0.85), "charcoal", 5000),
        ("contains", (0.00, 0.00, 1.00, 0.55), "gold", 30),
    ],
    "exports/mockups/youtube-banner.png": [
        ("contains", (0.00, 0.00, 1.00, 1.00), "indigo", 10000),
        ("contains", (0.20, 0.20, 0.80, 0.80), "ivory", 300),
    ],
    "exports/png/wordmark-specimen.png": [
        ("point", (0.50, 0.999), "ivory"),
        ("contains", (0.00, 0.00, 1.00, 0.30), "charcoal", 300),
        ("contains", (0.00, 0.00, 1.00, 0.30), "gold", 30),
    ],
    "exports/png/monogram-specimen.png": [
        ("point", (0.50, 0.999), "ivory"),
        ("contains", (0.00, 0.00, 1.00, 0.40), "charcoal", 300),
    ],
    "exports/png/devanagari-monogram-specimen.png": [
        ("point", (0.50, 0.999), "ivory"),
        ("contains", (0.00, 0.00, 1.00, 0.40), "charcoal", 300),
    ],
    "exports/png/lockups-specimen.png": [
        ("point", (0.50, 0.999), "ivory"),
        ("contains", (0.00, 0.00, 1.00, 1.00), "indigo", 5000),
        ("contains", (0.00, 0.00, 1.00, 0.40), "charcoal", 300),
    ],
    "exports/png/typography-specimen.png": [
        ("point", (0.50, 0.999), "ivory"),
        ("contains", (0.00, 0.00, 1.00, 0.10), "charcoal", 300),
    ],
    "exports/png/rtam-rdot-icon-ivory.png": [
        ("point", (0.02, 0.02), "charcoal"),
        ("contains", (0.00, 0.00, 1.00, 1.00), "ivory", 500),
    ],
    "exports/png/rtam-wordmark-ivory.png": [
        ("point", (0.02, 0.02), "charcoal"),
        ("contains", (0.00, 0.00, 1.00, 1.00), "ivory", 500),
    ],
    "exports/platform/favicon-16.png": [("contains", (0, 0, 1, 1), "charcoal", 8)],
    "exports/platform/favicon-32.png": [("contains", (0, 0, 1, 1), "charcoal", 30)],
    "exports/platform/favicon-48.png": [
        ("contains", (0, 0, 1, 1), "charcoal", 60),
        ("contains", (0, 0, 1, 1), "gold", 3),
    ],
    "exports/platform/apple-touch-icon-180.png": [
        ("point", (0.03, 0.03), "ivory"),
        ("contains", (0, 0, 1, 1), "charcoal", 50),
    ],
    "exports/platform/icon-192.png": [
        ("point", (0.03, 0.03), "ivory"),
        ("contains", (0, 0, 1, 1), "charcoal", 50),
    ],
    "exports/platform/icon-512.png": [
        ("point", (0.03, 0.03), "ivory"),
        ("contains", (0, 0, 1, 1), "charcoal", 300),
        ("contains", (0, 0, 1, 1), "gold", 50),
    ],
    "exports/platform/maskable-512.png": [
        ("point", (0.03, 0.03), "ivory"),
        ("contains", (0, 0, 1, 1), "charcoal", 200),
    ],
    "exports/platform/og-image-1200x630.png": [
        ("point", (0.02, 0.02), "ivory"),
        ("contains", (0, 0, 1, 1), "charcoal", 200),
        ("contains", (0, 0, 1, 1), "gold", 30),
    ],
}

PDF_MIN_BYTES = 10_000
PDFS = ["exports/pdf/brand-book.pdf", "exports/pdf/usage-rules.pdf"]


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.int16)


def close_mask(arr, token):
    return (np.abs(arr - hex_rgb(C[token])).max(axis=-1) <= TOL)


def main() -> int:
    fails = []
    for rel, probes in PROBES.items():
        p = BRAND / rel
        if not p.exists():
            fails.append(f"{rel}: MISSING")
            continue
        img = Image.open(p)
        if img.mode == "RGBA":
            # flatten onto white so transparent pixels never match a token
            bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
            img = Image.alpha_composite(bg, img)
        arr = np.asarray(img.convert("RGB"), dtype=np.int16)
        H, W = arr.shape[:2]
        for probe in probes:
            if probe[0] == "point":
                (fx, fy), token = probe[1], probe[2]
                px = arr[min(int(fy * H), H - 1), min(int(fx * W), W - 1)]
                if np.abs(px - hex_rgb(C[token])).max() > TOL:
                    fails.append(f"{rel}: point({fx},{fy}) = {tuple(int(v) for v in px)}, "
                                 f"expected {token} {C[token]}")
            else:
                (fx0, fy0, fx1, fy1), token, need = probe[1], probe[2], probe[3]
                reg = arr[int(fy0 * H):max(int(fy1 * H), int(fy0 * H) + 1),
                          int(fx0 * W):max(int(fx1 * W), int(fx0 * W) + 1)]
                got = int(close_mask(reg, token).sum())
                if got < need:
                    fails.append(f"{rel}: region {probe[1]} has {got}px of {token}, needs >= {need}")
    for rel in PDFS:
        p = BRAND / rel
        if not p.exists():
            fails.append(f"{rel}: MISSING")
        elif p.stat().st_size < PDF_MIN_BYTES:
            fails.append(f"{rel}: only {p.stat().st_size} bytes (< {PDF_MIN_BYTES})")
    if fails:
        print("EXPORT COLOUR GATE FAILED:")
        for f in fails:
            print("  -", f)
        return 1
    print(f"  export colours OK ({len(PROBES)} PNGs probed against the canon, "
          f"{len(PDFS)} PDFs present)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
