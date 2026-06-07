# F12 — No dark-ground story + a11y suppression

## Root cause

Two independent defects, both systemic across the 21 shipped assets.

**(a) No dark-ground story.** The brand declares indigo (`#1C1A3D`) a first-class
"sacred night" surface (`palette/colors.json`, `usage-rules.md` §4) and charcoal
(`#1A1A1A`) the dark-mode surface — yet almost nothing is built to live on them:

- All 4 **lockups** and `rtam-wordmark-sacred-RTAM-dot.svg` hardcode `fill="#1A1A1A"`
  on every `<text>`. On charcoal the letters render charcoal-on-charcoal (contrast
  ratio **1.00**) and vanish; on indigo they are near-invisible ghosts (≈1.05).
  Proof `F12-sacred-wordmark-matrix.png` / `F12-temple-lockup-matrix.png` show this
  directly: on charcoal only the gold bindu / gold rule survive.
- The **circle-gold icon** (`rtam-rdot-icon-circle-gold.svg`) and the **ऋ-circle**
  (`rtam-devanagari-ri-icon-circle.svg`) place a *charcoal* glyph inside a gold ring.
  The ring reads on dark; the glyph inside disappears — a hollow gold ring.
- The **favicon** hardcodes a charcoal `R`; on a dark browser-tab strip it is
  invisible (its own `<desc>` even says "swap the dark color via CSS" but ships no
  mechanism to do so).

**(b) Overlay suppression via baked grounds.** The three `-white` variants
(`rtam-wordmark-white.svg`, `rtam-rdot-icon-white.svg`,
`rtam-devanagari-ri-icon-white.svg`) each bake a *full-bleed opaque*
`<rect ... fill="#1A1A1A"/>`. The mark is therefore NOT overlay-ready: dropped onto
indigo or a photo it punches an identical charcoal hole regardless of what is behind
it (proof `F12-overlay-ready-matrix.png`, CURRENT row — the same black box appears on
ivory, charcoal, indigo and photo). `usage-rules.md` §1 documents the workaround as a
manual hand-edit: *"For indigo / photographic overlays, remove the first `<rect>` in
the SVG."* Asking every consumer to hand-edit XML is the defect.

**(c) a11y suppression.** Every shipped SVG carries `role="img"` **plus**
`aria-label="…"`. Per ARIA, an explicit `aria-label` on the element wins and the
rich `<title>`/`<desc>` already authored in each file are dropped from the
accessibility tree. The kit pays the cost of authoring good `<title>`/`<desc>` and
then suppresses them. (`aria-label` is also Latin-transliteration-only, e.g.
`"ṚTAM Foundation"`, so screen-reader users never get the Devanagari that `<title>`
carries in the lockups.)

These are durable architecture/contrast facts, independent of the Cinzel letterform.

---

## Files touched

This fix is realized inside the target generator (`brand/tools/generate.py` +
`brand/spec/brand.json`); the file list below is the **emitted-SVG manifest** the
generator must produce. "(edit)" = an existing shipped path whose bytes change;
"(NEW)" = a new path the generator adds.

### A. a11y pattern — applies to ALL 21 existing assets (edit)
Every emitted SVG drops `aria-label` and gains `aria-labelledby` + `aria-describedby`
(snippet in *Exact change* §1). No new files; the change is to the `<svg>` open tag
and the `id=` attributes on the existing `<title>`/`<desc>` of all 21 files.

### B. Remove baked grounds — overlay-readiness (edit, 3 files)
- `logos/rtam-wordmark-white.svg` — delete the comment + opaque `<rect>` (lines 7–9).
- `icons/rtam-rdot-icon-white.svg` — delete the comment + opaque `<rect>`.
- `icons/rtam-devanagari-ri-icon-white.svg` — delete the comment + opaque `<rect>`.
After this edit, `-white` = transparent all-ivory knockout (true overlay; the dark
analog of `-black`).

