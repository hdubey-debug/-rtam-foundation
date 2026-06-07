# F6 — Wordmark micro-typography: asymmetric padding and a two-object read

## Root cause
The wordmark composition is `RTAM` (Cinzel 500, fs 120, ls 12) at `x=80` plus
`Foundation` (Cinzel 400, fs 62, ls 8) at `x=540`, inside a `0 0 1080 240`
viewBox, with the bindu at `cx=118`. Two independent defects fall out of those
fixed numbers:

1. **Asymmetric optical margins.** With `R` pinned at `x=80`, the rendered ink
   sits left-of-centre. Pixel-truth (Chromium @3×, ink = dark columns on ivory):
   left margin ≈ **92px**, right margin ≈ **128px**, and the composite ink-centre
   lands at **x≈522**, not the viewBox centre 540. The mark visibly leans left.

2. **A two-object read.** The RTAM→Foundation gap is **≈118px of empty ink**
   (RTAM ink ends ≈x427, Foundation ink starts ≈x546). Combined with the abrupt
   120→62 size step, the eye parses two detached words rather than one mark.
   (The audit's "≈69" measured advance-to-ink including RTAM's trailing 12u
   letter-spacing; the honest ink-to-ink gulf is larger.)

Root cause of both: the layout was authored by typing in `x` attributes by eye,
never by composing the block and centring it. RTAM's `x=80` is an arbitrary
left inset, not a derived position; nothing pins the composite to viewBox centre.

A measurement note that matters for the fix: HarfBuzz glyf-bbox math and
Chromium's `getBBox`/`getExtentOfChar` both **diverged** from what actually
rasterises (the DOM extent APIs return advance-based boxes that count
side-bearings as "ink"; HB glyf bounds disagreed by 31–65px across the line —
larger than the spikes' ≤3px HB-vs-Chromium drift, so the cause is unconfirmed
and irrelevant). All numbers below are taken from **pixel-truth** renders — the
only authority for what the eye sees — reconciled across SCALE 2 and 3.

## Files touched
Every shipped asset inlines the wordmark composition verbatim (there is no
`<use>` / shared symbol — this duplication is itself the motivation for the
US-13 generator). The fix is **uniform** across all 8: hold viewBox `1080`,
re-centre the block's ink on x=540. This keeps logos and lockups identical
(brand-book.md:117 — "lockups inherit their wordmark's clear-space" — so they
must share the same framing), changes no aspect ratio, and edits no docs.

Change the two `<text>` `x` attributes in all 8, and the bindu `<circle cx>` in
the 7 that carry a bindu:

- `brand/logos/rtam-wordmark-gold.svg`            (text ×2 + circle cx)
- `brand/logos/rtam-wordmark-black.svg`           (text ×2 + circle cx)
- `brand/logos/rtam-wordmark-white.svg`           (text ×2 + circle cx)
- `brand/logos/rtam-wordmark-sacred-RTAM-dot.svg` (text ×2 + circle cx)
- `brand/logos/rtam-wordmark-public-RTAM.svg`     (text ×2 **only — no bindu circle in this variant**)
- `brand/lockups/rtam-bilingual-foundation.svg`   (text ×2 + circle cx; divider & Devanagari unchanged)
- `brand/lockups/rtam-sanskritic-pratishthan.svg` (text ×2 + circle cx; divider & Devanagari unchanged)
- `brand/lockups/donation-lockup.svg`             (text ×2 + circle cx; divider & supporting line unchanged)

No doc edits: `brand-book.md:113` / `usage-rules.md:68` say "1080×240 canonical"
— still correct. (Their separate "≈120 viewBox units = cap-height" wording is a
conflation bug, but out of F6 scope — see Residual risk.)

In the target architecture (`brand/spec/brand.json` + `brand/tools/generate.py`)
these become a single wordmark block definition emitted into every asset; the
numbers below are the values that block must encode.

Out of this fix's write-scope but carrying the same inlined defect (they will be
re-emitted when the generator regenerates previews, **not** hand-edited here):
`brand/previews/wordmark-specimen.html`, `brand/previews/index.html`,
`brand/previews/lockups-specimen.html`, and the mockups
`certificate.html`, `letterhead.html`, `website-header.html`,
`youtube-banner.html`, `donation-receipt.html`, `donation-poster.html`.
Documentation copy in `brand/guidelines/brand-book.md` and
`brand/guidelines/usage-rules.md` describes the clear-space rule but encodes no
wordmark x/gap, so it needs no change for F6 (see Residual risk re: its separate
"≈120px" wording bug).

## Exact change
Hold **viewBox `0 0 1080 240` (logos) / `1080×380`/`1080×360` (lockups),
font-sizes 120/62, letter-spacing 12/8, fills, and `y=160` baseline all
UNCHANGED.** Only the two `x` attributes and the bindu `cx` move. The block is
re-derived as one composition and centred on x=540.

Replace, in every file in "Files touched":

    <text x="80"  ... >RTAM</text>        ->  <text x="134" ... >RTAM</text>
    <text x="540" ... >Foundation</text>   ->  <text x="523" ... >Foundation</text>

