# F3 — Canonical bindu ratios

## Root cause

There is no canonical bindu system. Each bindu-bearing asset was sized and
positioned by eye against its own viewBox, so the gold dot — the brand
signature the brand book calls *"exact in size and position across every
reproduction surface"* (`brand/guidelines/brand-book.md`) — drifts ~30% in
both radius and vertical placement across the kit.

Measured from the shipped SVGs (faithful values, not estimates):

| asset | fs | baseline y | r | **r / fs** | gap (cy−base) | gap / fs | **gap / capH** |
|---|---|---|---|---|---|---|---|
| wordmark (4) | 120 | 160 | 10 | **0.0833** | 28 | 0.233 | **0.3333** |
| rdot plain (3) | 200 | 184 | 14 | **0.0700** | 34 | 0.170 | **0.2429** |
| rdot circle (2) | 170 | 178 | 11 | **0.0647** | 29 | 0.171 | **0.2437** |
| favicon (1) | 26 | 22 | 2.2 | **0.0846** | 5.5 | 0.212 | **0.3022** |

(capH = Cinzel cap-height = 0.70·fs, weight-invariant per **F4**.)

Two independent drifts are visible:

1. **Radius drift.** r/fs ranges 0.065 → 0.085. The wordmark (0.0833 = fs/12)
   and favicon (0.0846) agree; **the two icon groups are the outliers**, dipping
   to 0.065–0.070 — their dots read timid next to the wordmark's.
2. **Gap drift, two regimes.** The wordmark gap is *exactly* capH/3 (0.3333).
   The two icon groups cluster at a *tighter* ~0.243·capH — a genuinely
   different vertical relationship, not noise. The favicon sits between.

Proof `F3-isolated-across-scales.png` (row A) shows the consequence directly:
normalize all four R's to one cap-height and the shipped dots visibly differ in
size and gap — they are not "the same mark."

**Note on the audit's starting point.** The audit proposed `r = 0.08·fs`,
`gap = 0.15·fs`. The radius target is right (0.08 ≈ fs/12 = 0.0833 rounded —
adopted). The **gap = 0.15·fs is wrong and is discarded**: it matches *no*
shipped asset (the tightest real value is the icons at 0.17·fs; the primary
mark is 0.233·fs). It was an unanchored guess. The reference is the wordmark's
**capH/3 = 0.233·fs**, which F1 already retained as cy=188.

## Files touched

Thirteen shipped SVGs carry a bindu (gold/ink dot under the Latin R). The
Devanagari ऋ icons carry **no bindu** by design (no-dot invariant, §3.3 /
**F5**) and are excluded. The public wordmark variant
`rtam-wordmark-public-RTAM.svg` has **no circle** (public dropped-dot variant)
and is excluded.

F3 resolves the canonical ratios for all thirteen. **Net geometry edits F3
authorizes = the 5 icon files only**; the 7 wordmark-geometry files already
emit the canonical ratio (F3 blesses them, F1 owns their cx) and the favicon is
F14's exception.

**F3 changes geometry (5 files):**
1. `brand/icons/rtam-rdot-icon-black.svg` — bindu r 14→16.67, cy 218→230.67
2. `brand/icons/rtam-rdot-icon-gold.svg` — bindu r 14→16.67, cy 218→230.67
3. `brand/icons/rtam-rdot-icon-white.svg` — bindu r 14→16.67, cy 218→230.67
4. `brand/icons/rtam-rdot-icon-circle-gold.svg` — bindu r 11→14.17, cy 207→217.67
5. `brand/icons/rtam-rdot-icon-circle-charcoal.svg` — bindu r 11→14.17, cy 207→217.67

**F3 blesses unchanged (already canonical; cx owned by F1, value unchanged):**
6–9. `brand/logos/rtam-wordmark-{black,gold,white,sacred-RTAM-dot}.svg`
10–12. `brand/lockups/{rtam-sanskritic-pratishthan,rtam-bilingual-foundation,donation-lockup}.svg`
(all: r=10, cy=188 — already = fs/12 and capH/3. F1 separately moves cx 118→126.5.)

**F3 defers to F14 (small-size exception):**
13. `brand/icons/favicon.svg` — r/cy owned by **F14** (r=2.86, cy=27.2); F3
    records it as the small-size exception row, does not re-specify it.

