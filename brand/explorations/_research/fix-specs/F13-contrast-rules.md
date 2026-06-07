# F13 — Documented color pairings fail WCAG; one specimen endorses a failure

## Root cause

The brand documents color pairings by *role string* ("captions", "supporting copy",
"premium / ceremonial") without a contrast budget, and several of those documented
uses fail WCAG 2.x contrast on the brand's own default ground (ivory). Computed with
`brand/tools/contrast.py` (sRGB relative-luminance, WCAG formula `(L_hi+0.05)/(L_lo+0.05)`):

| Pairing | Ratio | 3:1 (graphics / large ≥24px or ≥18.66px-bold) | 4.5:1 (body) |
|---|---|---|---|
| antiqueGold `#C8A15A` on warmIvory `#F7F3E9` | **2.18:1** | FAIL | FAIL |
| antiqueGold on sandstone `#E6DED1` | **1.81:1** | FAIL | FAIL |
| stoneGray `#B8B1A4` on warmIvory | **1.92:1** | FAIL | FAIL |
| bronze `#9B6A2F` on warmIvory | **4.21:1** | PASS | FAIL |
| bronze on sandstone | **3.50:1** | PASS | FAIL |
| antiqueGold on charcoalBlack `#1A1A1A` | 7.21:1 | PASS | PASS |
| antiqueGold on deepIndigo `#1C1A3D` | 6.88:1 | PASS | PASS |
| stoneGray on charcoalBlack | 8.17:1 | PASS | PASS |
| stoneGray on deepIndigo | 7.80:1 | PASS | PASS |
| charcoalBlack on warmIvory | 15.71:1 | PASS | PASS |
| charcoalBlack on sandstone | 13.04:1 | PASS | PASS |
| warmIvory on charcoalBlack | 15.71:1 | PASS | PASS |
| warmIvory on deepIndigo | 14.99:1 | PASS | PASS |

Three role strings actively endorse a failing text use:

- `palette/colors.json:14` — stoneGray role `"Neutral metadata text, dividers, captions"`.
  On the default ivory ground that is **1.92:1** — fails body and large.
- `guidelines/brand-book.md:91` — stoneGray `"Supporting copy that should not compete."`
- `README.md:81` — stoneGray `"Captions, metadata, low-emphasis text"`.
- `guidelines/usage-rules.md:50` — `"Quiet supporting copy: stone gray (#B8B1A4)."`

And one specimen panel endorses gold-on-ivory display without a contrast caveat:

- `previews/wordmark-specimen.html:96` — panel head `"2 · All-gold — premium / ceremonial"`,
  rendering `fill="#C8A15A"` text on the panel's ivory body (2.18:1).

The CI gate `brand/tools/contrast.py` currently *masks* the problem: a prior edit
demoted the three failing text pairs to `claimed use="decorative"` (no minimum), so the
gate exits 0 and ratifies the failures instead of catching them. The claimed-use table
must be re-stated to match the corrected rules so the gate has teeth again.

This finding fixes the **rules, role strings, the one specimen panel head, and the
gate's claimed-use table**. It does NOT retrofit the rendered stone-gray caption text in
the mockups (`donation-receipt.html`, `lockups-specimen.html`, `index.html`, etc. — small
11–26px stone text at 1.92:1); those rendered failures are downstream usages owned by the
asset-regeneration work, but they are listed under Residual risk so US-16 can route them.

## Files touched

1. `brand/guidelines/usage-rules.md` — replace §4 (Color rules) with a thresholds block + a
   full pairing table with permitted uses.
2. `brand/palette/colors.json` — rewrite the `role` strings for `antiqueGold`, `bronze`,
   `stoneGray`, and `sandstone` so none implies a text use that fails on its stated ground.