(only the `x` value changes; every other attribute on each line stays byte-identical)

And in the 7 bindu-bearing files:

    <circle cx="118" ... />                ->  <circle cx="172" ... />

`rtam-wordmark-public-RTAM.svg` has **no** `<circle>` — apply only the two text
edits there.

The bindu offset used here (`cx = R_x + 38`, preserving the *current* R-relative
offset 118−80) is a **placeholder that keeps the bindu under R**. The exact `cx`
is owned by the bindu-centring finding's rule, not this one — see "Depends on".
After R moves to 134, that rule must be re-evaluated; 172 is correct only if the
bindu rule is "current offset, translated with R."

Lockup internals are deliberately untouched: the gold divider (`x1=420 x2=660`,
centre 540), the centred Devanagari (`text-anchor=middle x=540`), and the
donation supporting line (`text-anchor=middle x=540`) already anchor on viewBox
centre. Moving the wordmark ink-centre to 540 makes the wordmark agree with them
for the first time, with **zero change** to those elements — lockup coherence
improves for free.

## Parameters resolved
One uniform composition, all 8 files. Pixel offsets at x=0 (Chromium ink):
RTAM ink [11.67, 347.33], Foundation ink [6.00, 411.67]; Cinzel cap-height @fs120
= 84 (= the brand's clear-space unit); gap = 48.

| Parameter | FINAL value | Rationale |
|---|---|---|
| RTAM `x` (`R_x`) | **134** | Derived, not chosen: solve `R_x+F_x = 1080 − rtamInkL₀ − foundInkR₀` (ink-centre=540) and `F_x−R_x = gap − foundInkL₀ + rtamInkR₀` (gap=48) → 133.7 → 134. |
| Foundation `x` (`F_x`) | **523** | Same 2×2 solve → 523.0. |
| bindu `cx` | **172** (provisional, DEFERRED) | `R_x + 38`, preserving the current R-relative bindu offset. Final value owned by the bindu-centring finding once R moves. |
| RTAM letter-spacing | **12 (unchanged)** | The gap, not RTAM tracking, drives the two-object read (rendered 12/10/8: tightening RTAM widens the ink gulf and erodes Cinzel's titling air). Keeping 12 also minimises the diff. |
| Foundation letter-spacing | **8 (unchanged)** | Not implicated; changing it re-opens the solve for no benefit. |
| RTAM→Foundation gap | **≈48px** (provisional) | Chosen by eye from a 44/48/52 sweep (`F6-gap-tuning.png`): 48 reads as one locked unit with clear air between M and F (no near-collision at 44, no incipient re-split at 52). Final rounded placement measures 47.7px. |
| viewBox | **`0 0 1080 240` (unchanged)** | 1080 is the shared module across logos *and* lockups; brand-book.md:117 makes lockups inherit the wordmark's clear-space, so they must share framing. 1080 also bakes in the documented clear-space (margins land at 145 > cap-height 84). Shrinking it would under-spec clear-space (a 873 crop gives 42px margins = half the documented clear-space) and force aspect/doc/divergence churn. Reject. |
| Composite ink-centre | **540 (= viewBox centre)** | DURABLE rule. Measured 540.2 at the rounded x's. |
| Symmetric margins | **≈145.5px each** | A *consequence* of centring the block in the canonical 1080 frame, and a *feature*: 145 ≥ the documented clear-space (cap-height of R), satisfied on **both** sides — unlike today's L=92 (below the docs' ≈120). Measured 145.7 / 145.3 (symmetric within 0.4px). |

## Proof
- `proofs/F6-wordmark-candidates.png` — Current vs Option B (R@80, Foundation
  moved for symmetric margins) vs Option C (centred block) at ls 12 and 10.
- `proofs/F6-final-decision.png` — Current vs **B′** (R@80, symmetric margins)
  vs **C** (centred, gap≈44), each with the x=540 centre guide. The eye should
  see: Current leans left; **B′ makes margins symmetric but blows the gap out to
  155px — strictly worse for the two-object read**; **C binds RTAM+Foundation
  into one unit** with symmetric margins. This image is the load-bearing
  rejection of "just move Foundation" and the case for centring the block.
- `proofs/F6-gap-tuning.png` — Option C at gap 44/48/52. All read as one object;
  48 is the chosen balance (air between M and F without re-splitting).
- `proofs/F6-before-after.png` — final values (R_x=134, F_x=523, cx=172) on the
  wordmark **and** the bilingual lockup. The eye should see: the after-wordmark
  sits centred and reads as one mark; in the **lockup before** the wordmark
  floats left of the centred gold divider + Devanagari, whereas in the **lockup
  after** the wordmark ink-centre lines up over the divider and the Devanagari
  with **no change to either** — confirming the same uniform composition serves
  both logos and lockups and improves lockup coherence for free.
- `proofs/F6-viewbox-logo-vs-lockup.png` — the framing exploration that was
  *rejected*: a tight 873×240 crop (margins 42 = cap-height/2) vs the chosen
  1080 framing (margins ≈145). Retained as the record of why 873 was dropped: 42
  is **half** the brand's documented clear-space (cap-height of R), so the crop
  is under-spec; the 1080 framing's 145px margin is the clear-space doing its job.

## Verification steps (US-16 re-audit)
1. Render each of the 8 files faithfully (Playwright Chromium, `document.fonts.ready`
   + 400ms settle) on ivory at ≥2× and binarise to ink columns (dark < 128).
2. Assert composite ink-centre `(inkL + inkR)/2 = 540 ± 3px` (was ≈522).
3. Assert `|leftMargin − rightMargin| ≤ 3px` (was ≈36px asymmetric), and each
   margin `≥ 84px` (≥ cap-height of R = the documented clear-space; was L=92 /
   R=128, i.e. left was below the docs' ≈120).
4. Assert RTAM→Foundation ink-to-ink gap `= 48 ± 6px` (was ≈118px), and that it
   is a single connected empty band (no glyph collision between M and F).
5. Assert all 8 files keep their original viewBox (logos `1080×240`, lockups
   `1080×{380,360}`) — no viewBox edits.
6. For the three lockups, assert the wordmark ink-centre equals the divider
   centre (530–550 band) and that divider `x1/x2` and the Devanagari/supporting
   `text-anchor=middle x` are still exactly `540` (untouched).
7. Confirm `public-RTAM` still has no `<circle>`; confirm the other 7 bindu
   `cx` equals whatever the bindu-centring finding resolves (≈172 if that finding
   keeps the current R-relative offset).

## Residual risk
- **The ~145px symmetric margin "looks loose."** It is intentional: 145 ≥ the
  brand's documented clear-space (cap-height of R), satisfied on both sides. A
  reviewer expecting a tighter logotype crop may push back; the counter is
  brand-book.md:113/117 (clear-space = cap-height of R; lockups inherit it). The
  rejected 873/42 crop (`F6-viewbox-logo-vs-lockup.png`) is *under*-spec on that
  rule, so the loose-but-compliant framing is the correct trade. A future
  clear-space-driven crop, if ever wanted, should use margins = cap-height (84)
  → viewBox ≈958, not cap-height/2.
- **Everything is Cinzel-specific (provisional).** A Phase-2 letterform swap
  changes every ink offset; re-run the pixel solve. The *rules* (one centred
  block, ink-centre = viewBox centre, margins ≥ clear-space, gap binds to one
  object) survive.
- **The bindu `cx` is not independently owned here.** If the bindu-centring
  finding redefines the offset (e.g. true R-ink-centre 126.6 vs the current 118),
  `cx` ≠ 172. This spec defers it rather than forking a second bindu rule.
  Coordinate the two before applying.
- **Docs wording bug (out of scope).** `brand-book.md:113` / `usage-rules.md:68`
  say clear-space "≈120 viewBox units = cap-height of R" — that conflates em
  (120) with cap-height (Cinzel cap = 84). F6 does **not** touch this copy (the
  "1080×240 canonical" part is correct and unchanged); flag the 120-vs-84 bug for
  the clear-space/docs finding.
- **9 inlined preview/mockup copies will drift** until the generator regenerates
  them; they are not hand-edited by this fix. If previews ship before the
  generator lands, they show the old (left-leaning) wordmark.

## Depends on
- **Bindu-centring finding** (the `cx` value, last commit "center bindu under R")
  — F6 moves R, so that finding must supply the final `cx`; 68 (logo) and 172
  (lockup) are tracking placeholders preserving the current R-relative offset.
- **US-13 generator / `brand.json`** — the durable home for the single wordmark
  block; F6 supplies the numbers it must encode.
- Otherwise: none. The change is reversible (revert three attribute values per
  file).

## Durable or provisional
- **DURABLE (rules, survive a Cinzel swap):**
  - Compose RTAM + gap + Foundation as **one block**; never author `x` by eye.
  - Centre the block's **ink** on the viewBox centre (x=540). Left margin = right
    margin (symmetric optical margins), measured from **ink**, never from advance
    (trailing letter-spacing is phantom space).
  - Symmetric margins must be **≥ the clear-space unit** (cap-height of R). In the
    canonical 1080 frame they land well above it — the frame bakes the clear-space
    in; this is a feature, not slack.
  - The RTAM→Foundation gap is a single tuned word-break value (≈0.8× the
    subordinate font-size for Cinzel), set so the two words read as one mark; it
    is driven by the gap, not by RTAM's internal tracking.
  - One uniform composition serves logos and lockups (brand-book.md:117 — lockups
    inherit the wordmark's clear-space); keep viewBox 1080.
- **PROVISIONAL (Cinzel pixel instantiations, re-derive on letterform change):**
  R_x=134, F_x=523, bindu cx≈172, gap≈48px, margins≈145.5px, ink offsets
  (RTAM [11.67,347.33], Foundation [6.00,411.67] at x=0).