### C. New `-on-dark` two-color variants (NEW, 7 files)
Ivory letters `#F7F3E9` + gold bindu/rule `#C8A15A`, transparent ground.
- `logos/rtam-wordmark-sacred-RTAM-dot-on-dark.svg`
- `logos/rtam-wordmark-public-RTAM-on-dark.svg`  *(no bindu; ivory letters only)*
- `lockups/rtam-bilingual-foundation-on-dark.svg`
- `lockups/rtam-sanskritic-pratishthan-on-dark.svg`
- `lockups/rtambhareshvara-mandir-lockup-on-dark.svg`
- `lockups/donation-lockup-on-dark.svg`
- `icons/favicon-on-dark.svg`  *(see §F for the favicon decision)*

### D. New enclosed (ring) on-dark variants (NEW, 2 files)
Ivory glyph + gold ring + gold bindu, transparent ground.
- `icons/rtam-rdot-icon-circle-gold-on-dark.svg`
- `icons/rtam-devanagari-ri-icon-circle-on-dark.svg`

### E. Assets that need NO new file (enumerated so the matrix has zero gaps)
| Asset | Why no on-dark file |
|---|---|
| `logos/rtam-wordmark-gold.svg` | all-gold, transparent ground; gold passes ≥3 on charcoal (7.21) & indigo (6.88). Ground-agnostic. |
| `logos/rtam-wordmark-black.svg` | single-color mono floor; light-only by definition (the dark analog *is* `-white`). |
| `icons/rtam-rdot-icon-gold.svg` | all-gold, transparent. Ground-agnostic. |
| `icons/rtam-rdot-icon-black.svg` | mono, light-only. |
| `icons/rtam-rdot-icon-circle-charcoal.svg` | all-charcoal mono seal, light-only by definition. |
| `icons/rtam-devanagari-ri-icon-gold.svg` | all-gold, transparent. Ground-agnostic. |
| `icons/rtam-devanagari-ri-icon-black.svg` | mono, light-only. |
| `seal/rtam-12-medallion-seal.svg` | all-gold on transparent (verified: no opaque ground). Ground-agnostic. |
| `seal/rtam-12-medallion-pattern.svg` | all-gold tile fill on transparent (the `<rect fill="url(#tile)">` is the pattern paint, not an opaque ground). Ground-agnostic. |
| `logos/rtam-wordmark-public-RTAM.svg` | light-only original kept; its dark analog is the new §C `-on-dark`. |

Net: **9 new files**, **24 file-edits** (3 rect removals + 21 a11y swaps; the 3 rect
files are counted in both groups). Every one of the 21 assets is accounted for.

---

## Exact change

### §1 — a11y pattern (apply to every emitted SVG)

Replace the current pattern:
```xml
<svg ... role="img" aria-label="ṚTAM Foundation">
  <title>…</title>
  <desc>…</desc>
```
with **labelledby → title (concise NAME), describedby → desc (long description)**, using
**IDs derived from the file stem** so they stay unique when many SVGs are inlined into
one consumer page:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 240"
     role="img"
     aria-labelledby="rtam-wordmark-sacred-RTAM-dot-title"
     aria-describedby="rtam-wordmark-sacred-RTAM-dot-desc">
  <title id="rtam-wordmark-sacred-RTAM-dot-title">ṚTAM Foundation</title>
  <desc  id="rtam-wordmark-sacred-RTAM-dot-desc">Primary wordmark…</desc>