Target architecture: these ratios become outputs of `brand/spec/brand.json` +
`brand/tools/generate.py` (US-13), emitted from the rule below — not
hand-edited constants.

## Exact change

In each of the 5 icon files, change only the bindu `<circle>` `r` and `cy`
(`cx` and `fill` unchanged). 2-decimal rounding (matching F2's convention).

**Plain rdot-icons** (`-black`, `-gold`, `-white`), fs=200 baseline=184:
```
- <circle cx="128" cy="218" r="14" fill="..."/>
+ <circle cx="128" cy="230.67" r="16.67" fill="..."/>
```
**Circle rdot-icons** (`-circle-gold`, `-circle-charcoal`), fs=170 baseline=178:
```
- <circle cx="128" cy="207" r="11" fill="..."/>
+ <circle cx="128" cy="217.67" r="14.17" fill="..."/>
```
`cx=128` is **unchanged and correct** — but only because **F2** moves the icon
R's *ink* onto x=128 (the R `<text>` x is corrected per F2). With the R ink on
128, dot-cx=128 is dot-under-the-R's-ink-center, the F1 rule for the anchored
case. F3 depends on F2 for this.

(For the generator, do not hard-code these px — emit them from the rule in
*Parameters resolved*; the literals above are for the hand-edit of the current
SVGs.)

## Parameters resolved

Every number FINAL.

- **Canonical radius: r = fs/12 (= 0.0833·fs = capH/8.4).** Rationale: matches
  the primary mark exactly (r=10 at fs=120), matches the favicon (0.0846), is
  the clean fraction the audit's 0.08 rounds from, and F1 already recorded it.
  The two icon groups (0.065–0.070) are the **drift** and are corrected *up* to
  it: plain r 14→16.67, circle r 11→14.17. *Provisional on Cinzel cap metrics.*

- **Canonical gap: baseline→dot-center = capH/3 (= 0.3333·capH = 0.2333·fs),
  so cy = baseline + capH/3 = baseline + 0.2333·fs.** Rationale below.
  - This is the wordmark's existing relationship (cy=188 at fs=120) — so
    **F1's retained cy=188 stands unchanged; F3 confirms it.** The audit's
    0.15·fs is rejected (matches no asset; see Root cause).
  - capH is the **durable, weight-invariant** letterform metric (F4 proved
    Cinzel cap-height is identical at 500/600/700), so anchoring the gap to capH
    (not fs directly) is the face-independent form.
  - **One ratio, validated against the binding cell-fit constraint.** The icons'
    shipped tighter gap (~0.243·capH) was the candidate "exception." It was
    rejected as drift, not a constrained exception, by rendering canonical
    capH/3 **inside the real icon cells/rings** (proof `F3-canonical-in-cell.png`):
    - Plain icon (fs=200, 256 box): dot bottom = 230.67 + 16.67 = **247.3 →
      8.7px bottom margin**. Fits. Reads as a confident, present bindu (vs the
      timid shipped dot), on ivory and charcoal.
    - Circle icon (fs=170, ring r=118 → bottom 246): dot bottom = 217.67 +
      14.17 = **231.8 → 14.2px clearance inside the ring**. Fits. Reads as
      seated in the lower third of the ring, present and deliberate.
    Canonical *fits every cell without collision*, so **no per-cell gap
    exception is created** — one ratio everywhere. (The composite sits low in
    the icon cells; that is a baseline issue, not a gap issue — see Residual
    risk.)

- **Per-asset cx (provenance noted; F3 does not own cx — F1/F2 do):**
  - wordmark/lockup cx = **126.5** (owned by **F1**: ink-bbox center of the
    Cinzel-500 R at the wordmark metrics). Unchanged by F3.
  - all icon cx = **128** (owned by **F2** via the R-text-x correction that
    centers the R ink on 128). Unchanged by F3.
  - favicon cx = **16** (monogram case, advance-center = ink-center; **F2/F14**).

### Per-asset canonical table (what the generator emits)

| asset (count) | fs | R baseline y | **cx** (owner) | **cy** | **r** | r/fs | source |
|---|---|---|---|---|---|---|---|
| wordmark `RTAM` (4) | 120 | 160 | 126.5 (F1) | **188** | **10** | 0.0833 | canonical (already conforms) |
| sanskritic / bilingual / donation lockups (3) | 120 | 160 | 126.5 (F1) | **188** | **10** | 0.0833 | canonical (already conforms) |
| rdot plain `black/gold/white` (3) | 200 | 184 | 128 (F2) | **230.67** | **16.67** | 0.0833 | **F3 edit** (was cy218 r14) |
| rdot circle `gold/charcoal` (2) | 170 | 178 | 128 (F2) | **217.67** | **14.17** | 0.0833 | **F3 edit** (was cy207 r11) |
| favicon (1) | 26 | 22 | 16 (F2) | **27.2** | **2.86** | 0.110 | **F14 exception** (≤48px) |

13 files total. No value is TBD.

### Small-size exception (handoff to F14)

The favicon (rendered cap-height ~18px) is the documented small-size exception:
the bindu r/fs **rises** below 48px to survive the pixel grid (a sub-pixel
canonical dot dies, per F14's measurement). F3 **does not** apply r=fs/12 to the
favicon. **F14 owns** the favicon.svg value (r=2.86 = 0.110·fs, cy=27.2,
cx=16) and the per-size `.ico` ladder (r/fs 0.12→0.11→0.10→0.09 across
16/24/32/48px). F3 imports F14's resolved (r, cy) **verbatim** — do not
re-derive them from a center-gap, because F14 measures baseline→dot-*top* while
F3 measures baseline→dot-*center*. The ≥48px end of F14's ladder (~0.085)
converges to F3's canonical 0.0833, so the two are one coherent rule, not a
conflict. The plain (cap140) and circle (cap119) icons render **far above**
48px and therefore take **canonical**, not the exception.

## Proof

- `brand/explorations/_research/fix-specs/proofs/F3-isolated-across-scales.png`
  — the same R+bindu at fs 120/200/170/26, all normalized to one display
  cap-height, three candidate rows (A current-mix, B canonical r=fs/12
  gap=capH/3, C tighter gap=capH/4), on ivory and charcoal. **The eye should
  see:** in row A (shipped) the dots visibly differ in size and gap across the
  four scales — *not* the same mark; in row B every dot is identical in size and
  gap across all four columns — *the same mark at every scale*, the F3 goal; row
  C is also uniform but the dot hugs the R tighter (the rejected tighter gap).
- `brand/explorations/_research/fix-specs/proofs/F3-canonical-in-cell.png`
  — the canonical (r=fs/12, gap=capH/3) dropped into the **real** plain 256 box
  and the real gold ring, SHIPPED vs CANONICAL, ivory and charcoal. **The eye
  should see:** the SHIPPED dots read small/timid; the CANONICAL dots are larger
  and sit slightly lower yet stay clear of the cell edge (plain) and inside the
  ring (circle), reading as a deliberate, present bindu on both grounds — i.e.
  capH/3 fits the cells, so no exception is needed.

Generator: `brand/tools/_scratch/f3_canonical.py` (faithful — local Cinzel TTFs
via `@font-face file://`, Chromium, `document.fonts.ready` + 400ms settle;
cairosvg avoided, can't load web fonts). R weights match F4 (icons 600).

## Verification steps

US-16 re-audit:
1. Parse the 5 icon files; assert bindu `<circle>` = `cy=230.67 r=16.67`
   (plain ×3) / `cy=217.67 r=14.17` (circle ×2), `cx` and `fill` unchanged.
2. Parse the 7 wordmark-geometry files; assert bindu `cy=188 r=10` unchanged
   (canonical; cx is F1's check, not F3's).
3. Assert favicon bindu = F14's `cy=27.2 r=2.86 cx=16` (F3 defers; F14 checks).
4. **Ratio invariance gate** — for every canonical asset compute `r/fs` and
   `(cy−baseline)/capH` (capH = 0.70·fs) and assert `r/fs = 0.0833 ± 0.001` and
   `(cy−baseline)/capH = 0.3333 ± 0.003`. The favicon is exempt (F14 exception).
5. **Cell-fit gate** — assert canonical dot bottom (cy+r) ≤ box−5 for the plain
   icon (247.3 ≤ 251) and ≤ ring bottom−5 for the circle icon (231.8 ≤ 241).
6. **Eye gate** — `F3-isolated-across-scales.png` row B reads as one mark across
   scales; `F3-canonical-in-cell.png` canonical dots read present and uncrowded
   on ivory and charcoal.

## Residual risk

- **Icon R+bindu composite sits low in the cell — and canonical worsens it.**
  Honest disclosure: with canonical gap (capH/3 > the shipped icon gap), the
  R+dot composite center sits ~17px below the cell/ring center (plain: 145.7 vs
  128; circle: 145.4 vs 128), and the plain-icon bottom margin tightens from
  ~24px to **8.7px**. The dot still does not collide (verified), but the ring
  makes the low seat salient — in `F3-canonical-in-cell.png` the circle-icon
  canonical dot reads as seated in the *lower third* of the ring rather than
  centered. **Cause: the icon R baseline-y** (plain 184, circle 178), which was
  authored low, *not* the gap. **The correct lever is the baseline, which F3
  does not own** — moving the gap to "fix" centering would break the one-ratio
  canon and de-sync the icon bindu from the wordmark. **`baseline-y` of the icon
  R appears UNOWNED** by any current F-spec (F2 = R x only; F4 = R weight/fs;
  F5 = Devanagari): **flag a follow-up** to recenter the icon R+bindu composite
  in its cell by raising the baseline, after which cy follows via capH/3. F3's
  ratio is correct independent of where the baseline lands.
- **Provisional on Cinzel.** r=fs/12 and gap=capH/3 in *px* depend on Cinzel's
  cap-height fraction (0.70). The *rule* (r as a capH fraction, gap = capH/3)
  regenerates the px on a letterform swap. Marked provisional below.
- **Favicon two-sources caveat** is F14's (its single-SVG value vs the `.ico`
  ladder); F3 only references F14's value.

## Depends on

- **F1** — owns wordmark/lockup bindu **cx=126.5** and *retained* cy=188. F3
  confirms cy=188 = capH/3 as canonical, so F1's retention stands unchanged.
  F1 explicitly handed F3 "the vertical ratio" — F3 returns capH/3.
- **F2** — owns the icon R-text-x correction that centers the R **ink** on
  x=128. F3's icon dot-cx=128 is correct **only** with F2 applied (otherwise the
  dot centers under a right-shifted R ink). Must ship together.
- **F4** — owns R weight/fs and proved cap-height weight-invariance, which makes
  capH a durable anchor for the gap and radius.
- **F14** — owns the **small-size exception** (favicon.svg + `.ico` ladder,
  ≤48px). F3 imports F14's favicon (r=2.86, cy=27.2) verbatim and references its
  ladder; F3 supplies the ≥48px canonical the ladder converges to.

**Cross-spec cleanup flags (Rule 8 — stale references, not blocking):**
- **F14** states *"F5 owns the wordmark/lockup bindu r/fs ratio"* (lines 84) —
  **incorrect.** F5 is the Devanagari ऋ baseline spec; ऋ is **no-dot** by design
  and owns **no bindu**. The bindu radius/ratio is owned by **F3** (this spec).
  Flag F14's line for correction to point at F3.
- **F1** states *"r = fs/12 … F5 owns dot sizing if revisited"* — same stale
  reference; **F3 owns dot sizing**, not F5. Flag for correction.

## Durable or provisional

- **Durable (survives a Cinzel replacement) — the RULE:**
  > The bindu is one mark at every reproduction surface. Its radius and vertical
  > position are fixed *ratios* to the bearing glyph's cap-height (capH), the
  > weight-invariant letterform metric:
  > - **r = capH / 8.4 = fs/12** (one radius ratio for every surface);
  > - **cy = baseline + capH/3** (baseline→dot-center gap = capH/3);
  > - **cx** = the bearing glyph's ink-bbox center (F1's rule; advance-shifted
  >   for `text-anchor=middle` per F2).
  >
  > **Small-size exception (F14):** below ~48px rendered cap-height the radius
  > ratio rises (~+0.01 per halving, to ~0.12 at 16px) to survive the pixel
  > grid, and gap tightens; F14 owns those rows. Everything ≥48px takes the
  > canonical ratio.

- **Provisional (Cinzel-specific, tied to the 0.70 cap fraction and these
  metrics):** the px values cy=188/230.67/217.67, r=10/16.67/14.17, and the
  favicon exception numbers (F14). Regenerated from the durable rule on any
  Phase-2 letterform change by re-measuring capH and re-running the ratios.
