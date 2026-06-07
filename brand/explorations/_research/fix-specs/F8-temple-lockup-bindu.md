# F8 — Temple lockup lacks the brand signature entirely

## Root cause
`brand/lockups/rtambhareshvara-mandir-lockup.svg` is the only place the temple's
own name appears as the primary asset, yet its Latin line
(`RTAMBHARESHVARA MANDIR`) carries no bindu. Every other Latin-bearing asset in
the system draws the gold under-dot beneath the initial R as an absolute SVG
`<circle>` (the brand signature, per F1): the primary wordmark
(`logos/rtam-wordmark-sacred-RTAM-dot.svg`) and all three sacred lockups
(`lockups/rtam-bilingual-foundation.svg`, `rtam-sanskritic-pratishthan.svg`,
`donation-lockup.svg`) each ship `<circle cx="118" cy="188" r="10" fill="#C8A15A"/>`.
The temple lockup was authored at a different scale (font-size 72,
center-anchored at x=640 in a 1280-wide viewBox) and the bindu was simply never
added. Result: the foundation's most sacred named asset is unmarked. The fix is
purely additive — insert one `<circle>` placed by the F1 rule and scaled by the
F3 ratios to this composition's font size. The Latin line is also missing the
Ṛ diacritic, but the brand's established convention is to carry the sacred mark
as the drawn bindu (not a font diacritic — Cinzel has no U+1E5A/U+0323 glyph,
per the spikes README), so adding the bindu is the complete and correct signature.

## Files touched
- `brand/lockups/rtambhareshvara-mandir-lockup.svg` — add one `<circle>` element.

(No other file changes. The Devanagari line needs no change — see below.)

## Exact change
Insert exactly this line immediately after the closing `</text>` of the Latin
line (line 7) and before the `<line ...>` divider (line 8):

```xml
  <circle cx="60.3" cy="176.8" r="6" fill="#C8A15A"/>
```

Resulting fragment (lines 7–8 of the file become three lines):

```xml
  <text x="640" y="160" font-family="Cinzel, Marcellus, 'Trajan Pro', serif" font-size="72" font-weight="500" letter-spacing="6" text-anchor="middle" fill="#1A1A1A">RTAMBHARESHVARA MANDIR</text>
  <circle cx="60.3" cy="176.8" r="6" fill="#C8A15A"/>
  <line x1="520" y1="225" x2="760" y2="225" stroke="#C8A15A" stroke-width="1.5"/>
```

No other attribute, element, or value changes. The Latin `<text>`, the gold
`<line>`, and the Devanagari `<text>` are untouched.

## Parameters resolved

The F1 rule is: place the bindu at a fixed fraction of the initial R's advance
measured from the R's pen origin, dropped below the baseline by a fixed fraction
of font-size, with radius a fixed fraction of font-size, filled brand gold. The
canonical fractions are read off the shipped primary wordmark (fs=120, R pen
origin x=80, R advance 84.0px from `hmtx`, bindu cx=118 cy=188 r=10, baseline
y=160). This composition has fs=72, R pen origin x=37.5, R advance 50.4px,
baseline y=160.

| Param | Value | Rationale |
|---|---|---|
| `cx` | `60.3` | F1 rule `cx = R_pen_origin + k·R_advance`, with the canonical fraction `k = (118−80)/84 = 0.4524` from the shipped wordmark. Here `37.5 + 0.4524·50.4 = 60.3`. R pen origin 37.5 = `640 − textLength/2` (textLength 1205), confirmed independently by `getExtentOfChar(0).x` under BOTH the local TTF and the live `@import` Cinzel; R advance 50.4 = `504/1000·72` exact from `hmtx`. **`k` is owned by F1** (see Depends on). |
| `cy` | `176.8` | Baseline (160) + drop. Drop ratio is canonical `28/120 = 0.23333` (shipped 188−160=28 at fs=120). `160 + 0.23333·72 = 176.8`. |
| `r` | `6` | Radius ratio `r/fs = 10/120 = 1/12` exact. `72/12 = 6.0`. |
| `fill` | `#C8A15A` | Brand gold; identical hex to every shipped bindu and to this file's existing `<line>` stroke. |

No value is TBD. Every number is final under the current (status-quo) F1
fraction; the generative formula above lets the value re-derive automatically if
F1 re-resolves `k`.

