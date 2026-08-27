#!/usr/bin/env python3
"""ṚTAM stationery gate — every claim the masters make, asserted.

    python3 brand/stationery/checks.py

Covers: exact page boxes (A4 / A5L / Ø40 sheet), brand-fonts-only embedding
(the DroidSansDevanagari leak on the first receipt build is why this exists),
CDN-free print sources, load-bearing text present (honest line, address, 8
labels — counted whitespace-collapsed, letterspacing splits extraction),
mono-edition grayscale, and the seal's manufacturing floors recomputed from
the spec itself.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF — read-only checks; not a build dependency
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
BRAND = HERE.parent
DIST = HERE / "dist"
MM = 72 / 25.4
BRAND_FACES = ("Tiro", "Inter", "Cinzel")

FAIL = []


def check(name: str, ok: bool, detail: str = ""):
    print(f"  {'ok  ' if ok else 'FAIL'} {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAIL.append(name)


def pdf_page(path: Path, w_mm: float, h_mm: float, contains: list = (), fonts_brand_only=True):
    d = fitz.open(path)
    pg = d[0]
    w, h = pg.rect.width / MM, pg.rect.height / MM
    check(f"{path.name}: single page", len(d) == 1, f"{len(d)} pages")
    check(f"{path.name}: {w_mm:g}×{h_mm:g}mm", abs(w - w_mm) < 0.6 and abs(h - h_mm) < 1.2,
          f"{w:.1f}×{h:.1f}")
    if fonts_brand_only:
        names = sorted({f[3].split("+")[-1] for f in pg.get_fonts()})
        ok = all(any(b in n for b in BRAND_FACES) for n in names)
        check(f"{path.name}: brand fonts only", ok, ", ".join(names))
    text = re.sub(r"\s+", "", pg.get_text())
    for needle, n in contains:
        c = text.count(re.sub(r"\s+", "", needle))
        check(f"{path.name}: '{needle[:24]}' ×{n}", c == n, f"found {c}")


def main() -> int:
    print("== stationery checks ==")

    pdf_page(DIST / "letterhead.pdf", 210, 297,
             [("483001", 2), ("9098225177", 2), ("संस्थापक", 1),
              ("FOUNDERS—SHRIRAJESHDUBEY", 1), ("SMT.KIRANBALADUBEY", 1)])
    pdf_page(DIST / "letterhead-mono.pdf", 210, 297,
             [("483001", 2), ("FOUNDERS—SHRIRAJESHDUBEY", 1)])
    pdf_page(DIST / "receipt-a5.pdf", 210, 148,
             [("आयकर-कटौतीकादावानहींबनता", 1), ("483001", 2), ("मंदिरनिर्माणनिधि", 1),
              # bilingual doctrine: labels echo, scripture doesn't; compact address pair
              # uppercase: text-transform bakes into extracted glyphs
              ("Noincome-taxdeduction", 1), ("CONSTRUCTIONFUND", 1), ("GAUSEVA", 1),
              ("BARELA", 1), ("ऋतस्यपन्थाम्", 1)])
    pdf_page(DIST / "receipt-cover-a5.pdf", 210, 148,
             [("दान-रसीदबही", 1), ("BOOKNO.", 1)])
    pdf_page(DIST / "receipt-a5-color.pdf", 210, 148,
             [("आयकर-कटौतीकादावानहींबनता", 1), ("VILL.PAHADIKHEDA", 1)])
    pdf_page(DIST / "labels-st8.pdf", 210, 297,
             [("BARELA", 8), ("483001", 8), ("ऋतम्भरेश्वरमंदिर", 8),
              ("RTAMBHARESHVARAMANDIR", 8), ("VILL.PAHADIKHEDA", 8)])
    pdf_page(DIST / "labels-alignment-test.pdf", 210, 297, [])
    pdf_page(DIST / "seal-chakra-round.pdf", 50, 50, [], fonts_brand_only=False)  # outlined: no fonts at all
    pdf_page(DIST / "address-stamp.pdf", 75, 38, [], fonts_brand_only=False)

    # print sources carry no CDN reference
    for f in sorted(HERE.glob("*.html")) + [HERE / "stationery.css"]:
        check(f"{f.name}: CDN-free", "fonts.googleapis" not in f.read_text())

    # mono edition is achromatic
    mono = BRAND / "exports" / "stationery" / "letterhead-mono-preview.png"
    a = np.asarray(Image.open(mono).convert("RGB"), dtype=np.int16)
    spread = int((a.max(axis=2) - a.min(axis=2)).max())
    check("letterhead-mono: grayscale", spread <= 12, f"max channel spread {spread}")

    # seal floors recomputed from the spec (viewBox u per mm from widthMM)
    spec = json.loads((BRAND / "spec" / "brand.json").read_text())
    for sid in ("seal-chakra-round", "address-stamp"):
        seal = next(a for a in spec["assets"] if a["id"] == sid)
        u = seal["viewBox"][0] / seal["widthMM"]
        strokes = [sh["strokeWidth"] for sh in seal["shapes"] if "strokeWidth" in sh]
        strokes += [sh["strokeWidth"] for sh in seal["shapes"]
                    if sh.get("type") == "polarArray" and "strokeWidth" in sh]
        if strokes:
            check(f"{sid}: strokes ≥ 0.5mm", min(strokes) / u >= 0.5,
                  f"thinnest {min(strokes)/u:.2f}mm")
        # floors per script: Devanagari base-height ≥ 2.3mm; Latin type ≥ 7pt (2.46mm)
        deva_fs = [r["fs"] for r in seal["runs"] if r["font"] == "tiro"]
        lat_fs = [r["fs"] for r in seal["runs"] if r["font"] != "tiro"]
        if deva_fs:
            f = min(deva_fs)
            check(f"{sid}: Devanagari base ≥ 2.3mm", 0.75 * f / u >= 2.3,
                  f"{0.75*f/u:.2f}mm at fs {f}")
        if lat_fs:
            f = min(lat_fs)
            check(f"{sid}: Latin type ≥ 2.46mm (7pt)", f / u >= 2.46,
                  f"{f/u:.2f}mm at fs {f}")

    print("== " + ("ALL CHECKS PASS" if not FAIL else f"{len(FAIL)} FAILURES") + " ==")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
