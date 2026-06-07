# F5 — ऋ icon sits visibly low and reads as a different family

## Root cause

The Devanagari ऋ monogram is set as live `<text>` whose baseline `y` was chosen by
eye against the font's nominal em box, not against the glyph's actual ink. Measured
faithfully (Chromium + the vendored `tiro-devanagari-sanskrit-400.ttf`, fonts.ready
awaited), the ऋ ink extends **130.2 units above** the baseline and only **5.8 below**
it at `font-size=210`. With the shipped baseline at `y=215` in a 256-unit box, that
leaves **84.8 units of air above the ink and 35.2 below** — a 2.4:1 imbalance. The
glyph is not low because of its descent; it is low because almost all its ink lives
*above* the baseline and the baseline was placed as if a Latin cap (ink mostly above,
near-zero below) were being centered. The circle variant (`font-size=180`, baseline
`y=210`) has the same defect inside the gold ring: **88.2 above / 31.2 below** within
the ring's vertical span.

Two distinct problems are bundled in the finding:

1. **Vertical mis-centering** (the dominant, fixable defect) — addressed by resolving a
   new baseline per variant.
2. **The sibling read** — the ऋ is heavier and higher-contrast (Tiro's modulated
   strokes) than the airy Cinzel Ṛ. §3.3 documents the *absence of a dot* as
   intentional; the *weight* difference is glyph-intrinsic to Tiro. Centering alone
   makes the two marks share a vertical zone and read far more as siblings (see Proof
   `F5-siblings.png`); the residual weight difference is addressed by a harmonization
   lever below, not by mutilating either letterform.

Horizontal centering is already correct: with `text-anchor="middle" x="128"` the ink
bbox spans x 32.8–223.0, center 127.9 ≈ 128. **No x change is needed.**

## Files touched

Single-glyph ऋ monogram occurrences only (lockup strings like `ऋतम् फाउंडेशन` are a
different finding and are **not** touched here):

Shipped icon SVGs (the 4 ऋ variants):
- `brand/icons/rtam-devanagari-ri-icon-gold.svg` — open, fs=210
- `brand/icons/rtam-devanagari-ri-icon-black.svg` — open, fs=210
- `brand/icons/rtam-devanagari-ri-icon-white.svg` — open, fs=210 (ivory on baked charcoal rect)
- `brand/icons/rtam-devanagari-ri-icon-circle.svg` — circle, fs=180, inside gold ring

Previews that **inline** the same `<text>` (verified: live text, not `<img>` refs — so
they drift from the corrected icons unless updated in lockstep):
- `brand/previews/devanagari-monogram-specimen.html` — lines 120, 126, 132 (open fs=210),
  139 (circle fs=180), 152 (gold-on-indigo fs=210), 168 (side-by-side fs=210),
  179/185/191/197/203/209 (scale ladder fs=210). Every single-ऋ `y="215"` → new open
  value; the one `y="210"` → new circle value.
- `brand/previews/index.html` — lines 211, 219, 227 (open fs=210, `y="215"`), 236
  (circle fs=180, `y="210"`).