Sanity checks (no clash with existing geometry): dot top = 176.8 − 6 = 170.8,
below the baseline (160) and the R cap region; dot bottom = 176.8 + 6 = 182.8,
clear of the gold rule at y=225 by 42px. Dot center cx=60.3 sits within the
1280 viewBox far left of the centered rule (x 520–760), so no overlap.

## Proof
- Before: `brand/explorations/_research/fix-specs/proofs/F8-before.png`
- After:  `brand/explorations/_research/fix-specs/proofs/F8-after.png`

Both rendered faithfully in Chromium with `document.fonts.ready` awaited (+400ms
settle) on the ivory ground (#F7F3E9), the same path the audit uses; cairosvg is
not used because this is a live-text SVG. In the BEFORE image the Latin line has
no mark of any kind. In the AFTER image a single small gold dot appears centered
under the vertical stem of the initial R, sitting just below the baseline and
well clear of the gold divider rule beneath the line — visually identical in
proportion and color to the bindu on the primary wordmark and the other lockups.
The eye should read the temple name as now carrying the same sacred signature as
the rest of the system; the dot should look deliberate and stem-aligned, not
floating or touching the rule.

## Verification steps
US-16 re-audit confirms the fix by:
1. Asserting `rtambhareshvara-mandir-lockup.svg` now contains exactly one
   `<circle>` with `cx="60.3" cy="176.8" r="6" fill="#C8A15A"`.
2. Faithful Chromium render (fonts awaited): the gold bindu is present under the
   initial R, dot bottom (182.8) above the rule (225), dot fill matches the other
   bindú assets' `#C8A15A`.
3. Geometry re-check that the live `@import` Cinzel still yields R pen origin
   x = 37.5 (textLength 1205) for this exact string/fs/letter-spacing/anchor;
   if Cinzel's metrics ever shift, cx re-derives from `37.5 + k·50.4`. (Already
   verified once here: local TTF and `@import` agree to the decimal.)
4. Cross-asset consistency: the bindu's fraction-of-advance and drop/radius
   ratios match the shipped wordmark's (k=0.4524, drop/fs=0.2333, r/fs=1/12),
   so the temple lockup is no longer the outlier flagged by this finding.

## Residual risk
- Low. The change is one additive element; nothing existing is touched, so no
  caller, render, or other asset can regress. Undo = delete the one line.
- `cx=60.3` depends on Cinzel's R advance (50.4) and the center-anchor reflow of
  this specific string. If F1 re-resolves the canonical bindu fraction `k`
  (bindu_abc.py is actively weighing cx=118 vs 123 vs 126.5 for the wordmark),
  this lockup must re-derive with the SAME `k` via the formula above — do not
  leave 60.3 frozen while the wordmark moves.
- Vertical/optical rebalancing of the whole lockup (the Latin line currently
  sits high in the 380-tall viewBox) is **out of scope here and owned by F7**;
  F8 only adds the missing mark at the current composition. If F7 moves the
  Latin baseline, cy must move with it (cy = new_baseline + 0.2333·72) — flag
  the coupling, do not pre-empt F7.

## Depends on
- **F1** — owns the canonical bindu-placement rule and the fraction `k`
  (=0.4524 under status quo) plus the drop and radius ratios. F8 consumes F1's
  resolved values; if F1 changes them, F8's three numbers re-derive from the
  formulas, not from the literals.
- **F7** — owns vertical rebalancing of this lockup. If F7 changes the Latin
  baseline y (currently 160), F8's `cy` must track it. No ordering requirement
  beyond keeping the two consistent at integration time.

## Durable or provisional
- **Durable:** the rule itself and its ratios — `cx = R_pen_origin + k·R_advance`,
  drop/fs = 0.2333, r/fs = 1/12, fill = brand gold — and the fact that the temple
  lockup must carry the bindu like every other Latin asset. These survive a
  Phase-2 letterform change.
- **Provisional:** the concrete numbers `cx=60.3` and `k=0.4524`. Both are tied
  to Cinzel's specific R outline (its optical/advance center) and to this
  string's center-anchored reflow; a Phase-2 letterform swap changes the R
  advance and likely the optical fraction, so cx (and possibly k) must be
  re-measured then. `cy=176.8` is provisional only insofar as it tracks the
  baseline (durable ratio applied to a baseline F7 may move); `r=6` is durable
  (pure font-size ratio).
