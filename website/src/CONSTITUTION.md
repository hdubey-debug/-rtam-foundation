# The constitution — ṚTAM website

One rule generates everything: **depth = sanctity = darkness = simplicity.**
The site is the temple's own geography; you enter it, you don't browse it.
Rendered specimen: `dist/system.html` (not in the nav). Enforcement:
`website/tools/verify_site.py` — run before every commit; there is no CI, that is the gate.

## The axis — kṣetra to kṣetrajña

| depth | place | route | ground | gauge | footer |
|---|---|---|---|---|---|
| 0 | क्षेत्र THE LAND | `/` | chandra | chakra | fullest |
| 1 | सभा मंडप THE HALLS | `/seva/` `/utsava/` | bhasma | anāhata | thin |
| 2 | प्रदक्षिणा THE WALK | `/mandir/` | bhasma (mahakala bands) | anāhata | thin |
| 3 | गर्भगृह THE SANCTUM | `/darshana/` | mahakala | bindu | none |

**Recorded as interpretation, not quotation.** In Gītā 13 the kṣetra is the body
(इदं शरीरं … क्षेत्रम्). Reading the temple land and the temple as the field is the
founder's deliberate extension — consonant with the temple-as-body tradition (the
garbhagṛha is the womb-house; the murti codex maps sanctum → chest), but an extension.
On-site the line is cited as **भगवद्गीता · अध्याय १३**, no verse number (2 vs 3 varies
by recension). Paṇḍita review is invited, not assumed.

## Color law

- Palette canon: `brand/palette/colors.css` (generated from `colors.json`). 
- **Color literals live only on token-definition lines in `system.css`** — the canon
  section (values that must equal the palette file) plus the **effect registry**
  (`--fx-*`: foil ramp stops, halo alphas) plus the per-layer token blocks.
  Everywhere else: `var()`. Keywords `transparent` / `currentColor` are permitted.
- **Accent law — essential text per layer:** land: tamra `#7A5423` · halls/walk:
  ink `#1A1A1A` · sanctum: gold `#C8A15A` on mahakala. **Gold is decorative-only
  outside mahakala** (dots, rules, foil sheen — never running text).
- **Foil** is a specular state of dīpa gold, not a palette addition: a sheen over a
  readable base. Still page = still gold; reduced motion = plain `--foil-still`;
  browsers without `background-clip:text` get the plain base color.

## Type law

- Three faces: **Tiro** (Devanagari) · **Cinzel** (English display caps) ·
  **Inter** (body/UI). Marcellus is print-only — stated, not drifted.
- The couplet: sūtra (Tiro) first, bhāṣya (Cinzel caps) beneath. Never reversed.
- `lang="sa"` on Sanskrit, `lang="hi"` on Hindi — tagged by language, not script
  (`-Deva` is redundant per BCP-47 suppress-script).
- Fonts ship as **WOFF2 subsets only** — built from every shipped string plus
  shaping controls; full-face TTFs never leave `brand/fonts/`.

## Motion law

- One grammar: **contraction toward Him.** The budget increases with depth; the land
  is stillest and paints instantly; the sanctum moves most.
- Four verbs only: flame kindles · stone settles · thread draws · veil parts.
  The threshold (a hairline the flame is passed along, once) is verb 4's hairline form.
- The gauge morphs **once per threshold crossing** (700ms, opacity only), otherwise
  the header is still. `@view-transition` upgrades the crossing where supported.
- **One dominant action per view.** The nav's दर्शन carries a drawn bindu dot,
  never gilding. The veil never covers the LCP hero.
- `prefers-reduced-motion`: everything meaningful remains — statically.

## Structure law

- Five pages, no more. The axial door chain: land → `/mandir/` → `/darshana/`;
  the halls hang off the nav and the land's stones.
- The sanctum header carries **no OFFER and no inline nav** — gauge, brand,
  गर्भगृह, MENU. Sevā stays one menu tap away. No footer in the sanctum.
- Brand wordmark always routes home. The poetic exit (bindu → land) is the
  sanctum's addition, not a replacement.
- All internal hrefs are **relative** — the same dist works at a domain root, a
  GitHub Pages project path, and locally. Folder routes need a server:
  `python3 -m http.server -d website/dist`.

## Honesty law

- Draft builds show bracketed `[placeholders]` and sample-flagged dates.
- `build.py --production` **refuses to write** if any visible bracket, dead donation
  link, or unconfirmed date would ship; sections built to degrade (the year-wheel's
  "dates upon pañchāṅga confirmation" state) degrade instead.
- The landing states plainly: निर्माणाधीन, under construction; the hero is an
  architectural render and says so; ṚTAM Foundation is the steward.
- The murti reference photograph is design intent, **never distribution** — the
  sanctum shows the parametric construction drawing until prāṇa-pratiṣṭhā.

## The gates (`verify_site.py`)

A color law · B face law · C computed WCAG contrast on every text-token/ground pair
(≥4.5:1 body, ≥3:1 large display) · D live page probes (ground painted, gauge stage,
zero console errors, zero external requests) · E every link/asset resolves in-dist ·
F placeholder honesty vs build mode · G WOFF2-only under the byte cap.
