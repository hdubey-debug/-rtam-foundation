# F14 — The bindu dies at 16px (and floats at hero sizes)

## Root cause
The favicon carries a **single** absolute bindu geometry — `<circle cx="16" cy="27.5" r="2.2">` in a 32-unit viewBox — that is then linearly scaled to every deployment size. Two opposite failures fall out of one fixed circle:

1. **Death at 16px.** At a 16px tab the favicon scales by 0.5, so `r=2.2` → a **1.1px-radius / ~2.2px-diameter** disk. A sub-pixel circle cannot antialias into a legible dot: measured, the shipped bindu at 16px renders as **3px tall, ~3.6 effective gold pixels** — a pale ghost that all but merges into the ivory tab ground (proof row A, 16px). The file's own `<desc>` claims it is "sized so the R + bindu remain legible at 16px"; it is not. This is the favicon failing its single stated goal.

2. **Float at hero sizes.** The same `r=2.2` with `cy=27.5` puts the dot's top **3.3 units below the R baseline (y=22)**. That gap is a fixed fraction of the viewBox, so it scales up linearly: at 128/256px the bindu sits in a large void below the leg and reads as a **detached, floating dot**, not an integrated diacritic (proof `F14-float`). The brand book already admits this (`brand/guidelines/brand-book.md:54`, `usage-rules.md:28`: "detaches at 8× scale → use the full R-monogram"). The gap is purely geometric — there is no optical tie between the Cinzel leg terminal and the circle — so nothing about a scaled circle can fix it.

The deep cause is that one fixed circle is asked to do a job that is **size-dependent**: small rasters need a *proportionally larger, tighter* dot to survive the pixel grid; large rasters need the dot *closer to the leg* (or fused into it) to stop floating. A single `(r, cy)` cannot satisfy both.

## Files touched   (every file the fix will change)
- `brand/icons/favicon.svg` — change the bindu `<circle>` `r` and `cy` to the single-value compromise below. (R `<text>` is unchanged: weight `700`, fs `26`, x `16`, y `22` — locked by **F4**, do not touch.)
- `brand/spec/brand.json` (US-13, new) — add a `favicon` block carrying (a) the single-SVG bindu values and (b) the per-size optical-compensation table the generator uses to emit the `.ico` bitmap set.
- `brand/tools/generate.py` (US-13, new) — emit `favicon.svg` from the single-value row, and rasterize the `.ico` size set (16/32/48) from the per-size table (one optically-tuned bindu per bitmap, not a scaled one).
- `brand/previews/mockups/favicon-scale-test.html` — update the seven inline favicon copies' `<circle>` to the single-value compromise so the mockup matches the shipped asset. (Cosmetic mirror of the asset; in scope because it hard-codes the old `r=2.2 cy=27.5`.)
- `brand/guidelines/brand-book.md` / `usage-rules.md` — the ">64px detaches, use the monogram" rule **stays** (it is correct and is the routing that keeps the float out of scope); add one line noting the favicon's bindu is optically compensated per size. (Coordinate with **F15** docs-truth so we don't double-edit.)

No other shipped SVG changes. The wordmark/lockup bindu ratio is **F5's** territory, not F14's.

## Exact change

### A. `brand/icons/favicon.svg` — single-value bindu (serves 16–64px in one file)
Replace the circle line
```
  <circle cx="16" cy="27.5" r="2.2" fill="#C8A15A"/>
```
with
```
  <circle cx="16" cy="27.2" r="2.86" fill="#C8A15A"/>
```
`cx` stays `16` (centered under R; F3 owns horizontal centering and this is the monogram case where advance-center = ink-center, so 16 is correct). Nothing else in the file changes.

### B. `.ico` bitmap optical-compensation table (generator emits one bitmap per row)
Each bitmap is rendered from a 32-viewBox source whose bindu uses that row's `(r, cy)` — **not** one SVG scaled. R is `fs=26 y=22 weight=700` in every row.

| target px | bindu `r` (32-vB units) | `r`/fs ratio | bindu `cy` | gap (baseline→dot-top, units) | why this row |
|---|---|---|---|---|---|
| **16** | **3.12** | 0.120 | **27.0** | 1.88 | smallest pixel budget → fattest dot + tightest gap so the disk survives AA and stays attached |
| **24** | **2.86** | 0.110 | **27.2** | 2.34 | one step down in compensation |
| **32** | **2.60** | 0.100 | **27.4** | 2.80 | native viewBox size; moderate boost |
| **48** | **2.34** | 0.090 | **27.6** | 3.26 | enough pixels that the dot needs little help; converges toward the shipped proportion |

