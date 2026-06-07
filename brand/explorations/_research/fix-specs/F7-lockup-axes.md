# F7 — Lockups mix two alignment philosophies and sit off-axis

## Root cause

Two distinct, independent defects across the four lockups in `brand/lockups/`.

**Defect A — Foundation-style lockups center their sub-elements on the wrong axis (3 files).**
`rtam-bilingual-foundation.svg`, `rtam-sanskritic-pratishthan.svg`, and
`donation-lockup.svg` all reuse the identical, locked wordmark group
(`RTAM` at `x=80` + `Foundation` at `x=540` + bindu `cx=118`). Empirically
(Chromium + vendored Cinzel TTFs, `document.fonts.ready` awaited), that group's
ink spans **x[80.0 .. 1026.7]**, so its content axis (ink midpoint) is
**(80.0 + 1026.7) / 2 = 553.35 ≈ 553**.

But the divider line (`x1=420 x2=660`, center 540) and the centered sub-line
(`text-anchor="middle" x="540"`) are pinned to **540**. 540 is simultaneously
the viewBox center (1080/2) **and** the `x` start-coordinate of the `Foundation`
text — the original author appears to have grabbed `Foundation`'s left-edge
coordinate as the centering value. The result: the Latin wordmark is
**left-locked** (an asymmetric two-part mark beginning at x=80), while the
divider and Devanagari are **centered on the canvas/Foundation-edge, not on the
mark** — two alignment philosophies in one composition. The sub-elements sit
**13.4px left** of the mark's true content axis. Canvas-centering is not even
meaningful here: the wordmark's own padding is asymmetric (left 80, right 53.3),
so the viewBox center is not a brand axis.

**Defect B — Temple lockup is vertically top-heavy (1 file).**
`rtambhareshvara-mandir-lockup.svg` is horizontally clean (all three elements
share `text-anchor="middle"` at x=640 = viewBox center, and the ink is symmetric
about 640 — this composition's single centered philosophy is correct and is
**kept**). The defect is vertical: measured ink spans **y[90.0 .. 337.0]** in a
380-tall box → top pad **90.0**, bottom pad **43.0** (matches the audit's
T=89.6 / B=43.5). Ink center cy=213.5 sits 23.5px below the box center (190),
so the block reads as floating high with a heavy gap beneath.

**Why Foundation lockups get NO vertical fix (load-bearing scope rule):** their
Latin line is the *locked, shared wordmark group* — its `y=160` is fixed by the
canonical logo (`logos/rtam-wordmark-sacred-RTAM-dot.svg`) and may not move.
Their vertical padding (top 42.7 / bottom 27.3, mildly top-heavy) is therefore a
consequence of the locked mark and is genuinely out of scope. The temple Latin
line is **bespoke `<text>`** (not the shared group), so it is free to move — which
is exactly why only the temple receives a vertical re-balance.

## Files touched   (every file the fix will change)

- `brand/lockups/rtam-bilingual-foundation.svg` — horizontal (Defect A)
- `brand/lockups/rtam-sanskritic-pratishthan.svg` — horizontal (Defect A)
- `brand/lockups/donation-lockup.svg` — horizontal (Defect A)
- `brand/lockups/rtambhareshvara-mandir-lockup.svg` — vertical (Defect B)

(In the target architecture these become emitted outputs; the equivalent edit
lands in `brand/spec/brand.json` lockup parameters consumed by
`brand/tools/generate.py`. The exact pre/post attribute values below are the
contract either way.)

## Exact change   (implementable blind: exact attributes, exact numbers, exact replacement text)

### Foundation-style lockups (3 files) — re-center sub-elements on the mark's content axis (x=553)

Apply the **same** two edits to all three of `rtam-bilingual-foundation.svg`,
`rtam-sanskritic-pratishthan.svg`, `donation-lockup.svg`:

1. **Divider line** — re-center on 553, preserving its 240px width:
   - find: `x1="420" y1="245" x2="660" y2="245"`
   - replace with: `x1="433" y1="245" x2="673" y2="245"`
   - (553 − 120 = 433; 553 + 120 = 673)