3. `brand/guidelines/brand-book.md` — qualify the `--rtam-gold`, `--rtam-bronze`, and
   `--rtam-stone` role cells in the §4 table (lines 85, 90, 91) with their contrast budget;
   fix the `donation-lockup.svg` row (line 69) which endorses a quiet **stone-gray line**
   (= stone-gray text on the lockup's ivory ground, 1.92:1 — a failing pair); and add a
   contrast caveat to the open-form variant bullet (line 51) that implicitly blesses the
   all-gold wordmark on a plain (ivory) ground.
4. `brand/README.md` — fix the `--rtam-stone` role cell (line 81).
5. `brand/previews/wordmark-specimen.html` — amend the panel-2 head (line 96) so it no longer
   endorses gold-on-ivory legibility; add the contrast caveat.
6. `brand/tools/contrast.py` — restate the `pairs` claimed-use table to match the new rules
   (the three failing text pairs return to their true claimed use so the gate fails on
   regression), add the large-text pairs, and tighten the report wording.

## Exact change

### 1 · `brand/guidelines/usage-rules.md` — replace the whole of §4

Replace lines 44–53 (the `## 4 · Color rules` block, from the heading through the closing
`---`) with:

```markdown
## 4 · Color rules

**Grounds.** Default ground: **ivory** (`#F7F3E9`). Sacred ground: **indigo** (`#1C1A3D`).
Dark UI ground: **charcoal** (`#1A1A1A`).

**Contrast budget (WCAG 2.x).** Every text or essential-graphic pairing must clear:
- **4.5:1** for body / small text (anything under 24 px, or under 18.66 px bold).
- **3:1** for large text (≥ 24 px, or ≥ 18.66 px bold) and for essential graphics / UI strokes.
- Purely decorative ink (watermarks, the seal field, dividers that carry no information) has
  no minimum, but may never be the only thing distinguishing one state from another.

Run `python brand/tools/contrast.py` before shipping any new pairing; it gates CI.

**Permitted pairings** (computed ratios — do not re-derive by eye):

| Foreground | Ground | Ratio | Permitted use |
|---|---|---|---|
| charcoal `#1A1A1A` | ivory `#F7F3E9` | 15.71:1 | body, large, graphics |
| charcoal | sandstone `#E6DED1` | 13.04:1 | body, large, graphics |
| ivory `#F7F3E9` | charcoal | 15.71:1 | body, large, graphics |
| ivory | indigo `#1C1A3D` | 14.99:1 | body, large, graphics |
| gold `#C8A15A` | charcoal | 7.21:1 | body, large, graphics |
| gold | indigo | 6.88:1 | body, large, graphics |
| stone `#B8B1A4` | charcoal | 8.17:1 | body, large, graphics |
| stone | indigo | 7.80:1 | body, large, graphics |
| bronze `#9B6A2F` | ivory | 4.21:1 | **large & graphics only** — not body |
| bronze | sandstone | 3.50:1 | **large & graphics only** — not body |
| gold `#C8A15A` | ivory | 2.18:1 | **decorative only** — bindu, rules, fills; never text or essential graphics |
| gold | sandstone | 1.81:1 | **decorative only** |
| stone `#B8B1A4` | ivory | 1.92:1 | **decorative only** — dividers, panel chrome; never text |

Consequences you must respect:
- **Stone gray is not a text color on ivory.** For quiet metadata / captions on a light
  ground, use **charcoal at reduced size/weight** (Inter 300), not stone gray. Stone gray
  is text-legible only on charcoal or indigo grounds.
- **Bronze is large/graphics only on ivory** — emphasis headings and rules, never body copy.
- **Gold is decorative on ivory** — the bindu, gold rules, gold fills. The all-gold wordmark
  on ivory reads as a *ceremonial decorative treatment, not a legibility-grade mark*; when
  the mark must be read, put gold on charcoal or indigo, or use the charcoal+gold canonical
  mark.
- The wordmark MUST still reproduce in pure `#1A1A1A` — this is the reproduction floor.

---
```

### 2 · `brand/palette/colors.json` — role strings

Replace these four `role` values verbatim (hex/rgb unchanged):

- `antiqueGold` (line 6):
  `"role": "Sacred accent — bindu, gold rules, fills. Decorative on ivory/sandstone (2.18:1 / 1.81:1 — not text); text-legible only on charcoal (7.21:1) or indigo (6.88:1)."`
- `sandstone` (line 9):
  `"role": "Secondary surface, paper texture, low-contrast separators. Surface only — do not place gold or bronze body text on it."`
- `bronze` (line 13):
  `"role": "Optional accent — heavier weight than gold for print on ivory. Large text & graphics only on ivory/sandstone (4.21:1 / 3.50:1); never body copy."`
- `stoneGray` (line 14):
  `"role": "Neutral dividers and panel chrome. Text-legible only on charcoal (8.17:1) or indigo (7.80:1) — NOT a text color on ivory (1.92:1)."`

### 3 · `brand/guidelines/brand-book.md` — §4 table cells

- Line 85 `--rtam-gold` role cell → `Antique gold. The bindu, gold rules, accents. Decorative on ivory (2.18:1) — not text; legible only on charcoal/indigo.`
- Line 90 `--rtam-bronze` role cell → `Deeper gold. Emphasis on ivory at large sizes only (4.21:1) — never body copy.`
- Line 91 `--rtam-stone` role cell → `Quiet stone gray. Dividers and chrome; text only on charcoal/indigo grounds (1.92:1 on ivory — not text there).`

Also fix line 69 (the `donation-lockup.svg` row). Replace:
```markdown
| `donation-lockup.svg` | Wordmark + thin gold rule + a single quiet stone-gray line. Header, not CTA. |
```
with:
```markdown
| `donation-lockup.svg` | Wordmark + thin gold rule + a single quiet **charcoal** line (Inter 300). Header, not CTA. (Stone gray on this ivory ground is 1.92:1 — decorative only, never this text line.) |
```

And add a contrast caveat to line 51 (open-form variant bullet). Replace:
```markdown
- **Open form** — gold / black / ivory variants for plain-background contexts.
```
with:
```markdown
- **Open form** — gold / black / ivory variants for plain-background contexts. The all-gold variant on ivory is a ceremonial *decorative* treatment (2.18:1, not legibility-grade); when the mark must be read on a light ground, use the charcoal-letters canonical mark.
```

### 4 · `brand/README.md` — line 81

Replace the `--rtam-stone` row's role cell with:
`Dividers, chrome; text only on dark grounds (fails on ivory)`

### 5 · `brand/previews/wordmark-specimen.html` — line 96

Replace the panel head text:

```html
    <div class="panel-head">2 · All-gold — premium / ceremonial</div>
```
with:
```html
    <div class="panel-head">2 · All-gold — premium / ceremonial. Decorative on ivory (2.18:1, not legibility-grade); for a readable gold mark use charcoal or indigo ground.</div>
```

### 6 · `brand/tools/contrast.py` — claimed-use table + report

Replace the `pairs` list (lines 39–49) and the docstring's exit-code line so the gate again
fails on any text pairing below its threshold. New `pairs` (the three former-"decorative"
text pairs return to their honest claimed use; large-only pairs get a new `"large"` class;
add the dark-ground stone pairs that the rules now bless):

```python
    # (fg, bg, claimed_use): 'body' must clear 4.5, 'large'/'graphics' 3.0,
    # 'decorative' has no minimum but is reported. claimed_use is the use the
    # brand DOCUMENTS for the pair; the gate fails if the ratio can't support it.
    pairs = [
        ("charcoalBlack", "warmIvory", "body"),
        ("charcoalBlack", "sandstone", "body"),
        ("warmIvory", "charcoalBlack", "body"),
        ("warmIvory", "deepIndigo", "body"),
        ("antiqueGold", "charcoalBlack", "body"),
        ("antiqueGold", "deepIndigo", "body"),
        ("stoneGray", "charcoalBlack", "body"),
        ("stoneGray", "deepIndigo", "body"),
        ("bronze", "warmIvory", "large"),
        ("bronze", "sandstone", "large"),
        ("antiqueGold", "warmIvory", "decorative"),
        ("antiqueGold", "sandstone", "decorative"),
        ("stoneGray", "warmIvory", "decorative"),
    ]
    minimum = {"body": 4.5, "large": 3.0, "graphics": 3.0, "decorative": 0.0}
```

And update the docstring (line 8) to:
`Exit code 1 if any pairing fails the threshold its documented use requires.`

The grade string (line 58) already reports the WCAG class; leave it. No other logic changes —
`failures` already increments whenever `r < minimum[use]`, so with the corrected table the
gate now PASSES on the truthful claims and would FAIL the moment anyone re-documents
gold-on-ivory or stone-on-ivory as text (raise its claimed use above `decorative`) or
bronze body text (raise it above `large`).

## Parameters resolved

- **Thresholds 4.5:1 (body) / 3:1 (large & graphics)** — WCAG 2.1 SC 1.4.3 (AA). Final, durable.
- **Large-text boundary = 24px regular / 18.66px (14pt) bold** — WCAG definition of "large
  scale"; stated so reviewers can classify a given run. Final.
- **gold/ivory = 2.18:1 → decorative only** — computed; below 3:1 so fails even large. Final.
- **gold/sandstone = 1.81:1 → decorative only** — computed. Final.
- **stone/ivory = 1.92:1 → decorative only (dividers/chrome), never text** — computed. Final.
- **stone/charcoal = 8.17:1, stone/indigo = 7.80:1 → body OK** — computed; this is the *only*
  legible text use for stone gray. Final.
- **bronze/ivory = 4.21:1, bronze/sandstone = 3.50:1 → large & graphics only, not body** —
  computed; both clear 3:1, neither clears 4.5:1. Final.
- **gold/charcoal = 7.21, gold/indigo = 6.88, charcoal/ivory = 15.71, charcoal/sandstone =
  13.04, ivory/charcoal = 15.71, ivory/indigo = 14.99** — computed; all body-safe. Final.
- **contrast.py claimed-use for the 3 failing pairs = `decorative`; bronze = `large`** —
  chosen so the gate ratifies exactly the permitted-uses table and fails on any future
  over-claim. Final.
- Replacement role strings, the §4 table, the brand-book/README cells, and the specimen
  head — all written verbatim above. No TBD.

## Proof

No proof PNG required (this finding is documentation + a numeric gate). Evidence is the
computed ratio set, reproducible by:

```
python brand/tools/contrast.py
```

Current (masked) output exits 0 with three failing text pairs labelled `decorative`. After
the change the same command still exits 0 — but the claimed-use table now matches the
permitted-uses rules, so re-documenting any failing pair as text would flip the gate to
exit 1. The numbers above were produced by this exact tool on the shipped `colors.json`.

## Verification steps

US-16 re-audit confirms the fix when ALL hold:

1. `grep -niE "caption|metadata|supporting copy|stone-gray line" brand/palette/colors.json brand/README.md brand/guidelines/brand-book.md` no longer attaches those words to stone gray
   without a "dark grounds only / not on ivory" qualifier; `brand-book.md:69` now reads
   "quiet **charcoal** line", not "stone-gray line".
2. `grep -n "premium / ceremonial" brand/previews/wordmark-specimen.html` returns the line,
   and that line now contains the substring `Decorative on ivory (2.18:1`.
3. `brand/guidelines/usage-rules.md` §4 contains the thresholds block and the permitted-uses
   table; every row's ratio matches `contrast.py` output to two decimals.
4. `python brand/tools/contrast.py` exits 0, prints a `claimed use=decorative` line for
   gold/ivory, gold/sandstone, stone/ivory and `claimed use=large` for both bronze pairs,
   and a `claimed use=body` line for stone/charcoal and stone/indigo.
5. Regression probe: temporarily flip `("stoneGray","warmIvory","decorative")` to `"body"`
   in `contrast.py` and confirm it then exits 1 (proves the gate has teeth). Revert.

## Residual risk

- **Rendered stone-gray caption text in mockups is still failing** and is NOT touched here:
  `donation-receipt.html` (11–13px stone), `lockups-specimen.html:125` / `index.html:292` /
  `donation-receipt.html:140` (the 26px `#B8B1A4` "CONTRIBUTIONS SUPPORT…" line, 1.92:1),
  plus `letterhead.html`, `website-header.html`, `certificate.html`, `favicon-scale-test.html`,
  and the monogram/devanagari specimens that set stone text on ivory. The corrected rules make
  the right call (use charcoal Inter 300 instead); applying it to each asset belongs to the
  asset-regeneration findings. US-16 should open a follow-up to swap these to charcoal.
- **Stone on indigo/charcoal in specimens** (e.g. `monogram-specimen.html:59-60`) is now
  explicitly blessed (8.17 / 7.80) — no action, but worth noting it was previously undocumented.
- **`README.md:80` bronze "Heavier accent for print"** is left unqualified: "accent" does not
  endorse body text, so it is a consistency nit rather than a failing-pair endorsement. If
  US-16 wants strict parity with the qualified bronze cells in `colors.json`/`brand-book.md`,
  append "(large/graphics only on ivory — 4.21:1)"; not required by this finding.
- WCAG 2.x ratios are independent of the typeface, so this fix is unaffected by a future
  Cinzel replacement; only the *large-text size boundary* interacts with type, and that is
  stated as the standard 24px/18.66px rule, not a Cinzel-specific number.

## Depends on

none. (Independent of the SVG/spec-generator findings; touches only docs, the palette role
strings, one specimen head, and the contrast gate.)

## Durable or provisional

**Durable.** Thresholds, computed ratios, permitted-uses table, and the gate are tied to the
fixed hex tokens and the WCAG standard, not to any letterform. If a Phase-2 palette changes a
hex, re-run `contrast.py` and update the table — the *rule structure* (thresholds + a gated
table) stays. The only provisional element is the specimen panel-2 wording, which lives in a
preview HTML that the generator may later emit; the rule it states is durable.