Above 48px the favicon is **not** used (route to the full R-monogram per the brand book). The single-value SVG (row A) is what a browser uses when it scales `favicon.svg` directly; the table is what the `.ico` generator bakes per bitmap.

## Parameters resolved   (every number FINAL with one-line rationale)
All measured with `brand/tools/_scratch/f14/render_f14.py` + `proof_f14.py` (Chromium, `device_scale_factor=1`, true raster sizes, local Cinzel-700 TTF; gold isolated by warm-chroma `R−B>18`, mass = Σchroma / full-gold-chroma ≈ effective gold-pixel area).

- **favicon.svg `r` = 2.86 (= 0.110·fs).** Single-value compromise across 16–64px. Measured gold mass at 16px = **6.8 vs shipped 3.6** (≈1.9× the ink → a real dot, proof row B/RESOLVED-16); at 64px mass = 103 (a proportionate dot, not a blob). Best single value that survives 16px without over-dotting 48–64px.
- **favicon.svg `cy` = 27.2.** Pulls the dot up 0.3 units from shipped 27.5 → gap = `cy − r − 22` ≈ 2.34 units (vs shipped 3.3), reducing the hero-size float while staying clearly separated at 16px (measured gap 2px raster).
- **favicon.svg `cx` = 16.** Unchanged; centered under the R (monogram case, no ink-vs-advance asymmetry; F3-consistent).
- **`.ico` 16px row: r = 3.12 (0.120·fs), cy = 27.0.** Heaviest dot + tightest gap; measured mass **7.9** at 16px (2.2× shipped), diameter 3px — the most legible 16px bindu without merging into the leg. This is **the small-size exception row of F3/F5's r/fs table** that F14 owns.
- **`.ico` 24px row: r = 2.86 (0.110·fs), cy = 27.2.** Mass 14.8; one compensation step down.
- **`.ico` 32px row: r = 2.60 (0.100·fs), cy = 27.4.** Mass 23.2; moderate boost at native size.
- **`.ico` 48px row: r = 2.34 (0.090·fs), cy = 27.6.** Mass 41.5; near-shipped proportion — converges so the table is monotone and the ≥48px end matches the wordmark feel.
- **favicon.ico size set = {16, 32, 48}.** The conventional Windows/desktop favicon trio; 24 is provided in the table for any 24px UI use but is not a standard `.ico` member. (16 and 32 are the load-bearing tab sizes; 48 is the high-DPI tab / shortcut size.)
- **Ratio ladder is monotone 0.12→0.11→0.10→0.09 across 16→24→32→48**, asymptoting to ~0.085 (the shipped/large-size ratio). This is the **durable rule** F3/F5 should adopt as their small-size exception: *r/fs rises as rendered size falls, by ~0.01 per halving below 48px.*
- **R weight = 700, fs = 26 — unchanged (owned by F4).** F14 does not touch the R; it only re-tunes the bindu.

Every value above is final; none is left unresolved.

## Proof
- `brand/explorations/_research/fix-specs/proofs/F14-before-after-16-24-32-48.png` — top row SHIPPED (r=2.2), bottom row RESOLVED single-value (r=2.86, cy=27.2), at 16/24/32/48px, nearest-neighbour pixel-zoom (×14). **The eye should see:** at 16px the shipped bindu is a faint 1–2px pale ghost barely separable from the ivory tab, while the resolved bindu is a denser, clearly-present small gold dot; at 24/32px the resolved dot reads as a deliberate, rounder bindu; at 48px the two converge (the table is designed to).
- `brand/explorations/_research/fix-specs/proofs/F14-float-128-256.png` — shipped favicon scaled to 128/256px. **The eye should see:** the bindu sitting in a large void below the R, reading as a detached floating dot — the hero-size defect the brand book admits, and the reason >64px routes to the monogram, not the favicon.
- `brand/explorations/_research/fix-specs/proofs/F14-candidate-matrix-zoom.png` — full candidate sweep (shipped A + four compensations B–E) × five sizes, pixel-zoomed. **The eye should see:** how rising r/fs and tightening cy progressively rescue the 16px dot, and how the heaviest candidate (E, 0.13·fs) over-dots at 64px — bounding why the resolved ratios stop at 0.12 (16px) and taper to 0.09 (48px).

