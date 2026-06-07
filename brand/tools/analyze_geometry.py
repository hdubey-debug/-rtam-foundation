#!/usr/bin/env python3
"""Compute dimensional findings from geometry.json (written by measure_render.py):
bindu centering vs the actually-rendered R/ऋ glyph, content overflow vs viewBox,
padding asymmetry, and font-load status.

Usage: analyze_geometry.py [path/to/geometry.json]
"""

import json
import sys
from pathlib import Path

DEFAULT = Path(__file__).resolve().parent / "_scratch" / "geometry.json"
geo = json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else DEFAULT).read_text())

for name, g in geo.items():
    if "error" in g:
        print(f"\n=== {name}: MEASURE ERROR {g['error']}")
        continue
    vb = g["viewBox"]
    print(f"\n=== {name}  (viewBox {vb['w']:g}x{vb['h']:g})")

    # font status
    bad = [f for f in g.get("fontsLoaded", []) if f["status"] != "loaded"]
    fams = {f["family"] for f in g.get("fontsLoaded", []) if f["status"] == "loaded"}
    if fams:
        print(f"  fonts loaded: {sorted(fams)}")
    if bad:
        print(f"  fonts NOT loaded: {bad}")

    # overflow / padding
    ub = g.get("unionBox")
    if ub and vb:
        pad_l = ub["x0"] - vb["x"]
        pad_r = (vb["x"] + vb["w"]) - ub["x1"]
        pad_t = ub["y0"] - vb["y"]
        pad_b = (vb["y"] + vb["h"]) - ub["y1"]
        print(f"  content padding L/R/T/B: {pad_l:.1f} / {pad_r:.1f} / {pad_t:.1f} / {pad_b:.1f}")
        for side, v in (("LEFT", pad_l), ("RIGHT", pad_r), ("TOP", pad_t), ("BOTTOM", pad_b)):
            if v < -0.5:
                print(f"  !! OVERFLOW {side} by {-v:.1f} viewBox units")

    # bindu centering: compare each circle against first glyph of each text
    for t in g["texts"]:
        if not t["chars"]:
            continue
        c0 = t["chars"][0]
        # ink-cell center of the first glyph (includes letter-spacing in advance;
        # report both cell center and cell-minus-spacing center)
        ls = float(t["attrs"]["letterSpacing"] or 0)
        cell_cx = c0["x"] + c0["w"] / 2
        glyph_cx = c0["x"] + (c0["w"] - ls) / 2  # advance minus trailing letter-spacing
        first_line = f"  text '{t['content'][:28]}' @x={t['attrs']['x']} fs={t['attrs']['fontSize']} ls={ls:g} anchor={t['attrs']['anchor']}"
        if t["bbox"]:
            bb = t["bbox"]
            first_line += f"  bbox[{bb['x']:.1f},{bb['y']:.1f} {bb['w']:.1f}x{bb['h']:.1f}]"
        print(first_line)
        print(f"    first glyph '{c0['ch']}': cell x={c0['x']:.1f} w={c0['w']:.1f} -> cell-center={cell_cx:.1f}, advance-minus-ls center={glyph_cx:.1f}")
        for c in g["circles"]:
            # only compare circles plausibly tied to this glyph (below it, near it)
            if abs(c["cx"] - cell_cx) < c0["w"] * 1.5:
                err_cell = c["cx"] - cell_cx
                err_glyph = c["cx"] - glyph_cx
                print(f"    bindu cx={c['cx']:g} cy={c['cy']:g} r={c['r']:g}: off cell-center {err_cell:+.1f}, off glyph-center {err_glyph:+.1f}")

    if g["circles"]:
        cs = ", ".join(f"({c['cx']:g},{c['cy']:g} r{c['r']:g})" for c in g["circles"][:14])
        print(f"  circles: {cs}{' ...' if len(g['circles']) > 14 else ''}")
