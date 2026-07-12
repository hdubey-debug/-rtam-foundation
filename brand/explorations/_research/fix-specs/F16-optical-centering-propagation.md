# F16 — Optical centering propagation (P0.3)

**Status: APPLIED (2026-07). Proof: `spikes/center_audit.py` before/after tables below; eye-checked on faithful renders from `dist/outlined/`.**

The 2026-07 audit measured every asset's **composite ink bbox** (letters + bindu + rules, the F8 method made repeatable) against its viewBox center in Chromium with vendored fonts. Four assets sat measurably low; they are recentered by shifting all content (baseline, bindu, rule, support line) as one block, preserving every internal relationship. The bindu grammar (`cy = baseline + fs·0.233`) is re-baked against the new baselines.

## Method

`brand/explorations/_research/spikes/center_audit.py` — emits each asset's livetext SVG via brandlib, swaps `@import` for `file://` `@font-face` (parity.faithful; bare @import banned in proofs), renders in Chromium at device_scale_factor 2, thresholds ink against the render ground, reports bbox-center offset (dx/dy, viewBox units; +dy = ink sits low) and the four margins. Run it any time; it is the standing regression check for composition balance.

## Fixed (before → after)

| asset | dy before | shift applied | dy after | margins T/B after |
|---|---|---|---|---|
| wordmark-latin (all 6 outputs) | +15.5 | up 15.5 (y 160→144.5, bindu cy 188→172.5) | +0.0 | 58.0 / 58.0 |
| lockup-sanskritic-pratishthan | +22.8 | up 23 (y 137, cy 165, rule 222, deva 312) | −0.2 | 50.5 / 51.0 |
| lockup-bilingual-foundation | +22.8 | up 23 (same block) | −0.2 | 50.5 / 51.0 |
| lockup-donation | +9.2 | up 9 (y 151, cy 179, rule 236, support 296) | +0.2 | 64.5 / 64.0 |
| devanagari-ri-icon (3 outputs) | +5.8 | up 6 (y 196→190) | −0.2 | 60.0 / 60.5 |

## Measured and deliberately NOT changed

- **rdot-icon**: the audit's earlier "8.5u left (margins 45L/61.5R)" claim does **not** reproduce at HEAD — composite measures dx −0.2, margins 57.5/58.0. Superseded; no edit.
- **favicon** (+0.5u): calibrated for the 16px pixel grid (F14); sub-pixel at target size.
- **temple-wordmark-diacritic** (−3.8) / **temple-wordmark-devanagari** (−3.0): the "high" ink is diacritic/matra ink above the cap line; optical centering conventionally rides the letter body, not floating diacritics. Their bodies align with temple-wordmark-latin (−0.2), which stays the reference.
- **wordmark-devanagari-pratishthan / -faundeshan** (dx −253 / −236.5): the 1080-wide box is sized for the *Latin* wordmark; the Devanagari content spans only ~420u, leaving a 550–583u right void. Centering inside a wrong-size box would break left-aligned Latin↔Devanagari swaps; the real fix is script size/box parity — **Phase 2 `exp/letterform` scope**, recorded here so it isn't lost.

## Rules touched

- brand.json is the only edit surface; `build.sh --write` regenerated all 26 live sources + 25 outlined masters; parity gates PASS (coord-parity 0, r-indep ≤ 41px blob, drift ≤ 1.5px).
- `changed: true` flags were set for the write and removed after regeneration (coord-parity binding again).
