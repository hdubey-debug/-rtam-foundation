# F4 — One R, three weights: define the weight-stepping policy

## Root cause

The brand book says the R's shape is part of the mark (`brand/guidelines/brand-book.md:133`: "Don't substitute the Cinzel R with a different serif. The R's shape is part of the mark."), yet the shipped kit renders that R at three different Cinzel weights with no documented rule:

| Asset | font-weight | font-size | viewBox | file |
|---|---|---|---|---|
| Wordmark `RTAM` (all 5 variants) | **500** | 120 | 1080×240 | `brand/logos/rtam-wordmark-*.svg` |
| rdot-icon (`R` monogram, full-bleed) | **600** | 200 | 256×256 | `brand/icons/rtam-rdot-icon-{black,gold,white}.svg` |
| rdot-icon (`R` monogram, on gold/charcoal circle) | **600** | 170 | 256×256 | `brand/icons/rtam-rdot-icon-circle-*.svg` |
| favicon (`R` monogram) | **700** | 26 | 32×32 | `brand/icons/favicon.svg` |

The three weights are an *un-stated* design decision, not an error of inconsistency: they are three legitimate responses to two different problems (solo-letterform presence; small-size pixel-grid legibility). The defect is that the rule is undocumented, so the kit silently contradicts its own "the shape is the mark" claim. F4 does not change any weight; it **resolves and documents the policy** and records it as machine-readable data the US-13 generator will consume.

The Latin `R` is the only subject of F4. The Devanagari ऋ icons (`brand/icons/rtam-devanagari-ri-icon-*.svg`) carry no `font-weight` (Tiro Devanagari Sanskrit ships single-weight regular) and are out of scope.

### Why three weights is defensible (the evidence)

Objective glyph measurement via fontTools (left vertical stem of `R`, normalized to 1000 upem; scanline at 12% cap-height) — see `brand/tools/_scratch/f4_render.py` companion measurement:

| weight | cap-height (norm 1000) | left-stem width (norm 1000) | Δ stem vs 500 |
|---|---|---|---|
| 400 | 700 | 65 | — |
| **500** | **700** | **93** | baseline |
| **600** | **700** | **122** | **+31%** |
| **700** | **700** | **150** | **+61%** |

The cap-height is **identical at every weight** (700/1000 em). Only stroke weight changes; the silhouette, the bowl, the leg angle, the serif structure are preserved. This is the technical fact that makes weight-stepping legitimate under "the shape is the mark": stepping weight does **not** substitute a different letterform, it only thickens strokes of the *same* letterform. (Proof sheet `F4-r-weights-large.png` shows this at 256px: three Rs, one silhouette.)

Two visual findings drive the rule (proof `F4-monogram-step.png`, `F4-r-weights-small.png`):
1. **Solo-letterform presence.** A lone monogram `R` reads lighter than the same `R` packed inside a word. At a 48–64px box on ivory, the 500 monogram looks thin/under-set next to 600; on the gold circle the 500 strokes lose contrast against the gold. 600 restores the visual weight a standalone mark needs.
2. **Small-size legibility.** As the rendered `R` shrinks, the thinner 500 stems and serifs fade against the pixel grid. At ~16–18px rendered cap-height (favicon territory) the 700 stems survive rasterization where 500 thins and breaks up.

## Files touched (the fix this spec authorizes)

This is a **documentation + data** fix. No SVG geometry changes; all existing weights are *retained* as already-correct outputs of the new rule.

1. `brand/guidelines/brand-book.md` — append a sub-section to §5 (Typography) and a clarifying line to the §7 "Don't" about the R, stating the weight-stepping rule.
2. `brand/guidelines/usage-rules.md` — append a rule block under §5 (Type rules).
3. `brand/spec/brand.json` (target architecture; created in US-13) — encode the policy as the data the generator reads.
4. *(no change to any `brand/logos/*.svg`, `brand/icons/*.svg`, `brand/lockups/*.svg` — the current weights already conform to the resolved table below.)*

## Exact change

### The policy (durable structure)

> **The R is one letterform at one identity weight (Cinzel 500). Stroke weight may step heavier only to preserve that letterform's presence or legibility, never to restyle it. Two — and only two — conditions authorize a step, keyed to the *rendered* cap-height of the R in CSS px:**
>
> | Role | Rendered R cap-height | Cinzel weight |
> |---|---|---|
> | **Wordmark / in-word R** (R inside `RTAM`, any size) | any | **500** (identity) |
> | **Standalone monogram**, large | ≥ 24px | **600** |
> | **Standalone monogram**, small | < 24px | **700** |
>
> The wordmark R never steps: an in-word letter borrows weight from its neighbours and the bindu, so it stays at the identity weight at every deployment size. Only the *standalone* R (icon/favicon/watermark, no surrounding letters) steps, and only along the size axis.

### 1. `brand/guidelines/brand-book.md` — new sub-section appended to §5 (after line 107, before the `---` on line 109)

