# F1 — Bindu optically off-center under the wordmark R

## Root cause
The wordmark bindu (the gold dot that is the brand signature) is placed at
`cx=118`, which is **left of the optical center of the Cinzel-500 R**. It is
left of even the R's advance-width center.

The shipped value was chosen as if it were the glyph's geometric/advance center,
but two facts make that wrong for this letter:

1. **The Cinzel R's ink is asymmetric.** Measured from the vendored TTF
   (`brand/fonts/cinzel/cinzel-500.ttf`, upem=1000) at the wordmark metrics
   (text `x=80`, `font-size=120`): the R glyph advance is 700 units (84px), but
   its outline runs `x∈[55..722]` font units. The leg sweeps *past* the advance
   box (right side-bearing is negative, −2.64px). So:
   - advance-width center = **122.0px**
   - ink-bbox center = **126.62px** (TTF outline) / **126.5px** (pixel render — the two agree to 0.1px)
   - ink-mass centroid = **119.7px**
2. The dot must read centered under the *visible body* of the R, not under its
   metric box.

**Correction to the audit finding's numbers (US-16 must use these):** the
finding recorded "advance-width center 119.0". That conflated two values — the
true advance center is **122.0**; **119.7** is the ink centroid. The shipped
`cx=118` is therefore left of the advance center *and* left of the centroid —
the dot is more off-center than the finding stated, biased under the R's left
stem rather than under the glyph's body.

Eye confirmation (see Proof): with the dot under the left stem, the mark reads
unbalanced; moved to the ink-bbox center it sits in the optical gap between the
stem and where the leg lands and reads deliberately centered.

## Files touched
All seven shipped assets that draw the standalone wordmark R with a bindu. Every
one contains the identical text element
`<text x="80" y="160" font-size="120" ... letter-spacing="12">RTAM</text>` with
**no wrapping `transform`** and the identical circle `cx="118" cy="188" r="10"`
(verified — only the `fill` color differs per variant, which is left untouched):

- `brand/logos/rtam-wordmark-black.svg`
- `brand/logos/rtam-wordmark-gold.svg`
- `brand/logos/rtam-wordmark-white.svg`
- `brand/logos/rtam-wordmark-sacred-RTAM-dot.svg`
- `brand/lockups/rtam-sanskritic-pratishthan.svg`
- `brand/lockups/rtam-bilingual-foundation.svg`
- `brand/lockups/donation-lockup.svg`

**Not touched:** `brand/lockups/rtambhareshvara-mandir-lockup.svg` carries no
bindu by design — its "RTAMBHARESHVARA MANDIR" is full running text (fs=72,
`text-anchor=middle`), not the standalone brand R, so no dot is dropped.
Icon `rdot-icon-*` files share this exact root cause but are **out of scope**
for F1 (see Depends on → F4).

## Exact change
In each of the seven files above, change the bindu circle's horizontal center
only — the literal swap, valid identically in all seven because the R is drawn
at the same metrics with no enclosing transform:

```
cx="118"  →  cx="126.5"
```

Leave `cy="188"`, `r="10"`, and `fill="..."` unchanged. Net horizontal move:
**+8.5px** to the right at fs=120 (from advance-center-minus-4 to ink-bbox
center).

(For the future generator, do not hard-code 126.5 — emit it from the rule in
*Parameters resolved*; the literal value above is only for the hand-edit of the
current shipped SVGs.)

## Parameters resolved
- **bindu cx = 126.5** (FINAL). Rationale: ink-bbox center of the Cinzel-500 R
  at the wordmark metrics, where TTF-outline (126.62) and pixel-render (126.5)
  agree to 0.1px and the eye-check (122/124/126.5/128 sheet, ivory+charcoal,
  charcoal+gold) reads 126.5 as centered. *Provisional* (Cinzel-shape-dependent).
- **bindu cy = 188** (FINAL, retained). Rationale: gap from baseline (y=160) to
  dot center = 28px = capHeight/3 (capHeight=84px) = fs·(7/30). Retained from
  shipped, not eye-re-optimized — F1 owns horizontal centering; the vertical
  ratio belongs to F3 (see Depends on). If F3 redefines the baseline-offset
  ratio, cy follows F3.
- **bindu r = 10** (unchanged, out of scope). Observed durable ratio r = fs/12 =
  0.0833·fs. Not a flagged defect; recorded for the generator, not changed here.

**THE RULE (this is the real deliverable — survives a letterform swap):**
> The bindu's horizontal center is the **ink-bbox center of the outlined bearing
> glyph**, computed at build time from the glyph's outline (fontTools
> `BoundsPen` on the shaped glyf path), in the placed text's coordinate frame:
> `cx = text_x + xmin·(fs/upem) ... text_x + xmax·(fs/upem)`, midpoint; for a
> `text-anchor=middle/end` glyph, compute this **after** applying the anchor
> advance shift (−advance/2 or −advance). Letter-spacing does **not** shift the
> first glyph's left edge, so it does not enter the bearing-glyph bbox.
>
> Ink-bbox center is the **build-time default**, not a self-evident optical law:
> it is set by two outline extrema (for the R, the leg-tip on the right), and the
> mass centroid demonstrably read too far left here. The emitted value is
> therefore **provisional and MUST pass the US-10.3 eye-check gate** on any
> letterform change; if a future glyph's extremum pulls the bbox center past
> where the eye agrees, the gate catches it and a per-glyph override is recorded.
>
> Vertical: `cy = baseline + capHeight/3` (durable ratio; F3 owns the constant).
> Radius: `r = fs/12` (observed; F5 owns dot sizing if revisited).

