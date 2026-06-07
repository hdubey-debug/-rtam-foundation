# Main-Agent Eye-Check — US-10.3 Gate

Date: 2026-06-07. Every verdict below is from my own visual inspection of the
rendered PNG (not the spec text, not the numbers). Proofs live in
`fix-specs/proofs/`. The one systematic hazard checked on every image:
**is the letterform actually Cinzel/Tiro, or a fallback font?** (the kit's
core failure mode — and it struck one agent's proofs).

| Finding | Proof inspected | Verdict | Notes |
|---|---|---|---|
| F1 bindu cx | `F1-candidate-sheet.png`, `F1-before-after.png` | **PROOFS POISONED → superseded** | Both agent proofs rendered in fallback **sans-serif**, not Cinzel — the optical judgment was made on the wrong letterform. The number itself (cx=126.5) rests on TTF-outline math (126.62) and survived. I re-rendered the candidate sheet with the vendored Cinzel via `@font-face file://` → `F1-candidate-sheet-CINZEL.png`: **126.5 confirmed by eye** (122 reads left; 126.5 sits under the R's optical middle on both grounds). Poisoned PNGs kept for the record; do not cite them. |
| F2 circle-icon centers | `F2-circle-gold-before-after.png` | **PASS** | Real Cinzel. Before: R crowds right of axis. After (x=121.12): ink and dot share the axis; left/right air equal. Decisive. |
| F4 weight policy | `F4-monogram-step.png` | **PASS** | Real Cinzel, 500/600/700 at 64/48/32px standalone + on gold circle. Supports 500-identity / 600-monogram / 700-small policy. |
| F5 ऋ recentering | `F5-final.png` | **PASS** | Real Tiro. Open icon y=215→196 and circle y=210→186 both read centered; before clearly sits low. |
| F6 wordmark gap | `F6-before-after.png`, `F6-gap-tuning.png` | **PASS direction / FAIL value** | Real Cinzel. Centered composition + coupled lines: right. But the resolved gap=48 (and even 52) reads as one mashed word "RTAMFoundation" to my eye. **Build instruction for US-11: re-test gap 52–60 and pick the smallest value where the word gap clearly exceeds the internal letter-spacing rhythm.** cx=172 in the proofs is a placeholder pending F1-rule recomputation after the layout shift. |
| F7 lockup axes | temple + bilingual before/after | **PASS** | Real fonts. Temple lockup vertical air balanced; bilingual divider+Devanagari now on the content axis (guide lines coincide). |
| F8 temple bindu | `F8-after.png` | **PASS** | Bindu present under the initial R of RTAMBHARESHVARA, plausible scale; spelling untouched. |
| F9 seal geometry | `F9-seal-before-after.png`, `F9-seal-smallsize.png` | **PASS** | Medallions clearly inside the ring; hub reads dominant instantly. 96px clean; 64px marginal-acceptable (reduction tiers own below). |
| F11 poisoned exports | `F11-wordmark-poisoned-sidebyside.png` | **PASS** | The committed PNG is visibly generic sans vs the faithful Cinzel render. Proof is unambiguous. |
| F12 dark variants | `F12-sacred-wordmark-matrix.png` | **PASS** | Spec'd ivory-text variants crisp on charcoal/indigo/photo; current shipped row invisible on dark, as audited. (Matrix shows each variant blank on its own-color ground — correct pairing logic, not an error.) |
| F14 16px bindu | `F14-before-after-16-24-32-48.png` | **PASS** | Shipped dot is a speck at 16px; resolved table clearly visible and reads as the same mark across 16/24/32/48. Real Cinzel even at 16px. |
| F10 / F13 / F15 | — | **N/A (spec-only)** | Architecture / contrast / docs findings; no visual proof by design. Spec text reviewed instead. |
| F3 ratios | `F3-isolated-across-scales.png`, `F3-canonical-in-cell.png` | **PROOFS POISONED → superseded; ratios PASS** | Both agent proofs are fallback **sans** again (second agent caught by the same hazard). I re-rendered the in-cell comparison with vendored Cinzel 600 → `F3-in-cell-CINZEL.png`: canonical r=fs/12 + gap=capH/3 reads as the same confident mark as the wordmark on both grounds; shipped icon dots read timid; ring clearance clearly holds. **Eye-confirmed F3's own flag:** with canonical applied, the circle composite (R+dot) sits visibly low in the ring — the icon R baseline-y lever is unowned by any spec. **US-11 build instruction: raise the circle-icon R baseline so the R+dot composite centers in the ring, then recompute F2's x and F3's cy.** Also per F3: stale radius-ownership references in F1/F14 (cite F5; F3 owns r) — cleanup at build. |

Sampling note: 23 of 40 proof PNGs personally inspected — every
decision-bearing image (all before/afters, candidate sheets, small-size
sheets) plus representatives of each variant class; remaining files are
additional angles of classes already verified (other F5/F6 ladders, other
F7 lockups, F11 icon/PDF variants, F12 other matrices, F4 large/small
sheets, F14 float/zoom).

## Cross-cutting conclusions

1. **The fallback-font hazard is real even inside our own tooling.** One of
   fifteen agents shipped poisoned optical proofs. US-11+ rule: any render
   used for an optical judgment must use `@font-face` with `file://` URIs to
   `brand/fonts/` (never bare `@import`), and the reviewer must glance at the
   letterform first.
2. Numbers vs proofs are separable: F1's math survived its bad renders.
   Specs whose parameters come from font-file geometry are robust; specs
   whose parameters come from "which looks right" must be re-eyed on real
   letterforms (done for F1; F6's gap flagged).
3. The dependency chain for the build is F3 → F1/F2/F4 → F8/F14 → F6/F7
   (layout) with F10 as the frame; F13/F15 are independent.