```
Rules the generator must enforce:
- ID = `{file-stem}-title` / `{file-stem}-desc`. Stem-derived (not `t`/`d`) because
  this kit is inlined into pages that compose several marks at once
  (`previews/index.html` already does); duplicate `id="t"` would make every
  `aria-labelledby` bind to the first `<title>` on the page — silent a11y corruption.
- `aria-labelledby` points at **title only**; `aria-describedby` points at **desc
  only**. Do NOT fold `desc` into `labelledby` — that dumps the whole paragraph into
  the accessible *name*. Name = concise label; description = the prose.
- The `<title>` text becomes the canonical concise name; for bilingual lockups keep
  both scripts in `<title>` (e.g. `Rtambhareshvara Mandir · ऋतम्भरेश्वर मंदिर`) so
  screen-reader users get the Devanagari that `aria-label` was dropping.
- `aria-label` is **removed entirely** from all 21 files.

### §2 — Remove baked grounds (3 `-white` files)

Delete these exact lines from each (example = `rtam-wordmark-white.svg`):
```xml
  <!-- Charcoal ground so the ivory wordmark is visible when the file is opened standalone.
       Remove this rect to overlay the ivory mark on an indigo or photographic surface. -->
  <rect x="0" y="0" width="1080" height="240" fill="#1A1A1A"/>
```
(icon files: same comment + `<rect ... width="256" height="256" fill="#1A1A1A"/>`).
Nothing else changes; the ivory letters/bindu and the `<circle>` bindu stay. Result:
transparent-ground all-ivory knockout, overlay-ready.

### §3 — New `-on-dark` wordmark/lockup variants (§C)

Each is a byte-for-byte clone of its light sibling with **only the fills changed** and
the a11y pattern applied. Canonical example —
`logos/rtam-wordmark-sacred-RTAM-dot-on-dark.svg`:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 240"
     role="img"
     aria-labelledby="rtam-wordmark-sacred-RTAM-dot-on-dark-title"
     aria-describedby="rtam-wordmark-sacred-RTAM-dot-on-dark-desc">
  <title id="rtam-wordmark-sacred-RTAM-dot-on-dark-title">ṚTAM Foundation</title>
  <desc  id="rtam-wordmark-sacred-RTAM-dot-on-dark-desc">Sacred wordmark, on-dark variant. Ivory letters #F7F3E9, gold bindu #C8A15A. Transparent ground — overlay on charcoal, indigo, or a quiet dark surface. The bindu stays gold (it is the brand signature, never recolored away independently).</desc>
  <defs><style type="text/css">@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600&amp;display=swap');</style></defs>
  <g font-family="Cinzel, Marcellus, 'Trajan Pro', serif" fill="#F7F3E9">
    <text x="80" y="160" font-size="120" font-weight="500" letter-spacing="12">RTAM</text>
    <text x="540" y="160" font-size="62" font-weight="400" letter-spacing="8">Foundation</text>
  </g>
  <circle cx="118" cy="188" r="10" fill="#C8A15A"/>
</svg>
```
Fill rules for the family (everything else — coords, font-size, letter-spacing,
viewBox, the gold rule lines — is identical to the light sibling):

| New file | `<text>` fill(s) | bindu `<circle>` | rule `<line>` |
|---|---|---|---|
| `rtam-wordmark-sacred-RTAM-dot-on-dark` | `#F7F3E9` | `#C8A15A` | — |
| `rtam-wordmark-public-RTAM-on-dark` | `#F7F3E9` | (none — no-bindu variant) | — |
| `rtam-bilingual-foundation-on-dark` | both `<text>` `#F7F3E9` | `#C8A15A` | `#C8A15A` (unchanged) |
| `rtam-sanskritic-pratishthan-on-dark` | both `<text>` `#F7F3E9` | `#C8A15A` | `#C8A15A` (unchanged) |
| `rtambhareshvara-mandir-lockup-on-dark` | both `<text>` `#F7F3E9` | — | `#C8A15A` (unchanged) |
| `donation-lockup-on-dark` | RTAM/Foundation `#F7F3E9`; supporting line `#B8B1A4` (stone gray, contrast 8.17 on charcoal / 7.80 on indigo — passes) | `#C8A15A` | `#C8A15A` (unchanged) |

### §4 — New enclosed on-dark variants (§D)

