# Phase-0 Engineering Spikes — Results

Date: 2026-06-07 · All four spikes **PASSED**. The outlined-master strategy
(US-13 Track C) is viable end-to-end.

## Spike 1 — Devanagari shaping → outlined paths (GATING) ✅

Pipeline: **uharfbuzz shape → fontTools glyf → SVGPathPen → path-only SVG**,
run on all four shipped Devanagari strings with the vendored
Tiro Devanagari Sanskrit TTF (`shaping_spike.py`).

| string | glyphs | conjuncts formed | halants (expected) | Gate B max-blob (≤150) |
|---|---|---|---|---|
| ऋतम्भरेश्वर मंदिर | 17 cp → 13 | `dMBha`, `dShVa` | 0 (0) | 10px |
| ऋतम् प्रतिष्ठान | 15 cp → 11 | `dPRa`, `dSsTtha` | 1 (1) | 34px |
| ऋतम् फाउंडेशन | 13 cp → 13 | — (none expected) | 1 (1) | 4px |
| ऋ | 1 → 1 | — | 0 (0) | 63px |

- **Gate A (shaping correctness)**: exact glyph-name verification — every
  conjunct forms, the word-final explicit virāma in ऋतम् is preserved, no
  dotted-circle (broken-cluster) glyph anywhere.
- **Gate B (renderer independence)**: the outlined SVG renders identically
  in cairosvg and Chromium (see metric below).
- Informational: vs Chromium's own live-text rendering (same TTF via
  @font-face), residual differences are rasterizer advance-rounding only —
  cumulative drift ≤ 3px per ~874px line (0.34%), min strip IoU 0.95+.

## Spike 2 — Latin outlining ✅

Exact wordmark composition (Cinzel 500 RTAM fs=120 ls=12 + Cinzel 400
Foundation fs=62 ls=8 + bindu) through the same pipeline (`latin_spike.py`).
Gate B max-blob = **11px**. Letter-spacing is applied per HarfBuzz cluster
(after every cluster including the last, matching SVG/CSS semantics).

## Spike 3 — Negative-space boolean ops ✅

skia-pathops `DIFFERENCE` punches a circular counter out of the Cinzel R
outline: bite blob 2897px (real ink removed), cross-renderer max-blob 8px.
Concept (e) "bindu as negative space" is buildable. Proof:
`negative-space-R-sidebyside.png`.

## Spike 4 — Fonts vendored with licenses ✅

All 4 brand families (Cinzel 400/500/600/700, Marcellus 400, Inter
400/500/600, Tiro Devanagari Sanskrit 400) fetched as **full unsubset TTFs**
from the Google Fonts API and vendored to `brand/fonts/` with per-family
`OFL.txt`. Verified: family names, glyph counts, GSUB tables, all
brand-critical codepoints. (GitHub raw is blocked by this cluster's TLS
proxy; the Google Fonts CSS API with a non-woff2 UA serves full TTFs.)

## The fidelity metric (calibrated, negative-controlled)

`brand/tools/render_diff.py::structural_diff` — binarize both renders on a
common 1024 grid (aspect-preserving pad), register globally (±4px), dilate
1px (AA tolerance), take the symmetric difference, and gate on its
**largest connected blob ≤ 150px**.

Why not plain IoU: IoU normalizes by ink area while AA fringe scales with
perimeter, so sparse compositions score worse than dense ones for the same
(visually zero) difference — a dropped anusvara scored IoU 0.9934 while a
visually identical sparse wordmark pair scored 0.9765. IoU cannot order
defective above identical across compositions; blob concentration can.

Negative control (`negative_control.py`): identical pairs ≤ **10px**;
injected defects — dropped anusvara **256px**, i-matra shifted 5 units
**1094px**, swapped glyph **2823px**, dropped bindu **330px**. The gate at
150 sits in a 25× separation gap. This is the CI gate for US-13 `build.sh`,
where it compares cairosvg-vs-Chromium renders of identical outlined files
(no drift dimension by construction).

## Facts unlocked for `outline.py` (US-13)

- Per-glyph `<path>` elements with TransformPen `(s,0,0,-s,x,y)`; scale
  `s = font-size / upem`; HarfBuzz `x_offset/y_offset` for GPOS marks.
- letter-spacing: add once per cluster boundary (incl. last), never inside
  a cluster.
- `text-anchor=middle/end` (used by icons): shape first, then shift by
  −advance/2 or −advance (not yet exercised in spikes — exercise in US-13).
- Cinzel has no U+1E5A/U+0323 support — drawn bindu circle remains correct.
