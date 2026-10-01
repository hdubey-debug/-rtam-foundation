#!/usr/bin/env python3
"""Assemble posters/brand/ from the repository's canonical brand kit, so the posters use the same fonts and outlined
marks as everything else (brand/fonts, brand/dist/outlined, brand/palette). Run once after cloning:

    python3 build/setup_brand.py
"""
import shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; KIT = ROOT.parent / 'brand'; DST = ROOT / 'brand'
if not (KIT / 'dist' / 'outlined').exists(): raise SystemExit(f'brand kit not found at {KIT}')
(DST / 'fonts').mkdir(parents=True, exist_ok=True); (DST / 'marks').mkdir(parents=True, exist_ok=True)
n = 0
for f in sorted((KIT / 'fonts').glob('*/*.ttf')): shutil.copy2(f, DST / 'fonts' / f.name); n += 1
for f in sorted((KIT / 'dist' / 'outlined').glob('*/*.svg')): shutil.copy2(f, DST / 'marks' / f.name); n += 1
for f in sorted((ROOT / 'build' / 'qr').glob('*.svg')): shutil.copy2(f, DST / 'marks' / f.name); n += 1
shutil.copy2(KIT / 'palette' / 'colors.json', DST / 'colors.json')
print(f'brand/ assembled from the kit: {n} files')