`icons/rtam-rdot-icon-circle-gold-on-dark.svg` — clone of `…-circle-gold.svg`, change
only the glyph + bindu fills; keep the gold ring and the geometry:
```xml
  <circle cx="128" cy="128" r="118" fill="none" stroke="#C8A15A" stroke-width="5"/>
  <text x="128" y="178" font-family="Cinzel, Marcellus, 'Trajan Pro', serif"
        font-weight="600" font-size="170" text-anchor="middle" fill="#F7F3E9">R</text>
  <circle cx="128" cy="207" r="11" fill="#C8A15A"/>
```
`icons/rtam-devanagari-ri-icon-circle-on-dark.svg` — clone of `…-ri-icon-circle.svg`:
```xml
  <circle cx="128" cy="128" r="118" fill="none" stroke="#C8A15A" stroke-width="5"/>
  <text x="128" y="210" font-family="'Tiro Devanagari Sanskrit', 'Noto Serif Devanagari', serif"
        font-size="180" text-anchor="middle" fill="#F7F3E9">ऋ</text>
```
(Glyph `#1A1A1A` → `#F7F3E9`; ring/bindu stay gold.)

### §5 — Favicon dark story (§F decision)

Ship **both** a self-adapting primary AND a static `-on-dark` companion:
- **Primary `icons/favicon.svg` (edit):** the favicon path is fixed in every
  consumer's `<link rel="icon">`, so a *second file* cannot be swapped per theme by the
  browser. Add an in-SVG media query so the single referenced file adapts:
  ```xml
  <defs><style type="text/css">
    @media (prefers-color-scheme: dark) {
      #favicon-R { fill: #F7F3E9; }
    }
  </style></defs>
  <text id="favicon-R" x="16" y="22" font-family="Cinzel, Marcellus, 'Trajan Pro', serif"
        font-weight="700" font-size="26" text-anchor="middle" fill="#1A1A1A">R</text>
  <circle cx="16" cy="27.5" r="2.2" fill="#C8A15A"/>
  ```
  (Bindu stays gold in both themes — passes on charcoal and ivory.)
- **`icons/favicon-on-dark.svg` (NEW):** the same mark with `fill="#F7F3E9"` baked, for
  PWA manifests / `<link media="(prefers-color-scheme: dark)">` consumers that prefer an
  explicit asset over a media query. Listed in §C.

### §6 — Suffix / naming convention (the rule that resolves `-white` vs `-on-dark`)

Conformant with the existing files and Rule 8 (pick one pattern, state it):
- **Single-color marks keep COLOR suffixes:** `-black` (all-charcoal),
  `-white` (all-ivory), `-gold` (all-gold), `-circle-charcoal`. `-white` is the
  *single-color* dark knockout — the dark analog of `-black`. No bindu/letter color split.
- **Two-color brand marks get SEMANTIC suffixes:** `sacred` (charcoal letters + gold
  bindu), `-on-dark` (ivory letters + gold bindu). `-on-dark` is the *two-color* dark
  variant — the dark analog of `sacred`. The bindu/rule stays gold.

So `-white` and `-on-dark` are **not** duplicates: `-white` is a flat knockout for
single-color reproduction on dark; `-on-dark` is the full-color brand mark for dark
surfaces. Both ship. (`-on-dark` is preferred for normal dark-surface use; `-white`
remains for foil-knockout / single-channel dark printing.)

---

## Parameters resolved