```markdown
### The R's weight

The R is **one letterform** — Cinzel, cap-height fixed — rendered at **one identity weight, Cinzel 500**. The wordmark R is always 500. A *standalone* R monogram (icon, favicon, watermark — an R with no neighbouring letters) may step **heavier** so the lone letter keeps its presence and survives small sizes. Stepping thickens the strokes of the same R; it never substitutes a different shape (Cinzel's cap-height is identical at 500/600/700). The step is keyed to the R's **rendered** cap-height:

| Standalone monogram, R cap-height ≥ 24px | Cinzel **600** |
| Standalone monogram, R cap-height < 24px | Cinzel **700** |

This is the only sanctioned deviation from a single weight, and it applies to the standalone R alone — never the wordmark.
```

### 2. `brand/guidelines/brand-book.md` — clarify the §7 "Don't" line 133

Replace line 133:
```
- Don't substitute the Cinzel R with a different serif. The R's shape is part of the mark.
```
with:
```
- Don't substitute the Cinzel R with a different serif, and don't restyle it. The R's shape is part of the mark. Weight may step (500 → 600 → 700) only for a *standalone* monogram per the rule in §5 — that thickens the same shape, it does not change it.
```

### 3. `brand/guidelines/usage-rules.md` — new rule appended to §5 (after line 62, before the `---` on line 64)

```markdown
- The **R is one letterform at one weight: Cinzel 500**. The wordmark R is *always* 500, at every size. Only a **standalone R monogram** (icon/favicon/watermark) steps heavier, and only by rendered R cap-height: **≥24px → 600; <24px → 700**. Stepping thickens the same R (Cinzel's cap-height is weight-invariant); it does not restyle it.
```

### 4. `brand/spec/brand.json` — policy as data (the shape US-13's generator must read)

```json
{
  "letterform_R": {
    "font_family": "Cinzel",
    "identity_weight": 500,
    "comment": "One R. Cap-height is weight-invariant in Cinzel; stepping only thickens strokes.",
    "weight_policy": {
      "in_word": {
        "weight": 500,
        "rule": "R inside the wordmark RTAM (or any word) is always the identity weight; never steps."
      },
      "standalone_monogram": {
        "key": "rendered_cap_height_px",
        "steps": [
          { "min_cap_px": 24, "weight": 600, "reason": "solo-letterform presence" },
          { "max_cap_px": 24, "weight": 700, "reason": "small-size pixel-grid legibility" }
        ]
      }
    }
  }
}
```

Per-asset resolution the generator will emit from that policy (rendered cap-height computed as `font_size * 0.70`, Cinzel cap-height fraction):

| asset | role | font-size | R cap-height (vb units) | resolved weight | matches shipped? |
|---|---|---|---|---|---|
| `rtam-wordmark-*.svg` | in-word | 120 | 84 | **500** | ✅ 500 |
| `rtam-rdot-icon-{black,gold,white}.svg` | standalone, large | 200 | 140 | **600** | ✅ 600 |
| `rtam-rdot-icon-circle-*.svg` | standalone, large | 170 | 119 | **600** | ✅ 600 |
| `favicon.svg` | standalone, small | 26 | 18.2 | **700** | ✅ 700 |

Every shipped weight already conforms, so the fix ships **zero geometry edits** — it only writes down the rule that was implicit.

## Parameters resolved

| Parameter | Final value | Rationale |
|---|---|---|
| Identity weight | **Cinzel 500** | Already the wordmark weight (`rtam-wordmark-*.svg` line 8); usage-rules §5 line 61 already names "Cinzel 500" for headlines. The mark's canonical voice. |
| In-word R weight | **500, always** | An in-word R borrows weight from neighbours + bindu; it never needs stepping. Keeps the wordmark a single literal weight at every deploy size. |
| Step axis | **rendered R cap-height in px** (= font-size × 0.70) | Legibility/presence is driven by the *rendered* size of the actual letterform, not the asset's nominal viewBox. Durable: independent of viewBox and of the eventual letterform's metrics (recompute the 0.70 fraction for a Phase-2 face). |
| Monogram large weight | **600** | Empirically: at 48–64px box the 500 solo R reads thin and (on gold) low-contrast; 600 restores solo-mark presence (`F4-monogram-step.png`). +31% stem (fontTools), same silhouette. Matches shipped rdot-icons. |
| Monogram small weight | **700** | At ~16–18px rendered cap-height the 500/600 thin strokes fade against the pixel grid; 700 stems survive rasterization (`F4-r-weights-small.png` 16px ×8 block). Matches shipped favicon. |
| Step threshold | **24px rendered R cap-height** | Sits cleanly between the shipped data points: rdot-icon-circle at native 256px = 119px cap (≫24, → 600) and favicon at native 32px = 18.2px cap (<24, → 700). 24px ≈ the size below which Cinzel's hairline serifs begin sub-pixel thinning at 1× density. Boundary is `<` (favicon's 18.2 → 700) vs `≥` (any icon ≥24 → 600). |
| 400 weight | **not used for the R** | Measured 65-unit stem (−30% vs 500); too light to be the identity or any step. Listed in §5 type palette for body-adjacent display use, never the mark. |

No value is TBD.

## Proof