Stale raster to regenerate after the SVG edit:
- `brand/exports/png/devanagari-monogram-specimen.png` (re-render from the corrected
  specimen via the project's HTML→PNG path).

Target-architecture source of truth (US-13): the per-variant baseline values become
outputs of `brand/spec/brand.json` + `brand/tools/generate.py`, not hand-edited
constants — see Parameters resolved for the durable rule the generator must run.

## Exact change

Replace only the baseline `y` on each single-ऋ `<text>`. Everything else
(`x="128"`, `font-size`, `text-anchor="middle"`, `font-family`, `fill`, the ring) is
unchanged.

Open variants (gold / black / white), `font-size="210"`:
- `y="215"`  →  **`y="196"`**

Circle variant, `font-size="180"`, inside `<circle cx="128" cy="128" r="118" stroke-width="5"/>`:
- `y="210"`  →  **`y="186"`**

Concretely, e.g. `brand/icons/rtam-devanagari-ri-icon-gold.svg` line 7:
```
<text x="128" y="196" font-family="'Tiro Devanagari Sanskrit', 'Noto Serif Devanagari', serif" font-size="210" text-anchor="middle" fill="#C8A15A">ऋ</text>
```
and `brand/icons/rtam-devanagari-ri-icon-circle.svg` line 8:
```
<text x="128" y="186" font-family="'Tiro Devanagari Sanskrit', 'Noto Serif Devanagari', serif" font-size="180" text-anchor="middle" fill="#1A1A1A">ऋ</text>
```
Apply the identical `215→196` / `210→186` substitution to every single-ऋ `<text>` in
the two preview HTML files listed above (do not touch the multi-codepoint lockup
strings, which have their own fs and y).

Harmonization lever (durable, no geometry edit to existing files): adopt the
**circle-enclosed pair as the canonical cross-script sibling presentation**. Record in
`guidelines/brand-book.md` §3.3 (a doc edit, executed under the docs F-item, noted here
as the lever) that when the Latin Ṛ and Devanagari ऋ marks must read as a matched set,
the **enclosed (ring) variants** are the official pairing because the shared gold ring
is a *script-neutral enclosure* — see the no-dot argument below for why the ring is
permitted where a dot is not.

## Parameters resolved

**The durable rule (letterform-independent — generate.py runs this, not the constants):**
For a single-glyph monogram, render the glyph at its target `font-size` faithfully,
measure (a) the ink bbox `[y0,y1]` and (b) the vertical ink **centroid** `yc`, all
relative to a known baseline. Place the new baseline so that, within the frame band
`[T,B]` (open: `[0,256]`; circle: the ring's vertical span `[10,246]`), the
**bbox-center error and the mass-centroid error are equalized** — i.e. baseline =
midpoint of {baseline-that-centers-the-bbox, baseline-that-centers-the-centroid}. This
minimizes the *worse* of the two optical-center errors. It auto-recomputes if Phase-2
swaps the letterform.

**Why a bottom bias (not pure bbox equal-air):** measured, the ऋ's vertical centroid
sits **above** its bbox center by +11.4 (fs=210) and +9.9 (fs=180) — the dense
shirorekha (head-line) concentrates mass high, so the glyph is genuinely top-heavy.
Pure bbox equal-air therefore reads slightly *high* (heavy bar floats up); pure
mass-centering over-corrects and reads low again. The equalized midpoint is the optical
optimum. This holds in both forms because mass distribution is a property of the glyph,
not of the frame — the ring does not redistribute ink, so the same bias applies open
and enclosed.

**Provisional resolved values (Tiro-specific outputs of the rule above):**

| Variant | fs | bbox-center baseline | mass-center baseline | **chosen y = midpoint** | resulting bbox-C / centroid err |
|---|---|---|---|---|---|
| open (gold/black/white) | 210 | 190.2 | 201.6 | **196** | bbox +5.8 / centroid −5.6 |
| circle | 180 | 181.5 | 191.4 | **186** | bbox +4.5 / centroid −5.4 |

- **open y=196** — rounded from 195.9 = (190.2+201.6)/2. Air becomes 65.8 above / 54.2
  below (was 84.8 / 35.2). Both optical-center errors ≈ ±5.6, balanced.
- **circle y=186** — rounded from 186.5 = (181.5+191.4)/2. Within ring band 10–246, air
  becomes ≈64 above / 55 below (was 88.2 / 31.2). Errors ≈ ±5.0, balanced.
- **x stays 128** — ink bbox center is 127.9, already centered under `text-anchor=middle`.

(No TBD. The two integers are the only new numbers; both are derived, not guessed.)

## Proof

Faithful Chromium renders (local TTFs via `@font-face`, `document.fonts.ready` awaited,
+450ms settle), generated by `brand/tools/_scratch/f5_proof.py` / `f5_final.py`:

- `brand/explorations/_research/fix-specs/proofs/F5-final.png` — open BEFORE (y=215),
  open AFTER (y=196), circle BEFORE (y=210), circle AFTER (y=186), on the real ivory /
  gold-ring grounds. **The eye should see** both BEFORE panels sinking low (a moat of
  air above, ink hugging the bottom) and both AFTER panels sitting balanced — the heavy
  shirorekha near the optical middle, lighter strokes filling below; the circle AFTER
  seated symmetrically inside the gold ring.
- `brand/explorations/_research/fix-specs/proofs/F5-open-ladder.png` and
  `F5-circle-ladder.png` — BEFORE / equal-air / +bias / Latin-sibling, with center
  guides. **The eye should see** equal-air reading marginally high and the chosen bias
  settling the head-bar onto center.
- `brand/explorations/_research/fix-specs/proofs/F5-siblings.png` — R-open ↔ ऋ-open and
  R-circle ↔ ऋ-circle at the fixed values. **The eye should see** that after centering
  the two marks share the same vertical zone and read as a family; the only residual is
  Tiro's heavier stroke weight (intentional, §3.3) and, in the enclosed pair, the gold
  ring acting as the shared sibling device.

## Verification steps

US-16 re-audit, blind-runnable (reuse `brand/tools/ink_analysis.py`'s render harness or
`f5_measure.py`):

1. Render each corrected ऋ SVG faithfully; compute the ink bbox in viewBox units.
2. **Open variants** (box 0–256, fs=210, y=196): assert air_top ≈ **65.8** and
   air_bot ≈ **54.2**, tolerance ±2. (Fails if anyone reverted to 84.8/35.2.)
3. **Circle variant** (ring band 10–246, fs=180, y=186): assert air_top ≈ **64** and
   air_bot ≈ **55**, tolerance ±2.
4. Assert horizontal: ink bbox center x = 128 ± 1.
5. Grep that no single-ऋ `<text>` retains `y="215"` or `y="210"` in `brand/icons/` or
   `brand/previews/`; assert `brand/exports/png/devanagari-monogram-specimen.png` was
   regenerated (mtime newer than the specimen HTML).
6. Eye-check `F5-siblings.png` parity: confirm the family read.

## Residual risk

- **Weight/contrast mismatch persists.** Centering does not equalize Tiro's heavier,
  higher-contrast strokes vs Cinzel's airy caps. This is retained by design (§3.3 frames
  the Devanagari mark as a deliberate counterpart, not a clone). Optical-size
  compensation was considered and **rejected**: it adjusts apparent *size*, a different
  axis than *weight*, and Tiro's contrast is glyph-intrinsic — shrinking the ऋ would
  only shrink the mark, not lighten it. The accepted residual is weight; the lever for
  it is enclosure parity (below), not letterform surgery.
- **The no-dot rule must not be "fixed" by adding an accent.** §3.3: the ऋ glyph already
  *is* the sacred mark, so a dot on it is **semantically redundant** (it would assert the
  vocalic-R the bindu stands in for on Latin R, which ऋ already encodes). The gold
  **ring** is categorically different — a *script-neutral enclosure* applied identically
  to both scripts, carrying no phonetic claim — so sharing the ring harmonizes the pair
  **without** violating §3.3. The lever is therefore: designate the enclosed variants as
  the canonical sibling pairing; do **not** add any gold dot to the open ऋ.
- Provisional `y` values are tied to Tiro's outline. A Phase-2 letterform swap requires
  re-running the durable rule; a hardcoded 196/186 would silently mis-center. Mitigated
  by encoding the rule (not the constants) in generate.py.
- Live-text/web-font dependency (the system-wide architecture caveat) is unchanged here;
  the outlined-master pipeline (F10) will bake these baselines into paths.

## Depends on

- **F10** (outlined-masters / generate.py integration) — to encode the durable centering
  rule as a generator step and bake the resolved baselines into distribution paths.
- The §3.3 brand-book doc edit that records the enclosed-pair sibling lever is the docs
  F-item's to apply; this spec supplies the rationale and the exact text intent.
- Otherwise independent of other F-numbers.

## Durable or provisional

- **Durable:** the centering *rule* (measure bbox + centroid, equalize the two
  optical-center errors); the no-dot invariant and the precise ring-vs-dot argument; the
  enclosed-pair-as-canonical-sibling lever; horizontal centering already correct.
- **Provisional:** the resolved baselines **y=196 (open)** and **y=186 (circle)**, and
  the air targets in Verification — all tied to Tiro Devanagari Sanskrit's specific
  outline; recompute if the letterform changes.