| Parameter | Value | Rationale |
|---|---|---|
| On-dark letter fill | `#F7F3E9` (warmIvory) | 15.7:1 on charcoal, 15.0:1 on indigo — far above the 3:1 graphics floor; the brand's named ivory, not pure white. |
| On-dark bindu / ring / rule fill | `#C8A15A` (antiqueGold) | 7.21:1 on charcoal, 6.88:1 on indigo (both ≥3). Bindu must never be recolored away from gold independently (usage-rules §7). |
| Number of dark *ground* variants per asset | **1** (single `-on-dark`) | charcoal and indigo are both dark grounds where ivory+gold passes; one transparent variant overlays charcoal, indigo, AND any quiet dark photo. We do NOT ship separate `-charcoal`/`-indigo` files — variants are keyed by light-vs-dark, not by ground hue. Durable ratio-as-rule. |
| New files | **9** | 7 §C + 2 §D (favicon-on-dark is inside the 7). Enumerated above; no asset left without either a new file or a stated reason. |
| Edited files | **24** | 21 a11y swaps + 3 baked-rect removals (the 3 overlap the 21). |
| `donation-lockup-on-dark` supporting-line fill | `#B8B1A4` (stoneGray) | 8.17:1 on charcoal, 7.80:1 on indigo — passes 4.5:1 body floor; keeps the "quiet" hierarchy of the light original (which uses the same token). |
| Ground `<rect>` in `-white` files | **removed** | overlay-readiness; transparent ground is the fix. |
| a11y binding | `aria-labelledby={stem}-title` + `aria-describedby={stem}-desc` | name vs description split is the correct ARIA mapping; stem-scoped IDs avoid collisions across inlined SVGs. |
| `aria-label` | **removed** from all 21 | it suppresses `<title>`/`<desc>` and is Latin-only. |
| Favicon dark mechanism | in-SVG `@media (prefers-color-scheme: dark)` on `#favicon-R` + a baked `favicon-on-dark.svg` companion | favicon `<link href>` is fixed, so the browser can't swap files per theme; a media query adapts the single referenced file. Companion file serves manifest/`media`-attr consumers. |

No "TBD" remains.

---

## Proof

Faithful renders (Chromium + `document.fonts.ready` + 700ms settle; network @import).
Each sheet is a 2×4 matrix — CURRENT (shipped) vs SPEC'D (F12), across
ivory / charcoal / indigo / photo grounds. Script:
`brand/tools/_scratch/f12_proof.py`.

- `brand/explorations/_research/fix-specs/proofs/F12-sacred-wordmark-matrix.png`
  — **CURRENT:** the sacred wordmark is crisp on ivory but its letters vanish on
  charcoal (only the gold bindu floats, orphaned), are ghost-faint on indigo, and
  unreadable on photo. **SPEC'D:** the `-on-dark` variant is correctly invisible on
  ivory (its light sibling owns that ground) and reads cleanly in ivory-letters +
  gold-bindu on charcoal, indigo, and the quiet photo.
- `brand/explorations/_research/fix-specs/proofs/F12-temple-lockup-matrix.png`
  — **CURRENT:** the temple lockup hardcodes `#1A1A1A`, so on charcoal only the gold
  rule survives and both scripts disappear; indigo/photo are ghosts. **SPEC'D:** ivory
  Latin + Devanagari + gold rule, legible on every dark ground. Demonstrates a lockup
  that had ZERO dark variant now has one.
- `brand/explorations/_research/fix-specs/proofs/F12-overlay-ready-matrix.png`
  — **CURRENT:** the `-white` baked rect shows the *identical opaque charcoal box* on
  ivory, charcoal, indigo AND photo — proving it is not overlay-ready; it ignores the
  surface behind it. **SPEC'D:** rect removed → transparent on ivory (correctly the
  light mark's ground) and the ivory wordmark sits directly on the true indigo and
  photo grounds. This is the overlay-readiness fix made visible.

---

## Verification steps

For the US-16 re-audit:

1. **a11y suppression closed.** Grep every emitted SVG: `grep -L 'aria-label='` must
   match ALL 21+9 files (i.e. zero retain `aria-label`); each must contain
   `aria-labelledby="{stem}-title"`, `aria-describedby="{stem}-desc"`, and matching
   `<title id="{stem}-title">` / `<desc id="{stem}-desc">`. IDs must be unique within
   each file and stem-derived (no bare `id="t"`/`id="d"`).
