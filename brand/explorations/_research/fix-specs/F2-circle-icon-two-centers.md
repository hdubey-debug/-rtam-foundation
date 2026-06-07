# F2 — Circle icons torn between two centers (R ink not centered on the bindu/ring axis)

## Root cause
Every R-dot icon positions the `R` with `text-anchor="middle"` at `x=128`
(`x=16` for the favicon). `text-anchor="middle"` centers the glyph's **advance
box**, not its **ink**. The Cinzel `R` is right-biased: relative to its advance
box it carries a large left side-bearing and its leg/bowl ink *overhangs the
right edge of the advance* (negative right side-bearing). Measured on the
vendored Cinzel TTFs (upem=1000):

| weight | LSB (em) | ink xMin..xMax (em) | advance (em) | ink-center offset from advance-center |
|---|---|---|---|---|
| 600 | 0.050 | 0.050 .. 0.755 | 0.724 | **+0.0405 em** |
| 700 | 0.045 | 0.045 .. 0.789 | 0.747 | **+0.0435 em** |

So when the advance is centered on 128, the **ink** center lands right of 128
and the visible left air exceeds the right air. The ring (cx=128) and bindu
(cx=128) are centered correctly; only the glyph is off, which makes the R look
shoved right inside the ring and makes the bindu sit left of the R's optical
center.

Note on the finding's magnitude: the audit estimated the offset at "≈12.5
units" for both groups. The true, font-derived and pixel-confirmed offsets are
**8.1 units (plain fs200)** and **6.885 units (circle fs170)** — the direction
in the finding is right; the magnitude was overstated ~1.5–3×, and it is *not*
constant in units across the two font sizes (it is ~constant in em). The
measurement governs; numbers below are the corrected ones.

## Files touched
1. `brand/icons/rtam-rdot-icon-circle-gold.svg`
2. `brand/icons/rtam-rdot-icon-circle-charcoal.svg`
3. `brand/icons/rtam-rdot-icon-black.svg`
4. `brand/icons/rtam-rdot-icon-gold.svg`
5. `brand/icons/rtam-rdot-icon-white.svg`
6. `brand/icons/favicon.svg`  *(beyond the 5 named in the finding — same defect,
   same fix; see "Residual risk". Include it; it is the favicon and is the most
   widely seen mark. Likely no overlap with another F-finding, but flag for the
   re-audit to confirm it is not double-owned.)*

Only the `x` attribute of the single `<text>` element changes in each file. The
ring `<circle>`, the bindu `<circle>`, every `cy`, every `y` baseline, fills,
font-family, font-size, and the `text-anchor="middle"` all stay exactly as
shipped.

## Exact change
Replace `x="128"` with the corrected value in the one `<text>` line of each
file (`x="16"` for the favicon). Full before → after for each `<text>`:

**rtam-rdot-icon-circle-gold.svg** (line 8) and
**rtam-rdot-icon-circle-charcoal.svg** (line 8) — fs=170, wt=600:
```
- <text x="128" y="178" font-family="Cinzel, Marcellus, 'Trajan Pro', serif" font-weight="600" font-size="170" text-anchor="middle" fill="...">R</text>
+ <text x="121.12" y="178" font-family="Cinzel, Marcellus, 'Trajan Pro', serif" font-weight="600" font-size="170" text-anchor="middle" fill="...">R</text>
```
(circle-gold `fill="#1A1A1A"`, circle-charcoal `fill="#1A1A1A"` — fill unchanged;
both share the identical text geometry.)

**rtam-rdot-icon-black.svg** (line 7), **-gold.svg** (line 7),
**-white.svg** (line 10) — fs=200, wt=600:
```
- <text x="128" y="184" ... font-weight="600" font-size="200" text-anchor="middle" fill="...">R</text>
+ <text x="119.9" y="184" ... font-weight="600" font-size="200" text-anchor="middle" fill="...">R</text>
```
(black `fill="#1A1A1A"`, gold `fill="#C8A15A"`, white `fill="#F7F3E9"` — fills
unchanged; the three share the identical text geometry.)

**favicon.svg** (line 7) — fs=26, wt=700, center=16:
```
- <text x="16" y="22" ... font-weight="700" font-size="26" text-anchor="middle" fill="#1A1A1A">R</text>
+ <text x="14.87" y="22" ... font-weight="700" font-size="26" text-anchor="middle" fill="#1A1A1A">R</text>
```

Equivalent `dx` form (if a generator prefers `x` untouched + a shift attribute):
add `dx="-6.88"` (circle), `dx="-8.1"` (plain), `dx="-1.13"` (favicon). The spec
files below adopt the direct-`x` form to match the shipped convention (no file
currently uses `dx`).

## Parameters resolved
All x values are `new_x = center + advance/2 − ink_mid`, where
`ink_mid = (xMin+xMax)/2 × font_size/upem`, derived from the vendored Cinzel
TTF outline bounds (fontTools `BoundsPen`) and **confirmed by 8×-scale pixel
render** (ink-center after correction lands within 0.19 unit of center on all
three).

- **circle-gold / circle-charcoal → `x="121.12"`** — fs=170 wt=600, center=128.
  Shipped ink center 134.89 (offset +6.885); corrected pixel ink center 128.06,
  left air 68.12 vs right air 68.0.
- **black / gold / white → `x="119.9"`** — fs=200 wt=600, center=128.
  Shipped ink center 136.1 (offset +8.1); corrected pixel ink center 127.88,
  left air 57.38 vs right air 57.62.
- **favicon → `x="14.87"`** — fs=26 wt=700, center=16.
  Shipped ink center 17.13 (offset +1.131); corrected pixel ink center 16.19,
  left air 6.5 vs right air 6.12.