## Verification steps   (how US-16 re-audit confirms the fix)
1. **16px legibility gate.** Render the post-fix `favicon.svg` (and the generated 16px `.ico` bitmap) at a true 16px raster (Chromium, `device_scale_factor=1`, `document.fonts.ready` + 400ms). Isolate gold by warm-chroma `R−B>18`; require **gold ink mass ≥ 6.0** (shipped fails at 3.6; resolved single-value = 6.8, table-16 = 7.9). Re-use `brand/tools/_scratch/f14/render_f14.py::measure`.
2. **Eye check at 16/24/32px** on both ivory and charcoal tab grounds: the bindu must read as an intentional dot, distinct from the leg, not a stray pixel.
3. **Gap/float check.** Confirm `cy − r − 22 ≤ 2.4` units in the shipped SVG (resolved = 2.34) so the hero-scaled float is reduced; confirm the brand book still routes >64px to the monogram (the float is mitigated, not eliminated — see Residual risk).
4. **Table monotonicity.** Confirm the generator's per-size ratios decrease monotonically 0.12→0.09 across 16→48 and that each bitmap is rendered from its own row (not a scaled single source) — diff the four bitmaps' bindu diameters against the predicted `2·r·(px/32)`.
5. **No R change.** Assert the favicon `<text>` still reads `weight=700 fs=26 x=16 y=22` (F4 invariant) and `cx=16` (F3 invariant).
6. **Mockup parity.** Confirm `favicon-scale-test.html`'s seven inline circles match the shipped single-value `(r=2.86, cy=27.2)`.

## Residual risk
- **The hero-size float is mitigated, not solved.** Tightening cy and routing >64px to the monogram contains it, but a *circle* below a Cinzel leg will always read as an appended dot at large scale because there is no optical join. **Only a Phase-2 letterform** — a custom R whose leg terminal resolves into the bindu, or bindu-as-negative-space (Spike 3 proved buildable) — truly integrates the dot at hero sizes. Flagged for Phase-2; out of F14's scope.
- **Two sources of truth for one bindu.** The single-value SVG and the per-size `.ico` table can drift if hand-edited. Mitigation: both must originate from the `brand.json` `favicon` block via the US-13 generator; never edit the `.ico` bitmaps by hand.
- **Ratios are Cinzel-700-specific.** The exact r/fs numbers were tuned to Cinzel 700's stem/serif rasterization. If Phase-2 changes the letterform (or F4's weight policy is revised), the *numbers* must be re-derived — the *rule shape* (r/fs rises below 48px) carries over. Marked provisional below accordingly.
- **Charcoal-tab edge case.** Tuning was on the ivory tab ground (the documented default). On a charcoal tab (`fill` swapped to ivory R) the gold bindu has more contrast and reads slightly heavier; the resolved r is safe there (erring toward more-legible), but US-16 should eyeball the charcoal variant at 16px to confirm it doesn't look over-heavy.

## Depends on
- **F4** — owns the favicon R weight (700) and fs; F14 leaves the `<text>` untouched and must not be merged in a way that re-opens the weight.
- **F3** — owns the size→(r,gap) compensation table and horizontal centering; **F14 owns and supplies F3's small-size exception rows (≤48px)** and the `cx=16` monogram-centering value. F3 should import this table verbatim.
- **F5** — owns the wordmark/lockup bindu r/fs ratio; F14's small-size ratio ladder (0.12→0.09) must be referenced as F5's documented small-size exception so the two specs state one coherent rule.
- **F15** — owns docs-truth; coordinate the one brand-book/usage-rules line so the ">64px → monogram" routing and the "optically compensated per size" note are edited once.
- **US-13** — `brand.json` + `generate.py` are the delivery vehicle for both the single-value SVG and the `.ico` table.

## Durable or provisional
- **Durable:** the *rule* (one fixed circle cannot serve both 16px survival and hero-size integration; therefore the bindu r/fs **rises** as rendered size falls, ~+0.01 per halving below 48px, and the `.ico` ships per-size-tuned bitmaps rather than one scaled source); the favicon's ≤64px ceiling with monogram routing above; cx=16 monogram centering; both outputs sourced from `brand.json`.
- **Provisional (Cinzel-700-specific):** the exact numbers — favicon.svg `r=2.86 cy=27.2`, and the table rows (16: r3.12/cy27.0; 24: r2.86/cy27.2; 32: r2.60/cy27.4; 48: r2.34/cy27.6). Re-derive if the letterform or weight policy changes in Phase-2.
- **Phase-2-only:** true elimination of the hero-size float (leg-into-bindu letterform or negative-space bindu) — no live-text + circle solution can achieve it.