2. **Centered sub-line** — change only the `x` of the `text-anchor="middle"` element:
   - `rtam-bilingual-foundation.svg`: `<text x="540" y="335"` → `<text x="553" y="335"` (the `ऋतम् फाउंडेशन` line)
   - `rtam-sanskritic-pratishthan.svg`: `<text x="540" y="335"` → `<text x="553" y="335"` (the `ऋतम् प्रतिष्ठान` line)
   - `donation-lockup.svg`: `<text x="540" y="305"` → `<text x="553" y="305"` (the `CONTRIBUTIONS SUPPORT…` line)

Do **not** touch the wordmark `<g>` (RTAM, Foundation), the bindu `<circle>`,
any `y`, the viewBox, or any width/font attribute.

### Temple lockup (1 file) — equalize top/bottom padding by translating the block up 23.5px

In `rtambhareshvara-mandir-lockup.svg`, subtract **23.5** from every vertical
coordinate (uniform translation preserves all inter-line spacing; only frame
padding changes):

- Latin text: `y="160"` → `y="136.5"`
- Divider line: `y1="225" x2="760" y2="225"` → `y1="201.5" x2="760" y2="201.5"`
- Devanagari text: `y="320"` → `y="296.5"`

Do **not** change any `x`, `text-anchor`, the viewBox (`0 0 1280 380` stays), or
any font attribute. After the shift: top pad 66.5, bottom pad 66.5.

## Parameters resolved   (every number FINAL with one-line rationale)

| Param | Value | Rationale |
|---|---|---|
| Foundation sub-axis target | **x = 553** | Mark content axis = ink midpoint of the locked RTAM+Foundation group, (80.0+1026.7)/2 = 553.35, rounded to 553 (0.35px residual ≪ perception and ≪ the 4px registration tolerance of the fidelity gate). |
| Foundation divider | **x1=433, x2=673** | Keep original 240px width; 553±120. |
| Foundation sub-line x | **553** | `text-anchor="middle"` centers on this; same axis as divider → one philosophy. |
| Foundation shift magnitude | **+13.4px right** (540→553.35) | Pure consequence of the two values above; the visible correction. |
| Temple vertical shift dy | **−23.5** | Ink cy 213.5 → box center 190; equalizes pads to 66.5/66.5. Uniform across all 3 vertical coords. |
| Temple new pads | **66.5 / 66.5** | (top 90.0 + bottom 43.0)/2 each side. |
| Temple horizontal axis | **640 (unchanged)** | Already symmetric on viewBox center; correct single philosophy — kept. |

All values measured empirically with the vendored TTFs via Chromium getBBox /
getExtentOfChar (`brand/tools/_scratch/f7_measure.py`,
`brand/tools/_scratch/f7_geometry.json`).

**Axis is the wordmark-GROUP midpoint, not the per-file ink union.** Per-file
union centers differ because sub-lines have different widths — bilingual union
cx=553.4 but donation union cx=549.9 (its supporting line is wider than the
mark). The target is the same **553** for all three, derived solely from
RTAM+Foundation ink. A re-auditor must compute the axis from the mark, not the
whole-file union.

## Proof   (before/after PNG paths)

Rendered in Chromium with the vendored TTFs via `@font-face` (faithful), guide
lines overlaid: **red** = current sub-axis (540), **green** = target mark axis
(553.4), **blue dashed** = viewBox center.
(`brand/tools/_scratch/f7_proof.py`.)

Foundation lockups (Defect A):
- `brand/explorations/_research/fix-specs/proofs/F7-rtam-bilingual-foundation-before.png`
- `brand/explorations/_research/fix-specs/proofs/F7-rtam-bilingual-foundation-after.png`
- `brand/explorations/_research/fix-specs/proofs/F7-rtam-sanskritic-pratishthan-before.png`
- `brand/explorations/_research/fix-specs/proofs/F7-rtam-sanskritic-pratishthan-after.png`
- `brand/explorations/_research/fix-specs/proofs/F7-donation-lockup-before.png`
- `brand/explorations/_research/fix-specs/proofs/F7-donation-lockup-after.png`