Proof PNGs (faithful Playwright/Chromium renders with `document.fonts.ready` awaited + 400 ms settle, local Cinzel TTFs via `@font-face` `file://`; cairosvg avoided because it cannot load the web font):

- `brand/explorations/_research/fix-specs/proofs/F4-r-weights-large.png` — The R at 256px in 500 / 600 / 700 side by side. **The eye should see one identical R silhouette** (same bowl, leg, serifs, cap-height) **getting only heavier in stroke** left → right; the 500 is clearly the elegant display identity, the 700 the heaviest. This proves stepping ≠ restyling.
- `brand/explorations/_research/fix-specs/proofs/F4-r-weights-small.png` — The R at native 32px and 16px, each weight, each also shown ×8. **At 16px ×8 the 500 stems/serifs thin and start breaking against the pixel grid while 600 holds and 700 is solid** — this is why the favicon must step to 700.
- `brand/explorations/_research/fix-specs/proofs/F4-monogram-step.png` — Standalone R at 64/48/32px boxes on ivory and on the gold circle, 500/600/700. **At 48–64px the 500 solo R reads thin next to 600; on the gold circle the 500 nearly washes out** — this is why a *standalone* monogram steps to 600 even at moderate size, while the in-word R stays 500.

## Verification steps (US-16 re-audit)

1. **Grep each shipped R asset's weight and confirm it equals the table.** For every `*.svg` containing a Latin `>R<` or `>RTAM<` text node, extract `font-weight` and `font-size`, compute `cap = font-size × 0.70`, classify role (in-word if the text is `RTAM`/in a word; standalone if a lone `R`), and assert the weight matches the policy: in-word→500; standalone & cap≥24→600; standalone & cap<24→700. All 11 R-bearing assets must pass with zero geometry change.
2. **Confirm the docs carry the rule.** Assert `brand/guidelines/brand-book.md` §5 contains the "The R's weight" sub-section and §7 line 133 contains "step (500 → 600 → 700)"; assert `brand/guidelines/usage-rules.md` §5 contains "R is one letterform at one weight: Cinzel 500" and the "≥24px → 600; <24px → 700" thresholds.
3. **Confirm the data.** Assert `brand/spec/brand.json` has `letterform_R.weight_policy` with `identity_weight: 500` and the two-step `standalone_monogram.steps` array, and that running the US-13 generator emits exactly the shipped weights (regenerate → diff against shipped SVG weights = empty).
4. **Cap-height invariance regression.** Re-run the fontTools stem measurement; assert cap-height is identical across 500/600/700 (still 700/1000), confirming the "same shape" premise the policy rests on.

## Residual risk

- **24px threshold is a judgement line, not a hard rasterization cliff.** It is placed to (a) sit between the existing shipped data points and (b) correspond to where Cinzel hairline serifs begin sub-pixel thinning at 1× density. An asset rendered at exactly 22–26px cap-height could reasonably go either way; the rule resolves it deterministically (≥24→600) but a designer reviewing a borderline new asset should eye-check. Mitigation: the boundary is documented and code-checkable, so any future asset is unambiguous.
- **"Rendered cap-height" depends on deployment scale, which an SVG file cannot know.** The policy is resolved per-asset at *design* size (the size the file is authored for). A wordmark SVG dropped into a 200px-wide header renders its R at ~15px yet stays 500 — by design (in-word R never steps). This is intentional, but a consumer who shrinks the *standalone* rdot-icon far below its 256px design size will get a 600 R at favicon scale rather than 700; the rule's answer is "use `favicon.svg` at favicon scale," which the existing asset set already provides. No new asset is required.
- **Weight values are Cinzel-specific.** A Phase-2 letterform swap invalidates 500/600/700 and the 0.70 cap fraction. The *policy structure* (one identity weight; standalone-only stepping; threshold keyed to rendered cap-height; two steps for presence + legibility) is face-independent and survives. See "Durable or provisional."

## Depends on

none. (F4 is self-contained: it documents/encodes existing weights without changing geometry. The US-13 generator and `brand/spec/brand.json` are shared target-architecture artifacts, not a dependency on another F-finding.)

## Durable or provisional

**Mixed, explicitly partitioned:**

- **Durable** (survives a Cinzel replacement): the *policy as a rule* — the R is one letterform at one identity weight; only a *standalone* monogram steps; the step is keyed to **rendered R cap-height**; there are exactly two steps, justified by *solo-letterform presence* and *small-size legibility*; the in-word R never steps. The `brand.json` schema shape (`identity_weight` + `standalone_monogram.steps[]` keyed on cap-px) is durable. The principle "stepping must thicken the same shape, never restyle it (verify cap-height invariance)" is durable.
- **Provisional** (tied to Cinzel's specific shapes/metrics): the weight numbers **500 / 600 / 700**, the **24px** threshold, and the **0.70** cap-height fraction used to convert font-size → cap-height. On a Phase-2 face these must be re-derived: re-measure cap-height invariance across the new weights, re-find the size at which hairlines thin, and re-fit the identity/large/small weights to the new face's weight ramp.