2. **No baked grounds.** No file under `logos/`, `icons/`, `lockups/` contains a
   full-bleed opaque `<rect ... fill="#1A1A1A"/>` (or any opaque background rect
   covering the viewBox). The seal `<rect fill="url(#…)">` pattern paint is exempt.
3. **Dark legibility, measured.** Re-run a contrast pass (extend `tools/contrast.py`
   semantics): for each `-on-dark` and `-white` file, letter fill vs both `#1A1A1A`
   and `#1C1A3D` must be ≥4.5:1; bindu/ring/rule gold vs both ≥3:1. All pass by the
   table above.
4. **Render gate.** Faithful-render each `-on-dark` file on charcoal and on indigo
   (the `measure_render.py` path); assert non-trivial ink (the mark is visible, not a
   charcoal-on-charcoal null). Re-render each `-white` file with NO injected ground and
   confirm transparency (alpha=0 outside the glyphs).
5. **Coverage.** Assert the emitted manifest contains all 9 new files and that every
   one of the 21 originals either has an `-on-dark` sibling or appears in the
   "no new file" table with its stated reason — no silent gaps.
6. **Favicon.** Assert `favicon.svg` contains the `prefers-color-scheme: dark` rule and
   that `favicon-on-dark.svg` exists with a baked ivory `R`.

---

## Residual risk

- **Photo ground is conditional, not unconditional.** The single transparent
  `-on-dark` variant is guaranteed only where contrast is guaranteed — charcoal and
  indigo. On a *busy* photo it can still fail locally, and `usage-rules.md` §9 already
  bans the wordmark on busy photos. The proof used a *quiet dark scrim*; the spec'd
  variant assumes a dark scrim / quiet surface behind it. US-16 must not read "works on
  photo" as unconditional — a contrasting scrim or the existing photo-ban rule still
  applies.
- **ID collision with consumer page.** Stem-derived IDs are unique *across our files*
  but a host page could theoretically already use `rtam-wordmark-sacred-RTAM-dot-title`.
  Low risk given the specificity; a future hardening step could prefix with `rtam-`
  (already effectively the case for most stems).
- **`prefers-color-scheme` in favicons** has partial browser support for the in-SVG
  media query; the baked `favicon-on-dark.svg` companion is the fallback for engines
  that ignore it.
- **Variant proliferation.** 9 new files roughly +40% asset count; mitigated because
  they are generator-emitted (one spec entry → light + on-dark pair), not hand-authored.

---

## Depends on

- **Soft dependency on the generator finding** (the F-number that establishes
  `brand/spec/brand.json` + `brand/tools/generate.py`): this spec is expressed as
  generator output. If applied to the legacy hand-authored tree instead, the same
  edits/new-files apply file-by-file with no logic change.
- **Coordinate with the contrast finding** (the F-number auditing gold-on-ivory): note
  that `rtam-wordmark-gold.svg` / `rtam-rdot-icon-gold.svg` fail 3:1 *on ivory* (2.18) —
  that is a separate finding; F12 only relies on gold passing on the **dark** grounds,
  which it does (7.21 / 6.88).
- Otherwise **none** — the a11y swap and rect removal are self-contained.

---

## Durable or provisional

**Durable.** The variant matrix, the one-`-on-dark`-per-asset rule (keyed by
light/dark rather than ground hue), the overlay-ready "no baked ground" pattern, the
suffix convention, and the `role=img` + `aria-labelledby`/`aria-describedby` a11y
pattern are all architecture- and ratio-level decisions independent of the Cinzel
letterform. A Phase-2 letterform swap changes the glyph outlines but not which fills go
on which ground, nor the a11y structure. The only provisional numbers are the literal
glyph coordinates inherited from the light siblings (font-size, letter-spacing, bindu
`cx/cy/r`), which are already provisional in their source files and are copied
unchanged.