In BEFORE, the red and green guides are visibly separated and the divider +
Devanagari sit on red — left of the mark's center, breaking the wordmark's
rightward optical weight. In AFTER, the divider and sub-line shift right onto
green; the whole stack now hangs from one axis and reads as a single unit.
(Donation's supporting line is near-full-width, so its per-glyph shift is
imperceptible; the visible improvement there is the divider snapping under the
mark's center.)

Temple lockup (Defect B):
- `brand/explorations/_research/fix-specs/proofs/F7-rtambhareshvara-mandir-lockup-before.png`
- `brand/explorations/_research/fix-specs/proofs/F7-rtambhareshvara-mandir-lockup-after.png`

In BEFORE, the two-line block clings to the top of the frame with an obvious
empty band beneath the Devanagari. In AFTER, the block drops so the empty bands
above and below match; the lockup sits centered in its box. Horizontal centering
(green = x=640) is unchanged and correct in both.

## Verification steps   (how US-16 re-audit will confirm the fix)

Re-render each lockup faithfully (Chromium + vendored TTFs, `document.fonts.ready`
+400ms), then assert via getBBox/getExtentOfChar (`f7_measure.py` is the
reference harness):

1. **Foundation lockups (3 files)** — compute the mark axis as
   `(RTAM.bbox.x + Foundation.bbox.right) / 2` (≈ 553, NOT the whole-file union
   cx). Assert:
   - centered sub-line `bbox.cx == 553 ± 1`
   - divider midpoint `(x1 + x2) / 2 == 553 ± 1`
   - sub-line cx **==** divider midpoint (one shared axis)
   - wordmark group, bindu (`cx=118`), and all `y` unchanged.
2. **Temple lockup** — assert ink union `y[66.5 .. 313.5]` (±1), i.e. top pad
   == bottom pad == 66.5 ± 1; horizontal axis still 640; viewBox still
   `0 0 1280 380`.
3. Eyeball the AFTER proofs: no mixed-axis tension in any Foundation lockup; the
   temple block visually centered in its frame.

## Residual risk

- **Provisional axis (Cinzel-dependent):** 553 and dy −23.5 are tied to Cinzel's
  exact glyph widths (RTAM ink 391.4, Foundation right edge 1026.7). A Phase-2
  letterform swap shifts the ink axis; the **rule** survives, the **number** must
  be re-measured from the new mark.
- **Donation supporting line** is near-full-bleed (ink x[73.1 .. 1006.9]); the
  13px shift to 553 is imperceptible per-glyph and is kept solely for
  divider/mark coherence, not because the line itself looked off. Its right edge
  after the shift (~1020) stays inside the mark's right ink edge (1026.7) — no
  clipping, no overflow of the viewBox.
- **Rounding:** 553 vs the measured 553.35 leaves a 0.35px residual — sub-pixel,
  below the fidelity gate's 4px registration tolerance; harmless.
- The temple fix is a uniform translation, so inter-line spacing and the
  divider–text gaps are provably unchanged; the only variable touched is frame
  padding.

## Depends on

- **F8 (temple bindu) — bidirectional coupling, vertical only.** The temple
  lockup currently has **no** bindu (`<circle>`); F8 adds one in the Latin–divider
  gap, under the R of RTAMBHARESHVARA. That bindu falls within the Latin ink's
  vertical extent, so it does **not** change the temple ink union (still
  y[90..337] pre-fix) — F7's vertical centering is robust to F8 and need not be
  re-derived. The only coupling: F8 must place the bindu off F7's **post-shift**
  Latin baseline (y 160 → 136.5). Concretely — whichever lands second applies the
  other's delta: if F7 lands first, F8 computes bindu cy from y=136.5; if F8
  lands first, whoever applies F7 also subtracts 23.5 from the new bindu's cy.
  F7 owns the temple's axes/balance; F8 owns its bindu.
- **Donation lockup ownership:** F7 folds `donation-lockup.svg` under the same
  one-philosophy rule (same composition type, same Defect A) even though the
  audit text named only the two bilingual files. US-16 should confirm no other
  F-finding separately owns `donation-lockup.svg`'s horizontal alignment.

## Durable or provisional

- **Durable (rules):** (1) "In an asymmetric left-locked wordmark composition,
  center all secondary elements — divider, sub-line — on the *wordmark group's
  measured ink axis*, never on the viewBox center or a glyph's start coordinate."
  (2) "Equalize a stacked lockup's top and bottom ink padding by translating the
  movable block; do not reshape the viewBox." (3) The scope rule: locked/shared
  elements (the wordmark group) are immovable; only bespoke elements are
  re-balanced.
- **Provisional (Cinzel-tied instances):** the axis value **553** and the temple
  shift **dy = −23.5** (and derived 433/673, 136.5/201.5/296.5) — re-measure from
  the mark if the letterform changes in Phase 2.