## Proof
- `brand/explorations/_research/fix-specs/proofs/F1-zoom-candidates.png` —
  isolated R zoomed 1.6×, candidates 122/124/126.5/128 on ivory/charcoal and
  charcoal/gold, with guide lines (green=advance-center 122, blue=centroid 119.7,
  red=ink-bbox-center 126.6). The eye should see: at 122/124 the dot hugs under
  the left stem (left-biased); at 126.5 it sits in the optical gap between stem
  and leg (centered); at 128 it begins drifting toward the leg.
- `brand/explorations/_research/fix-specs/proofs/F1-before-after.png` — full
  RTAM wordmark, BEFORE cx=118 vs AFTER cx=126.5, ivory/charcoal and
  charcoal/gold. The eye should see the BEFORE dot tucked under the R's left
  stem (reads off to the left), and the AFTER dot centered under the R's body —
  the correction holds on both surfaces and both ink colors.
- `brand/explorations/_research/fix-specs/proofs/F1-candidate-sheet.png` — the
  full 4-candidate × 4-surface/ink matrix used to settle the number.

Generators: `brand/tools/_scratch/f1_zoom_R.py`, `f1_before_after.py`,
`f1_candidate_sheet.py` (all render Cinzel via local TTF @font-face file://,
Chromium + `document.fonts.ready` + 400ms settle).

## Verification steps
US-16 re-audit confirms the fix by:
1. Parsing all seven files; assert every bindu `<circle cx>` = `126.5` (was 118)
   with `cy=188 r=10` unchanged.
2. Recompute the R's **ink-bbox center** by the rule's own method and assert the
   new `cx` matches it to |Δ| ≤ 0.5px (expected center ≈ 126.6 at these metrics).
   Use either `ink_analysis.py`'s `bbox_center_x` (update its hard-coded
   `118`→`126.5` so the printed offset goes to ≈0), or `BoundsPen` on the shaped
   Cinzel-500 R (`text_x + xmin·fs/upem … text_x + xmax·fs/upem`, midpoint) —
   the two were proven to agree to 0.1px.
   **Do NOT gauge F1 with `analyze_geometry.py`:** its bindu check compares
   against the glyph's *advance/cell center* (~122, line 64 `off cell-center` /
   `off glyph-center`), which is the very center F1 rejects. Run against the
   fixed asset it will report the dot ~+4.5px "off glyph-center" — that is
   expected and correct, not a regression; the tool encodes the bug being fixed.
3. Eye-check gate (US-10.3): the dot reads centered under the R on ivory and
   charcoal, charcoal-ink and gold-ink. Use `F1-before-after.png` as the
   reference for "centered".
4. Discard the stale "advance-center 119.0" figure from the finding; the correct
   reference values are advance-center 122.0, centroid 119.7, ink-bbox 126.5.

## Residual risk
- **Provisional on Cinzel.** 126.5 is tied to this R's leg sweep. A Phase-2
  letterform replacement invalidates the *number*; the *rule* (ink-bbox center +
  eye-gate) regenerates it. Marked provisional accordingly.
- **Single-glyph bbox sensitivity.** Because bbox-center depends on one extremum
  (the leg tip), a future R with a longer/shorter leg moves the dot; the US-10.3
  eye-gate is the backstop and is explicitly part of the rule.
- **cy coupling.** cy=188 is retained, not eye-re-tested vertically. If F3
  changes the baseline-offset ratio, cy must be recomputed; flagged below.

## Depends on
- **F3** (vertical ratio system) — F1 assumes gap = capHeight/3 = 28px (cy=188).
  If F3 redefines the baseline-offset ratio, cy follows F3. Horizontal (cx=126.5)
  is independent of F3.
- **F4** (icon/monogram bindu) — the `rdot-icon-*` files place their dot at the
  R's **advance**-center (cx=128) under a `text-anchor=middle` glyph: the
  identical "advance-center instead of ink-bbox-center" defect, just anchored.
  F4 owns those; F1's RULE explicitly covers the anchored case (compute bbox
  center *after* the anchor advance shift) so F4 can reuse it. Coordinate the
  shared rule with F4; do not let F1 and F4 diverge on it.

## Durable or provisional
- **Durable:** the RULE (bindu cx = ink-bbox center of the outlined bearing
  glyph, computed at build time, anchor-aware, gated by the US-10.3 eye-check);
  the vertical relation cy = baseline + capHeight/3; the radius relation r = fs/12.
- **Provisional:** the concrete numbers cx=126.5 / cy=188 / r=10 and the +8.5px
  delta — all tied to Cinzel-500's specific letterforms and the fs=120 wordmark
  metrics. Regenerated from the durable rule on any letterform change.