- Rounding: 2 decimals. Sub-0.2-unit residual is below visual threshold (the
  corrected-x pixel ink centers above already include the rounding). Two
  decimals on a 256 viewBox is 1/12800 of width — far finer than any rasterizer.

Source-of-truth note: Chromium `getBBox()` on `<text>` was tested and found
**unreliable** for this purpose — it returns the advance-box left edge as `x`
(includes the empty LSB) but the true ink `xMax` as the right edge, yielding an
asymmetric box whose center (131.0) disagrees with both the glyph outline
(136.1) and the pixel render (136.0). The fix is therefore computed from
fontTools outline bounds, not getBBox. (`getExtentOfChar` has the same
advance-cell ambiguity.)

## Proof
- `brand/explorations/_research/fix-specs/proofs/F2-circle-gold-before-after.png`
  — circle-gold, BEFORE `x=128` vs AFTER `x=121.12`, red dashed guide at x=128.
  BEFORE: the guide cuts left of the R's optical middle; wide left air inside
  the ring, leg crowds the right. AFTER: the guide bisects the R; bowl and leg
  balance left↔right and the R reads concentric with ring + bindu. Dot at 128 in
  both.
- `brand/explorations/_research/fix-specs/proofs/F2-plain-before-after.png`
  — plain, BEFORE `x=128` vs AFTER `x=119.9`. BEFORE: the bindu sits under the
  R's left bowl, not its center. AFTER: the bindu sits under the R's optical
  center — the brand-critical "dot under the R" relationship is restored.

Renders are faithful (local Cinzel-600 TTF via `@font-face file://`,
`document.fonts.ready` awaited + 400ms settle).

## Verification steps (US-16 re-audit)
For each of the 6 files, faithfully render (Playwright Chromium, fonts awaited),
then measure the R's **ink** center and the air:
1. Compute the corrected ink center from the corrected `x`:
   `ink_cx = x − advance/2 + ink_mid` using the Cinzel outline bounds above (or
   equivalently read leftmost/rightmost dark ink column from an 8× render).
   Assert `|ink_cx − center| ≤ 0.5` unit (center = 128, or 16 for favicon).
2. Assert `left_air ≈ right_air` within ≤ 1 unit: `left = ink_left`,
   `right = viewBox − ink_right`.
3. Assert the ring `<circle cx>` and bindu `<circle cx>` are unchanged
   (128 / 16) and all `y`, `cy`, fills, font-size unchanged from shipped.
4. The em-offset table in "Root cause" is the durable artifact — re-derive it if
   needed via fontTools `BoundsPen` on the vendored Cinzel TTF (do not rely on a
   `_scratch/` script; `_scratch` is gitignored and won't be present at re-audit).
   The corrected pixel ink center must land within ±0.2 of center for all three
   geometries (121.12 / 119.9 / 14.87).
Do NOT use `getBBox().x` as the ink-center oracle (see source-of-truth note).

Served-vs-vendored parity is confirmed: the **actual shipped**
`rtam-rdot-icon-circle-gold.svg`, rendered with the network-served Google Cinzel
(Chromium, fonts awaited), measures ink center **134.938** — matching the
vendored-TTF prediction (134.94) to 0.002 unit. So the baked x values are correct
against the fonts the live-text SVGs actually load, not just the vendored copies.

## Residual risk
- **Provisional on Cinzel.** The numbers are tied to Cinzel's R outline. If a
  Phase-2 program swaps the letterform, all six x values must be recomputed from
  the new font's R bounds (the *rule* below does this automatically). The
  shipped `font-family` fallback chain (`Marcellus, 'Trajan Pro', serif`) has a
  different R offset; if Cinzel fails to load, the correction is mistuned — but
  that is the same web-font-dependency caveat that already governs these
  live-text assets (out of scope for F2).
- **Favicon is beyond the finding's 5 named files.** It carries the identical
  defect; I included it rather than silently drop or silently absorb it. The
  re-audit should confirm the favicon is not also claimed by another F-finding;
  if it is, defer the favicon line to that finding and keep the durable rule.
- **Ink-center is deliberately not optical-center-of-mass.** The Cinzel R's leg
  overhangs its advance (ink xMax 151 > advance 144.8 at fs200) as a thin
  diagonal tip, while the left side is the solid stem — so the ink-bbox center is
  slightly right of the glyph's mass centroid. This spec centers the **ink bbox**
  because the finding/task says "the R INK centers on 128" and because equal
  left/right air is an extents property. A future designer who eyeballs a hair of
  remaining mass-imbalance should know this was the chosen target, not an
  oversight; do not "correct" it to a centroid without re-deciding the air rule.
- The fix is per-file static `x`; it does not change with viewer or DPI. Lowest-
  risk possible change (one attribute, fully reversible by restoring `x=128`/16).

## Depends on
None. (Independent of all other F-findings; touches only the `x` of `<text>` in
six icon files. The durable rule overlaps the US-13 generator surface but does
not block any other fix.)

## Durable or provisional
- **Provisional:** the six concrete `x` values (Cinzel-shape-tied).
- **Durable — generator rule for `brand/tools/generate.py` / the outline
  pipeline:** when a single glyph is centered on a target axis, centering the
  **advance** (plain `text-anchor="middle"`) is wrong for right/left-biased
  glyphs. Center the **ink bbox** instead:
  `x = center + advance/2 − (xMin+xMax)/2 × (font_size/upem)`,
  i.e. after the standard `−advance/2` anchor shift, apply an additional
  `−ink_mid` so the ink — not the advance — sits on the axis. This is exactly
  the `text-anchor=middle` case the spikes README flagged as "not yet exercised
  in spikes"; F2 exercises it. The outlined-path masters get this for free since
  they already carry per-glyph outline bounds; the live-text SVGs need the
  precomputed `x` baked in by the generator.
