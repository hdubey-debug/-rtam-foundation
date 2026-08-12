#!/usr/bin/env python3
"""Subset brand fonts -> public/fonts/*.woff2.

Same options as website/src/build.py: keep all GSUB layout features
(Devanagari conjuncts + matras) and all name records (the OFL notices stay
inside the fonts). Full-face TTFs never ship.

M0 corpus: ASCII + the strings the shell actually shows. The corpus-perfect
pass over the full app content happens at M12 when content freezes.
"""
from pathlib import Path
from shutil import copyfile

from fontTools import subset

HERE = Path(__file__).resolve().parent
APP = HERE.parent
BRAND = APP.parent / "brand" / "fonts"
OUT = APP / "public" / "fonts"

ASCII = "".join(chr(c) for c in range(0x20, 0x7F))
PUNCT = " ·—–‘’“”…′″°×"
# Devanagari shown by the shell (title + crown terms) + digits
DEVA = (
    "ऋतम्भरेश्वर मंदिर ॐ ऋतम्भरा प्रज्ञा शिखर आमलक कलश ध्वज गर्भगृह "
    "०१२३४५६७८९"
)

JOBS = [
    ("cinzel/cinzel-500.ttf", "cinzel-500.woff2", ASCII + PUNCT),
    ("cinzel/cinzel-600.ttf", "cinzel-600.woff2", ASCII + PUNCT),
    ("inter/inter-400.ttf", "inter-400.woff2", ASCII + PUNCT),
    ("inter/inter-500.ttf", "inter-500.woff2", ASCII + PUNCT),
    ("tiro-devanagari-sanskrit/tiro-devanagari-sanskrit-400.ttf", "tiro-400.woff2", ASCII + PUNCT + DEVA),
]

LICENSES = [
    ("cinzel/OFL.txt", "OFL-cinzel.txt"),
    ("inter/OFL.txt", "OFL-inter.txt"),
    ("tiro-devanagari-sanskrit/OFL.txt", "OFL-tiro-devanagari-sanskrit.txt"),
]


def subset_font(src: Path, out: Path, text: str) -> int:
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]  # keep GSUB — Devanagari shaping
    opts.name_IDs = ["*"]  # keep the OFL notices inside the font
    opts.notdef_outline = True
    font = subset.load_font(str(src), opts)
    s = subset.Subsetter(opts)
    s.populate(text=text)
    s.subset(font)
    subset.save_font(font, str(out), opts)
    font.close()
    return out.stat().st_size


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for rel, name, text in JOBS:
        size = subset_font(BRAND / rel, OUT / name, text)
        print(f"  {name}: {size / 1024:.1f} KB")
    for rel, name in LICENSES:
        copyfile(BRAND / rel, OUT / name)
        print(f"  {name}")


if __name__ == "__main__":
    main()
